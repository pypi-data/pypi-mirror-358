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

import gradio as gr
import openai

from erniekit.webui.common import config


class ChatBotGenerator:
    """聊天机器人生成器，支持多模态响应和思考过程生成"""

    def __init__(self):
        self.default_ip = "0.0.0.0"
        self.openai_client = None
        self.stop_generation = False  # 添加停止标志

    def stop(self):
        """设置停止标志，中断生成过程"""
        self.stop_generation = True

    def reset(self):
        """重置停止标志"""
        self.stop_generation = False

    def _create_openai_client(self, port):
        base_url = f"http://{self.default_ip}:{port}/v1"
        return openai.Client(base_url=base_url, api_key="EMPTY_API_KEY")

    async def _build_message_history(self, message, history, role_setting, system_prompt, include_thoughts=False):
        """构建消息历史，统一处理不同格式的历史记录"""
        messages = []

        # 基础系统消息
        if role_setting or system_prompt:
            system_content = ""
            if role_setting:
                system_content += f"你现在扮演: {role_setting}"
            if system_prompt:
                system_content += system_prompt
            if system_content:
                messages.append({"role": "system", "content": system_content})

        # 处理历史记录（兼容新旧格式）
        if history:
            print(f"历史记录格式检查: {history[:3]}")
            for entry in history:
                # 处理新格式（字典）
                if isinstance(entry, dict) and "role" in entry:
                    role = entry["role"]
                    content = entry.get("content", "")
                    if role == "user":
                        messages.append({"role": "user", "content": content})
                    elif role == "assistant":
                        messages.append({"role": "assistant", "content": content})
                # 兼容旧格式（二元组）
                elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                    user_msg, bot_msg = entry
                    messages.append({"role": "user", "content": user_msg})
                    if bot_msg:
                        messages.append({"role": "assistant", "content": bot_msg})
                else:
                    print(f"警告: 无法解析的历史记录格式: {entry}")

        # 添加当前消息
        messages.append({"role": "user", "content": message})
        return messages

    async def mm_response(
        self,
        message,
        history,
        role_setting,
        system_prompt,
        max_length,
        top_p,
        temperature,
        port=8188,
    ):
        """多模态响应生成，统一处理历史记录格式"""
        if not message:
            yield [], gr.update(value="")
            return

        self.reset()

        try:
            client = self._create_openai_client(port)
            messages = await self._build_message_history(
                message, history, role_setting, system_prompt, include_thoughts=False
            )

            response = client.chat.completions.create(
                model="default",
                messages=messages,  # 确保使用完整的消息历史
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_length,
                stream=True,
            )

            # 直接使用历史记录，不再进行转换
            new_history = list(history) if history else []

            # 添加当前用户消息
            user_message = {"role": "user", "content": message}
            new_history.append(user_message)

            # 创建一个新的assistant响应对象
            assistant_response = {"role": "assistant", "content": ""}
            new_history.append(assistant_response)

            # 处理流式响应
            for chunk in response:
                if self.stop_generation:
                    break

                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    assistant_response["content"] += chunk.choices[0].delta.content
                    yield new_history, gr.update(value="")
                    await asyncio.sleep(0.01)

            yield new_history, gr.update(value="")

        except Exception as e:
            print(f"mm_response错误: {e}")
            error_msg = {"role": "assistant", "content": f"API调用失败：{e!s}"}
            yield [{"role": "user", "content": message}, error_msg], gr.update(value="")
        finally:
            self.reset()

    async def thought_response(
        self,
        message,
        history,
        role_setting=None,
        system_prompt=None,
        max_length=1000,
        top_p=0.8,
        temperature=0.7,
        port=8188,
    ):
        """带思考过程的响应生成，统一历史记录格式"""
        if not message:
            yield [], gr.update(value="")
            return

        self.reset()  # 重置停止标志

        try:
            client = self._create_openai_client(port)

            # 构建消息历史（兼容新旧格式）
            messages = await self._build_message_history(
                message, history, role_setting, system_prompt, include_thoughts=True
            )

            # 创建流式响应
            response = client.chat.completions.create(
                model="default",
                messages=messages,  # 确保使用完整的消息历史
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_length,
                stream=True,
            )

            # 直接使用传入的历史记录（避免重复转换）
            new_history = list(history) if history else []

            # 添加当前用户消息（避免重复添加）
            user_message = {"role": "user", "content": message}
            new_history.append(user_message)

            # 创建新的assistant响应对象
            assistant_response = {"role": "assistant", "content": ""}
            new_history.append(assistant_response)

            current_thought = ""
            current_response = ""

            for chunk in response:
                if self.stop_generation:  # 检查停止标志
                    break

                if chunk.choices[0].delta:
                    thought_part = getattr(chunk.choices[0].delta, "reasoning_content", "")
                    answer_part = getattr(chunk.choices[0].delta, "content", "")

                    current_thought += thought_part
                    current_response += answer_part

                    formatted_response = (
                        f"<details open><summary>思考过程</summary>\n"
                        f"<div class='thought-container' style='font-size: 13px;opacity: 0.85;"
                        f"padding-left:20px;border-left:3px solid #ddd;"
                        f"margin-bottom: 1em;'>{current_thought}</div>\n"
                        f"</details>\n"
                        f"<div class='response-container' style='line-height: 1.5;'>{current_response}</div>"
                    )

                    assistant_response["content"] = formatted_response
                    yield new_history, gr.update(value="")
                    await asyncio.sleep(0.01)

            yield new_history, gr.update(value="")  # 最终返回完整历史

        except Exception as e:
            print(f"thought_response错误: {e}")
            error_msg = {"role": "assistant", "content": f"思考过程生成失败：{e!s}"}
            yield [{"role": "user", "content": message}, error_msg], gr.update(value="")
        finally:
            self.reset()  # 确保标志位被重置

    def _check_thought_model(self, model_name):
        return config.is_thought_model(model_name)


chatbot = ChatBotGenerator()
