# Copyright (c) 2025 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelArguments:
    """Model Argument"""

    # model
    model_path: str = field(
        default=None,
        metadata={"help": "Pretrained model path to local directory."},
    )
    model_name_or_path: str = field(
        default=None,
        metadata={"help": "Pretrained model path to local directory."},
    )
    continue_training: bool = field(
        default=True,
        metadata={
            "help": (
                "Whether to train from existing paddleformers model weights.\n"
                "If set True, the model_path argument must exist in the paddleformers models."
            )
        },
    )
    stage: str = field(
        default="SFT",
        metadata={"help": "The type of training, including PPT, SFT, RM, DPO."},
    )
    tokenizer_alpha: float = field(
        default=None,
        metadata={"help": "Tokenizer will tokenize randomly"},
    )
    use_flash_attention: bool = field(
        default=True,
        metadata={"help": "Whether to use flash attention"},
    )
    use_attn_mask_start_row_indices: bool = field(
        default=True,
        metadata={"help": "Whether to use attn_mask_start_row_indices in flash attention."},
    )
    use_sparse_flash_attn: bool = field(
        default=True,
        metadata={"help": "Under use attn_mask_start_row_indices=True, whether use sparse flash attention or not."},
    )
    use_fast_ln: bool = field(
        default=False,
        metadata={"help": "use_fast_ln"},
    )
    use_sparse_head_and_loss_fn: bool = field(
        default=False,
        metadata={"help": "Whether to use sparse LM Head and loss function."},
    )
    use_fused_head_and_loss_fn: bool = field(
        default=False,
        metadata={"help": "Whether to fuse LM Head and loss function."},
    )
    fuse_linear: bool = field(
        default=False,
        metadata={"help": "Whether to use fused_gemm_epilogue"},
    )
    fuse_rope: bool = field(
        default=False,
        metadata={"help": "Whether to fuse rotary postition embedding"},
    )
    fuse_softmax_mask: bool = field(
        default=False,
        metadata={"help": "Whether to fuse softmax and add"},
    )

    # performance
    virtual_pp_degree: int = field(
        default=1,
        metadata={"help": "virtual_pp_degree"},
    )
    pp_seg_method: str = field(
        default="layer:Ernie4_5_DecoderLayer|EmptyLayer",
        metadata={
            "help": (
                "The method used to segment the pipeline layers among pipeline stages. "
                "Possible values include `layer:Ernie4_5_DecoderLayer`, "
                "`layer:Ernie4_5_DecoderLayer|Empty`, `uniform`, `[0, 30, 59]`."
            )
        },
    )
    tensor_parallel_output: bool = field(
        default=True,
        metadata={
            "help": "If set to True, this option is used with fleet.meta_parallel. "
            "ParallelCrossEntropy to calculate cross-entropy loss for parallel model."
        },
    )
    add_tail_layers: int = field(
        default=False,
        metadata={"help": ("Add EmptyLayer after Ernie4_5_DecoderLayerPipe. Only for Pipeline Parallel")},
    )

    # MoE
    moe_group: Optional[str] = field(
        default="dummy",
        metadata={"help": "moe 的通信组，目前支持“data|dummy”"},
    )
    moe_use_aux_free: Optional[bool] = field(
        default=False,
        metadata={"help": "是否使用aux free"},
    )
    moe_multimodal_dispatch_use_allgather: Optional[str] = field(
        default="v2-alltoall-unpad",
        metadata={"help": "moe dispatch use unpad allgather strategy."},
    )
    use_recompute_moe: Optional[bool] = field(
        default=False,
        metadata={"help": "是否使用recompute_moe"},
    )

    # LoRA
    fine_tuning: str = field(default="LoRA", metadata={"help": "The checkpoint type."})
    lora: bool = field(
        default=False,
        metadata={"help": "Whether to use LoRA technique."},
    )
    lora_rank: int = field(
        default=8,
        metadata={"help": "Lora rank."},
    )
    lora_path: str = field(default=None, metadata={"help": "Initialize lora state dict."})
    rslora: bool = field(
        default=False,
        metadata={"help": "Whether to use RsLoRA"},
    )
    lora_plus_scale: float = field(
        default=1.0,
        metadata={"help": "Lora B scale in LoRA+ technique"},
    )
    lora_alpha: int = field(
        default=-1,
        metadata={"help": "lora_alpha"},
    )
    rslora_plus: bool = field(
        default=False,
        metadata={"help": "Strengthen lora performance"},
    )
    use_quick_lora: bool = field(
        default=False,
        metadata={"help": "quick lora"},
    )
    loraga: bool = field(
        default=False,
        metadata={"help": "Whether to use LoRA-GA:https://arxiv.org/pdf/2407.05000"},
    )
    loraga_init_iters: int = field(
        default=32,
        metadata={"help": "The batch size for lora ga"},
    )
    loraga_stable_gamma: int = field(
        default=64,
        metadata={"help": "Lora Ga stable gamma"},
    )
    loraga_gradient_offload: bool = field(
        default=False,
        metadata={"help": "Whether to offload gradient to CPU during loraga initialization"},
    )

    # recompute
    recompute_granularity: str = field(
        default="full",
        metadata={
            "help": "The granularity of recompute training can be selected as `full` or `full_attn` or `core_attn`. "
            " `full` means complete all transformers, `full_attn` indicates only recompute all self attention parts,"
            " `core_attn` indicates that only the `softmax (qkT) v` part is recomputed. Note: In terms of memory usage,"
            " `core_attn` > `full_attn` > `full`, if the selected policy generates an OOM error, the recompute can be"
            " changed appropriately recompute_granularity. (default: `full`)"
        },
    )
    no_recompute_layers: Optional[int] = field(
        default=None,
        metadata={"help": "Specify the full transformer layers that should not be recomputed."},
    )
    offload_recompute_inputs: bool = field(
        default=False,
        metadata={"help": "Whether to offload input Tensors of recompute to Pinned-Memory/CPU."},
    )
    recompute_use_reentrant: bool = field(
        default=True,
        metadata={
            "help": (
                "If it is True, it means that recompute is implemented using the PyLayer method. "
                "If it is False, recompute internally implements it using the hook method, "
                "and the default value is True. In some scenarios, "
                "such as when recompute is combined with data parallelism, "
                "the no_sync function needs to be called separately. "
                "At this time, use_reentrant=False can be set. "
                "Using the hook method of recompute can avoid calling the no_sync function separately"
            )
        },
    )

    def __post_init__(self):
        self.model_name_or_path = self.model_path
        if self.fine_tuning.lower() == "LoRA".lower():
            self.lora = True
        else:
            self.lora = False
