from copy import deepcopy
import io
import json
import math
import os
import random
import traceback
from typing import Dict
import numpy as np
import torch
from PIL import Image, UnidentifiedImageError
from namo.dataset import expand2square
from namo.models.symbols import IGNORE_INDEX
from typing import Dict

from torch.utils.data import ConcatDataset, WeightedRandomSampler
from loguru import logger
from namo.utils import convs as conversation_lib

import torch.nn.functional as F
import torchvision.transforms as T
from torchvision.transforms.functional import InterpolationMode
from torch.utils.data import Dataset
from namo.utils.utils import is_main_process, rank0_print


class WeightedConcatDataset(ConcatDataset):
    def __init__(self, datasets, weights):
        super().__init__(datasets)
        self.weights = torch.DoubleTensor(weights)
        self.total_size = sum(len(d) for d in datasets)
        self.sampler = WeightedRandomSampler(
            weights=self.weights, num_samples=self.total_size, replacement=True
        )

    def __iter__(self):
        return iter(self.sampler)

    def __len__(self):
        return self.total_size


def dpo_concat_pad_data_collator(features, pad_id=0):

    first = features[0]
    batch = {}

    for prefix in ["chosen_", "rejected_"]:
        batch_lens = [feat[f"{prefix}input_ids"].shape[0] for feat in features]
        max_item_length = max(batch_lens)
        for idx in range(len(features)):
            feat = features[idx]
            temp_input_ids = torch.LongTensor([pad_id] * max_item_length)
            temp_input_ids[: feat[f"{prefix}input_ids"].shape[0]] = feat[
                f"{prefix}input_ids"
            ]
            feat[f"{prefix}input_ids"] = temp_input_ids
            temp_labels = torch.LongTensor([IGNORE_INDEX] * max_item_length)
            temp_labels[: feat[f"{prefix}labels"].shape[0]] = feat[f"{prefix}labels"]
            feat[f"{prefix}labels"] = temp_labels
            feat[f"{prefix}attention_mask"] = feat[f"{prefix}input_ids"].ne(pad_id)

    # Handling of all other possible keys.
    # Again, we will use the first element to figure out which key/values are not None for this model.
    for k, v in first.items():
        if (
            k
            not in (
                "pixel_values",
                "image_flags",
                "spatial_shapes",
                "pixel_attention_mask",
            )
            and v is not None
            and not isinstance(v, str)
        ):
            if isinstance(v, torch.Tensor):
                batch[k] = torch.stack([f[k] for f in features])
            elif isinstance(v, np.ndarray):
                batch[k] = torch.tensor(np.stack([f[k] for f in features]))
            else:
                batch[k] = torch.tensor([f[k] for f in features])
        if k in (
            "pixel_values",
            "image_flags",
            "spatial_shapes",
            "pixel_attention_mask",
        ):
            if isinstance(v, torch.Tensor):
                batch[k] = torch.concat([f[k] for f in features])
            elif isinstance(v, np.ndarray):
                batch[k] = torch.concat(np.stack([f[k] for f in features]))
            else:
                batch[k] = torch.concat([f[k] for f in features])
    # print(batch)
    # print("------batch")
    # for k, v in batch.items():
    #     print(f"{k} {v.shape} {v.dtype}")
    # print("------batch")
    return batch


class LazySupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(
        self,
        template_name,
        meta,
        tokenizer,
        tcs_loader,
        ds_name,
        num_image_token,
        image_size=448,
        image_processor=None,
        is_train=True,
        group_by_length=False,
        min_num_frame=8,  # for video data
        max_num_frame=32,  # for video data
        sampling_method="rand",  # for video data
        repeat_time=1,
        normalize_type="imagenet",
        random_seed=0,
    ):
        super(LazySupervisedDataset, self).__init__()
        self.ds_name = ds_name
        self.tokenizer = tokenizer
        self.template_name = template_name
        self.num_image_token = num_image_token
        if is_main_process():
            logger.info(f"[Dataset] num_image_token: {num_image_token}")

        self.image_size = image_size
        self.is_train = is_train
        self.max_num_frame = max_num_frame
        self.min_num_frame = min_num_frame
        self.sampling_method = sampling_method

        self.image_processor = image_processor

        if is_main_process():
            logger.info("Formatting inputs...Skip in lazy mode")

        assert meta["annotation"].endswith(
            "jsonl"
        ), f'annotation must be jsonl, but got {meta["annotation"]}'
        # fixed
        self.root_path = "data/posttraining"
        meta["annotation"] = os.path.join(self.root_path, meta["annotation"])

        with open(meta["annotation"], "r") as f:
            self.raw_data = f.readlines()
            if repeat_time < 1:
                # If repeat_time is less than 1, select a portion of the data
                self.raw_data = random.sample(
                    self.raw_data, k=int(len(self.raw_data) * repeat_time)
                )
            if repeat_time > 1:
                repeat_time = int(repeat_time)
                assert isinstance(repeat_time, int)
                # Repeat the list if repeat_time is greater than 1
                self.raw_data = self.raw_data * repeat_time

        self.rng = np.random.default_rng(seed=random_seed)
        self.rng.shuffle(self.raw_data)

        self.root = os.path.join(self.root_path, meta["root"])
        self.cached_data_dict = {}
        self.tcs_loader = tcs_loader
        self.group_by_length = group_by_length

        self.normalize_type = normalize_type

        # If the precomputed length does not exist, roughly estimate the length of
        # each sample to improve the efficiency of group_by_length.
        if self.group_by_length:
            self.conv2length = (
                {}
            )  # Using a dictionary to speed up token length calculation
            self.length = []
            for data_item in self.raw_data:
                data_item = json.loads(data_item)
                if "length" in data_item:
                    token_length = data_item[
                        "length"
                    ]  # Use precomputed length if available
                else:
                    # Compute token length using the tokenizer
                    conversations = "\n".join(
                        [temp["value"] for temp in data_item["conversations"]]
                    )
                    str_length = len(conversations)
                    if str_length not in self.conv2length:
                        token_length = tokenizer(
                            conversations,
                            return_tensors="pt",
                            padding=False,
                            truncation=False,
                        ).input_ids.size(1)
                        self.conv2length[str_length] = token_length + num_image_token
                    else:
                        token_length = self.conv2length[str_length]
                self.length.append(token_length)

    def __len__(self):
        return len(self.raw_data)

    def get_preprocess_function(self):
        from namo.utils.process_template import preprocess_qwen

        # Select the appropriate preprocessing function based on the template name
        if self.template_name == "qwen":
            preprocess_function = preprocess_qwen
        else:
            raise NotImplementedError(f"{self.template_name}")
        return preprocess_function

    def load_image(self, image_path):
        return Image.open(image_path).convert("RGB")

    def get_image_path(self, image_path):
        if image_path.startswith("s3://"):  # for ceph
            image_path = self.root + image_path
        else:  # for local image
            image_path = os.path.join(self.root, image_path)
        return image_path

    @staticmethod
    def get_longest_common_prefix_index(tensor1, tensor2):
        min_len = min(len(tensor1), len(tensor2))

        for i in range(min_len):
            if tensor1[i] != tensor2[i]:
                return i

        return min_len

    def multi_modal_get_item(self, data_item):
        def is_valid_image(img):
            width, height = img.size
            # must bigger than 28 pixels
            if width > 14 and height > 14:
                return True
            else:
                return False

        if "<image>" not in data_item["question"]:
            data_item["question"] = "<image>\n" + data_item["question"]

        if data_item["question"].count("<image>") != 1:
            parts = data_item["question"].split("<image>", 1)
            if len(parts) > 1:
                # Keep first <image>, remove any subsequent ones
                data_item["question"] = (
                    parts[0] + "<image>" + parts[1].replace("<image>", "")
                )

            print(f'==> [warn] possibaly wrong data: {data_item["question"]}')

        image_path = self.get_image_path(data_item["image"])
        image = self.load_image(image_path)

        if isinstance(image, list):
            for img in image:
                if not is_valid_image(img):
                    rank0_print(f"Invalid image found, passing... {img.size}")
                    raise ValueError(f"Invalid image found {img.size}")
        else:
            if not is_valid_image(image):
                rank0_print(f"Invalid image found, passing... {image.size}")
                raise ValueError(f"Invalid image found {image.size}")

        images = [image]
        # Apply the transformation to each image and stack the results into a tensor
        inputs = self.image_processor.preprocess(images)
        pixel_values = inputs["pixel_values"]
        spatial_shapes = None
        pixel_attention_mask = None
        if "spatial_shapes" in inputs:
            spatial_shapes = inputs["spatial_shapes"]
            pixel_attention_mask = inputs["pixel_attention_mask"]

        # Ensure that there is only one patch if dynamic image size is not enabled
        num_patches = pixel_values.size(0)

        # Select the appropriate preprocessing function based on the template name
        preprocess_function = self.get_preprocess_function()

        # Preprocess the conversations and generate the return dictionary
        chosen_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["chosen"]},
        ]
        chosen_ret = preprocess_function(
            [deepcopy(chosen_conversations)], self.tokenizer, has_image=True
        )

        rejected_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["rejected"]},
        ]
        rejected_ret = preprocess_function(
            [deepcopy(rejected_conversations)],
            self.tokenizer,
            has_image=True,
        )

        # Create the final return dictionary
        ret = dict(
            chosen_input_ids=chosen_ret["input_ids"][0],
            chosen_labels=chosen_ret["labels"][0],
            chosen_attention_mask=chosen_ret["attention_mask"][0],
            rejected_input_ids=rejected_ret["input_ids"][0],
            rejected_labels=rejected_ret["labels"][0],
            rejected_attention_mask=rejected_ret["attention_mask"][0],
            pixel_values=pixel_values,
            spatial_shapes=spatial_shapes,
            pixel_attention_mask=pixel_attention_mask,
            image_flags=torch.tensor([1] * num_patches, dtype=torch.long),
        )
        return ret

    def multi_modal_multi_image_get_item(self, data_item):
        def is_valid_image(img):
            width, height = img.size
            # must bigger than 28 pixels
            if width > 14 and height > 14:
                return True
            else:
                return False

        images, num_tiles = [], []
        num_image = len(data_item["image"])
        for image_path in data_item["image"]:
            # Merge the image path
            image_path = self.get_image_path(image_path)
            # Load the image using tcs_loader if available, otherwise use PIL
            image = self.load_image(image_path)

            if isinstance(image, list):
                for img in image:
                    if not is_valid_image(img):
                        rank0_print(f"Invalid image found, passing... {img.size}")
                        raise ValueError(f"Invalid image found {img.size}")
            else:
                if not is_valid_image(image):
                    rank0_print(f"Invalid image found, passing... {image.size}")
                    raise ValueError(f"Invalid image found {image.size}")

            images.append(image)
            num_tiles.append(1)

        if data_item["question"].count("<image>") != len(images):
            raise ValueError(
                f'{data_item["question"]} not equal to real images: {len(images)}'
            )

        inputs = self.image_processor.preprocess(images)
        pixel_values = inputs["pixel_values"]
        spatial_shapes = None
        pixel_attention_mask = None
        if "spatial_shapes" in inputs:
            spatial_shapes = inputs["spatial_shapes"]
            pixel_attention_mask = inputs["pixel_attention_mask"]

        num_patches = pixel_values.size(0)

        # Select the appropriate preprocessing function based on the template name
        preprocess_function = self.get_preprocess_function()

        # Preprocess the conversations and generate the return dictionary
        num_image_tokens = [self.num_image_token * num_tile for num_tile in num_tiles]

        chosen_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["chosen"]},
        ]
        chosen_ret = preprocess_function(
            [deepcopy(chosen_conversations)], self.tokenizer, has_image=True
        )

        rejected_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["rejected"]},
        ]
        rejected_ret = preprocess_function(
            [deepcopy(rejected_conversations)], self.tokenizer, has_image=True
        )

        # Create the final return dictionary
        ret = dict(
            chosen_input_ids=chosen_ret["input_ids"][0],
            chosen_labels=chosen_ret["labels"][0],
            chosen_attention_mask=chosen_ret["attention_mask"][0],
            rejected_input_ids=rejected_ret["input_ids"][0],
            rejected_labels=rejected_ret["labels"][0],
            rejected_attention_mask=rejected_ret["attention_mask"][0],
            pixel_values=pixel_values,
            spatial_shapes=spatial_shapes,
            pixel_attention_mask=pixel_attention_mask,
            image_flags=torch.tensor([1] * num_patches, dtype=torch.long),
        )
        return ret

    def video_get_item(self, data_item):
        # Ensure the first conversation contains a video placeholder
        if "<video>" not in data_item["question"]:
            data_item["question"] = "<video>\n" + data_item["question"]

        # Get the video file path
        video_file = data_item["video"]
        video_path = os.path.join(self.root, video_file)

        # Load the video frames using tcs_loader
        # TODO: Load videos without using tcsloader.
        image_list = self.tcs_loader(
            video_path,
            image_type="video",
            max_num_frames=self.max_num_frame,
            min_num_frames=self.min_num_frame,
            sample=self.sampling_method,
            clip=data_item.get("clip", None),
        )

        # Generate special tokens for each video frame
        special_tokens = "\n".join(
            ["Frame{}: <image>".format(i + 1) for i in range(len(image_list))]
        )
        data_item["question"] = data_item["question"].replace(
            "<video>\n", special_tokens
        )

        # Transform each frame image and stack them into a tensor
        inputs = self.image_processor.preprocess(image_list)
        pixel_values = inputs["pixel_values"]
        spatial_shapes = None
        pixel_attention_mask = None
        if "spatial_shapes" in inputs:
            spatial_shapes = inputs["spatial_shapes"]
            pixel_attention_mask = inputs["pixel_attention_mask"]
        num_patches = pixel_values.size(0)

        # Select the appropriate preprocessing function based on the template name
        preprocess_function = self.get_preprocess_function()

        # Preprocess the conversations and generate the return dictionary
        num_image_tokens = [self.num_image_token] * num_patches

        chosen_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["chosen"]},
        ]
        chosen_ret = preprocess_function(
            [deepcopy(chosen_conversations)],
            self.tokenizer,
            num_image_tokens,
            has_image=True,
        )

        rejected_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["rejected"]},
        ]
        rejected_ret = preprocess_function(
            self.template_name,
            [deepcopy(rejected_conversations)],
            self.tokenizer,
            num_image_tokens,
            group_by_length=True,
            use_packed_ds=self.use_packed_ds,
            ds_name=self.ds_name,
            num_image=num_patches,
        )

        ret = dict(
            chosen_input_ids=chosen_ret["input_ids"][0],
            chosen_labels=chosen_ret["labels"][0],
            chosen_attention_mask=chosen_ret["attention_mask"][0],
            rejected_input_ids=rejected_ret["input_ids"][0],
            rejected_labels=rejected_ret["labels"][0],
            rejected_attention_mask=rejected_ret["attention_mask"][0],
            pixel_values=pixel_values,
            spatial_shapes=spatial_shapes,
            pixel_attention_mask=pixel_attention_mask,
            image_flags=torch.tensor([1] * num_patches, dtype=torch.long),
        )
        return ret

    def pure_text_get_item(self, data_item):
        # Create a blank white image
        image = Image.new("RGB", (224, 224), (255, 255, 255))

        # Apply the transformation to each image patch and stack them into a tensor
        inputs = self.image_processor.preprocess([image])
        pixel_values = inputs["pixel_values"]
        spatial_shapes = None
        pixel_attention_mask = None
        if "spatial_shapes" in inputs:
            spatial_shapes = inputs["spatial_shapes"]
            pixel_attention_mask = inputs["pixel_attention_mask"]

        num_patches = pixel_values.size(0)

        # Ensure there is only one patch
        assert (
            num_patches == 1
        ), f"The number of patches should be 1, but got {num_patches}."

        # Select the appropriate preprocessing function based on the template name
        preprocess_function = self.get_preprocess_function()

        # Preprocess the conversations and generate the return dictionary
        chosen_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["chosen"]},
        ]
        chosen_ret = preprocess_function(
            [deepcopy(chosen_conversations)], self.tokenizer, has_image=True
        )

        rejected_conversations = [
            {"from": "human", "value": data_item["question"]},
            {"from": "gpt", "value": data_item["rejected"]},
        ]
        rejected_ret = preprocess_function(
            [deepcopy(rejected_conversations)], self.tokenizer, has_image=True
        )

        # Create the final return dictionary
        ret = dict(
            chosen_input_ids=chosen_ret["input_ids"][0],
            chosen_labels=chosen_ret["labels"][0],
            chosen_attention_mask=chosen_ret["attention_mask"][0],
            rejected_input_ids=rejected_ret["input_ids"][0],
            rejected_labels=rejected_ret["labels"][0],
            rejected_attention_mask=rejected_ret["attention_mask"][0],
            pixel_values=pixel_values,
            spatial_shapes=spatial_shapes,
            pixel_attention_mask=pixel_attention_mask,
            image_flags=torch.tensor([0] * num_patches, dtype=torch.long),
        )
        return ret

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        i = i % len(self.raw_data)

        try_cnt, max_try = 0, 10
        while True:
            if try_cnt > max_try:
                raise StopIteration
            try:
                data_item = json.loads(self.raw_data[i])
                if "image" in data_item and len(data_item["image"]) != 0:
                    if type(data_item["image"]) == list:
                        ret = self.multi_modal_multi_image_get_item(data_item)
                        # i = random.randint(0, len(self.raw_data) - 1)
                        # print(data_item)
                        # try_cnt += 1
                        # continue
                    else:
                        ret = self.multi_modal_get_item(data_item)

                    assert (
                        ret["pixel_values"].shape[1] == 1764
                    ), f"{ret['pixel_values'].shape} is wrong!"
                    assert (
                        len(ret["pixel_values"].shape) == 3
                    ), f"{ret['pixel_values'].shape} is wrong!"
                    # for k, v in ret.items():
                    #     print(f'{k} {v.shape}')
                elif (
                    "video" in data_item
                    and data_item["video"] is not None
                    and data_item["video"] != ""
                ):
                    # ret = self.video_get_item(data_item)
                    continue
                else:
                    # ret = self.pure_text_get_item(data_item)
                    continue
                break
            except Exception as e:
                try_cnt += 1
                print(e, self.ds_name, flush=True)
                if not isinstance(e, (UnidentifiedImageError, FileNotFoundError)):
                    traceback.print_exc()
                data_item = json.loads(self.raw_data[i])
                if "image" in data_item:
                    if type(data_item["image"]) == list:
                        images = [self.root + item for item in data_item["image"]]
                        print(
                            f"Failed to load image: {images}, the dataset is: {self.ds_name}"
                        )
                    else:
                        if data_item["image"].startswith("s3://"):
                            data_path = self.root + data_item["image"]
                        else:
                            data_path = os.path.join(self.root, data_item["image"])
                        print(
                            f"Failed to load image: {data_path}, the dataset is: {self.ds_name}"
                        )
                elif "video" in data_item:
                    data_path = os.path.join(self.root, data_item["video"])
                    print(
                        f"Failed to load video: {data_path}, the dataset is: {self.ds_name}"
                    )
                i = random.randint(0, len(self.raw_data) - 1)
        return ret


def build_datasets(
    data_args,
    tokenizer,
    tcs_loader,
    model,
    group_by_length=False,
    min_num_frame=8,
    max_num_frame=32,
    normalize_type="imagenet",
    use_data_resampling=False,
):
    datasets = []
    lengths = []

    if data_args.version in conversation_lib.conv_templates:
        conversation_lib.default_conversation = conversation_lib.conv_templates[
            data_args.version
        ]
    else:
        conversation_lib.default_conversation = conversation_lib.conv_templates[
            "vicuna_v1"
        ]

    # dataset_path is meta data path in MMPR-1.1
    data_path = data_args.data_path
    if isinstance(data_args.data_path, list):
        data_path = data_args.data_path[0]
    ds_collections = json.loads(open(data_path).read())

    image_processor = data_args.image_processor
    for ds_idx, ds_name in enumerate(ds_collections.keys()):
        repeat_time = ds_collections[ds_name]["repeat_time"]

        dataset = LazySupervisedDataset(
            data_args.version,
            ds_collections[ds_name],
            tokenizer,
            tcs_loader,
            ds_name=ds_name,
            # num_image_token=model.num_image_token,
            num_image_token=578,
            # image_size=data_args.force_image_size,
            image_processor=image_processor,
            is_train=ds_collections[ds_name].get("data_augment", False),
            group_by_length=group_by_length,
            min_num_frame=min_num_frame,
            max_num_frame=max_num_frame,
            repeat_time=repeat_time,
            normalize_type=normalize_type,
            random_seed=ds_idx,
        )
        logger.info(f"Add dataset: {ds_name} with length: {len(dataset)}")
        datasets.append(dataset)
        if use_data_resampling:
            lengths.append(math.sqrt(len(dataset)))
        else:
            lengths.append(len(dataset))

    if use_data_resampling:
        total_length = sum(lengths)
        weights = [l / total_length for l in lengths]
        train_dataset = WeightedConcatDataset(datasets, weights)
    else:
        train_dataset = ConcatDataset(datasets)
    return train_dataset
