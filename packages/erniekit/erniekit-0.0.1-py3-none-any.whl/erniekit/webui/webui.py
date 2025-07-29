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
import resource
import sys
from pathlib import Path

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
webui_dir = Path(__file__).parent
sys.path.insert(0, str(webui_dir))

import gradio as gr
from alert import alert
from manager import manager
from view import basic, chat, eval, export, train
from view.css import CSS

"""_summary_
评估
Returns:
    _type_: _description_
"""


def create_ui():
    """_summary_
    评估
    Returns:
        _type_: _description_
    """

    with gr.Blocks(title="ErnieKit WebUI", theme=gr.themes.Ocean()) as demo:
        gr.HTML(f"<style>{CSS}</style>")

        manager.demo = demo
        language = basic.build(manager)
        with gr.Tabs(elem_classes="large-tabs"):
            train.build(manager)
            chat.build(manager)
            eval.build(manager)
            export.build(manager)

        if language:
            manager.setup_language_switching(language, demo, alert)

        manager.setup_component_tracking(demo)

    return demo


def run_webui():
    print("Starting ErnieKit WebUI")
    demo = create_ui()
    demo.queue().launch(server_name="0.0.0.0", server_port=8080, share=False)


if __name__ == "__main__":
    run_webui()
