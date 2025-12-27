import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from st_cytoscape import cytoscape
from src.utils.sidebar_manager import SidebarManager
from src.libs.schema_parser import VSDXParser
from src.libs.llm_interfaces import get_gemini_response
from src.libs import algorithms, cytoscape_parser

class VisoViewApp:
    """
    A class to manage the Streamlit app for algorithm visualization.
    """

    def __init__(self):
        self.sidebar_manager = SidebarManager()
        if "messages" not in st.session_state:
            st.session_state.messages = []

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
        """
        Inject custom CSS from an external file to style buttons, headers, and the general layout.
        """
        css_file_path = os.path.join(os.path.dirname(__file__), "styles", "viso_view.css")
        with open(css_file_path, "r") as css_file:
            css_content = css_file.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    def render_main_content(self, selection_data):
        """
        Render the main content area of the app (Visualization).

        Args:
            selection_data (tuple): (Algorithm Name, File Content) from sidebar.
        """
        selected_algo_name, file_content = selection_data

        st.markdown(f"### Visualizing: {selected_algo_name}")

        if file_content:
            with st.expander("View Parsed VSDX Schema (JSON)", expanded=False):
                parsed_data = self.parse_vsdx_file(file_content)
                st.json(parsed_data)

        st.markdown("### Visualization Workspace")

        vsdx_json = {}
        if file_content:
            parsed_data = self.parse_vsdx_file(file_content)
            vsdx_json = parsed_data

        data_graph = algorithms.get_scenario_data()

        blocks = vsdx_json.get("blocks", [])
        trace = []

        if "A*" in selected_algo_name:
            trace = algorithms.run_astar_simulation(data_graph, "A", "C", vsdx_blocks=blocks)
        elif "Dijkstra" in selected_algo_name:
            trace = algorithms.run_dijkstra_simulation(data_graph, "A", "C", vsdx_blocks=blocks)
        elif "Prim" in selected_algo_name:
            trace = algorithms.run_prim_simulation(data_graph, "A", vsdx_blocks=blocks)
        else:
            trace = algorithms.run_astar_simulation(data_graph, "A", "C", vsdx_blocks=blocks)

        elements_data = cytoscape_parser.convert_nx_to_cytoscape(data_graph)
        elements_flow = cytoscape_parser.convert_vsdx_to_cytoscape(vsdx_json)

        if trace:
            step = st.slider("Execution Step", 0, len(trace) - 1, 0)
            current_frame = trace[step]

            for ele in elements_data:
                ele_id = ele["data"].get("id")
                ele["classes"] = "data-node" if "source" not in ele["data"] else "data-edge"

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
                    width="100%", height="500px", layout={"name": "preset"},
                    key="graph_data"
                )

            with col2:
                st.subheader("Algorithm Logic")
                if elements_flow:
                    cytoscape(
                        elements=elements_flow, stylesheet=self.styles["flowchart"],
                        width="100%", height="500px", layout={"name": "breadthfirst"},  # Safe layout
                        key="graph_flow"
                    )
                else:
                    st.info("No VSDX flow loaded.")

            st.info(f"**Step {step}:** {current_frame['description']}")

    @staticmethod
    def parse_vsdx_file(file_content: bytes):
        """
        Parse the uploaded .vsdx file and extract blocks and connections.

        Args:
            file_content (bytes): The content of the uploaded .vsdx file.

        Returns:
            dict: Parsed data containing blocks and connections.
        """
        try:
            with open("temp.vsdx", "wb") as temp_file:
                temp_file.write(file_content)
            parser = VSDXParser("temp.vsdx")
            parsed_data = parser.parse()
            return parsed_data
        except Exception as e:
            st.error(f"Error parsing file: {e}")
            return {}
        finally:
            if os.path.exists("temp.vsdx"):
                os.remove("temp.vsdx")

    def render_chat_component(self):
        """
        Render the chat interface.
        The st.chat_input handles the bottom pinning automatically.
        """
        st.divider()

        st.subheader("AI Visualization Assistant")

        st.caption("Ask questions about the logic, flow, or specific blocks in your diagram.")

        user_avatar = "🧑‍💻"
        assistant_avatar = "🤖"

        for message in st.session_state.messages:
            role = message["role"]
            avatar = user_avatar if role == "user" else assistant_avatar

            with st.chat_message(role, avatar=avatar):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask questions about the algorithm..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user", avatar=user_avatar):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar=assistant_avatar):
                with st.spinner("Analysing diagram structure..."):
                    try:
                        response = get_gemini_response(prompt)
                        st.markdown(response)

                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Failed to get response: {e}")

    def run(self):
        """
        Run the Streamlit app.
        """
        st.set_page_config(page_title="Algorithm Visualization", layout="wide")

        try:
            self.apply_custom_styles()
        except:
            pass

        st.title("Algorithm Visualization Tool")
        st.markdown("Visualize algorithms presented as block schemas and chat with AI for insights.")

        selection_data = self.sidebar_manager.render_sidebar()

        if selection_data and selection_data[0]:
            self.render_main_content(selection_data)

        self.render_chat_component()


if __name__ == "__main__":
    app = VisoViewApp()
    app.run()
