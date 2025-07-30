# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
from functools import partial

import torch
from .action_head_utils import action_head_pytorch_forward

import starforce
from starforce.data.dataset import LeRobotSingleDataset
from starforce.experiment.data_config import DATA_CONFIG_MAP
from starforce.model.policy import Gr00tPolicy
from .compare import compare_predictions

try:
    from trt_model_forward import setup_tensorrt_engines
except Exception as e:
    print("tensorrt disabled. infer with torch compile mode.")


import os
import torch
import argparse
from starforce.data.schema import EmbodimentTag


class StarForceVLA:
    def __init__(
        self,
        model_path="nvidia/GR00T-N1.5-3B",
        inference_mode="pytorch",
        denoising_steps=4,
        trt_engine_path="gr00t_engine",
        embodiment_tag=EmbodimentTag.NEW_EMBODIMENT,
        data_config_tag="bimanual_agilex",
        torch_compile=False,
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = model_path
        self.inference_mode = inference_mode
        self.trt_engine_path = trt_engine_path
        self.embodiment_tag = embodiment_tag
        self.torch_compile = torch_compile

        data_config = DATA_CONFIG_MAP[data_config_tag]
        modality_config = data_config.modality_config()
        processor_type = 'eagle' if 'gr00t' in model_path.lower() else 'qwenvl'
        modality_transform = data_config.transform(processor_type=processor_type)

        self.policy = Gr00tPolicy(
            model_path=model_path,
            embodiment_tag=embodiment_tag,
            modality_config=modality_config,
            modality_transform=modality_transform,
            denoising_steps=denoising_steps,
            device=self.device,
        )

        self.modality_config = self.policy.modality_config

        if inference_mode == "tensorrt" or inference_mode == "compare":
            setup_tensorrt_engines(self.policy, trt_engine_path)

    def _prepare_starforce_inputs_dict(self, step_data):
        new_data = {}
        for key, value in step_data.items():
            if key.startswith("observation.images"):
                # value = value[None, ...]
                # convert single frame image to a video with temporal
                if isinstance(value, torch.Tensor):
                    assert len(value.shape) == 4, f'{value.shape} should be [1, C, H, W]'
                    # inside need a uint8 numpy array
                    value = (value[0].clamp(0, 1) * 255).byte().numpy().transpose(1, 2, 0)
                    value = value[None, ...]
                new_data[key.replace("observation.images", "video")] = value
            elif "task" in key:
                new_data["language"] = value
            else:
                new_data[key] = value
        return new_data

    def select_action(self, step_data):
        """
        Given step_data same as lerobot format
        support both image and video

        "observation.images.head": torch.tensor [H, W, C]
        "observation.images.left": torch.tensor [H, W, C]
        "observation.images.right": torch.tensor [H, W, C]
        "task": "pick up apple"
        "state": torch.tensor [1, D]

        to:


        "video.<>": np.ndarray,  # (T, H, W, C)
        "state.<>": np.ndarray, # (T, D)
        "language":
        """
        step_data = self._prepare_starforce_inputs_dict(step_data)
        if self.inference_mode == "pytorch":
            return self._run_pytorch(step_data)

        elif self.inference_mode == "tensorrt":
            return self._run_tensorrt(step_data)

        elif self.inference_mode == "compare":
            return self._compare_outputs(step_data)

        else:
            raise ValueError(f"Unsupported inference mode: {self.inference_mode}")

    def _run_pytorch(self, step_data):
        predicted_action = self.policy.get_action(step_data)
        print("\n=== PyTorch Inference Results ===")
        for key, value in predicted_action.items():
            print(key, value.shape)
        return predicted_action

    def _run_tensorrt(self, step_data):
        predicted_action = self.policy.get_action(step_data)
        print("\n=== TensorRT Inference Results ===")
        for key, value in predicted_action.items():
            print(key, value.shape)
        return predicted_action

    def _compare_outputs(self, step_data):
        if not hasattr(self.policy.model.action_head, "init_actions"):
            self.policy.model.action_head.init_actions = torch.randn(
                (
                    1,
                    self.policy.model.action_head.action_horizon,
                    self.policy.model.action_head.action_dim,
                ),
                dtype=torch.float16,
                device=self.device,
            )
        # PyTorch inference
        self.policy.model.action_head.get_action = partial(
            action_head_pytorch_forward, self.policy.model.action_head
        )
        predicted_action_torch = self.policy.get_action(step_data)

        # Setup TensorRT engines and run inference
        setup_tensorrt_engines(policy, args.trt_engine_path)
        predicted_action_tensorrt = self.policy.get_action(step_data)
        # Compare predictions
        compare_predictions(predicted_action_tensorrt, predicted_action_torch)

    @staticmethod
    def get_example_data():
        # You can use this to fetch one example input
        repo_path = os.path.dirname(os.path.dirname(__file__))
        dataset_path = os.path.join(repo_path, "demo_data/robot_sim.PickNPlace")
        dataset = LeRobotSingleDataset(
            dataset_path=dataset_path,
            modality_configs=DATA_CONFIG_MAP["fourier_gr1_arms_only"].modality_config(),
            video_backend="decord",
            video_backend_kwargs=None,
            transforms=None,
            embodiment_tag="gr1",
        )
        return dataset[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GR00T inference")
    parser.add_argument("--model_path", type=str, default="nvidia/GR00T-N1.5-3B")
    parser.add_argument(
        "--inference_mode", type=str, choices=["pytorch", "tensorrt", "compare"], default="pytorch"
    )
    parser.add_argument("--denoising_steps", type=int, default=4)
    parser.add_argument("--trt_engine_path", type=str, default="gr00t_engine")
    args = parser.parse_args()

    vla_model = StarForceVLA(
        model_path=args.model_path,
        inference_mode=args.inference_mode,
        denoising_steps=args.denoising_steps,
        trt_engine_path=args.trt_engine_path,
    )

    example_data = vla_model.get_example_data()
    vla_model.select_action(example_data)
