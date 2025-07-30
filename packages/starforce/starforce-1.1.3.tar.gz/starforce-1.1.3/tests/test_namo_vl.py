"""

Testing ability to call Namo VL models

should install `pip install -U namo` first.

Example run:

python tests/test_namo_vl.py checkpoints/Qwen3-VL-2B/

"""

from namo.api.vl import VLInfer
import os
from termcolor import colored
import torch
import sys
from loguru import logger
import argparse
import json
import random


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", default="checkpoints/namo-500m")
    parser.add_argument("--eval", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--think", action="store_true")
    args = parser.parse_args()
    model_p = args.model
    chat(model_p, args.debug, args.think)


def chat(model_p, verbose=False, thinking=False):
    model = VLInfer(
        model_type="hydra",
        model_path=model_p,
        device="cuda:0" if torch.cuda.is_available() else "cpu",
    )

    # crt_input = ["images/cats.jpg", None]
    crt_input = [None, None]

    # enable_thinking = False
    enable_thinking = thinking

    while True:
        img_or_txt = input(colored("\nUser (txt/img_path): ", "cyan")).strip()

        if os.path.exists(img_or_txt.split(" ")[0]):
            crt_input[0] = img_or_txt
            print(colored("System: Image updated.", "green"))
            continue
        else:
            crt_input[1] = img_or_txt

        if crt_input[0] and crt_input[1]:
            print(colored("Assistant:", "green"), end=" ")
            model.generate(
                images=crt_input[0],
                prompt=crt_input[1],
                verbose=verbose,
                enable_thinking=enable_thinking,
            )
            crt_input[0] = None
        elif not crt_input[0] and crt_input[1]:
            # pure text
            print(colored("Assistant:", "green"), end=" ")
            model.generate(
                images=None,
                prompt=crt_input[1],
                verbose=verbose,
                enable_thinking=enable_thinking,
            )
        else:
            print(colored("System: Please provide either an image or text input.", "red"))


if __name__ == "__main__":
    main()
