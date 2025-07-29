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

"""_summary_
评估
Returns:
    _type_: _description_
"""

import asyncio
import os
import re
import subprocess

from erniekit.webui import common
from erniekit.webui.alert import alert

"""_summary_
评估
Returns:
    _type_: _description_
"""


class CommandRunner:
    """执行命令并实时流式输出的类"""

    def __init__(self):
        self.current_process = None
        self.process_lock = asyncio.Lock()
        self.was_terminated_by_user = False
        self.lines_history = []
        self.track_progress = True
        self.current = 0
        self.total = 0
        self.progress_line_buffer = {}  # 用于缓存进度条行

    async def execute(self, command: str):
        """异步执行命令并流式返回输出"""
        self.lines_history = []
        self.progress_line_buffer = {}
        separator = "\n" + "-" * 50 + "\n"
        start_text = alert.get("progress", "run_command").format(separator, command) + "\n"
        self.lines_history.extend([start_text])

        # 初始输出（立即返回）
        yield "\n".join(self.lines_history), 0, 0

        print("\n" + start_text, flush=True)
        process = None

        try:
            # 创建子进程（设置无缓冲输出）
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["FORCE_COLOR"] = "1"
            process = await asyncio.create_subprocess_shell(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
            )
            self.current_process = process

            buffer = b""
            while True:
                # 读取输出块（1KB）
                chunk = await process.stdout.read(1024)
                if not chunk:
                    break

                buffer += chunk
                # 尝试提取完整行
                while b"\n" in buffer or b"\r" in buffer:
                    line, buffer = self._extract_next_line(buffer)
                    if not line:
                        break

                    line_str = line.decode("utf-8", errors="replace")

                    # 始终打印到命令行（保持原有行为）
                    print(line_str, end="", flush=True)

                    # 清理ANSI颜色代码（保留日志格式）
                    line_clean = re.sub(r"\x1b\[[0-9;]*[mGKH]", "", line_str)
                    line_clean = line_clean.rstrip("\n\r").strip()

                    if line_clean:
                        should_update = self._process_line(line_clean)
                        self._parse_progress(line_clean)

                        # 只有在需要更新时才推送到前端
                        if should_update:
                            yield "\n".join(self.lines_history), self.current, self.total

        except Exception as e:
            error_msg = alert.get("progress", "execution_error").format(str(e))
            self.lines_history.append(error_msg)
            print(error_msg, flush=True)
            yield "\n".join(self.lines_history), self.current, self.total

        finally:
            # 确保所有缓存的进度条都被添加到历史记录
            self._flush_progress_buffer()

            if process:
                return_code = await process.wait()
                if return_code == 0:
                    success_msg = alert.get("progress", "progress_success")
                    self.lines_history.append(f"\n{success_msg}")
                    print(f"\n{success_msg}", flush=True)
                    yield "\n".join(self.lines_history), self.current, self.total
            self.current_process = None

    def _extract_next_line(self, buffer):
        """提取完整行（处理\n和\r）"""
        nl_pos = buffer.find(b"\n")
        cr_pos = buffer.find(b"\r")

        if nl_pos >= 0 and cr_pos >= 0:
            end_pos = min(nl_pos, cr_pos) + 1
        elif nl_pos >= 0:
            end_pos = nl_pos + 1
        elif cr_pos >= 0:
            end_pos = cr_pos + 1
        else:
            return buffer, b""

        return buffer[:end_pos], buffer[end_pos:]

    def _process_line(self, line_clean):
        """处理单行输出，决定是否需要更新前端"""
        # 检查是否是进度条行
        progress_key = self._get_progress_key(line_clean)
        if progress_key:
            # 这是一个进度条行，始终更新缓冲区
            self.progress_line_buffer[progress_key] = line_clean

            # 检查是否应该显示这个进度（只显示关键进度点）
            if self._should_show_progress(line_clean):
                self._update_progress_in_history(progress_key, line_clean)
                return True
            return False
        else:
            # 非进度条行，直接添加
            self.lines_history.append(line_clean)
            return True

    def _get_progress_key(self, line):
        """获取进度条的键（用于识别同一个进度条）"""
        # 匹配进度条模式并提取关键信息
        patterns = [
            r"(Loading\s+\w+):\s*\d+%",  # Loading Layers: 50%
            r"(\w+\s+\w+):\s*\d+%",  # 通用进度条
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)

        return None

    def _should_show_progress(self, line):
        """决定是否显示这个进度条状态（只显示关键进度点）"""
        # 提取百分比
        percent_match = re.search(r"(\d+)%", line)
        if percent_match:
            percent = int(percent_match.group(1))
            # 只显示 0%, 10%, 20%, ..., 100% 的进度（每10%显示一次）
            return percent == 0 or percent == 100 or percent % 10 == 0

        # 如果没有百分比，检查是否是完成状态
        return "100%" in line or "complete" in line.lower() or "finished" in line.lower()

    def _update_progress_in_history(self, progress_key, line):
        """更新历史记录中的进度条"""
        # 查找是否已有相同的进度条
        for i, history_line in enumerate(self.lines_history):
            if progress_key in history_line and self._get_progress_key(history_line):
                # 找到了，替换它
                self.lines_history[i] = line
                return

        # 没找到，添加新的进度条行
        self.lines_history.append(line)

    def _flush_progress_buffer(self):
        """将缓存的进度条刷新到历史记录"""
        for progress_key, line in self.progress_line_buffer.items():
            self._update_progress_in_history(progress_key, line)

    def _parse_progress(self, line):
        """解析进度信息（如global_step）"""
        try:
            # 匹配global_step格式：global_step: X
            step_match = re.search(r"global_step:\s*(\d+)", line)
            if step_match:
                step = int(step_match.group(1))
                self.current = step
                return

            # 匹配X/Y格式进度
            ratio_match = re.search(r"(\d+)/(\d+)", line)
            if ratio_match:
                self.current = int(ratio_match.group(1))
                self.total = int(ratio_match.group(2))
        except Exception as e:
            # 处理其他意外异常
            print(f"发生意外错误: {e}")

    async def stop(self):
        """停止当前正在执行的进程"""
        async with self.process_lock:
            # 先获取当前进程的引用，避免后续被其他协程修改
            process = self.current_process

            if process is None:
                no_terminated_msg = "\n" + alert.get("progress", "no_progress") + "\n"
                self.lines_history.append(no_terminated_msg)
                return "\n".join(self.lines_history)

            try:
                if process.returncode is not None:
                    progress_end_msg = "\n" + alert.get("progress", "progress_end") + "\n"
                    self.lines_history.append(progress_end_msg)
                    return "\n".join(self.lines_history)

                try:
                    common.abort_process(process.pid)
                except Exception:
                    process.terminate()

                await asyncio.sleep(0.5)

                if process.returncode is None:
                    process.kill()
                    force_terminated_msg = "\n" + alert.get("progress", "force_terminated") + "\n"
                    print(force_terminated_msg)
                    self.lines_history.append(force_terminated_msg)
                    await process.wait()

                self.was_terminated_by_user = True
                user_terminated_msg = "\n" + alert.get("progress", "user_terminated") + "\n"
                self.lines_history.append(user_terminated_msg)
                print(user_terminated_msg)
            except Exception as e:
                error_msg = alert.get("progress", "terminate_error").format(str(e))
                self.lines_history.append(error_msg)
                print(error_msg.strip())
            finally:
                self.current_process = None

            return "\n".join(self.lines_history)

    def clear_output(self):
        """清空输出并设置重置标志"""
        self.output_reset = True
        self.current_output = ""
        self.progress_line_buffer = {}
        return ""
