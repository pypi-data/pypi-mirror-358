import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import soundfile as sf
from coreai.tasks.audio.codecs.xcodec2.modeling_xcodec2 import XCodec2Model


import torch
import soundfile as sf
from transformers import AutoTokenizer, AutoModelForCausalLM


class TextToSpeech:
    def __init__(
        self,
        model_path="checkpoints/Llasa-1B-Multilingual",
        codec_path="checkpoints/XCodec2",
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = (
            AutoModelForCausalLM.from_pretrained(model_path).to(self.device).eval()
        )
        self.codec_model = (
            XCodec2Model.from_pretrained(codec_path).to(self.device).eval()
        )
        self.speech_end_id = self.tokenizer.convert_tokens_to_ids(
            "<|SPEECH_GENERATION_END|>"
        )

    @staticmethod
    def ids_to_speech_tokens(speech_ids):
        return [f"<|s_{sid}|>" for sid in speech_ids]

    @staticmethod
    def extract_speech_ids(speech_tokens_str):
        return [
            int(token[4:-2])
            for token in speech_tokens_str
            if token.startswith("<|s_") and token.endswith("|>")
        ]

    def generate_speech(self, text, prompt_wav=None, output_file="gen.wav"):
        formatted_text = f"<|TEXT_UNDERSTANDING_START|>{text}<|TEXT_UNDERSTANDING_END|>"

        speech_ids_prefix = []
        if prompt_wav is not None:
            assert os.path.exits(prompt_wav), f"{prompt_wav} not found!"
            prompt_wav, sr = sf.read(prompt_wav)
            prompt_wav = (
                torch.from_numpy(prompt_wav).float().unsqueeze(0).to(self.device)
            )
            vq_code_prompt = self.codec_model.encode_code(input_waveform=prompt_wav)[
                0, 0, :
            ]
            speech_ids_prefix = self.ids_to_speech_tokens(vq_code_prompt)

        chat = [
            {"role": "user", "content": "Convert the text to speech:" + formatted_text},
            {
                "role": "assistant",
                "content": "<|SPEECH_GENERATION_START|>" + "".join(speech_ids_prefix),
            },
        ]

        input_ids = self.tokenizer.apply_chat_template(
            chat, tokenize=True, return_tensors="pt", continue_final_message=True
        ).to(self.device)

        outputs = self.model.generate(
            input_ids,
            max_length=300,
            eos_token_id=self.speech_end_id,
            do_sample=True,
            top_p=1,
            temperature=0.2,
        )

        generated_ids = outputs[0][input_ids.shape[1] - len(speech_ids_prefix) : -1]
        speech_tokens = self.extract_speech_ids(
            self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        )

        speech_tokens = (
            torch.tensor(speech_tokens).to(self.device).unsqueeze(0).unsqueeze(0)
        )
        gen_wav = self.codec_model.decode_code(speech_tokens)
        sf.write(output_file, gen_wav[0, 0, :].cpu().numpy(), 16000)
        return output_file


def main():
    tts = TextToSpeech()

    tts.generate_speech(
        text="""Hello, world. We are on a mission to create vivid assistant.""",
        prompt_wav=None,
    )


if __name__ == "__main__":
    main()
