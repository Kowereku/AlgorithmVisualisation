import streamlit as st
from typing import Optional


class SidebarManager:
    """
    A class to manage the Streamlit sidebar components.
    """

    def __init__(self):
        self.uploaded_file = None

    def render_sidebar(self) -> Optional[bytes]:
        """
        Render the sidebar components for file upload and visualization generation.

        Returns:
            Optional[bytes]: The uploaded file content, or None if no file is uploaded.
        """
        st.sidebar.title("Algorithm Visualization")
        st.sidebar.info("Upload a block schema file to generate a visualization.")

        # File uploader
        self.uploaded_file = st.sidebar.file_uploader("Upload your .vsdx file", type=["vsdx"])

        # Generate visualization button
        if st.sidebar.button("Generate Visualization"):
            return self._handle_generate_visualization()

        return None

    def _handle_generate_visualization(self) -> Optional[bytes]:
        """
        Handle the logic for the 'Generate Visualization' button.

        Returns:
            Optional[bytes]: The uploaded file content, or None if no file is uploaded.
        """
        if self.uploaded_file is not None:
            st.sidebar.success("File uploaded successfully!")
            return self.uploaded_file.read()
        else:
            st.sidebar.error("Please upload a file before generating visualization.")
            return None
