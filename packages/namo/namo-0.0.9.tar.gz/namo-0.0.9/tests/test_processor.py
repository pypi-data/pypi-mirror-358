from transformers import AutoProcessor, Qwen2_5_VLProcessor

processor_path = './checkpoints/Qwen3-VL-2B-Unofficial'
a = Qwen2_5_VLProcessor.from_pretrained(
                processor_path, trust_remote_code=True
            )
print(a)