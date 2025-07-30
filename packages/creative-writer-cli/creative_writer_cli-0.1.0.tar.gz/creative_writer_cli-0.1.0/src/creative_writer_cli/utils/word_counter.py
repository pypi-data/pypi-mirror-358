def get_text_from_content(content, section_name, project_type):
    text = ""
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if section_name == "Characters":
                    text += item.get("Background", "") + " "
                    text += item.get("Skills", "") + " "
                    text += item.get("Positive Traits", "") + " "
                    text += item.get("Negative Traits", "") + " "
                elif section_name == "Plot":
                    text += item.get("Name", "") + " "
                    text += item.get("Details", "") + " "
                elif section_name == "Worldbuilding":
                    text += item.get("Description", "") + " "
                    text += item.get("History/Lore", "") + " "
                elif section_name == "Themes":
                    text += item.get("Description", "") + " "
                elif section_name == "Notes/Ideas":
                    text += item.get("Content", "") + " "
                elif section_name == "References":
                    # References are structured data, not typically counted for word count
                    pass
                elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                    text += item.get("Chapter Content", "") + " "
            elif isinstance(item, str):
                text += item + " "
    elif isinstance(content, str):
        text += content + " "
    return text

def calculate_word_count(project_name, project_meta, sections, get_section_content_func):
    total_words = 0
    project_type = project_meta.get('type')

    for section_name in sections:
        content = get_section_content_func(project_name, section_name)
        text_content = get_text_from_content(content, section_name, project_type)
        total_words += len(text_content.split())

    return total_words
