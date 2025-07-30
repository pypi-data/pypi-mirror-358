import questionary

def get_simple_text_input(prompt, default_value=""):
    return questionary.text(prompt, default=default_value, multiline=True).ask()
