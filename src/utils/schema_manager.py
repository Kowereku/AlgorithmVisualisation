import json
import re
import os
import streamlit as st
from src.libs.llm_interfaces import get_gemini_response
from src.prompts.generate_prompt import get_generate_prompt
from src.libs.schema_parser import VSDXParser


class SchemaManager:

    @staticmethod
    def generate_schema(user_prompt: str, example_data: dict) -> dict:
        system_prompt = get_generate_prompt(example_data)
        full_prompt = f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
        raw_response = get_gemini_response(full_prompt)
        return SchemaManager._clean_and_parse_json(raw_response)

    @staticmethod
    def parse_vsdx_file(file_content: bytes) -> dict:
        temp_filename = "temp_upload.vsdx"
        try:
            with open(temp_filename, "wb") as temp_file:
                temp_file.write(file_content)

            parser = VSDXParser(temp_filename)
            parsed_data = parser.parse()

            if parsed_data and "title" not in parsed_data:
                parsed_data["title"] = "Imported Visio Schema"

            return parsed_data

        except Exception as e:
            raise ValueError(f"Failed to parse VSDX file: {str(e)}")
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    @staticmethod
    def _clean_and_parse_json(text: str) -> dict:
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'(\{.*\})', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError("Could not parse valid JSON from AI response.")

    @staticmethod
    def save_to_session(schema: dict):
        if "ai_generated_schemas" not in st.session_state:
            st.session_state.ai_generated_schemas = []

        entry = {
            "title": schema.get("title", f"Schema {len(st.session_state.ai_generated_schemas) + 1}"),
            "schema": schema
        }
        st.session_state.ai_generated_schemas.append(entry)
