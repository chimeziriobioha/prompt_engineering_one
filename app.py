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


def welcome_response_new_user():
    """
    Genarate greeting for a new LLM user and save the response to a new file.
    Multiple run will update appropriate file in `/responses` with the new content.
    """
    # Make a request for a response from assistant
    # with ``messages`` arg completely configured in settings
    response = client.chat.completions.create(
        model=g_settings['model'],
        messages=SETTINGS['welcome_prompts']['messages'],
        response_format=g_settings['response_format']
    )

    # Check for responses/welcome.json file and get the data
    try:
        with open("responses/welcome.json", "r") as fp:
            all_data = json.load(fp)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        all_data = []

    # Append new data to existing one
    all_data.append(response.choices[0].message.content)

    # Write all data back to the file
    with open("responses/welcome.json", "w") as fp:
        json.dump(all_data, fp, indent=4)
    
    print("Welcome note genarated and written to file.")


def generate_code_for_dropdown():
    """
    Genarate HTML and CSS code for a dropdown button and save the response to a new file.
    Multiple run will update appropriate file in `/responses` with the new content.
    Also extract and write the HTML and CSS in separate `.html` and `.css` files.
    """
    # Make a request for a response from assistant
    # with ``messages`` arg partly configured in settings
    response = client.chat.completions.create(
        model=g_settings['model'],
        messages=[
            {'role': 'system', 'content': SETTINGS['code_prompts']['system_persona']},
            {'role': 'user', 'content': SETTINGS['code_prompts']['user_instruction']}
        ]
    )

    # Check for responses/dropdown.json file and get the data
    try:
        with open("responses/dropdown.json", "r") as fp:
            all_data = json.load(fp)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        all_data = []

    # Append new data to existing one
    content = response.choices[0].message.content
    all_data.append(content)

    # Write all data back into /responses/dropdown.json
    with open("responses/dropdown.json", "w") as fp:
        json.dump(all_data, fp, indent=4)
    
    # UPDATE /dropdowns 
    # WITH THE NEW DATA

    # Extract the code part of the content
    code_str = ""
    # ``` separates the json'd code from the 
    # rest of the strings at both start and end
    for s in content.split('```'):
        # check that content meets the specified settings
        if s.startswith('json') \
            and any(t in s for t in ["'HTML':", '"HTML":']) \
            and any(t in s for t in ['"CSS":', "'CSS':"]):
            code_str = s
            break
    
    # Raise exception if code_str is ""
    if not code_str:
        raise ValueError("Content does not meet specified settings")
    
    # Remove "json" at the start of code_str
    code_str = code_str[4:]

    # Specify/create folder for new data, 
    # makes use of len(all_data) to achieve uniquness
    folder = f"dropdowns/r{len(all_data)}"
    Path(folder).mkdir(parents=True, exist_ok=True)
    
    # Write the html/css code in subscriptable json file
    with open(f"{folder}/code.json", "w", encoding="utf-8") as f:
        f.write(code_str)
    
    # Read the json file to access the code
    with open(f"{folder}/code.json", "r") as f:
        code = json.load(f)
    
    # Write the HTML code into it's own file
    with open(f"{folder}/index.html", "w", encoding="utf-8") as f:
        f.write(code['HTML'])
    
    # Write the CSS code into it's own file
    with open(f"{folder}/styles.css", "w", encoding="utf-8") as f:
        f.write(code['CSS'])
    
    print(f"Dropdown code genarated and written to {folder}.")


if __name__ == "__main__":

    welcome_response_new_user()

    generate_code_for_dropdown()

