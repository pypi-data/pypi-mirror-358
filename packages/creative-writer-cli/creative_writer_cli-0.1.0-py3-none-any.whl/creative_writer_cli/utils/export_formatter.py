from typing import List, Dict, Any

def format_characters_to_markdown(characters: List[Dict[str, Any]]) -> str:
    if not characters:
        return "## Characters\n\nNo characters found.\n"

    markdown_output = "## Characters\n\n"
    for char in characters:
        markdown_output += f"### {char.get('name', 'Unnamed Character')}\n"
        for key, value in char.items():
            if key != 'name' and value: # Exclude 'name' as it's already in the heading
                markdown_output += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        markdown_output += "\n" # Add a newline for separation between characters
    return markdown_output

def format_plot_points_to_markdown(plot_points: List[Dict[str, Any]]) -> str:
    if not plot_points:
        return "## Plot Points\n\nNo plot points found.\n"

    markdown_output = "## Plot Points\n\n"
    # Sort by timeline_order if it's a number, otherwise keep original order
    sorted_plot_points = sorted(plot_points, key=lambda x: int(x.get('timeline_order', 0) or 0) if str(x.get('timeline_order', 0) or 0).isdigit() else 0)

    for pp in sorted_plot_points:
        markdown_output += f"### {pp.get('name', 'Unnamed Plot Point')}\n"
        for key, value in pp.items():
            if key != 'name' and value:
                markdown_output += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        markdown_output += "\n"
    return markdown_output

def format_worldbuilding_to_markdown(elements: List[Dict[str, Any]]) -> str:
    if not elements:
        return "## Worldbuilding Elements\n\nNo worldbuilding elements found.\n"

    markdown_output = "## Worldbuilding Elements\n\n"
    for el in elements:
        markdown_output += f"### {el.get('name', 'Unnamed Element')}\n"
        for key, value in el.items():
            if key != 'name' and value:
                markdown_output += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        markdown_output += "\n"
    return markdown_output

def format_themes_to_markdown(themes: List[Dict[str, Any]]) -> str:
    if not themes:
        return "## Themes\n\nNo themes found.\n"

    markdown_output = "## Themes\n\n"
    for theme in themes:
        markdown_output += f"### {theme.get('theme_name', 'Unnamed Theme')}\n"
        for key, value in theme.items():
            if key != 'theme_name' and value:
                markdown_output += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        markdown_output += "\n"
    return markdown_output

def format_notes_to_markdown(notes: List[Dict[str, Any]]) -> str:
    if not notes:
        return "## Notes and Ideas\n\nNo notes or ideas found.\n"

    markdown_output = "## Notes and Ideas\n\n"
    for note in notes:
        markdown_output += f"### {note.get('title', 'Untitled Note')}\n"
        for key, value in note.items():
            if key != 'title' and value:
                markdown_output += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        markdown_output += "\n"
    return markdown_output

def format_references_to_markdown(references: List[Dict[str, Any]]) -> str:
    if not references:
        return "## References\n\nNo references found.\n"

    markdown_output = "## References\n\n"
    for ref in references:
        markdown_output += f"### {ref.get('title', 'Untitled Reference')}\n"
        for key, value in ref.items():
            if key != 'title' and value:
                markdown_output += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        markdown_output += "\n"
    return markdown_output

def format_chapters_to_markdown(chapters: List[Dict[str, Any]]) -> str:
    if not chapters:
        return "## Chapters\n\nNo chapters found.\n"

    markdown_output = "## Chapters\n\n"
    for chapter in chapters:
        markdown_output += f"### {chapter.get('chapter_title', 'Untitled Chapter')}\n"
        for key, value in chapter.items():
            if key != 'chapter_title' and value:
                markdown_output += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        markdown_output += "\n"
    return markdown_output

def format_generic_text_section_to_markdown(content: List[str], section_name: str) -> str:
    if not content or not content[0]:
        return f"## {section_name}\n\nNo content found.\n"
    
    # Assuming content for these sections is a list with a single string element
    return f"## {section_name}\n\n{content[0]}\n"