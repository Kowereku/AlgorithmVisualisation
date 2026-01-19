import json
import re
import logging
from src.libs.llm_interfaces import get_gemini_response
from src.prompts.generate_prompt import get_generate_prompt
from src.prompts.code_prompts import get_data_setup_prompt, get_simulation_logic_prompt, get_fix_code_prompt
from src.utils.schema_manager import SchemaManager

logger = logging.getLogger(__name__)

class AlgorithmGenerator:

    def generate_full_algorithm(self, user_request: str) -> dict:
        logger.info(f"Starting generation pipeline for: {user_request}")

        schema = SchemaManager.generate_schema(user_request, {"blocks": [], "connections": []})

        logger.info("Generating Data Setup Code...")
        data_code = self._generate_data_code(user_request)

        logger.info("Generating Simulation Logic...")
        sim_code = self._generate_sim_code(user_request, schema, data_code)

        return {
            "title": schema.get("title", "Generated Algorithm"),
            "schema": schema,
            "data_code": data_code,
            "sim_code": sim_code
        }

    def fix_generated_code(self, broken_pkg: dict, error_msg: str) -> dict:
        logger.warning(f"Requesting AI Code Fix for Runtime Error: {error_msg}")
        prompt = get_fix_code_prompt(broken_pkg, error_msg)
        response = get_gemini_response(prompt)

        try:
            fixes = self._clean_and_parse_json(response)
            if fixes.get("data_code"):
                broken_pkg["data_code"] = fixes.get("data_code")
            if fixes.get("sim_code"):
                broken_pkg["sim_code"] = fixes.get("sim_code")

            logger.info("Code Fix received and applied.")
            return broken_pkg
        except Exception as e:
            logger.error(f"Failed to parse fix response: {e}")
            return broken_pkg

    def _generate_data_code(self, request: str) -> str:
        prompt = get_data_setup_prompt(request)
        response = get_gemini_response(prompt)
        return self._extract_python(response)

    def _generate_sim_code(self, request: str, schema: dict, data_code: str) -> str:
        block_list = "\n".join(
            [f"- ID '{b.get('id', '?')}': {b.get('text', 'No Text')}" for b in schema.get("blocks", [])])
        prompt = get_simulation_logic_prompt(request, block_list, data_code)
        response = get_gemini_response(prompt)
        return self._extract_python(response)

    @staticmethod
    def _clean_and_parse_json(text: str) -> dict:
        if not isinstance(text, str): text = str(text)
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```", "", text).strip()
        try:
            return json.loads(text)
        except:
            match = re.search(r'(\{.*\})', text, re.DOTALL)
            return json.loads(match.group(1)) if match else {}

    @staticmethod
    def _extract_python(text: str) -> str:
        if not isinstance(text, str): text = str(text)
        text = re.sub(r"```python\s*", "", text)
        text = re.sub(r"```", "", text).strip()
        return text