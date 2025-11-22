import streamlit as st
import os
from typing import Optional


class SidebarManager:
    """
    A class to manage the Streamlit sidebar components.
    """

    # Define your available examples here
    # Key = Display Name, Value = Relative path to the .vsdx file
    EXAMPLES = {
        "A* Algorithm": "src/assets/aAsteriskAlgorithm.vsdx",
        "Dijkstra's Algorithm": "src/assets/dijkstraAlgorithm.vsdx",
        "Prim's Algorithm": "src/assets/primsAlgorithm.vsdx",
        "Floyd Warshall's Algorithm": "src/assets/floydWarshallAlgorithm.vsdx"
    }

    def __init__(self):
        self.uploaded_file = None
        self.selected_example_path = None

    def render_sidebar(self) -> Optional[bytes]:
        """
        Render the sidebar components for file upload or example selection.

        Returns:
            Optional[bytes]: The file content (uploaded or example), or None.
        """
        st.sidebar.title("Algorithm Visualization")

        mode = st.sidebar.radio(
            "Choose Source:",
            options=["Upload File", "Select Example"]
        )

        st.sidebar.markdown("---")

        if mode == "Upload File":
            return self._render_upload_mode()
        else:
            return self._render_example_mode()

    def _render_upload_mode(self) -> Optional[bytes]:
        st.sidebar.info("Upload a block schema file.")
        self.uploaded_file = st.sidebar.file_uploader("Upload your .vsdx file", type=["vsdx"])

        if st.sidebar.button("Generate Visualization"):
            return self._handle_file_upload()
        return None

    def _render_example_mode(self) -> Optional[bytes]:
        st.sidebar.info("Choose a pre-defined algorithm.")

        selected_name = st.sidebar.selectbox(
            "Select Algorithm",
            options=list(self.EXAMPLES.keys())
        )

        self.selected_example_path = self.EXAMPLES.get(selected_name)

        if st.sidebar.button("Load Example"):
            return self._handle_example_load()
        return None

    def _handle_file_upload(self) -> Optional[bytes]:
        if self.uploaded_file is not None:
            st.sidebar.success("File uploaded successfully!")
            return self.uploaded_file.read()
        else:
            st.sidebar.error("Please upload a file first.")
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