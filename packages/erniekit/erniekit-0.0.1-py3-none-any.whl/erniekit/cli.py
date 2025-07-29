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
"""cli
"""
import os
import subprocess
import sys
from copy import deepcopy
from functools import partial
from pathlib import Path

script_dir = Path(__file__).parent.resolve()
parent_dir = script_dir.parent

if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from .utils.env import VERSION
from .utils.process import terminate_process_tree

USAGE = (
    "-" * 60
    + "\n"
    + "| Usage:                                                     |\n"
    + "|   erniekit train -h: model finetuning                      |\n"
    + "|   erniekit export -h: model export                         |\n"
    + "|   erniekit split -h: model split                           |\n"
    + "|   erniekit eval -h: model evaluation                       |\n"
    + "|   erniekit server -h: model deployment                     |\n"
    + "|   erniekit chat -h: launch a chat interface in CLI         |\n"
    + "|   erniekit webui -h: launch webui                          |\n"
    + "|   erniekit version: show version info                      |\n"
    + "|   erniekit help: show helping info                         |\n"
    + "-" * 60
)


WELCOME = (
    "-" * 48
    + "\n"
    + f"| Welcome to ErnieKit, version {VERSION}"
    + " " * (16 - len(VERSION))
    + "|\n|"
    + " " * 46
    + "|\n"
    + "-" * 48
)


def main():
    """cli main process"""
    from . import launcher
    from .chat.chat import run_chat
    from .chat.server import run_server
    from .eval.eval import run_eval
    from .export.export import run_export
    from .export.split import run_split
    from .train.tuner import run_tuner
    from .webui import run_webui

    COMMAND_MAP = {
        "train": run_tuner,
        "export": run_export,
        "split": run_split,
        "eval": run_eval,
        "server": run_server,
        "chat": run_chat,
        "version": partial(print, WELCOME),
        "help": partial(print, USAGE),
        "webui": run_webui,
    }

    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    distributed_funcs = ['train', 'export', 'split', 'eval']
    erniekit_dist_log = os.getenv("ERNIEKIT_DIST_LOG", "erniekit_dist_log")
    nnodes = os.getenv("NNODES", "1")
    master_ip = os.getenv("MASTER_ADDR", "127.0.0.1")
    master_port = os.getenv("MASTER_PORT", "8080")
    cuda_visible_gpu = os.getenv("CUDA_VISIBLE_DEVICES", "0")

    if command in distributed_funcs:

        # if os.path.exists(erniekit_dist_log):
        #     try:
        #         shutil.rmtree(erniekit_dist_log)
        #         print(f"Succeed to delete {erniekit_dist_log}.")
        #     except Exception as e:
        #         print(f"Error occurs while deleting {erniekit_dist_log}: {e}")

        # launch distributed training
        env = deepcopy(os.environ)
        command = (
            (
                "python -m paddle.distributed.launch --log_dir {erniekit_dist_log} "
                "--gpus {gpus} --master {master_ip}:{master_port} "
                "--nnodes {nnodes} {file_name} {args}"
            )
            .format(
                erniekit_dist_log=erniekit_dist_log,
                gpus=cuda_visible_gpu,
                master_ip=master_ip,
                master_port=master_port,
                nnodes=nnodes,
                file_name=launcher.__file__,
                args=" ".join(sys.argv[1:]),
            )
            .split()
        )

        process = subprocess.Popen(
            command,
            env=env,
        )

        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nReceived interrupt, terminating server...")
            terminate_process_tree(process.pid)
            sys.exit(1)
        except Exception as e:
            print(f"Server process failed: {e}")
            terminate_process_tree(process.pid)
            sys.exit(1)
        finally:
            sys.exit(process.returncode)

    elif command in COMMAND_MAP:
        COMMAND_MAP[command]()
    else:
        print(f"Unknown command: {command}.\n{USAGE}")


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    main()
