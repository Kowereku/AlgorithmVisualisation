import sys
import os
import json
import time
import inspect
import logging
import streamlit as st
import networkx as nx
import numpy as np
from st_cytoscape import cytoscape

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.sidebar_manager import SidebarManager
from src.utils.schema_manager import SchemaManager
from src.utils.algorithm_generator import AlgorithmGenerator
from src.libs import algorithms, cytoscape_parser
from src.prompts.analyze_prompt import get_analyze_prompt
from src.libs.llm_interfaces import get_gemini_response


class VisoViewApp:
    def __init__(self):
        self.sidebar_manager = SidebarManager()
        self.generator = AlgorithmGenerator()

        if "messages" not in st.session_state: st.session_state.messages = []
        if "ai_generated_schemas" not in st.session_state: st.session_state.ai_generated_schemas = []
        if "selected_context" not in st.session_state: st.session_state.selected_context = None
        if "new_algorithm_loaded" not in st.session_state: st.session_state.new_algorithm_loaded = False
        if "simulation_step" not in st.session_state: st.session_state.simulation_step = 0
        if "is_playing" not in st.session_state: st.session_state.is_playing = False

        self.styles = self.load_cytoscape_styles()

    def load_cytoscape_styles(self):
        style_path = os.path.join(os.path.dirname(__file__), "styles", "cytoscape_styles.json")
        default_styles = {"data_graph": [], "flowchart": []}
        if os.path.exists(style_path):
            try:
                with open(style_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load styles: {e}")
                return default_styles
        return default_styles

    @staticmethod
    def _sanitize_for_json(obj):
        if isinstance(obj, dict):
            return {k: VisoViewApp._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [VisoViewApp._sanitize_for_json(i) for i in obj]
        elif isinstance(obj, (np.ndarray, set)):
            return [VisoViewApp._sanitize_for_json(i) for i in list(obj)]
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        return obj

    @staticmethod
    def apply_custom_styles():
        css_file_path = os.path.join(os.path.dirname(__file__), "styles", "viso_view.css")
        try:
            with open(css_file_path, "r") as css_file:
                st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            pass

    def render_main_content(self, context_data):

        final_schema = None
        data_graph = None
        trace = []
        display_title = "VISO - Algorithm Visualization"

        if isinstance(context_data, tuple) or isinstance(context_data, bytes):
            file_content = context_data[1] if isinstance(context_data, tuple) else context_data
            algo_name = context_data[0] if isinstance(context_data, tuple) else "Imported Schema"
            display_title = algo_name

            if file_content:
                try:
                    final_schema = SchemaManager.parse_vsdx_file(file_content)
                    final_schema = self._normalize_schema(final_schema)
                    final_schema["title"] = algo_name
                except Exception as e:
                    logger.error(f"Error parsing legacy file: {e}")
                    st.error(f"Error parsing file: {e}")
                    return

            if final_schema:
                data_graph = algorithms.get_scenario_data()
                blocks = final_schema.get("blocks", [])
                label = (algo_name or "").lower()

                if "a*" in label or "astar" in label:
                    trace = algorithms.run_astar_simulation(data_graph, "A", "C", vsdx_blocks=blocks)
                elif "dijkstra" in label:
                    trace = algorithms.run_dijkstra_simulation(data_graph, "A", "C", vsdx_blocks=blocks)
                elif "prim" in label:
                    trace = algorithms.run_prim_simulation(data_graph, "A", vsdx_blocks=blocks)
                else:
                    trace = algorithms.run_astar_simulation(data_graph, "A", "C", vsdx_blocks=blocks)

        elif isinstance(context_data, dict):
            final_schema = context_data.get("schema")
            data_code = context_data.get("data_code")
            sim_code = context_data.get("sim_code")
            display_title = context_data.get("title", final_schema.get("title", "Generated Algorithm"))

            execution_scope = {
                "algorithms": algorithms, "nx": nx, "networkx": nx,
                "heapq": algorithms.heapq, "math": algorithms.math, "random": algorithms.random,
                "get_id": lambda b, k: next((x['id'] for x in b if k.lower() in x.get('text', '').lower()), None),
                "print": lambda *args: None
            }
            try:
                exec(data_code, execution_scope)
                if "get_data" in execution_scope:
                    data_graph = execution_scope["get_data"]()

                if data_graph is None or not isinstance(data_graph, nx.Graph):
                    logger.error(f"Invalid data type: {type(data_graph)}")
                    st.error(f"Runtime Error: Generated data was {type(data_graph).__name__}, expected NetworkX Graph.")
                    return

                exec(sim_code, execution_scope)
                if "run_simulation" in execution_scope:
                    trace = execution_scope["run_simulation"](data_graph, final_schema.get("blocks", []))

            except Exception as e:
                logger.error(f"Runtime Exception in Generated Algo: {e}", exc_info=True)
                st.error(f"Runtime Error in Generated Algorithm: {e}")
                return

        st.markdown(f"#### {display_title}")

        if not trace:
            return

        max_step = len(trace) - 1

        def on_slider_change():
            st.session_state.simulation_step = st.session_state.slider_internal_key

        if st.session_state.simulation_step > max_step:
            st.session_state.simulation_step = 0

        st.session_state.slider_internal_key = st.session_state.simulation_step
        frame_index = st.session_state.simulation_step
        current_frame = trace[frame_index]

        elements_data_raw = cytoscape_parser.convert_nx_to_cytoscape(data_graph)
        elements_flow_raw = cytoscape_parser.convert_vsdx_to_cytoscape(final_schema)

        elements_data = self._sanitize_for_json(elements_data_raw)
        elements_flow = self._sanitize_for_json(elements_flow_raw)

        self._apply_trace_highlights(elements_data, elements_flow, current_frame)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data Structure")
            if "data_values" in current_frame:
                self._update_node_labels(elements_data, current_frame["data_values"])

            cytoscape(
                elements=elements_data, stylesheet=self.styles["data_graph"],
                width="100%", height="600px", layout={"name": "preset"},
                key="graph_data", user_zooming_enabled=False, user_panning_enabled=False
            )

        with col2:
            st.subheader("Flow Logic")
            cytoscape(
                elements=elements_flow, stylesheet=self.styles["flowchart"],
                width="100%", height="600px", layout={"name": "breadthfirst"},
                key="graph_flow", user_zooming_enabled=False, user_panning_enabled=False
            )

        st.info(f"**Step {frame_index}:** {current_frame.get('description', '')}")

        col_btn, col_slider = st.columns([1, 4])
        with col_btn:
            if st.button("⏸ Pause" if st.session_state.is_playing else "▶ Play"):
                st.session_state.is_playing = not st.session_state.is_playing
                st.rerun()

        with col_slider:
            st.slider("Step", 0, max_step, key="slider_internal_key", on_change=on_slider_change)

        if st.session_state.is_playing:
            time.sleep(1.0)
            if st.session_state.simulation_step < max_step:
                st.session_state.simulation_step += 1
                st.rerun()
            else:
                st.session_state.is_playing = False
                st.rerun()

    def _apply_trace_highlights(self, data_elements, flow_elements, frame):
        current_nodes = [str(x) for x in (frame.get("path_found", []) or [])]
        visited_nodes = [str(x) for x in (frame.get("visited", []) or [])]
        node_colors = frame.get("node_colors") or {}

        for ele in data_elements:
            eid = ele["data"].get("id")
            if not eid: continue
            eid = str(eid)

            if eid in node_colors:
                ele["data"]["color"] = node_colors[eid]

            if eid in current_nodes:
                ele["classes"] += " current"
            elif eid in visited_nodes:
                ele["classes"] += " visited"

        active_vsdx_id = frame.get("vsdx_id")
        if active_vsdx_id:
            for ele in flow_elements:
                if str(ele["data"].get("id")) == str(active_vsdx_id):
                    ele["classes"] += " active-step"

    def _update_node_labels(self, elements, values_dict):
        for ele in elements:
            eid = ele["data"].get("id")
            if eid and str(eid) in values_dict:
                ele["data"]["label"] = str(values_dict[str(eid)])

    def render_chat_component(self):
        st.divider()
        st.subheader("AI Visualization Assistant")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if isinstance(msg["content"], dict):
                    self._render_schema_summary(msg["content"])
                else:
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about visualized algorithm or create the new one."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            user_msg = st.session_state.messages[-1]["content"]
            mode = st.session_state.get("ai_mode", "Generate")

            with st.chat_message("assistant"):
                if mode == "Generate":
                    with st.spinner("Generating..."):

                        MAX_RETRIES = 3
                        attempt = 0
                        valid_package = None
                        last_error = None

                        try:
                            pkg = self.generator.generate_full_algorithm(user_msg)

                            while attempt < MAX_RETRIES:
                                try:
                                    def get_id(blocks, keyword):
                                        for b in blocks:
                                            if keyword.lower() in b.get("text", "").lower():
                                                return b["id"]
                                        return None

                                    scope = {
                                        "algorithms": algorithms, "nx": nx, "networkx": nx,
                                        "heapq": algorithms.heapq, "math": algorithms.math, "random": algorithms.random,
                                        "get_id": get_id, "print": lambda *args: None
                                    }
                                    exec(pkg['data_code'], scope)
                                    if 'get_data' not in scope: raise ValueError("get_data() missing")
                                    data = scope['get_data']()

                                    if not isinstance(data, nx.Graph):
                                        raise ValueError(
                                            f"get_data() returned {type(data)}. Must return networkx.Graph")

                                    exec(pkg['sim_code'], scope)
                                    if 'run_simulation' not in scope: raise ValueError("run_simulation() missing")
                                    trace = scope['run_simulation'](data, pkg['schema'].get('blocks', []))

                                    if not trace or not isinstance(trace, list):
                                        raise ValueError("Simulation returned no trace")

                                    valid_package = pkg
                                    break

                                except Exception as e:
                                    last_error = str(e)
                                    attempt += 1
                                    logger.warning(f"Runtime attempt {attempt} failed: {e}. Fixing code...")
                                    if attempt < MAX_RETRIES:
                                        st.toast(f"Refining code (Attempt {attempt}): {e}", icon="🔧")
                                        pkg = self.generator.fix_generated_code(pkg, last_error)

                            if valid_package:
                                st.session_state.selected_context = valid_package
                                st.session_state.new_algorithm_loaded = True
                                self._save_generated_algo(valid_package)
                                st.rerun()
                            else:
                                st.error(f"Failed to generate valid visualization after {MAX_RETRIES} attempts.")
                                if last_error:
                                    st.error(f"Last Error: {last_error}")

                        except Exception as api_err:
                            st.error(f"AI Service Error: {str(api_err)}")

                elif mode == "Analyze":
                    with st.spinner("Analyzing..."):
                        try:
                            chat_history = "\n".join(
                                [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
                            context_data = st.session_state.selected_context
                            schema_ctx = {}
                            code_ctx = ""

                            if isinstance(context_data, dict) and "sim_code" in context_data:
                                schema_ctx = context_data.get("schema", {})
                                code_ctx = f"DATA:\n{context_data.get('data_code')}\n\nSIM:\n{context_data.get('sim_code')}"
                            else:
                                schema_ctx = {"info": "Pre-defined VSDX schema."}
                                algo_name = context_data[0] if isinstance(context_data, tuple) else "Imported"
                                label = algo_name.lower()
                                target_func = None
                                if "a*" in label or "astar" in label:
                                    target_func = algorithms.run_astar_simulation
                                elif "dijkstra" in label:
                                    target_func = algorithms.run_dijkstra_simulation
                                elif "prim" in label:
                                    target_func = algorithms.run_prim_simulation

                                if target_func:
                                    code_ctx = inspect.getsource(target_func)
                                else:
                                    code_ctx = "Standard algorithms library."

                            full_prompt = get_analyze_prompt(chat_history, schema_ctx, code_ctx)
                            response = get_gemini_response(full_prompt)
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")

    def _render_schema_summary(self, pkg):
        st.markdown(f"**Generated: {pkg['schema'].get('title')}**")
        st.caption("Algorithm generated successfully.")

    def _save_generated_algo(self, pkg):
        if "ai_generated_schemas" not in st.session_state:
            st.session_state.ai_generated_schemas = []
        entry = {"title": pkg["schema"].get("title", "Unknown"), "schema": pkg}
        st.session_state.ai_generated_schemas.append(entry)

    @staticmethod
    def _normalize_schema(schema: dict) -> dict:
        allowed = {"process", "decision", "input", "output", "data", "terminator", "start", "end"}
        blocks = schema.get("blocks", [])
        for block in blocks:
            label = block.get("text", "")
            raw_type = (block.get("type", "") or "").lower()
            if "start" in label.lower():
                b_type = "start"
            elif "end" in label.lower():
                b_type = "terminator"
            elif raw_type in allowed:
                b_type = "terminator" if raw_type == "end" else raw_type
            else:
                b_type = "process"
            block["type"] = b_type
        schema["blocks"] = blocks
        return schema

    def run(self):
        st.set_page_config(page_title="VISO", layout="wide")
        self.apply_custom_styles()

        if st.session_state.new_algorithm_loaded:
            st.session_state.messages = []
            st.session_state.new_algorithm_loaded = False
            if isinstance(st.session_state.selected_context, dict) and "schema" in st.session_state.selected_context:
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.selected_context})

        new_selection = self.sidebar_manager.render_sidebar()

        if new_selection and new_selection != st.session_state.selected_context:
            logger.info("Context switch detected.")
            st.session_state.selected_context = new_selection
            st.session_state.simulation_step = 0
            st.session_state.is_playing = False
            st.session_state.new_algorithm_loaded = True
            st.rerun()

        self.render_main_content(st.session_state.selected_context)
        self.render_chat_component()


if __name__ == "__main__":
    app = VisoViewApp()
    app.run()