import os

import torch
from torch import nn
from transformers import AutoConfig, AutoModel, AutoModelForCausalLM
from transformers.feature_extraction_utils import BatchFeature
from transformers.models.qwen2_5_vl import Qwen2_5_VLForConditionalGeneration


class Qwen2_5_VL_Backbone(nn.Module):

    def __init__(
        self,
        vllm_base_model_path=None,
        tune_llm: bool = False,
        tune_visual: bool = False,
        select_layer: int = -1,
        reproject_vision: bool = False,
        use_flash_attention: bool = False,
        load_bf16: bool = False,
        eagle_path: str | None = None,
        project_to_dim: int = 1536,
    ):
        """
        Args:
            tune_llm: whether to tune the LLM model (default: True)
            tune_visual: whether to tune the visual model (default: False)
        """
        super().__init__()
        assert not reproject_vision, "Reproject vision is not implemented here, set to False"

        if vllm_base_model_path is None:
            vllm_base_model_path = "Qwen/Qwen2.5-VL-3B-Instruct"
        self.vllm_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            vllm_base_model_path,
            trust_remote_code=True,
            attn_implementation="flash_attention_2" if torch.cuda.is_available() else "eager",
        )

        print(self.vllm_model)

        if project_to_dim is not None:
            # self.eagle_linear = torch.nn.Linear(2048, project_to_dim)
            self.eagle_linear = torch.nn.Linear(2048, project_to_dim)
        else:
            self.eagle_linear = torch.nn.Identity()

        # print(self.vllm_model.model.layers)
        # print(select_layer)
        # needed since we don't use these layers. Also saves compute
        while len(self.vllm_model.model.layers) > select_layer:
            self.vllm_model.model.layers.pop(-1)

        self.select_layer = select_layer
        self.set_trainable_parameters(tune_llm, tune_visual)

    def set_trainable_parameters(self, tune_llm: bool, tune_visual: bool):
        self.tune_llm = tune_llm
        self.tune_visual = tune_visual
        for p in self.parameters():
            p.requires_grad = True
        if not tune_llm:
            self.vllm_model.model.requires_grad_(False)
            self.vllm_model.lm_head.requires_grad_(False)
        if not tune_visual:
            self.vllm_model.visual.requires_grad_(False)
            # self.vllm_model.mlp1.requires_grad_(False)
        print(f"Tune backbone llm: {self.tune_llm}")
        print(f"Tune backbone visual: {self.tune_visual}")
        # Check if any parameters are still trainable. If not, print a warning.
        if not tune_llm and not tune_visual:
            for name, p in self.named_parameters():
                if p.requires_grad:
                    print(f"Backbone trainable parameter: {name}")
        if not any(p.requires_grad for p in self.parameters()):
            print("Warning: No backbone trainable parameters found.")

    def set_frozen_modules_to_eval_mode(self):
        """
        Huggingface will call model.train() at each training_step. To ensure
        the expected behaviors for modules like dropout, batchnorm, etc., we
        need to call model.eval() for the frozen modules.
        """
        if self.training:
            if self.vllm_model.model and not self.tune_llm:
                self.vllm_model.model.eval()
            if self.vllm_model.visual and not self.tune_visual:
                self.vllm_model.visual.eval()

    def prepare_input(self, batch: dict) -> BatchFeature:
        # print(batch)
        return BatchFeature(data=batch)

    def forward_eagle(self, vl_input: BatchFeature) -> BatchFeature:
        eagle_prefix = "eagle_"
        eagle_input = {
            k.removeprefix(eagle_prefix): v
            for k, v in vl_input.items()
            if k.startswith(eagle_prefix)
        }
        # del eagle_input["image_sizes"]
        # preparing inputs for qwen2.5 vl
        if 'image_sizes' in eagle_input:
            eagle_input["image_grid_thw"] = torch.stack(
                [torch.tensor([1, h // 14, w // 14]) for h, w in eagle_input["image_sizes"]]
            )
            del eagle_input["image_sizes"]
        # print(eagle_input)
        # print(eagle_input['pixel_values'].shape)
        eagle_output = self.vllm_model(**eagle_input, output_hidden_states=True, return_dict=True)
        eagle_features = eagle_output.hidden_states[self.select_layer]
        # print(f'eagle feature: {eagle_features.shape}')
        eagle_features = self.eagle_linear(eagle_features)
        return eagle_features, eagle_input["attention_mask"]

    def forward(self, vl_input: BatchFeature) -> BatchFeature:
        self.set_frozen_modules_to_eval_mode()

        eagle_embeds, eagle_mask = self.forward_eagle(vl_input)
        # print(f'eagle_embeds: {eagle_embeds.shape}')
        # print(f'eagle_mask: {eagle_mask.shape}')
        return BatchFeature(
            data={"backbone_features": eagle_embeds, "backbone_attention_mask": eagle_mask}
        )  # [B, T2, hidden_size]
