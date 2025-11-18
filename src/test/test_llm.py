from libs.llm_interfaces import get_gemini_response

if __name__ == "__main__":
    """
    Test script for the Google Gemini LLM interface.

    This script sends a sample prompt to the Gemini model and prints the response.
    """

    sample_prompt = "Explain the concept of machine learning in simple terms."
    response = get_gemini_response(sample_prompt)
    print(f'Sample Prompt: \n {sample_prompt}')
    print(f"Gemini Response: \n {response}")
