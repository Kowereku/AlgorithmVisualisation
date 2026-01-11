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
        Render the sidebar components for file upload or example selection.

        Returns:
            Tuple[str, Optional[bytes]]: (Selected Algorithm Name, File Content or None)
        """
        st.sidebar.title("Algorithm Visualization")

        st.sidebar.markdown("---")

        return self._render_example_mode()


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