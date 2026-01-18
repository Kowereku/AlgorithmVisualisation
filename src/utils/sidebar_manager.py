import streamlit as st
import os
from . import EXAMPLES
from typing import Optional, Tuple


class SidebarManager:
    """
    A class to manage the Streamlit sidebar components.
    """


    def __init__(self):
        self.EXAMPLES = EXAMPLES
        if "active_algo_data" not in st.session_state:
            st.session_state.active_algo_data = (None, None)

    def render_sidebar(self) -> Tuple[str, Optional[bytes]]:
        """
        Render the sidebar components for file upload or example selection and also
        expose a toggle for selecting either example algorithms or AI-generated schemas.

        Returns:
            Tuple[str, Optional[bytes]]: (Selected Algorithm Name, File Content or None)
        """
        st.sidebar.title("Algorithm Visualization")

        st.sidebar.markdown("### AI Mode")
        ai_mode = st.sidebar.radio(
            "Select AI Mode",
            options=["Generate", "Analyze"],
            index=0 if st.session_state.get("ai_mode", "Generate") == "Generate" else 1
        )
        st.session_state.ai_mode = ai_mode

        st.sidebar.markdown("---")

        st.sidebar.markdown("### Context Source")
        context_source = st.sidebar.radio(
            "Select context source",
            options=["Example Algorithms", "AI-Generated Schemas"],
            index=0
        )
        st.session_state.context_source = context_source

        st.sidebar.markdown("---")

        if context_source == "Example Algorithms":
            st.sidebar.markdown("### Example Algorithms")
            selected_name = st.sidebar.selectbox(
                "Select Algorithm",
                options=list(self.EXAMPLES.keys())
            )
            self.selected_example_path = self.EXAMPLES.get(selected_name)

            if st.sidebar.button("Visualize Algorithm"):
                file_content = self._handle_example_load()
                if file_content:
                    st.session_state.selected_context = file_content.decode("utf-8")
                else:
                    st.session_state.selected_context = ""


        elif context_source == "AI-Generated Schemas":

            st.sidebar.markdown("### AI-Generated Schemas")
            schemas_list = st.session_state.get("ai_generated_schemas", [])

            if schemas_list:

                options = {item["title"]: item["schema"] for item in schemas_list}
                selected_title = st.sidebar.selectbox("Select Schema", options=list(options.keys()))

                if st.sidebar.button("Load Generated Schema"):
                    selected_data = options[selected_title]
                    st.session_state.selected_context = selected_data
            else:
                st.sidebar.info("No AI-generated schemas available.")
                st.session_state.selected_context = ""

        st.sidebar.markdown("---")

        return None

    def _render_example_mode(self) -> Tuple[str, Optional[bytes]]:
        st.sidebar.info("Choose a pre-defined algorithm.")

        selected_name = st.sidebar.selectbox(
            "Select Algorithm",
            options=list(self.EXAMPLES.keys()),
            index=0
        )

        self.selected_example_path = self.EXAMPLES.get(selected_name)

        if st.sidebar.button("Generate Visualization"):
            content = self._handle_example_load()
            st.session_state.active_algo_data = (selected_name, content)
            st.session_state.simulation_step = 0
            st.session_state.is_playing = False
        return st.session_state.active_algo_data

    def _handle_example_load(self) -> Optional[bytes]:
        """Reads the local example file and returns bytes."""
        if self.selected_example_path and os.path.exists(self.selected_example_path):
            try:
                with open(self.selected_example_path, "rb") as f:
                    content = f.read()
                st.sidebar.success(f"Loaded: {self.selected_example_path}")
                return content
            except Exception as e:
                st.sidebar.error(f"Error loading example: {e}")
                return None
        else:
            st.sidebar.error(f"File not found: {self.selected_example_path}")
            return None
