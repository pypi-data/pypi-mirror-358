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

"""
公共组件
"""
import ast
import copy
import json
import os
import re
import signal
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Set

import GPUtil
import yaml
from psutil import NoSuchProcess, Process

WEBUI_PATH = os.path.dirname(os.path.abspath(__file__))
ERNIEKIT_PATH = os.path.dirname(WEBUI_PATH)
ROOT_PATH = os.path.dirname(ERNIEKIT_PATH)
CONFIG_PATH = os.path.join(WEBUI_PATH, "config")
DEFAULT_DATASET_PATH = os.path.join(CONFIG_PATH, "dataset.json")
EXECUTE_PATH = os.path.join(CONFIG_PATH, "execute")

"""_summary_
评估
Returns:
    _type_: _description_
"""


class ConfigManager:
    """_summary_
    评估
    Returns:
        _type_: _description_
    """

    def __init__(self):
        self._initialized = True
        self.user_dict = {}
        self._default_path_config = {
            "default_yaml": os.path.join(CONFIG_PATH, "default.yaml"),
            "dataset_info_json": os.path.join(CONFIG_PATH, "dataset_info.json"),
            "save_checkpoint_dir": os.path.join(ERNIEKIT_PATH, "save"),
            "output_dir": "./output",
            "logging_dir": "vdl_log",
            "paddle_log_dir": "paddle_dist_log",
        }

        self._commands_cli = {
            "train": "erniekit train",
            "export": "erniekit export",
            "eval": "erniekit eval",
            "server": "erniekit server",
            "split": "erniekit split",
            "chat": "erniekit chat",
            "version": "erniekit version",
            "help": "erniekit help",
        }

        self._user_default_config = self._init_user_dict()
        self._execute_yaml_path = self._init_execute_yaml_path()
        self._dataset_info = self._init_dataset_info()
        self._thought_models = ["ERNIE-X1-300B-A47B"]
        self._choices_kwargs = {
            "model_name": [
                "ERNIE-4.5-300B-A47B-Base",
                "ERNIE-4.5-300B-A47B",
                "ERNIE-4.5-300B-A47B-W4A8C8-TP4",
                "ERNIE-4.5-300B-A47B-FP8",
                "ERNIE-4.5-300B-A47B-2BITS",
                "ERNIE-4.5-21B-A3B-Base",
                "ERNIE-4.5-21B-A3B",
                "ERNIE-4.5-0.3B-Base",
                "ERNIE-4.5-0.3B",
                "Customization",
            ],
            "model_path_selector": ["Local", "Hugging_face"],
            "model_path_local": {
                "ERNIE-4.5-300B-A47B-Base": "./baidu/ERNIE-4.5-300B-A47B-Base",
                "ERNIE-4.5-300B-A47B": "./baidu/ERNIE-4.5-300B-A47B",
                "ERNIE-4.5-300B-A47B-W4A8C8-TP4": "./baidu/ERNIE-4.5-300B-A47B-W4A8C8-TP4",
                "ERNIE-4.5-300B-A47B-FP8": "./baidu/ERNIE-4.5-300B-A47B-FP8",
                "ERNIE-4.5-300B-A47B-2BITS": "./baidu/ERNIE-4.5-300B-A47B-2BITS",
                "ERNIE-4.5-21B-A3B-Base": "./baidu/ERNIE-4.5-21B-A3B-Base",
                "ERNIE-4.5-21B-A3B": "./baidu/ERNIE-4.5-21B-A3B",
                "ERNIE-4.5-0.3B-Base": "./baidu/ERNIE-4.5-0.3B-Base",
                "ERNIE-4.5-0.3B": "./baidu/ERNIE-4.5-0.3B",
            },
            "model_path_hugging_face": {
                "ERNIE-4.5-300B-A47B-Base": "/baidu/ERNIE-4.5-300B-A47B-Base",
                "ERNIE-4.5-300B-A47B": "/baidu/ERNIE-4.5-300B-A47B",
                "ERNIE-4.5-300B-A47B-W4A8C8-TP4": "/baidu/ERNIE-4.5-300B-A47B-W4A8C8-TP4",
                "ERNIE-4.5-300B-A47B-FP8": "/baidu/ERNIE-4.5-300B-A47B-FP8",
                "ERNIE-4.5-300B-A47B-2BITS": "/baidu/ERNIE-4.5-300B-A47B-2BITS",
                "ERNIE-4.5-21B-A3B-Base": "/baidu/ERNIE-4.5-21B-A3B-Base",
                "ERNIE-4.5-21B-A3B": "/baidu/ERNIE-4.5-21B-A3B",
                "ERNIE-4.5-0.3B-Base": "/baidu/ERNIE-4.5-0.3B-Base",
                "ERNIE-4.5-0.3B": "/baidu/ERNIE-4.5-0.3B",
            },
            "fine_tuning": ["LoRA", "Full"],
            "existed_dataset_list": list(self._dataset_info.keys()),
            "stage": ["SFT", "DPO"],
            "compute_type_Full": ["bf16", "fp16"] + self.check_h_series_gpu(),
            "compute_type_LoRA": ["bf16", "fp16", "wint8", "wint4/8"] + self.check_h_series_gpu(),
            "best_config": ["SFT", "DPO"],
            "language": ["zh", "en"],
            "boolean_choice": ["True", "False"],
            "moe_group": ["dummy", "mp"],
            "dataset_type": ["file", "alpaca"],
        }

    def get_compute_type_by_fine_tuning(self, fine_tuning):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        result = self._choices_kwargs["compute_type_" + fine_tuning].keys()
        if result is None:
            return self._choices_kwargs["compute_type_LoRA"]
        return result

    def _init_user_dict(self):
        """读取YAML文件并返回字典对象"""
        try:
            with open(self.get_path_config("default_yaml"), "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            if "train_sft" in data:
                data["train"] = copy.deepcopy(data["train_sft"])
            return data
        except FileNotFoundError:
            print(f"错误：找不到文件 {self.get_path_config('default_yaml')}")
            return None
        except yaml.YAMLError as e:
            print(f"YAML解析错误：{e}")
            return None

    def is_thought_model(self, model_name: str) -> bool:
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        if not isinstance(model_name, str):
            return False

        return model_name in self._thought_models

    def check_h_series_gpu(self):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return []

            gpu_names = result.stdout.strip().split('\n')
            for name in gpu_names:
                if re.search(r'\bH(100|200|800)\b', name, re.IGNORECASE):
                    return ["fp8"]

            return []

        except Exception as e:
            return []

    def get_model_path(self, model_name, model_path_selector="Local"):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        return self._choices_kwargs["model_path"+"_"+model_path_selector].get(model_name)

    def get_execute_command(self, name):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        execute_command = {
            "export": self.get_commands_cli("export") + " " + self.get_execute_yaml_path("export_yaml_path"),
            "split": self.get_commands_cli("split") + " " + self.get_execute_yaml_path("export_yaml_path"),
            "eval": self.get_commands_cli("eval") + " " + self.get_execute_yaml_path("eval_yaml_path"),
            "chat": self.get_commands_cli("server") + " " + self.get_execute_yaml_path("chat_yaml_path"),
            "train_sft": self.get_commands_cli("train") + " " + self.get_execute_yaml_path("train_sft_yaml_path"),
            "train_dpo": self.get_commands_cli("train") + " " + self.get_execute_yaml_path("train_dpo_yaml_path"),
        }

        return execute_command.get(name)

    def get_execute_yaml_path(self, name: str):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        return self._execute_yaml_path[name]

    def get_default_user_dict(self, module, name):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        try:
            return self._user_default_config[module][name]
        except KeyError:
            return None

    def get_default_dict_module(self, module):
        """

        Args:
            module:

        Returns:

        """
        try:
            return self._user_default_config[module]
        except KeyError:
            return None

    def _init_execute_yaml_path(self):
        """初始化执行YAML配置路径"""
        execute_path_list = self.get_default_dict_module("execute")
        return {
            "chat_yaml_path": os.path.join(EXECUTE_PATH, execute_path_list["chat_yaml_path"]),
            "export_yaml_path": os.path.join(EXECUTE_PATH, execute_path_list["export_yaml_path"]),
            "eval_yaml_path": os.path.join(EXECUTE_PATH, execute_path_list["eval_yaml_path"]),
            "train_sft_yaml_path": os.path.join(EXECUTE_PATH, execute_path_list["train_sft_yaml_path"]),
            "train_dpo_yaml_path": os.path.join(EXECUTE_PATH, execute_path_list["train_dpo_yaml_path"]),
        }

    def get_gpu_count(self):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        try:
            return len(GPUtil.getGPUs())
        except Exception as e:
            print(f"获取GPU信息失败: {e}")
            return 0

    def get_path_config(self, name: str):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        return self._default_path_config[name]

    def get_choices_kwargs(self, name: str):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        value = self._choices_kwargs[name]

        if not isinstance(value, (list, tuple, dict)):
            return None

        return self._choices_kwargs[name]

    def get_dataset_info_kwagrs(self, name: str):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        try:
            value = self._dataset_info[name]
        except KeyError:
            return None
        return value

    def get_commands_cli(self, name: str):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        return self._commands_cli[name]

    def update_config(self, new_config: Dict[str, Any], deep: bool = True) -> None:
        """
        更新配置，支持深度更新
        Args:
            new_config: 要更新的配置
            deep: 是否使用深度更新，默认为True
        """
        if deep:
            self.user_dict = self.deep_update(self.user_dict, new_config)
        else:
            self.user_dict.update(new_config)

    def deep_update(self, source: Dict, updates: Dict) -> Dict:
        """递归更新嵌套字典"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in source and isinstance(source[key], dict):
                source[key] = self.deep_update(source[key], value)
            else:
                source[key] = value
        return source

    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.user_dict

    def get_checkpoint_choices(self, model_name, fine_tuning) -> Any:
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        try:
            checkpoints_dir = os.path.join(self.get_path_config("save_checkpoint_dir"), model_name, fine_tuning)
            checkpoints = [x for x in os.listdir(checkpoints_dir)]
            return sorted(checkpoints)
        except FileNotFoundError:
            return []

    def update_checkpoint_choices(self, model_name, fine_tuning):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        try:

            if model_name is None or fine_tuning is None:
                return []

            checkpoints_dir = os.path.join(self.get_path_config("save_checkpoint_dir"), model_name, fine_tuning)
            checkpoints = [x for x in os.listdir(checkpoints_dir)]
            return sorted(checkpoints)
        except FileNotFoundError:
            return []

    def load_dataset(self) -> Dict:
        """加载数据集（带错误处理）"""
        try:
            with open(self.get_path_config("dataset_json"), "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARN] Failed to load dataset: {e}")
            return {}

    def _init_dataset_info(self):
        """
        加载数据集信息
        Returns:

        """
        try:
            with open(self.get_path_config("dataset_info_json"), "r") as f:
                data = dict(json.load(f))
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARN] Failed to load dataset: {e}")
            return []


config = ConfigManager()


def load_data(data_path, page=1, page_size=2):
    """
    从多个JSON文件加载数据并支持分页

    参数:
        data_path: 单个文件路径字符串或包含多个文件路径的列表
        page: 页码，默认为1
        page_size: 每页数据量，默认为2

    返回:
        当前页的数据列表和总数据量
    """
    # 确保data_path是列表类型
    if isinstance(data_path, str):
        data_path = [data_path]

    if page is None:
        page = 1

    all_data = []

    # 遍历所有文件路径
    for path in data_path:
        try:
            # 处理绝对路径和相对路径
            if not os.path.isabs(path):
                # 假设相对路径是相对于当前工作目录
                path = os.path.join(os.getcwd(), path)

            # 检查文件是否存在
            if not os.path.exists(path):
                print(f"警告: 文件不存在 - {path}")
                continue

            # 检查文件扩展名是否为json或jsonl
            ext = os.path.splitext(path)[1].lower()

            # 根据文件类型读取数据
            with open(path, "r", encoding="utf-8") as f:
                if ext == ".json":
                    # 普通JSON文件
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)
                elif ext == ".jsonl":
                    # JSONL格式文件（每行一个JSON对象）
                    for line in f:
                        if line.strip():  # 忽略空行
                            all_data.append(json.loads(line))
                else:
                    print(f"警告: 不支持的文件格式 - {path}")
        except Exception as e:
            print(f"错误: 读取文件时发生错误 - {path}: {e!s}")

    # 分页处理
    total = len(all_data)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return all_data[start_idx:end_idx], total


# def load_data(data_path, page=1, page_size=2):
#     with open(data_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#         total = len(data)
#         start_idx = (page - 1) * page_size
#         end_idx = start_idx + page_size
#         return data[start_idx:end_idx], total


def format_json(data):
    """_summary_
    评估
    Returns:
        _type_: _description_
    """
    return json.dumps(data, ensure_ascii=False, indent=2)


def dict_to_cli_args(params, include_keys=None):
    """
    将字典转换为命令行参数列表
    Args:
        params: 参数词典
        include_keys: 需要包含的键名列表，默认为None表示包含所有键

    Returns:
        命令行参数字符串列表
    """
    cli_args = []
    for key, value in params.items():
        # 如果指定了include_keys且当前key不在其中，则跳过
        if include_keys is not None and key not in include_keys:
            continue

        # 跳过值为None的项
        if value is None:
            continue

        if isinstance(value, dict):
            # 递归处理子字典
            cli_args.extend(dict_to_cli_args(value))
        else:
            if isinstance(value, list):
                value_str = " ".join(map(str, value)) if value else ""
            else:
                value_str = str(value)
            cli_args.append(f"--{key} {value_str}")
    return cli_args


def concatenate_params(command_type, params_dict, sub_commands=None):
    """
    将命令类型和参数字典拼接成完整的命令行参数字符串
    Args:
        command_type: 命令类型
        params_dict: 参数词典
        sub_commands: 需要包含的子命令列表，如 ['chat', 'train']

    Returns:
        完整的命令行参数字符串
    """
    # 基础命令
    base_command = config.get_commands_cli(command_type)

    # 所有类型都必须包含的3个顶级参数
    top_level_params = [
        "model_name",
        "fine_tuning",
        "model_path",
        "compute_type",
        "tensor_parallel_degree",
        "pipeline_parallel_degree",
        "sharding_parallel_degree",
        "checkpoint_path",
    ]
    basic_params = params_dict.get("basic", {})  # 使用 get 避免 KeyError
    filtered_dict = {k: basic_params[k] for k in top_level_params if k in basic_params}

    top_level_args = dict_to_cli_args(filtered_dict)

    # 根据sub_commands参数决定包含哪些子命令的参数
    sub_command_args = []
    if sub_commands:
        for sub_cmd in sub_commands:
            if sub_cmd in params_dict:
                sub_cmd_args = dict_to_cli_args(params_dict[sub_cmd])
                sub_command_args.extend(sub_cmd_args)

    # 合并所有参数
    all_args = top_level_args + sub_command_args
    params_string = " \\\n    ".join(all_args)

    return f"{base_command} {params_string}"


def yaml_to_args(yaml_path, erniekit_execute):
    """
    读取YAML配置文件并转换为命令行参数字符串

    Args:
        yaml_path (str): YAML文件路径

    Returns:
        str: 转换后的命令行参数字符串
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    args_list = []
    indentation = "    "

    for key, value in config.items():
        arg_name = f"--{key}"

        if isinstance(value, bool):
            args_list.append(f"{indentation}{arg_name} {str(value).lower()}")
        elif isinstance(value, list):
            args_list.append(f"{indentation}{arg_name} {','.join(map(str, value))}")
        else:
            args_list.append(f"{indentation}{arg_name} {value}")

    return erniekit_execute + "\n" + "\n".join(args_list)


def run_command(command):
    """
    运行命令
    Args:
        command: 要执行的命令
    Returns:
        子进程对象
    """
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,  # 直接返回字符串而非字节
    )
    print(f"执行命令: {command}")

    # 处理输出的生成器
    def output_generator():
        for line in iter(process.stdout.readline, ""):
            yield line.strip()
        process.wait()  # 确保进程完全结束

    # 在后台线程中打印输出
    def print_output():
        for line in output_generator():
            print(line)

    threading.Thread(target=print_output, daemon=True).start()

    return process


def kill_process_command(pid):
    """
    终止进程
    Args:
        pid:

    Returns:

    """
    subprocess.run(["kill", "-9", str(pid)], check=True)


def mkdir_checkpoint_dir(model_name=None, fine_tuning=None):
    """
    创建模型保存目录
    Args:
        current_config:
        model_name:
        fine_tuning:

    Returns:

    """
    if model_name is not None:
        full_path = Path(config.get_path_config("save_checkpoint_dir")) / model_name

        try:
            full_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"创建目录失败: {full_path}, 错误: {e}")

    if fine_tuning is not None and model_name is not None:
        full_path = Path(config.get_path_config("save_checkpoint_dir")) / model_name / fine_tuning

        try:
            full_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"创建目录失败: {full_path}, 错误: {e}")


def flatten_section(section: Dict[str, Any]) -> Dict[str, Any]:
    """将单个嵌套配置项（如eval）扁平化为无前缀的键值对"""
    flat_data = {}
    for key, value in section.items():
        flat_data[key] = value
    return flat_data


def merge_config(
    existing_config: Dict[str, Any],
    new_required: Dict[str, Any],
    new_sections: Dict[str, Dict[str, Any]],
    allowed_updates: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    合并配置：支持选择性更新和纯追加
    - allowed_updates: 允许更新的字段白名单（已有字段可被覆盖）
    - 不在白名单中的字段仅在不存在时追加
    """
    allowed_updates = allowed_updates or set()
    merged = existing_config.copy()

    # 1. 处理必需的顶级参数
    for key, value in new_required.items():
        if key in allowed_updates:
            merged[key] = value  # 允许更新的字段直接覆盖
        elif key not in merged:
            merged[key] = value  # 不允许更新的字段仅追加

    # 2. 处理筛选的嵌套配置项
    for section_name, section_data in new_sections.items():
        flat_section = flatten_section(section_data)
        for key, value in flat_section.items():
            if key in allowed_updates:
                merged[key] = value  # 允许更新的字段直接覆盖
            elif key not in merged:
                merged[key] = value  # 不允许更新的字段仅追加

    return merged


def abort_process(pid: int) -> None:
    r"""Abort the processes recursively in a bottom-up way."""
    # 用于存储所有待终止的进程ID
    pids_to_kill = []

    try:
        # 获取当前进程对象
        parent = Process(pid)
        # 递归获取所有子进程
        children = parent.children(recursive=True)
        # 将子进程的ID添加到待终止列表
        pids_to_kill = [child.pid for child in children]
        # 将父进程的ID添加到待终止列表
        pids_to_kill.append(pid)
    except NoSuchProcess:
        # 如果进程不存在，直接返回
        return

    # 尝试终止所有进程
    for pid in pids_to_kill:
        try:
            os.kill(pid, signal.SIGABRT)
        except OSError:
            # 进程可能已经终止，继续处理下一个
            pass

    # 等待一段时间，让进程有机会终止
    time.sleep(0.5)

    # 检查哪些进程还在运行
    still_alive = []
    for pid in pids_to_kill:
        try:
            # 尝试获取进程状态
            Process(pid).status()
            still_alive.append(pid)
        except NoSuchProcess:
            # 进程已终止，继续检查下一个
            pass

    # 对仍然运行的进程发送SIGKILL信号
    for pid in still_alive:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            # 进程可能在最后一刻终止了
            pass


def flatten_dict(nested_dict, parent_key="", separator=".", exclude_keys=None):
    """
    将嵌套字典扁平化，可排除特定键

    参数:
        nested_dict: 嵌套字典
        parent_key: 父键前缀
        separator: 键之间的分隔符
        exclude_keys: 需要排除的键列表

    返回:
        扁平化后的字典
    """
    if exclude_keys is None:
        exclude_keys = []

    items = {}
    for key, value in nested_dict.items():
        # 跳过需要排除的键
        if key in exclude_keys:
            continue

        if isinstance(value, dict):
            # 递归处理子字典
            items.update(flatten_dict(value, "", separator, exclude_keys))
        else:
            items[key] = value
    return items


def parse_string_to_list(value):
    """
    将字符串形式的列表解析为真正的列表

    参数:
        value: 字符串形式的列表，如 "['a', 'b']" 或 "[1.0]"

    返回:
        解析后的列表，如果解析失败则返回原值
    """
    if not isinstance(value, str):
        return value

    # 检查是否像列表字符串
    if value.strip().startswith("[") and value.strip().endswith("]"):
        try:

            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # 如果解析失败，返回原值
            return value

    return value


def format_list_value(value, is_numeric=False):
    """
    格式化列表值，字符串加引号，数字不加引号，特殊处理布尔值字符串

    参数:
        value: 列表值
        is_numeric: 是否强制转换为数字类型

    返回:
        格式化后的字符串，并标记为需要去除引号
    """
    if not isinstance(value, list):
        return value

    formatted_items = []
    for item in value:
        if is_numeric:
            # 强制转换为数字
            try:
                # 尝试转换为浮点数，如果是整数则保持为整数
                num_value = float(item)
                if num_value.is_integer():
                    formatted_items.append(str(int(num_value)))
                else:
                    formatted_items.append(str(num_value))
            except (ValueError, TypeError):
                # 如果转换失败，当作字符串处理
                formatted_items.append(f'"{item!s}"')
        elif isinstance(item, str):
            # 特殊处理布尔值字符串
            if item.lower() == "true":
                formatted_items.append("True")
            elif item.lower() == "false":
                formatted_items.append("False")
            else:
                # 普通字符串加双引号
                formatted_items.append(f'"{item}"')
        elif isinstance(item, (int, float)):
            # 数字不加引号
            formatted_items.append(str(item))
        else:
            # 其他类型转换为字符串并加引号
            formatted_items.append(f'"{item!s}"')

    # 返回特殊标记的字符串，后面会用来识别和去除引号
    # 使用较紧凑的格式，减少跨行的可能性
    return f"__NOQUOTE_START__[{','.join(formatted_items)}]__NOQUOTE_END__"


def convert_boolean_strings(value):
    """
    将字符串形式的布尔值转换为Python布尔值

    参数:
        value: 要转换的值

    返回:
        转换后的值
    """
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
    return value


def merge_dict_to_yaml(
    manager,
    dict_data,
    yaml_file_path,
    first_level_keys=None,
    exclude_keys=None,
    special_list_keys=None,
):
    """
    将扁平化后的字典数据更新到YAML文件中，可排除特定键并对特定键进行列表格式化处理

    参数:
        dict_data: 源字典数据
        yaml_file_path: YAML文件路径
        first_level_keys: 要处理的第一层键列表，如果为None则处理所有键
        exclude_keys: 需要排除的键列表
        special_list_keys: 需要进行特殊列表处理的键列表
    """

    all_components = manager.get_all_specific_component_values()
    filtered_dict = {
        k.replace("specific_", ""): v
        for k, v in all_components.items()
        if k.replace("specific_", "") in set(first_level_keys)
    }

    merged_dict = deep_merge(filtered_dict, dict_data.copy())

    if first_level_keys:
        merged_dict = {key: merged_dict.get(key, {}) for key in first_level_keys}
        merged_dict = update_dataset_paths(merged_dict, manager)

    flattened_dict = flatten_dict(merged_dict, exclude_keys=exclude_keys)

    special_list_keys = special_list_keys or []

    for key, value in flattened_dict.items():
        should_special_process = key in special_list_keys

        is_prob_key = "prob" in key.lower()

        # 自动将包含 "path" 或 "prob" 的键视为需要特殊处理
        if should_special_process:
            # 对特殊键进行处理
            if isinstance(value, str):
                # 如果是字符串，尝试按逗号分割成列表
                if "," in value:
                    # 分割字符串并去除空白
                    parsed_list = [item.strip() for item in value.split(",") if item.strip()]
                    # 如果是包含prob的键，转换为数字列表
                    if is_prob_key:
                        flattened_dict[key] = format_list_value(parsed_list, is_numeric=True)
                    else:
                        flattened_dict[key] = format_list_value(parsed_list)
                else:
                    # 单个值也转换为列表
                    single_value = value.strip()
                    if is_prob_key:
                        flattened_dict[key] = format_list_value([single_value], is_numeric=True)
                    else:
                        flattened_dict[key] = format_list_value([single_value])
            elif isinstance(value, list):
                # 如果已经是列表，直接格式化
                if is_prob_key:
                    flattened_dict[key] = format_list_value(value, is_numeric=True)
                else:
                    flattened_dict[key] = format_list_value(value)
        else:
            # 先尝试解析字符串形式的列表
            parsed_value = parse_string_to_list(value)
            # 如果解析成功得到列表，则格式化它
            if isinstance(parsed_value, list):
                flattened_dict[key] = format_list_value(parsed_value)
            # 如果原本就是列表，也格式化它
            elif isinstance(value, list):
                flattened_dict[key] = format_list_value(value)
            else:
                # 新增：处理布尔值字符串
                flattened_dict[key] = convert_boolean_strings(value)

    if os.path.exists(yaml_file_path):
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f) or {}
    else:
        yaml_data = {}

    yaml_data.update(flattened_dict)

    # 先写入YAML文件，设置较大的行宽度避免自动换行
    with open(yaml_file_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, width=1000)

    # 读取文件内容并去除特定格式的引号
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 使用正则表达式去除标记字符串的引号
    # 匹配 '__NOQUOTE_START__[...]__NOQUOTE_END__' 前后的引号
    content = re.sub(r"'__NOQUOTE_START__(.*?)__NOQUOTE_END__'", r"\1", content)
    content = re.sub(r'"__NOQUOTE_START__(.*?)__NOQUOTE_END__"', r"\1", content)

    # 去除标记符号
    content = content.replace("__NOQUOTE_START__", "").replace("__NOQUOTE_END__", "")

    # 写回文件
    with open(yaml_file_path, "w", encoding="utf-8") as f:
        f.write(content)


def deep_merge(source, destination):
    """
    递归合并两个字典：
    - 若键存在且值都是字典，递归合并内部字段
    - 否则用destination的值覆盖source的值
    """
    for key, value in source.items():
        if key in destination and isinstance(destination[key], dict) and isinstance(value, dict):
            destination[key] = deep_merge(value, destination[key])
        else:
            destination[key] = value
    return destination


def update_dataset_paths(config_dict, manager):
    """
    在配置字典中查找并替换所有以 "dataset" 结尾的键，将其值替换为默认路径。

    Args:
        config_dict: 待处理的配置字典。
    Returns:
        经过处理的新配置字典。
    """

    def merge_values(base, addition, separator=','):
        """安全合并两个值，处理None和空字符串"""
        if base is None:
            return addition
        if addition is None:
            return base
        return f"{base}{separator}{addition}"

    basic_config = config_dict.get("basic", {})
    train_config = config_dict.get("train", {})

    if train_config != {}:

        if basic_config["output_dir_view"]:
            basic_config["output_dir"] = basic_config["output_dir_view"]
        else:
            basic_config["output_dir"] = mkdir_output_dir(manager)

        train_config["train_dataset_path"] = merge_values(
            train_config["train_customize_dataset_path"], train_config["train_existed_dataset_path"]
        )

        train_config["train_dataset_prob"] = merge_values(
            train_config["train_customize_dataset_prob"], train_config["train_existed_dataset_prob"]
        )

        train_config["train_dataset_type"] = merge_values(
            train_config["train_customize_dataset_type"], train_config["train_existed_dataset_type"]
        )

        train_config["eval_dataset_path"] = merge_values(
            train_config["eval_customize_dataset_path"], train_config["eval_existed_dataset_path"]
        )

        train_config["eval_dataset_prob"] = merge_values(
            train_config["eval_customize_dataset_prob"], train_config["eval_existed_dataset_prob"]
        )

        train_config["eval_dataset_type"] = merge_values(
            train_config["eval_customize_dataset_type"], train_config["eval_existed_dataset_type"]
        )

        train_config["logging_dir"] = os.path.join(basic_config["output_dir"], config.get_path_config("logging_dir"))

    eval_config = config_dict.get("eval", {})
    if eval_config != {}:

        if basic_config["output_dir_view"]:
            basic_config["output_dir"] = basic_config["output_dir_view"]
        else:
            basic_config["output_dir"] = config.get_path_config("output_dir")

        eval_config["eval_dataset_path"] = merge_values(
            eval_config["eval_customize_dataset_path"], eval_config["eval_existed_dataset_path"]
        )

        eval_config["eval_dataset_prob"] = merge_values(
            eval_config["eval_customize_dataset_prob"], eval_config["eval_existed_dataset_prob"]
        )

        eval_config["eval_customize_dataset_type"] = None

        eval_config["eval_dataset_type"] = merge_values(
            eval_config["eval_customize_dataset_type"], eval_config["eval_existed_dataset_type"]
        )

        eval_config["logging_dir"] = os.path.join(basic_config["output_dir"], config.get_path_config("logging_dir"))

    export_config = config_dict.get("export", {})

    if export_config != {}:

        if basic_config["output_dir_view"]:
            basic_config["output_dir"] = basic_config["output_dir_view"]
        else:
            basic_config["output_dir"] = config.get_path_config("output_dir")

        export_config["logging_dir"] = os.path.join(basic_config["output_dir"], config.get_path_config("logging_dir"))

    chat_config = config_dict.get("chat", {})
    if chat_config != {}:

        if basic_config["output_dir_view"]:
            basic_config["output_dir"] = basic_config["output_dir_view"]
        else:
            basic_config["output_dir"] = config.get_path_config("output_dir")

        chat_config["logging_dir"] = os.path.join(basic_config["output_dir"], config.get_path_config("logging_dir"))

    if basic_config != {}:
        export_paddle_log(basic_config["output_dir"])

    return config_dict


def mkdir_output_dir(manager):
    """_summary_
    评估
    Returns:
        _type_: _description_
    """

    model_name = manager.get_component_value("basic", "model_name")
    stage = manager.get_component_value("train", "stage")
    fine_tuning = manager.get_component_value("basic", "fine_tuning")
    current_date = datetime.now().strftime("%Y%m%d")
    dir_name = f"{model_name}_{stage}_{fine_tuning}_{current_date}"

    output_dir_default = config.get_path_config("output_dir")
    output_dir_view = manager.get_component_value("basic", "output_dir_view")
    base_output_dir = output_dir_view if output_dir_view else output_dir_default

    if os.path.isabs(base_output_dir):
        full_path = Path(base_output_dir) / dir_name
    else:
        full_path = Path(ROOT_PATH) / base_output_dir / dir_name

    full_path.mkdir(parents=True, exist_ok=True)

    return os.path.join(base_output_dir, dir_name)


def export_paddle_log(output_dir):
    """_summary_
    评估
    Returns:
        _type_: _description_
    """

    paddle_log_dir = os.path.join(output_dir, config.get_path_config("paddle_log_dir"))
    os.environ["ERNIEKIT_DIST_LOG"] = paddle_log_dir
