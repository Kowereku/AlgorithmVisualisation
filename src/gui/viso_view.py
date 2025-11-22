import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from src.utils.sidebar_manager import SidebarManager
from src.libs.schema_parser import VSDXParser


class VisoViewApp:
    """
    A class to manage the Streamlit app for algorithm visualization.
    """

    def __init__(self):
        self.sidebar_manager = SidebarManager()

    def render_main_content(self, uploaded_file_content: bytes):
        """
        Render the main content area of the app.

        Args:
            uploaded_file_content (bytes): The content of the uploaded file.
        """
        if uploaded_file_content:
            st.success("[FUTURE] Visualization generated successfully!")
            parsed_data = self.parse_vsdx_file(uploaded_file_content)
            st.write("Parsed Data:", parsed_data)
        else:
            st.info("Please upload a file and click 'Generate Visualization'.")

    def parse_vsdx_file(self, file_content: bytes):
        """
        Parse the uploaded .vsdx file and extract blocks and connections.

        Args:
            file_content (bytes): The content of the uploaded .vsdx file.

        Returns:
            dict: Parsed data containing blocks and connections.
        """
        with open("temp.vsdx", "wb") as temp_file:
            temp_file.write(file_content)

        parser = VSDXParser("temp.vsdx")
        parsed_data = parser.parse()
        os.remove("temp.vsdx")  # Clean up the temporary file
        return parsed_data

    def run(self):
        """
        Run the Streamlit app.
        """
        st.set_page_config(page_title="Algorithm Visualization", layout="wide")
        st.title("Algorithm Visualization Tool")
        st.write("Visualize algorithms presented as block schemas.")

        file_content = self.sidebar_manager.render_sidebar()

        self.render_main_content(file_content)


if __name__ == "__main__":
    app = VisoViewApp()
    app.run()
