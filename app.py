import os
import json
import tomllib
from pathlib import Path
from openai import OpenAI


client = OpenAI(api_key=os.getenv('OPEN_API_KEY_ONE'))


settings_path = Path("settings.toml")
with settings_path.open("rb") as settings_file:
    SETTINGS = tomllib.load(settings_file)
    g_settings = SETTINGS['general']


def welcome_new_user():
    """
    Genarate greeting for a new LLM user and save the response to a new file.
    Multiple runs will update the file with contants new responses.
    """
    # make a request for a response from assistant
    # with ``messages`` arg completely configured in settings
    response = client.chat.completions.create(
        model=g_settings['model'],
        messages=SETTINGS['welcome_prompts']['messages'],
        response_format=g_settings['response_format']
    )

    # Check for welcome.json file and get the data
    try:
        with open("welcome.json", "r") as fp:
            all_data = json.load(fp)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        all_data = []

    # Append new data to existing one
    all_data.append(response.choices[0].message.content)

    # Write all data back to the file
    with open("welcome.json", "w") as fp:
        json.dump(all_data, fp, indent=4)


def generate_code_for_dropdown():
    """
    Genarate HTML and CSS code for a dropdown button and save the response to a new file.
    Multiple runs will update the file with contants new responses.
    """
    # make a request for a response from assistant
    # with ``messages`` arg partly configured in settings
    response = client.chat.completions.create(
        model=g_settings['model'],
        messages=[
            {'role': 'system', 'content': SETTINGS['code_prompts']['system_persona']},
            {'role': 'user', 'content': SETTINGS['code_prompts']['user_instruction']}
        ]
    )

    # Check for dropdown_code.json file and get the data
    try:
        with open("dropdown_code.json", "r") as fp:
            all_data = json.load(fp)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        all_data = []

    # Append new data to existing one
    all_data.append(response.choices[0].message.content)

    # Write all data back into dropdown_code.json
    with open("dropdown_code.json", "w") as fp:
        json.dump(all_data, fp, indent=4)


if __name__ == "__main__":

    welcome_new_user()

    generate_code_for_dropdown()

