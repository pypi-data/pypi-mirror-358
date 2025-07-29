"""
Preparing dataset for Qwen2.5-VL

it used with simpler interface than Namo itself.
"""

import copy
import os
from dataclasses import dataclass, field
from typing import Dict
import torch
import transformers
import ujson as json
import jsonlines
from torch.utils.data import Dataset
from qwen_vl_utils import process_vision_info
from PIL import Image
import re
import random
from .params import DataArguments
from .models.symbols import (
    DEFAULT_IMAGE_PATCH_TOKEN,
    DEFAULT_IMAGE_TOKEN_QWENVL,
    DEFAULT_VIDEO_TOKEN_QWENVL,
    LLAVA_IMAGE_TOKEN,
    LLAVA_VIDEO_TOKEN,
    DEFAULT_IM_START_TOKEN,
    DEFAULT_IM_END_TOKEN,
    SYSTEM_MESSAGE,
    SYSTEM_NAV,
    IGNORE_INDEX,
    VISION_START_TOKEN,
    VISION_END_TOKEN,
)
from loguru import logger
from torch.nn.utils.rnn import pad_sequence as torch_pad_sequence


def truncate_sequence(input_ids, labels, max_length, eos_token_id):
    if input_ids.size(0) > max_length:
        input_ids = input_ids[: max_length - 1]
        labels = labels[: max_length - 1]

    if eos_token_id is not None:
        input_ids = torch.cat([input_ids, torch.tensor([eos_token_id])])
        labels = torch.cat([labels, torch.tensor([eos_token_id])])

    return input_ids, labels


def pad_sequence(sequences, padding_side="right", padding_value=0, max_length=None):
    """
    Pad (or truncate) a list of [L_i, *] tensors:
      - pads all up to the longest sequence in `sequences`
      - if max_length is provided and < that longest length, truncates instead
    padding_side: "right" (default) or "left"
    padding_value: fill value for padding
    """
    assert padding_side in ("right", "left"), "padding_side must be 'right' or 'left'"

    natural_max = max(seq.size(0) for seq in sequences)
    target_len = (
        natural_max if (max_length is None or max_length >= natural_max) else max_length
    )

    if padding_side == "right":
        padded = torch_pad_sequence(
            sequences, batch_first=True, padding_value=padding_value
        )
    else:
        rev_seqs = [seq.flip(0) for seq in sequences]
        padded = torch_pad_sequence(
            rev_seqs, batch_first=True, padding_value=padding_value
        )
        padded = padded.flip(1)

    if padded.size(1) > target_len:
        if padding_side == "right":
            return padded[:, :target_len]
        else:
            return padded[:, -target_len:]
    return padded


# def pad_sequence(sequences, padding_side="right", padding_value=0):
#     """
#     Pad a list of sequences to the same length.
#     sequences: list of tensors in [seq_len, *] shape
#     """
#     assert padding_side in ["right", "left"]
#     max_size = sequences[0].size()
#     trailing_dims = max_size[1:]
#     max_len = max(len(seq) for seq in sequences)
#     batch_size = len(sequences)
#     output = sequences[0].new_full((batch_size, max_len) + trailing_dims, padding_value)
#     for i, seq in enumerate(sequences):
#         length = seq.size(0)
#         if padding_side == "right":
#             output.data[i, :length] = seq
#         else:
#             output.data[i, -length:] = seq
#     return output


def get_image_info(image_path, min_pixel, max_pixel, width, height):
    # Using this because of process_vision_info function
    # Need to fix this in the future

    content = {
        "type": "image",
        "image": image_path,
        "min_pixels": min_pixel,
        "max_pixels": max_pixel,
    }

    if width is not None and height is not None:
        content["resized_width"] = width
        content["resized_height"] = height

    messages = [{"role": "user", "content": [content]}]
    image_input, _ = process_vision_info(messages)
    return image_input[0]


def get_video_info(
    video_path,
    min_pixels,
    max_pixels,
    total_pixels,
    width,
    height,
    min_frames,
    max_frames,
    fps,
):
    # Using this because of process_vision_info function
    # Need to fix this in the future
    content = {
        "type": "video",
        "video": video_path,
        "min_pixels": min_pixels,
        "max_pixels": max_pixels,
        "fps": fps,
    }

    if width is not None and height is not None:
        content["resized_width"] = width
        content["resized_height"] = height

    if total_pixels is not None:
        content["total_pixels"] = total_pixels

    if min_frames is not None:
        content["min_frames"] = min_frames

    if max_frames is not None:
        content["max_frames"] = max_frames

    messages = [{"role": "user", "content": [content]}]

    _, video_input, video_kwargs = process_vision_info(
        messages, return_video_kwargs=True
    )

    return video_input[0], video_kwargs


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(
        self,
        data_path: str | list,
        processor: transformers.ProcessorMixin,
        data_args: DataArguments,
        model_id,
        padding=True,
    ):
        super(SupervisedDataset, self).__init__()
        if isinstance(data_path, str):
            list_data_dict = json.load(open(data_path, "r"))
            for itm in list_data_dict:
                itm["ds"] = os.path.basename(data_path).split(".")[0].split("_train")[0]
        else:
            list_data_dict = []
            for data in data_path:
                if data.endswith("jsonl"):
                    with jsonlines.open(data, mode="r") as reader:
                        raw_data = [item for item in reader]
                else:
                    if not os.path.exists(data):
                        raise ValueError(f'{data} not exist!! pls check!')
                    
                    raw_data = json.load(open(data, "r"))

                for i in raw_data:
                    if "conversations" in i.keys():
                        i["id"] = len(list_data_dict)
                        i["ds"] = (
                            os.path.basename(os.path.dirname(data))
                            + " | "
                            + os.path.basename(data).split(".")[0].split("_train")[0]
                        )
                        list_data_dict.append(i)
            print(f"all data samples: {len(list_data_dict)}")

        random.shuffle(list_data_dict)
        self.model_id = model_id
        self.processor = processor
        self.list_data_dict = list_data_dict
        self.data_args = data_args
        self.padding = padding
        self.image_min_pixels = data_args.image_min_pixels
        self.image_max_pixels = data_args.image_max_pixels
        self.video_min_pixels = data_args.video_min_pixels
        self.video_max_pixels = data_args.video_max_pixels
        self.total_pixels = data_args.total_pixels
        self.min_frames = data_args.min_frames
        self.max_frames = data_args.max_frames
        self.image_resized_w = data_args.image_resized_width
        self.image_resized_h = data_args.image_resized_height
        self.video_resized_w = data_args.video_resized_width
        self.video_resized_h = data_args.video_resized_height
        self.fps = data_args.fps
        logger.info(
            f"image_min_pixels: {self.image_min_pixels}, image_max_pixels: {self.image_max_pixels}, video_min_pixels: {self.video_min_pixels}, video_max_pixels: {self.video_max_pixels}"
        )

    def __len__(self):
        return len(self.list_data_dict)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        attempt, max_attempt = 0, 10
        while attempt < max_attempt:
            try:
                # sample an item
                data_dict = self._sample_item(i)
                # if data_dict is not None:
                break
            except Exception as e:
                attempt += 1
                print(f"Error in loading {i}, retrying {attempt}...")
                import traceback

                print(e)
                traceback.print_exc()
                i = random.randint(0, len(self.list_data_dict) - 1)
        return data_dict

    def _sample_item(self, i) -> Dict[str, torch.Tensor]:
        sources = self.list_data_dict[i]

        is_video = False

        is_thinking_item = sources.get("enable_thinking", False)

        SYSTEM_MESSAGE_REAL = SYSTEM_MESSAGE

        processor = self.processor
        if "image" in sources:
            videos = None
            grid_key = "image_grid_thw"
            pixel_key = "pixel_values"

            image_files = sources["image"]
            image_folder = self.data_args.image_folder

            if isinstance(image_files, str):
                image_files = [image_files]

            images = []

            ds = sources["ds"].split(" | ")[1]

            # print(ds, sources["ds"])

            if "QUARD" in sources["ds"]:
                image_folder = os.path.join(image_folder, "QUARD_full/")
                SYSTEM_MESSAGE_REAL = SYSTEM_NAV
            elif "m4_instruct" in sources["ds"].lower():
                image_folder = os.path.join(image_folder, "M4-Instruct/")
            elif "mammoth_ov" in sources["ds"].lower():
                image_folder = os.path.join(image_folder, "mammoth_multi_image_data")
            elif "mammo" in sources["ds"].lower():
                # mammo vl images root
                image_folder = os.path.join(image_folder, "mammoth_si_10M")
            elif "nav_json" in sources["ds"]:
                image_folder = os.path.join(image_folder, "real_data_all")

            if (
                ("llava" in ds and "llavar" not in ds and "llava_recap" not in ds)
                or "sharegpt4v_instruct" in ds
                or "sharegpt4v_" in ds
                or "share-captioner" in ds
                or "gemini" in ds
                or "bunny_695k" in ds
                or "allava_laion" in ds
                or "allava_vflan" in ds
                or "multi_llava" in ds
                or "Cambrian7M" in ds
                or "c7s-" in ds
                or "ureader_tr" in ds
                or "VLAA-Thinking" in ds
                or "mammo" in ds
                or "vla_v" in ds
                or "m4_instruct" in ds
            ):
                pass
            else:
                if "llavar" in ds:
                    ds = "llavar"
                elif "bunny" in ds and "bunny_695k" not in ds:
                    ds = "bunny_pretrain_laion_2m"
                elif "qa_" in ds:
                    ds = "qa_data"
                elif "sharegpt4o" in ds:
                    ds = "sharegpt4o/images"
                elif "mathv360k_cot" in ds:
                    ds = "mathv360k_cot/images"

                image_folder = os.path.join(image_folder, ds)

            # print(image_folder, image_files, sources["ds"])
            for image_file in image_files:
                image_file = os.path.join(image_folder, image_file)
                if not os.path.exists(image_file):
                    print(f"{image_file} not found in local!")

                images.append(
                    get_image_info(
                        image_file,
                        self.image_min_pixels,
                        self.image_max_pixels,
                        self.image_resized_w,
                        self.image_resized_h,
                    )
                )
            # print(f'{[im for im in images]}')
        elif "video" in sources:
            # logger.info('video not supported for now!')
            is_video = True
            images = None
            grid_key = "video_grid_thw"
            pixel_key = "pixel_values_videos"

            video_files = sources["video"]
            # video_folder = self.data_args.image_folder

            ds = sources["ds"].split(" | ")[1]

            # todo: special handle video datasets
            video_folder = os.path.join(self.data_args.image_folder, ds)

            if isinstance(video_files, str):
                video_files = [video_files]

            videos = []
            for video_file in video_files:
                if not os.path.exists(video_file):
                    if not video_file.startswith("http"):
                        video_file = os.path.join(video_folder, video_file)
                # print(video_file)
                if not os.path.exists(video_file):
                    raise ValueError(f"{video_file} file not found!")
                video_input, video_kwargs = get_video_info(
                    video_file,
                    self.video_min_pixels,
                    self.video_max_pixels,
                    self.total_pixels,
                    self.video_resized_w,
                    self.video_resized_h,
                    self.min_frames,
                    self.max_frames,
                    self.data_args.fps,
                )
                # print(video_input.shape)
                # print(f"video_input: {video_input.shape}")
                videos.append(video_input)
        else:
            grid_key = None
            pixel_key = None
            images = None
            videos = None

            # todo: handling pure text data

        sources = copy.deepcopy(
            llava_to_openai(sources["conversations"], is_video=is_video)
        )
        # print(sources, is_video)

        all_input_ids = []
        all_labels = []
        all_pixel_values = []
        all_image_grid_thw = []
        all_second_gird = []

        # Qwen2-VL uses a default system message so I've added this.
        if len(SYSTEM_MESSAGE_REAL) > 0:
            system_message = f"{DEFAULT_IM_START_TOKEN}system\n{SYSTEM_MESSAGE_REAL}{DEFAULT_IM_END_TOKEN}\n"
            system_message_input_ids = processor.tokenizer(
                system_message, add_special_tokens=False, return_tensors="pt"
            )["input_ids"]
            system_labels = torch.full_like(system_message_input_ids, IGNORE_INDEX)

            all_input_ids.append(system_message_input_ids.squeeze(0))
            all_labels.append(system_labels.squeeze(0))

        # print(f'sources: {sources}')
        for _, j in enumerate(range(0, len(sources), 2)):
            user_input = sources[j]
            gpt_response = sources[j + 1]

            # adding this will no thinking for Qwen3
            no_thinking_append = "<think>\n\n</think>\n\n"
            user_input = f"{DEFAULT_IM_START_TOKEN}{user_input['role']}\n{user_input['content']}{DEFAULT_IM_END_TOKEN}\n{DEFAULT_IM_START_TOKEN}{gpt_response['role']}\n"
            # todo: add Qwen3 check, enable_thinking check
            if "Qwen3" in self.model_id and not is_thinking_item:
                user_input += no_thinking_append
            gpt_response = f"{gpt_response['content']}{DEFAULT_IM_END_TOKEN}\n"

            if DEFAULT_IMAGE_TOKEN_QWENVL in user_input:
                inputs = processor(
                    text=[user_input],
                    images=images,
                    videos=videos,
                    padding=False,
                    return_tensors="pt",
                )
                prompt_input_ids = inputs["input_ids"]
                all_pixel_values.append(inputs[pixel_key])
                all_image_grid_thw.append(inputs[grid_key])

            elif DEFAULT_VIDEO_TOKEN_QWENVL in user_input:
                if "Qwen2.5" in self.model_id or "Qwen3" in self.model_id:
                    inputs = processor(
                        text=[user_input],
                        images=images,
                        videos=videos,
                        padding=False,
                        return_tensors="pt",
                        **video_kwargs,
                    )
                    all_second_gird.extend(inputs["second_per_grid_ts"])
                else:
                    inputs = processor(
                        text=[user_input],
                        images=images,
                        videos=videos,
                        padding=False,
                        return_tensors="pt",
                    )
                prompt_input_ids = inputs["input_ids"]
                all_pixel_values.append(inputs[pixel_key])
                all_image_grid_thw.append(inputs[grid_key])
            else:
                prompt_input_ids = processor.tokenizer(
                    user_input,
                    add_special_tokens=False,
                    padding=False,
                    return_tensors="pt",
                )["input_ids"]

            response_input_ids = processor.tokenizer(
                gpt_response,
                add_special_tokens=False,
                padding=False,
                return_tensors="pt",
            )["input_ids"]

            # replace prompt_input_ids  <|vision_start|><|image_pad|>xxx<|vision_end|> to -100
            # 151652, 151655, 151655.., 151653
            # print(f'before: {prompt_input_ids}')
            # 216 -> [1, 24, 36]
            # print(f'image tokens: {len([i for i in prompt_input_ids[0] if i == 151655])}, {all_image_grid_thw[0]} {all_pixel_values[0].shape}')
            # print(f'image tokens: {len([i for i in prompt_input_ids[0] if i == 151656])}, {all_image_grid_thw} {all_pixel_values[0].shape}')
            # TODO: use <|video_pad|> for video frames rather than <|image_pad|>, they can be different.
            prompt_input_ids = replace_to_llava_image_ignore_token_v2(prompt_input_ids)
            # print(f'after: {len([i for i in prompt_input_ids[0] if i == -200])}')

            input_ids = torch.cat(
                [prompt_input_ids, response_input_ids], dim=1
            ).squeeze(0)
            labels = torch.cat(
                [
                    torch.tensor([IGNORE_INDEX] * len(prompt_input_ids[0])),
                    response_input_ids.squeeze(0),
                ],
                dim=0,
            )

            all_input_ids.append(input_ids)
            all_labels.append(labels)

        # print(f'inputs: {inputs['pixel_values'].shape}')
        # print(f'inputs: {all_input_ids},')
        # if pixel_key is not None and 'video' in pixel_key:
        #     print(f'{processor.tokenizer.decode([t for t in all_input_ids[0] if t != -200])}')
        # There is no need for eos or bos tokens in the input_ids
        # Qwen2-VL does not use them
        input_ids = torch.cat(all_input_ids, dim=0).to(torch.long)
        labels = torch.cat(all_labels, dim=0).to(torch.long)

        # eos_token_id = processor.tokenizer.convert_tokens_to_ids(DEFAULT_IM_END_TOKEN)
        # input_ids, labels = truncate_sequence(input_ids, labels, self.max_length, eos_token_id)

        attention_mask = (input_ids > -1000000).to(torch.long)

        data_dict = dict(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )

        if pixel_key and grid_key:
            pixel_values = torch.cat(all_pixel_values, dim=0)
            image_thw = torch.cat(all_image_grid_thw, dim=0)
            data_dict[pixel_key] = pixel_values
            data_dict[grid_key] = image_thw
            # print(pixel_values.shape, image_thw, (input_ids == -200).sum().item())

        if len(all_second_gird) > 0:
            second_gird = all_second_gird
            data_dict["second_per_grid_ts"] = second_gird

        return data_dict

    @property
    def lengths(self):
        length_list = []
        for sample in self.list_data_dict:
            img_tokens = 512 if "image" in sample else 0
            length_list.append(
                sum(len(conv["value"].split()) for conv in sample["conversations"])
                + img_tokens
            )
        logger.info("Calculating lengths done.")
        return length_list

    @property
    def modality_lengths(self):
        length_list = []
        logger.info("Calculating lengths...")
        for i, sample in enumerate(self.list_data_dict):
            # item = self.__getitem__(i)
            # cur_len = item["input_ids"].shape[0]
            # cur_len += torch.sum(torch.prod(item['image_grid_thw'], dim=1)).item()
            cur_len = sum(
                len(conv["value"].split()) for conv in sample["conversations"]
            )
            cur_len = cur_len if "image" in sample or "video" in sample else -cur_len
            length_list.append(cur_len)
        logger.info("Calculating lengths done.")
        return length_list


class DataCollatorForSupervisedDataset(object):
    """Collate examples for supervised fine-tuning."""

    def __init__(self, pad_token_id: int, model_id, model_max_length):
        self.pad_token_id = pad_token_id
        self.model_id = model_id
        self.model_max_length = model_max_length

    def __call__(self, examples):
        batch_input_ids = []
        batch_label_ids = []
        batch_pixel_values = []
        batch_pixel_video_values = []
        batch_video_thw = []
        batch_image_thw = []
        batch_second_per_grid_ts = []

        # if pure text, batch item all text
        # is_pure_text = not any("pixel_values" in e for e in examples)

        for example in examples:
            keys = example.keys()
            if "pixel_values_videos" in keys:
                if "namo" in self.model_id:
                    # namo treat image and video same.
                    batch_pixel_values.append(example["pixel_values_videos"])
                    batch_image_thw.append(example["video_grid_thw"])
                else:
                    batch_pixel_video_values.append(example["pixel_values_videos"])
                    batch_video_thw.append(example["video_grid_thw"])
            elif "pixel_values" in keys:
                batch_pixel_values.append(example["pixel_values"])
                batch_image_thw.append(example["image_grid_thw"])

            # whenever pure text or not, adding dummy images avoid rank0 got pure text
            # and rank1 got image&text, this will caused hangout
            if "pixel_values" not in keys:
                # print(f'not pure text and batch contains image text: {example}')
                # placeholder of image-text interleave
                pixel_values_placeholder = torch.ones((16, 1176)) * 0.12
                image_grid_thw_placeholder = torch.tensor([[1, 4, 4]])
                batch_pixel_values.append(pixel_values_placeholder)
                batch_image_thw.append(image_grid_thw_placeholder)
         

            batch_input_ids.append(example["input_ids"])
            batch_label_ids.append(example["labels"])

            if "second_per_grid_ts" in keys:
                batch_second_per_grid_ts.extend(example["second_per_grid_ts"])

        input_ids = pad_sequence(
            batch_input_ids,
            padding_side="right",
            padding_value=self.pad_token_id,
            max_length=self.model_max_length,
        )

        attention_mask = input_ids != self.pad_token_id
        labels = pad_sequence(
            batch_label_ids,
            padding_side="right",
            padding_value=IGNORE_INDEX,
            max_length=self.model_max_length,
        )
        # input_ids and labels are same length, same max_length constraint
        # print(f'input_ids: {input_ids.shape}, labels: {labels.shape} {is_pure_text}')

        data_dict = {
            "input_ids": input_ids,
            "labels": labels,
            "attention_mask": attention_mask,
        }

        if len(batch_pixel_values) > 0:
            pixel_values = torch.cat(batch_pixel_values, dim=0)
            image_thw = torch.cat(batch_image_thw, dim=0)
            data_dict["pixel_values"] = pixel_values
            if "namo" in self.model_id:
                data_dict["image_sizes"] = image_thw
            else:
                # pure Qwen2.5 VL model train
                data_dict["image_grid_thw"] = image_thw
            # compatible with namo input params
            # print(f'pixel_values: {pixel_values.shape} {image_thw}')

        if len(batch_pixel_video_values) > 0:
            pixel_video_values = torch.cat(batch_pixel_video_values, dim=0)
            video_thw = torch.cat(batch_video_thw, dim=0)
            # data_dict["pixel_values_videos"] = pixel_video_values
            # (TODO): not supported in namo yet.

            if "namo" in self.model_id:
                # pixel_values and pixel_values_video not distinguishable in namo
                data_dict["pixel_values"] = pixel_video_values
                data_dict["image_sizes"] = video_thw
            else:
                # pure Qwen2.5 VL model train
                data_dict["video_grid_thw"] = video_thw
                data_dict["pixel_values_videos"] = pixel_video_values

        if len(batch_second_per_grid_ts) > 0 and "namo" not in self.model_id:
            data_dict["second_per_grid_ts"] = batch_second_per_grid_ts
        return data_dict


def replace_image_tokens(input_string, is_video=False):
    if is_video:
        if LLAVA_IMAGE_TOKEN in input_string:
            pattern = r"\n?" + re.escape(LLAVA_IMAGE_TOKEN) + r"\n?"
        else:
            pattern = r"\n?" + re.escape(LLAVA_VIDEO_TOKEN) + r"\n?"
        replacement = VISION_START_TOKEN + DEFAULT_VIDEO_TOKEN_QWENVL + VISION_END_TOKEN
    else:
        pattern = r"\n?" + re.escape(LLAVA_IMAGE_TOKEN) + r"\n?"
        replacement = VISION_START_TOKEN + DEFAULT_IMAGE_TOKEN_QWENVL + VISION_END_TOKEN

    return re.sub(pattern, replacement, input_string)


def replace_to_llava_image_ignore_token(prompt_input_ids):
    result = []
    i = 0
    prompt_input_ids = prompt_input_ids[0]
    n = len(prompt_input_ids)
    while i < n:
        # currently force hard coded QwenVL image token ids
        if prompt_input_ids[i] == 151652:
            while i < n and prompt_input_ids[i] != 151653:
                i += 1
            if i < n:  # llave default image token
                result.append(-200)
                i += 1
        else:
            result.append(prompt_input_ids[i])
            i += 1
    return torch.as_tensor(result).unsqueeze(0).to(prompt_input_ids.device)


def replace_to_llava_image_ignore_token_v2(prompt_input_ids):
    result = []
    i = 0
    prompt_input_ids = prompt_input_ids[0]
    n = len(prompt_input_ids)

    while i < n:
        if prompt_input_ids[i] == 151652:
            result.append(151652)
            i += 1

            start_idx = i
            while i < n and prompt_input_ids[i] != 151653:
                i += 1

            if i < n:
                result.append(-200)
                result.append(151653)
                i += 1
            else:
                result.extend(prompt_input_ids[start_idx:])
        else:
            result.append(prompt_input_ids[i])
            i += 1
    return torch.as_tensor(result).unsqueeze(0).to(prompt_input_ids.device)


def llava_to_openai(conversations, is_video=False):
    role_mapping = {"human": "user", "gpt": "assistant"}

    transformed_data = []
    for conversation in conversations:
        transformed_content = replace_image_tokens(
            conversation["value"], is_video=is_video
        )
        transformed_entry = {
            "role": role_mapping.get(conversation["from"], conversation["from"]),
            "content": transformed_content,
        }
        transformed_data.append(transformed_entry)

    return transformed_data


def make_supervised_data_module(model_id, processor, data_args):
    """Make dataset and collator for supervised fine-tuning."""
    sft_dataset = SupervisedDataset(
        data_path=data_args.data_path,
        processor=processor,
        data_args=data_args,
        model_id=model_id,
    )
    data_collator = DataCollatorForSupervisedDataset(
        pad_token_id=processor.tokenizer.pad_token_id,
        model_id=model_id,
        model_max_length=data_args.model_max_length,
    )

    return dict(
        train_dataset=sft_dataset, eval_dataset=None, data_collator=data_collator
    )
