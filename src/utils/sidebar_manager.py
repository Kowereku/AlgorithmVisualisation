import streamlit as st
import os
from . import EXAMPLES
from typing import Optional


class SidebarManager:
    """
    A class to manage the Streamlit sidebar components.
    """


    def __init__(self):
        self.EXAMPLES = EXAMPLES
        self.uploaded_file = None
        self.selected_example_path = None

    def render_sidebar(self) -> Optional[bytes]:
        """
        Render the sidebar components for file upload or example selection.

        Returns:
            Optional[bytes]: The file content (uploaded or example), or None.
        """
        st.sidebar.title("Algorithm Visualization")

        st.sidebar.markdown("---")

        return self._render_example_mode()


    def _render_example_mode(self) -> Optional[bytes]:
        st.sidebar.info("Choose a pre-defined algorithm.")

        selected_name = st.sidebar.selectbox(
            "Select Algorithm",
            options=list(self.EXAMPLES.keys())
        )

        self.selected_example_path = self.EXAMPLES.get(selected_name)

        if st.sidebar.button("Generate Visualization"):
            return self._handle_example_load()
        return None

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