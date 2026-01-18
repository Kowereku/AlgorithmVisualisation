import sys
import os
import json
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from st_cytoscape import cytoscape
from src.utils.sidebar_manager import SidebarManager
from src.utils.schema_manager import SchemaManager
from src.libs.llm_interfaces import get_gemini_response
from src.libs import algorithms, cytoscape_parserfrom src.prompts.analyze_prompt import get_analyze_prompt


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

        # Current simulation state
        if "simulation_step" not in st.session_state:
            st.session_state.simulation_step = 0
        if "is_playing" not in st.session_state:
            st.session_state.is_playing = False

        self.styles = self.load_cytoscape_styles()

    def load_cytoscape_styles(self):
        """Loads Cytoscape stylesheets from external JSON file."""
        style_path = os.path.join(os.path.dirname(__file__), "styles", "cytoscape_styles.json")
        default_styles = {"data_graph": [], "flowchart": []}

        if os.path.exists(style_path):
            try:
                with open(style_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading styles: {e}")
                return default_styles
        else:
            st.warning("Style file not found. Using defaults.")
            return default_styles

        # Current simulation state
        if "simulation_step" not in st.session_state:
            st.session_state.simulation_step = 0
        if "is_playing" not in st.session_state:
            st.session_state.is_playing = False

        self.styles = self.load_cytoscape_styles()

    def load_cytoscape_styles(self):
        """Loads Cytoscape stylesheets from external JSON file."""
        style_path = os.path.join(os.path.dirname(__file__), "styles", "cytoscape_styles.json")
        default_styles = {"data_graph": [], "flowchart": []}

        if os.path.exists(style_path):
            try:
                with open(style_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading styles: {e}")
                return default_styles
        else:
            st.warning("Style file not found. Using defaults.")
            return default_styles

    @staticmethod
    def apply_custom_styles():
        css_file_path = os.path.join(os.path.dirname(__file__), "styles", "viso_view.css")
        try:
            with open(css_file_path, "r") as css_file:
                css_content = css_file.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            pass

    def render_main_content(self, selection_data):
        """
        Render the main content area of the app (Visualization).

        Args:
            selection_data (tuple): (Algorithm Name, File Content) from sidebar.
        """
        selected_algo_name, file_content = selection_data

        st.markdown("### Visualization Workspace")

        if not selection_data:
            st.info("Please select an algorithm from the sidebar or generate one with AI.")
            return
        
        final_schema = None

        if isinstance(selection_data, bytes):
            with st.spinner("Parsing Visio file..."):
                try:
                    final_schema = SchemaManager.parse_vsdx_file(selection_data)
                except Exception as e:
                    st.error(str(e))
                    return

        elif isinstance(selection_data, dict):
            final_schema = selection_data

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

        vsdx_json = {}
        if file_content:
            vsdx_json = self.parse_vsdx_file(file_content)

        data_graph = algorithms.get_scenario_data()

        blocks = vsdx_json.get("blocks", [])
        trace = []

        if "A*" in selected_algo_name:
            trace = algorithms.run_astar_simulation(data_graph, "A", "C", vsdx_blocks=blocks)
        elif "Dijkstra" in selected_algo_name:
            trace = algorithms.run_dijkstra_simulation(data_graph, "A", "C", vsdx_blocks=blocks)
        elif "Prim" in selected_algo_name:
            trace = algorithms.run_prim_simulation(data_graph, "A", vsdx_blocks=blocks)
        if not trace:
            st.warning("No trace generated.")
            return

        max_step = len(trace) - 1

        def on_slider_change():
            st.session_state.simulation_step = st.session_state.slider_internal_key

        if st.session_state.simulation_step > max_step:
            st.session_state.simulation_step = 0

        st.session_state.slider_internal_key = st.session_state.simulation_step

        frame_index = st.session_state.simulation_step
        current_frame = trace[frame_index]

        elements_data = cytoscape_parser.convert_nx_to_cytoscape(data_graph)
        elements_flow = cytoscape_parser.convert_vsdx_to_cytoscape(vsdx_json)

        if trace:
            for ele in elements_data:
                ele_id = ele["data"].get("id")
                ele["classes"] = "data-node" if "source" not in ele["data"] else "data-edge"
                ele["locked"] = True
                ele["grabbable"] = False

                if ele_id and ele_id == current_frame["current_node"]:
                    ele["classes"] += " current"
                elif ele_id and ele_id in current_frame["visited"]:
                    ele["classes"] += " visited"
                elif ele_id and ele_id in current_frame["path_found"]:
                    ele["classes"] += " final-path"

            active_vsdx_id = current_frame.get("vsdx_id")
            for ele in elements_flow:
                base_type = ele["data"].get("type", "process")
                ele["classes"] = f"flow-{base_type}"

                ele_id = ele["data"].get("id")
                if active_vsdx_id and ele_id and str(ele_id) == str(active_vsdx_id):
                    ele["classes"] += " active-step"

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Data Processing")
                cytoscape(
                    elements=elements_data, stylesheet=self.styles["data_graph"],
                    width="80%", height="400px", layout={"name": "preset"},
                    key="graph_data", user_zooming_enabled=False,
                    user_panning_enabled=False,
                )

            with col2:
                st.subheader("Algorithm Logic")
                if elements_flow:
                    cytoscape(
                        elements=elements_flow, stylesheet=self.styles["flowchart"],
                        width="80%", height="400px", layout={"name": "breadthfirst"},
                        key="graph_flow", user_zooming_enabled=False,
                        user_panning_enabled=False,
                    )
                else:
                    st.info("No VSDX flow loaded.")

            st.info(f"**Step {frame_index}:** {current_frame['description']}")

            col_btn, col_slider = st.columns([1, 4])

            with col_btn:
                btn_label = "⏸ Pause" if st.session_state.is_playing else "▶ Play"
                if st.button(btn_label):
                    st.session_state.is_playing = not st.session_state.is_playing
                    st.rerun()

            with col_slider:
                st.slider(
                    "Execution Step", 0, max_step,
                    key="slider_internal_key",
                    on_change=on_slider_change
                )

        if st.session_state.is_playing:
            time.sleep(1.0)
            if st.session_state.simulation_step < max_step:
                st.session_state.simulation_step += 1
                st.rerun()
            else:
                st.session_state.is_playing = False
                st.rerun()



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

        try:
            self.apply_custom_styles()
        except:
            pass

        st.title("Algorithm Visualization Tool")

        file_content_bytes = self.sidebar_manager.render_sidebar()

        if file_content_bytes:
            st.session_state.selected_context = file_content_bytes

        self.render_main_content(st.session_state.selected_context)

        self.render_chat_component()


if __name__ == "__main__":
    app = VisoViewApp()
    app.run()
