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

import gradio as gr
import lang as la


class Manager:
    """_summary_
    评估
    Returns:
        _type_: _description_
    """

    def __init__(self):
        self._id_to_elem = {}
        self.specific_id_to_elem = {}
        self.specific_component_value = {}
        self._locale_data = la.LOCALES
        self._current_lang = "zh"
        self._component_values = {}
        self._debug = False
        self._dependencies = {}
        self.demo = None

    def add_specific_elem_by_id(self, module_id, elem_id, elem, initial_value=None):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        full_id = f"{module_id}.{elem_id}"
        self.specific_id_to_elem[full_id] = elem
        self.specific_component_value[full_id] = initial_value

    def get_specific_elem_by_id(self, module_id, elem_id):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """

        full_id = f"{module_id}.{elem_id}"
        return self.specific_id_to_elem.get(full_id)

    def set_specific_component_value(self, module_id, elem_id, value):
        """更新特定模块中某个组件的值"""
        full_id = f"{module_id}.{elem_id}"
        self.specific_component_value[full_id] = value

    def get_specific_component_value(self, module_id, elem_id):
        """获取组件的当前值"""
        full_id = f"{module_id}.{elem_id}"
        if full_id in self.specific_component_value:
            return self.specific_component_value[module_id].get(elem_id)
        return None

    def get_all_specific_component_values(self):
        """获取所有特定模块的所有组件值，格式为 {"specific_" + module_id: {elem_id: value}}"""
        result = {}
        for full_id, value in self.specific_component_value.items():
            module_id, elem_id = full_id.split(".", 1)  # 分割完整ID为模块和元素ID
            specific_key = f"specific_{module_id}"
            if specific_key not in result:
                result[specific_key] = {}
            result[specific_key][elem_id] = value
        return result

    def add_elem(self, module_id, elem_id, elem, initial_value=None):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        """注册组件并设置初始值，按模块分层存储"""
        full_id = f"{module_id}.{elem_id}"
        self._id_to_elem[full_id] = elem

        # 确保模块存在
        if module_id not in self._component_values:
            self._component_values[module_id] = {}

        # 设置初始值
        self._component_values[module_id][elem_id] = initial_value

        if self._debug:
            print(f"[Manager] 注册组件: {full_id} ({type(elem).__name__}), 初始值: {initial_value}")

    def get_elem_by_id(self, module_id, elem_id):
        """按模块和组件ID获取组件"""
        full_id = f"{module_id}.{elem_id}"
        return self._id_to_elem.get(full_id)

    def get_component_value(self, module_id, elem_id):
        """获取组件的当前值"""
        if module_id in self._component_values:
            return self._component_values[module_id].get(elem_id)
        return None

    def get_module_values(self, module_id):
        """获取指定模块的所有组件值"""
        return self._component_values.get(module_id, {})

    def get_all_component_values(self):
        """获取所有模块的所有组件值"""
        return self._component_values

    def change_lang(self, lang):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        if lang not in ["zh", "en"]:
            return {}

        updates = {}
        for full_id, elem in self._id_to_elem.items():
            parts = full_id.split(".")
            elem_name = parts[-1]  # 使用最后一部分作为元素名称

            if elem_name not in self._locale_data:
                continue

            lang_config = self._locale_data[elem_name].get(lang, {})
            if not lang_config:
                continue

            update_kwargs = {}

            # 处理不同组件类型
            if isinstance(elem, gr.Button):
                if "value" in lang_config:
                    update_kwargs["value"] = lang_config["value"]
            elif isinstance(elem, gr.Markdown):
                if "value" in lang_config:
                    update_kwargs["value"] = lang_config["value"]
            elif isinstance(elem, gr.Tab):
                if "label" in lang_config:
                    update_kwargs["label"] = lang_config["label"]
            elif isinstance(elem, gr.HTML):
                if "value" in lang_config:
                    update_kwargs["value"] = lang_config["value"]
            else:
                if "label" in lang_config:
                    update_kwargs["label"] = lang_config["label"]
                if "info" in lang_config:  # 处理info参数
                    update_kwargs["info"] = lang_config["info"]
                if "placeholder" in lang_config:
                    update_kwargs["placeholder"] = lang_config["placeholder"]

            if update_kwargs:
                updates[elem] = gr.update(**update_kwargs)

        return updates

    def setup_language_switching(self, language, demo, alert):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        """设置语言切换事件"""
        all_components = list(self._id_to_elem.values())
        input_components = [
            comp
            for comp in all_components
            if isinstance(
                comp,
                (
                    gr.Textbox,
                    gr.Dropdown,
                    gr.Slider,
                    gr.Checkbox,
                    gr.CheckboxGroup,
                    gr.Radio,
                    gr.Chatbot,
                    gr.Button,
                    gr.HTML
                ),
            )
        ]

        if self._debug:
            print(f"[语言切换初始化] 总组件数: {len(all_components)}")
            print(f"[语言切换初始化] 输入组件数: {len(input_components)}")

        def update_fn(lang, *values):
            """_summary_
            评估
            Returns:
                _type_: _description_
            """
            # 保存当前组件值到分层结构
            for comp in input_components:
                for full_id, elem in self._id_to_elem.items():
                    if elem == comp:
                        parts = full_id.split(".")
                        if len(parts) >= 2:
                            module_id, elem_id = parts[0], ".".join(parts[1:])
                            if isinstance(comp, gr.Chatbot):
                                if values and input_components.index(comp) < len(values):
                                    self._component_values[module_id][elem_id] = values[input_components.index(comp)]
                            else:
                                if values and input_components.index(comp) < len(values):
                                    self._component_values[module_id][elem_id] = values[input_components.index(comp)]
                        break

            # 执行语言更新
            updates = self.change_lang(lang)

            # 构建输出列表
            return [updates.get(comp, comp) for comp in all_components]

        # 设置事件处理
        language.change(fn=update_fn, inputs=[language] + input_components, outputs=all_components)

        if self.demo:
            initial_values = []
            for comp in input_components:
                for full_id, elem in self._id_to_elem.items():
                    if elem == comp:
                        parts = full_id.split(".")
                        if len(parts) >= 2:
                            module_id, elem_id = parts[0], ".".join(parts[1:])
                            initial_values.append(self._component_values[module_id].get(elem_id, None))
                        break

            demo.load(
                fn=lambda: update_fn(self._current_lang, *initial_values),
                outputs=all_components,
            )

    def add_dependency(
        self,
        source_module_id,
        source_elem_id,
        dependent_module_ids,
        dependent_elem_ids,
        update_callback,
    ):
        """注册组件依赖关系"""
        source_full_id = f"{source_module_id}.{source_elem_id}"
        dependent_full_ids = [
            f"{mod_id}.{elem_id}" for mod_id, elem_id in zip(dependent_module_ids, dependent_elem_ids)
        ]

        self._dependencies[source_full_id] = {
            "dependent_ids": dependent_full_ids,
            "callback": update_callback,
        }

        if self._debug:
            print(f"[Manager] 注册依赖关系: {source_full_id} -> {dependent_full_ids}")

    def add_module_dependency(
        self,
        source_module_id,
        source_elem_id,
        update_module_id,
        update_callback,
        exclude_components=None,
    ):
        """
        为整个模块添加依赖关系，当源组件变化时更新整个模块

        参数:
        - source_module_id: 源组件所在的模块ID
        - source_elem_id: 源组件ID
        - update_callback: 更新回调函数，接收源组件的值，返回更新字典
        - exclude_components: 不更新的组件ID列表（不含模块前缀）
        """
        source_full_id = f"{source_module_id}.{source_elem_id}.{update_module_id}"

        # 收集模块内的所有组件ID
        module_components = []
        exclude_components = exclude_components or []

        for full_id in self._id_to_elem.keys():
            if full_id.startswith(f"{update_module_id}."):
                # 提取组件ID（去掉模块前缀）
                elem_id = full_id[len(update_module_id) + 1 :]

                # 检查是否在排除列表中
                if elem_id not in exclude_components:
                    module_components.append(full_id)

        # 注册依赖关系
        self._dependencies[source_full_id] = {
            "dependent_ids": module_components,
            "callback": update_callback,
        }

    def get_dependencies(self, source_id):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        return self._dependencies[source_id]

    def setup_component_tracking(self, demo):
        """设置所有组件的值跟踪和初始值"""
        for full_id, elem in self._id_to_elem.items():
            # 解析模块ID和组件ID
            parts = full_id.split(".")
            if len(parts) < 2:
                continue

            module_id, elem_id = parts[0], ".".join(parts[1:])

            # 检查组件是否为可输入类型
            if isinstance(
                elem,
                (
                    gr.Textbox,
                    gr.Dropdown,
                    gr.Slider,
                    gr.Checkbox,
                    gr.CheckboxGroup,
                    gr.Radio,
                    gr.Number,
                    gr.HTML
                ),
            ):
                # 为组件添加变化事件处理
                elem.change(
                    fn=lambda value, mid=module_id, eid=elem_id: self._update_component_value(mid, eid, value),
                    inputs=[elem],
                    outputs=[],
                )

                # 在页面加载时设置初始值
                initial_value = self._component_values[module_id].get(elem_id)
                if initial_value is not None:
                    # 对于不同类型的组件，使用不同的方式设置初始值
                    if isinstance(elem, gr.Textbox):
                        elem.value = initial_value
                    elif isinstance(elem, gr.Dropdown):
                        elem.value = initial_value
                    elif isinstance(elem, gr.Slider):
                        elem.value = initial_value
                    elif isinstance(elem, gr.Checkbox):
                        elem.value = initial_value
                    elif isinstance(elem, gr.CheckboxGroup):
                        elem.value = initial_value
                    elif isinstance(elem, gr.Radio):
                        elem.value = initial_value
                    elif isinstance(elem, gr.Number):
                        elem.value = initial_value
                    elif isinstance(elem, gr.HTML):
                        elem.value = initial_value

    def _update_component_value(self, module_id, elem_id, value):
        """更新组件值并打印调试信息"""
        if module_id in self._component_values and elem_id in self._component_values[module_id]:
            old_value = self._component_values[module_id][elem_id]
            self._component_values[module_id][elem_id] = value
            if self._debug and old_value != value:
                print(f"[Manager] 值更新: {module_id}.{elem_id} = {old_value} → {value}")
        else:
            print(f"[Manager] 错误: 未注册的组件 {module_id}.{elem_id}")

    def setup_dropdown(self, module_id, dropdown_id):
        """_summary_
        评估
        Returns:
            _type_: _description_
        """
        full_id = f"{module_id}.{dropdown_id}"
        if full_id not in self._dependencies:
            print(f"[Manager] 警告: {full_id} 没有注册依赖关系")
            return

        source_elem = self.get_elem_by_id(module_id, dropdown_id)
        if not source_elem:
            print(f"[Manager] 错误: 找不到组件 {full_id}")
            return

        dependency_info = self._dependencies[full_id]
        dependent_ids = dependency_info["dependent_ids"]
        update_callback = dependency_info["callback"]

        all_components = [self.get_elem_by_id(*id.split(".", 1)) for id in [full_id] + dependent_ids]
        all_components = [c for c in all_components if c is not None]

        def dropdown_change_handler(selected_value):
            """_summary_
            评估
            Returns:
                _type_: _description_
            """
            self._component_values[module_id][dropdown_id] = selected_value
            updates = update_callback(selected_value)
            output_updates = [updates.get(comp, comp) for comp in all_components]
            return output_updates

        # 使用self.demo绑定事件
        source_elem.change(fn=dropdown_change_handler, inputs=[source_elem], outputs=all_components)

        # 修改：使用实际的初始值而不是None
        if self.demo:
            initial_value = self._component_values[module_id].get(dropdown_id)
            self.demo.load(
                fn=lambda: dropdown_change_handler(initial_value),
                outputs=all_components,
            )


manager = Manager()
