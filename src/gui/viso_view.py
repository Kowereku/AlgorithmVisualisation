import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from src.utils.sidebar_manager import SidebarManager
from src.utils.schema_manager import SchemaManager
from src.libs.llm_interfaces import get_gemini_response
from src.prompts.analyze_prompt import get_analyze_prompt


class VisoViewApp:
    def __init__(self):
        self.sidebar_manager = SidebarManager()

        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "ai_mode" not in st.session_state:
            st.session_state.ai_mode = "Generate"
        if "ai_generated_schemas" not in st.session_state:
            st.session_state.ai_generated_schemas = []
        if "selected_context" not in st.session_state:
            st.session_state.selected_context = None

    @staticmethod
    def apply_custom_styles():
        css_file_path = os.path.join(os.path.dirname(__file__), "styles", "viso_view.css")
        try:
            with open(css_file_path, "r") as css_file:
                css_content = css_file.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            pass

    def render_main_content(self, context_data):
        st.markdown("### Visualization Workspace")

        if not context_data:
            st.info("Please select an algorithm from the sidebar or generate one with AI.")
            return

        final_schema = None

        if isinstance(context_data, bytes):
            with st.spinner("Parsing Visio file..."):
                try:
                    final_schema = SchemaManager.parse_vsdx_file(context_data)
                except Exception as e:
                    st.error(str(e))
                    return

        elif isinstance(context_data, dict):
            final_schema = context_data

        else:
            st.error(f"Unknown data format: {type(context_data)}")
            return

        if final_schema:
            title = final_schema.get("title", "Algorithm")
            summary = final_schema.get("summary", "")

            st.markdown(f"#### {title}")
            if summary:
                st.caption(summary)

            st.markdown("##### Schema Structure")
            st.json(final_schema)

            st.success("Schema loaded successfully into workspace.")
        else:
            st.error("Failed to extract valid schema data.")

    def render_chat_component(self):
        st.divider()
        st.subheader("AI Visualization Assistant")

        for message in st.session_state.messages:
            role = message["role"]
            with st.chat_message(role):
                if role == "assistant" and isinstance(message["content"], dict):
                    self._render_schema_block(message["content"], is_new=False)
                else:
                    st.markdown(message["content"])

        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            mode = st.session_state.get("ai_mode", "Generate")

            with st.chat_message("assistant"):
                if mode == "Generate":
                    with st.spinner("Designing schema..."):
                        try:
                            current_context = st.session_state.selected_context if isinstance(
                                st.session_state.selected_context, dict) else {"blocks": [], "connections": []}

                            parsed_schema = SchemaManager.generate_schema(prompt, current_context)

                            self._render_schema_block(parsed_schema, is_new=True)
                            st.session_state.messages.append({"role": "assistant", "content": parsed_schema})

                            SchemaManager.save_to_session(parsed_schema)
                            st.toast(f"Schema '{parsed_schema.get('title')}' saved!")
                        except Exception as e:
                            st.error(f"Generation failed: {e}")

                elif mode == "Analyze":
                    with st.spinner("Analyzing..."):
                        try:
                            chat_history = "\n".join([f"{msg['role'].capitalize()}: {str(msg['content'])}" for msg in
                                                      st.session_state.messages])
                            enhanced_prompt = get_analyze_prompt(chat_history)
                            response = get_gemini_response(enhanced_prompt)

                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")

    def _render_schema_block(self, schema_data: dict, is_new: bool):
        title = schema_data.get("title", "Generated Schema")
        summary = schema_data.get("summary", "No summary provided.")

        st.markdown(f"**{title}**")
        st.caption(summary)

        with st.expander("View JSON Schema", expanded=False):
            st.json(schema_data)
            if st.button("Load into Workspace", key=f"btn_{id(schema_data)}"):
                st.session_state.selected_context = schema_data
                st.rerun()

    def run(self):
        st.set_page_config(page_title="Algorithm Visualization", layout="wide")
        self.apply_custom_styles()

        st.title("Algorithm Visualization Tool")

        file_content_bytes = self.sidebar_manager.render_sidebar()

        if file_content_bytes:
            st.session_state.selected_context = file_content_bytes

        self.render_main_content(st.session_state.selected_context)

        self.render_chat_component()


if __name__ == "__main__":
    app = VisoViewApp()
    app.run()
