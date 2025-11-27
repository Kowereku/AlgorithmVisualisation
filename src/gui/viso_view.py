import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from src.utils.sidebar_manager import SidebarManager
from src.libs.schema_parser import VSDXParser
from src.libs.llm_interfaces import get_gemini_response


class VisoViewApp:
    """
    A class to manage the Streamlit app for algorithm visualization.
    """

    def __init__(self):
        self.sidebar_manager = SidebarManager()
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @staticmethod
    def apply_custom_styles():
        """
        Inject custom CSS from an external file to style buttons, headers, and the general layout.
        """
        css_file_path = os.path.join(os.path.dirname(__file__), "styles", "viso_view.css")
        with open(css_file_path, "r") as css_file:
            css_content = css_file.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    def render_main_content(self, uploaded_file_content: bytes):
        """
        Render the main content area of the app (Visualization).

        Args:
            uploaded_file_content (bytes): The content of the uploaded file.
        """
        st.markdown("### Visualization Workspace")

        if uploaded_file_content:
            with st.container(border=True):
                st.success("Visualization generated successfully!")
                parsed_data = self.parse_vsdx_file(uploaded_file_content)

                with st.expander("View Raw Parsed Data"):
                    st.json(parsed_data)

                st.info("Graphical visualization would be rendered here based on parsed_data.")
        else:
            st.info("Please select an algorithm and click 'Generate Visualization'.")

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

        self.apply_custom_styles()

        st.title("Algorithm Visualization Tool")
        st.markdown("Visualize algorithms presented as block schemas and chat with AI for insights.")

        file_content = self.sidebar_manager.render_sidebar()

        self.render_main_content(file_content)

        self.render_chat_component()


if __name__ == "__main__":
    app = VisoViewApp()
    app.run()
