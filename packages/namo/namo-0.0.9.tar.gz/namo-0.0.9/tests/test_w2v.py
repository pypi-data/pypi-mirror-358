from transformers import AutoFeatureExtractor, Wav2Vec2BertModel
import torch
from datasets import load_dataset
from transformers import AutoProcessor

dataset = load_dataset(
    "hf-internal-testing/librispeech_asr_demo", "clean", split="validation"
)
dataset = dataset.sort("id")
sampling_rate = dataset.features["audio"].sampling_rate

# processor = AutoProcessor.from_pretrained("checkpoints/w2v-bert-2.0")
model = Wav2Vec2BertModel.from_pretrained("checkpoints/w2v-bert-2.0")

model.to(torch.bfloat16)
model.save_pretrained("checkpoints/w2v-bert-2.0-bf16")

# audio file is decoded on the fly
# inputs = processor(
#     dataset[0]["audio"]["array"], sampling_rate=sampling_rate, return_tensors="pt"
# )
# with torch.no_grad():
#     outputs = model(**inputs)
