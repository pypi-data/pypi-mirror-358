from namo.api.vl import VLInfer
import os
from termcolor import colored
import torch
import json
import random


model = VLInfer(
    model_type="qwen2.5-vl", device="cuda:0" if torch.cuda.is_available() else "cpu"
)


def handle_eval_item(item):

    p = random.choice([item["question1"], item["question2"]])
    img_f = item["image"]

    print(f"\nImage: {img_f}\nQ: {p}\n", end="")
    print(colored("AI: ", "yellow"), end="")
    out = model.generate(images=img_f, prompt=p, verbose=False)
    print("\n")


def eval():
    with open("images/evals.json") as f:
        for item in json.load(f):
            handle_eval_item(item)


if __name__ == "__main__":
    eval()
