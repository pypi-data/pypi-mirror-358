import os

def get_section_filepath(project_name, section_name):
    sanitized_section_name = section_name.lower().replace(' ', '_').replace('/', '_')
    return os.path.join(project_name, f"{sanitized_section_name}.json")
