import configparser
import os
from langchain_google_genai import ChatGoogleGenerativeAI


def get_api_key(config_file="credentials.ini") -> str | None:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parent_dir = os.path.dirname(script_dir)
    grandparent_dir = os.path.dirname(parent_dir)

    absolute_path = os.path.join(grandparent_dir, config_file)

    try:
        if not os.path.exists(absolute_path):
            absolute_path = os.path.join(parent_dir, config_file)
            if not os.path.exists(absolute_path):
                raise FileNotFoundError(f"File not found at {absolute_path}")

        config = configparser.ConfigParser()
        config.read(absolute_path)

        return config['google']['api_key']

    except FileNotFoundError:
        print(f"Error: The configuration file was not found.")
        return None
    except KeyError:
        print(f"Error: Could not find 'api_key' under [google] section in '{config_file}'.")
        return None
    except configparser.MissingSectionHeaderError:
        print(f"Error: File '{absolute_path}' is empty or not a valid .ini file (missing [google] header).")
        return None


def get_gemini_response(prompt: str) -> str:
    try:
        MY_API_KEY = get_api_key()

        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=MY_API_KEY)

        response = model.invoke(prompt)

        content = response.content

        if isinstance(content, list):
            return "".join([str(item) for item in content])

        return str(content)

    except Exception as e:
        return f"An error occurred while communicating with the API: {e}"