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

""" Eval Ernie Model. """

import os
from functools import partial
from typing import Any, Optional

import paddle
from paddleformers.trainer import (
    IntervalStrategy,
    RuntimeTimer,
    get_last_checkpoint,
    set_seed,
)
from paddleformers.trainer.trainer_utils import ShardingOption
from paddleformers.transformers.model_utils import unwrap_model
from paddleformers.utils.log import logger

from ernie.configuration import Ernie4_5_MoeConfig
from ernie.modeling_moe import Ernie4_5_MoeForCausalLM
from ernie.modeling_moe_pp import Ernie4_5_MoeForCausalLMPipe
from ernie.tokenizer import Ernie4_5_Tokenizer
from ernie.utils.common_utils import (
    save_stop_info,
    update_refined_recompute,
)

from ..hparams import get_eval_args, read_args
from ..train.sft.trainer import ErnieMoETrainer


def run_eval(args: Optional[dict[str, Any]] = None) -> None:
    """ERNIE MODEL EVALUATION

    Args:
        args (Optional[dict[str, Any]], optional): arguments. Defaults to None.
    """
    # read args
    args = read_args(args)
    model_args, data_args, generating_args, finetuning_args = get_eval_args(args)

    if finetuning_args.sequence_parallel:
        if finetuning_args.pipeline_parallel_degree > 1:
            assert (
                hasattr(finetuning_args, "pipeline_parallel_config")
                and "disable_partial_send_recv" in finetuning_args.pipeline_parallel_config
            ), "Should set '--pipeline_parallel_config disable_partial_send_recv' in bash script for pp with sp."
        if finetuning_args.tensor_parallel_degree <= 1:
            finetuning_args.sequence_parallel = False
            logger.info("Tensor_parallel_degree = 1. Set sequence_parallel to False.")
    if model_args.lora and model_args.fuse_linear:
        model_args.fuse_linear = False
        logger.info("LoRA does not support fuse_linear. Set fuse_linear to False.")
    if finetuning_args.recompute and model_args.offload_recompute_inputs:
        assert (
            model_args.recompute_use_reentrant
        ), "offload_recompute_inputs can only be enabled along with reentrant recompute."
        assert (
            model_args.recompute_granularity == "full"
        ), "To save device memory, please try higher recompute_granularity before enabling offload_recompute_inputs."
        if finetuning_args.pipeline_parallel_degree > 1:
            logger.debug(
                "offload_recompute_inputs is not supported in pipeline parallel. Set offload_recompute_inputs to False."
            )
            model_args.offload_recompute_inputs = False

    runtime_timer = RuntimeTimer("Training")

    if finetuning_args.sharding_parallel_degree > 1:
        if (
            ShardingOption.SHARD_GRAD_OP in finetuning_args.sharding
            or ShardingOption.FULL_SHARD in finetuning_args.sharding
        ):
            if finetuning_args.release_grads is True:
                finetuning_args.release_grads = False

    # checkpoint O1 quantization is open by default.
    if (
        not finetuning_args.disable_ckpt_quant
        and finetuning_args.ckpt_quant_stage == "O0"
        and model_args.stage not in ["Embedding", "RM"]
        and not model_args.lora
    ):
        finetuning_args.ckpt_quant_stage = "O1"
    elif finetuning_args.disable_ckpt_quant:
        finetuning_args.ckpt_quant_stage = "O0"

    finetuning_args.print_config(model_args, "Model")
    finetuning_args.print_config(data_args, "Data")

    paddle.set_device(finetuning_args.device)

    set_seed(finetuning_args.seed)

    logger.warning(
        f"Process rank: {finetuning_args.local_rank}, device: {finetuning_args.device}, world_size: "
        f"{finetuning_args.world_size}, distributed training: {bool(finetuning_args.local_rank != -1)}, "
        f"16-bits training: {finetuning_args.fp16 or finetuning_args.bf16}"
    )

    last_checkpoint = None
    if os.path.isdir(finetuning_args.output_dir) and not finetuning_args.overwrite_output_dir:
        uc_async_save = (
            finetuning_args.unified_checkpoint and "async_save" in finetuning_args.unified_checkpoint_config
        )
        last_checkpoint = get_last_checkpoint(
            finetuning_args.output_dir,
            signal_folder=finetuning_args.output_signal_dir,
            uc_async_save=uc_async_save,
        )
        if last_checkpoint is not None and finetuning_args.resume_from_checkpoint is None:
            logger.info(
                f"Checkpoint detected, resuming training at {last_checkpoint}. To avoid this behavior, change "
                "the `--output_dir` or add `--overwrite_output_dir` to train from scratch."
            )

    if last_checkpoint is not None and model_args.continue_training and not model_args.lora:
        model_args.continue_training = False
        logger.info(f"Checkpoint detected, resuming training at {last_checkpoint}. Set `continue_training` to False.")

    # Set the dtype for loading model
    dtype = paddle.get_default_dtype()
    if finetuning_args.fp16_opt_level == "O2":
        if finetuning_args.fp16:
            dtype = "float16"
        if finetuning_args.bf16:
            dtype = "bfloat16"

    logger.info("Start to load model ...")
    model_class = Ernie4_5_MoeForCausalLM
    if finetuning_args.pipeline_parallel_degree > 1:
        model_class = Ernie4_5_MoeForCausalLMPipe
    if model_args.moe_group.lower() in {"data", "dp"} and finetuning_args.data_parallel_degree > 1:
        finetuning_args.use_expert_parallel = True

    # fuse_softmax_mask only support for rocm.
    if not paddle.is_compiled_with_rocm():
        if model_args.fuse_softmax_mask:
            logger.warning(
                "The fuse_softmax_mask flag is only available when using the ROCM version of paddlepaddle. "
            )
            model_args.fuse_softmax_mask = False

    rr_res = update_refined_recompute(
        finetuning_args.refined_recompute, finetuning_args.sequence_parallel, lora=model_args.lora
    )
    finetuning_args.refined_recompute = rr_res

    runtime_timer.start("basemodel loading time")
    if finetuning_args.weight_quantize_algo is not None:
        if finetuning_args.weight_quantize_algo == "weight_only_mix":
            weight_quantize_algo = {
                "weight_only_int4": [".*mlp.experts.*"],
                "weight_only_int8": [
                    ".*self_attn.qkv_proj.*",
                    ".*self_attn.o_proj.*",
                    ".*mlp.up_gate_proj.*",
                    ".*mlp.down_proj.*",
                ],
            }
        else:
            weight_quantize_algo = finetuning_args.weight_quantize_algo
        quantization_config = dict(
            weight_quantize_algo=weight_quantize_algo,
            ignore_modules=[".*out_linear.*"],
            apply_hadamard=finetuning_args.apply_hadamard,
            hadamard_block_size=finetuning_args.hadamard_block_size,
            quant_input_grad=finetuning_args.quant_input_grad,
            quant_weight_grad=finetuning_args.quant_weight_grad,
            apply_online_actscale_step=finetuning_args.apply_online_actscale_step,
            actscale_moving_rate=finetuning_args.actscale_moving_rate,
            fp8_format_type=finetuning_args.fp8_format_type,
        )
    else:
        quantization_config = dict(weight_quantize_algo=finetuning_args.weight_quantize_algo)

    model_config = Ernie4_5_MoeConfig.from_pretrained(
        model_args.model_path,
        dtype=dtype,
        quantization_config=quantization_config,
    )
    model_config.tensor_parallel_degree = finetuning_args.tensor_parallel_degree
    model_config.tensor_parallel_rank = finetuning_args.tensor_parallel_rank
    model_config.recompute = finetuning_args.recompute
    model_config.recompute_granularity = model_args.recompute_granularity
    model_config.no_recompute_layers = model_args.no_recompute_layers
    model_config.refined_recompute = finetuning_args.refined_recompute
    model_config.offload_recompute_inputs = model_args.offload_recompute_inputs
    model_config.use_flash_attention = model_args.use_flash_attention
    model_config.sequence_parallel = finetuning_args.sequence_parallel
    model_config.use_sparse_head_and_loss_fn = model_args.use_sparse_head_and_loss_fn
    model_config.use_fused_head_and_loss_fn = model_args.use_fused_head_and_loss_fn
    model_config.tensor_parallel_output = model_args.tensor_parallel_output
    model_config.virtual_pp_degree = model_args.virtual_pp_degree
    model_config.pp_seg_method = model_args.pp_seg_method
    model_config.fuse_linear = model_args.fuse_linear
    model_config.fuse_rope = model_args.fuse_rope
    model_config.fuse_softmax_mask = model_args.fuse_softmax_mask
    model_config.max_sequence_length = data_args.max_seq_len
    model_config.use_fast_ln = model_args.use_fast_ln
    model_config.recompute_use_reentrant = model_args.recompute_use_reentrant
    model_config.use_sparse_flash_attn = model_args.use_sparse_flash_attn
    model_config.use_recompute_moe = model_args.use_recompute_moe
    model_config.moe_group = model_args.moe_group
    model_config.moe_use_aux_free = model_args.moe_use_aux_free
    model_config.hidden_dropout_prob = finetuning_args.hidden_dropout_prob
    model_config.attention_probs_dropout_prob = finetuning_args.attention_probs_dropout_prob
    model_config.moe_multimodal_dispatch_use_allgather = model_args.moe_multimodal_dispatch_use_allgather
    model_config.num_acc_steps = finetuning_args.gradient_accumulation_steps

    if (
        model_args.continue_training and not finetuning_args.autotuner_benchmark
    ) or finetuning_args.weight_quantize_algo is not None:
        model = model_class.from_pretrained(
            model_args.model_path,
            config=model_config,
        )
    else:
        model = model_class.from_config(model_config, dtype=dtype)

    paddle.device.cuda.empty_cache()
    logger.info("Loading model successfully !")
    logger.debug(f"Model config: {model.config}")
    logger.info(f"{runtime_timer.log()}")

    tokenizer = Ernie4_5_Tokenizer.from_pretrained(
        model_args.model_path,
        tokenizer_alpha=model_args.tokenizer_alpha,
    )

    logger.info("Start to create dataset ...")
    dataset_config = {
        "tokenizer": tokenizer,
        "max_seq_len": data_args.max_seq_len,
        "random_seed": finetuning_args.seed,
        "num_replicas": finetuning_args.dataset_world_size,
        "rank": finetuning_args.dataset_rank,
    }
    if model_args.stage == "PPT":
        from ernie.dataset.posttraining import collate_fn, create_dataset
    elif model_args.stage == "SFT":
        from ernie.dataset.finetuning import collate_fn

        if data_args.dataset_type == "map":
            from ernie.dataset.finetuning import (
                create_indexed_dataset as create_dataset,
            )
        else:
            from ernie.dataset.finetuning import create_dataset
        dataset_config.update(
            {
                "num_samples_each_epoch": data_args.num_samples_each_epoch,
                "random_shuffle": data_args.random_shuffle,
                "greedy_intokens": data_args.greedy_intokens,
            }
        )
    else:
        raise ValueError(f"Invalid stage: {data_args.stage}")

    if finetuning_args.do_eval and finetuning_args.should_load_dataset:
        if model_args.stage == "SFT" and data_args.dataset_type == "map":
            eval_file_path = os.path.join(data_args.offline_dataset_path, "eval")
            eval_dataset = create_dataset(data_file_prefix=eval_file_path)
        else:
            eval_dataset = create_dataset(
                task_group=data_args.eval_dataset_path,
                task_group_prob=data_args.eval_dataset_prob,
                sub_dataset_type=data_args.eval_dataset_type,
                is_valid=True,
                **dataset_config,
            )

    logger.info("Creating dataset successfully ...")

    data_collator = partial(collate_fn, tokenizer=tokenizer, model_args=model_args, max_seq_len=data_args.max_seq_len)

    if model_args.lora:
        logger.info("Start to wrap model with LoRA config ...")

        from ernie.utils.peft_utils import initialize_lora_model

        loraga_gradient_dict = None
        if model_args.loraga and last_checkpoint is None and model_args.lora_path is None:
            # LoRA-GA gradient estimation
            from paddleformers.peft.lora.loraga_utils import LoRAGATrainer

            # Create a temporary dataset for LoRA-GA gradient estimation
            runtime_timer.start("LoRA-GA gradient estimation Time")
            loraga_trainer = LoRAGATrainer(
                model=model,
                args=finetuning_args,
                train_dataset=None,
                tokenizer=tokenizer,
                data_collator=data_collator,
                loraga_init_iters=model_args.loraga_init_iters,
                gradient_offload=model_args.loraga_gradient_offload,
            )
            loraga_gradient_dict = loraga_trainer.estimate_gradient(model)
            logger.info(f"{runtime_timer.log()}")

        model = initialize_lora_model(
            model=model,
            training_args=finetuning_args,
            model_args=model_args,
            resume_from_checkpoint=last_checkpoint is not None,
            dtype=dtype,
            loraga_gradient_dict=loraga_gradient_dict,
        )
    # Create the learning_rate sheduler and optimizer
    if finetuning_args.decay_steps is None:
        finetuning_args.decay_steps = finetuning_args.max_steps

    if finetuning_args.save_strategy == IntervalStrategy.EPOCH:
        finetuning_args.save_strategy = IntervalStrategy.STEPS
        finetuning_args.save_steps = int(finetuning_args.max_steps / finetuning_args.num_train_epochs)
    if finetuning_args.evaluation_strategy == IntervalStrategy.EPOCH:
        finetuning_args.evaluation_strategy = IntervalStrategy.STEPS
        finetuning_args.eval_steps = int(finetuning_args.max_steps / finetuning_args.num_train_epochs)
    if finetuning_args.logging_strategy == IntervalStrategy.EPOCH:
        finetuning_args.logging_strategy = IntervalStrategy.STEPS
        finetuning_args.logging_steps = int(finetuning_args.max_steps / finetuning_args.num_train_epochs)

    if not model_args.use_sparse_head_and_loss_fn and not finetuning_args.prediction_loss_only:
        unwraped_model = unwrap_model(model)
        if hasattr(model, "compute_metrics"):
            compute_metrics = model.compute_metrics
        elif hasattr(unwraped_model, "compute_metrics"):
            # NOTE(liuting): if model is LoRAModel, we need to unwrap it first.
            compute_metrics = unwraped_model.compute_metrics
        else:
            compute_metrics = None
    else:
        compute_metrics = None

    trainer = ErnieMoETrainer(
        model=model,
        args=finetuning_args,
        train_dataset=None,
        eval_dataset=(eval_dataset if finetuning_args.do_eval and finetuning_args.should_load_dataset else None),
        tokenizer=tokenizer,
        do_generation=False,
        data_args=data_args,
        data_collator=data_collator,
    )
    trainable_parameters = [
        p for p in model.parameters() if not p.stop_gradient or ("quantization_linear" in p.name and "w_1" in p.name)
    ]
    trainer.set_optimizer_grouped_parameters(trainable_parameters)

    trainer._load_from_checkpoint(resume_from_checkpoint=last_checkpoint)
    trainer.create_optimizer_and_scheduler(num_training_steps=10)
    model = trainer._wrap_model(trainer.model_wrapped)
    if model is not trainer.model:
        trainer.model_wrapped = model
    if finetuning_args.do_eval:
        eval_result = trainer.evaluate()
        trainer.log_metrics("eval", eval_result)
        # NOTE(gongenlei): set combined=False to avoid overwriting errors on AFS
        trainer.save_metrics("eval", eval_result, combined=False)

    save_stop_info(
        finetuning_args,
        trainer.state.global_step,
        outside_eval=finetuning_args.do_eval,
        outside_predict=0,
    )
