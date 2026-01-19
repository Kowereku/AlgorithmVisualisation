import streamlit as st
import os
import logging
from . import EXAMPLES
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SidebarManager:
    def __init__(self):
        self.EXAMPLES = EXAMPLES
        if "active_algo_data" not in st.session_state:
            st.session_state.active_algo_data = (None, None)

    def render_sidebar(self) -> Tuple[str, Optional[bytes]]:
        st.sidebar.title("Algorithm Visualization")

        st.sidebar.markdown("### AI Mode")

        if "ai_mode" not in st.session_state:
            st.session_state.ai_mode = "Generate"

        st.sidebar.radio(
            "Select AI Mode",
            options=["Generate", "Analyze"],
            key="ai_mode"
        )

        st.sidebar.markdown("---")

        st.sidebar.markdown("### Context Source")
        context_source = st.sidebar.radio(
            "Select context source",
            options=["Example Algorithms", "AI-Generated Schemas"],
            index=0
        )
        st.session_state.context_source = context_source

        st.sidebar.markdown("---")

        current_selection = st.session_state.get("selected_context")

        if context_source == "Example Algorithms":
            st.sidebar.markdown("### Example Algorithms")
            selected_name = st.sidebar.selectbox(
                "Select Algorithm",
                options=list(self.EXAMPLES.keys())
            )
            self.selected_example_path = self.EXAMPLES.get(selected_name)

            if st.sidebar.button("Visualize Algorithm"):
                logger.info(f"Loading example algorithm: {selected_name}")
                file_content = self._handle_example_load()
                if file_content:
                    return (selected_name, file_content)

        elif context_source == "AI-Generated Schemas":
            st.sidebar.markdown("### AI-Generated Schemas")
            schemas_list = st.session_state.get("ai_generated_schemas", [])

            if schemas_list:
                options = {item["title"]: item["schema"] for item in schemas_list}
                selected_title = st.sidebar.selectbox("Select Schema", options=list(options.keys()))

                if st.sidebar.button("Load Generated Schema"):
                    logger.info(f"Loading generated schema: {selected_title}")
                    return options[selected_title]
            else:
                st.sidebar.info("No AI-generated schemas available.")
                return None

        st.sidebar.markdown("---")
        return current_selection

    def _handle_example_load(self) -> Optional[bytes]:
        if self.selected_example_path and os.path.exists(self.selected_example_path):
            try:
                with open(self.selected_example_path, "rb") as f:
                    content = f.read()
                st.sidebar.success(f"Loaded: {self.selected_example_path}")
                return content
            except Exception as e:
                logger.error(f"Error loading example file: {e}")
                st.sidebar.error(f"Error loading example: {e}")
                return None
        else:
            logger.error(f"Example file not found: {self.selected_example_path}")
            st.sidebar.error(f"File not found: {self.selected_example_path}")
            return None