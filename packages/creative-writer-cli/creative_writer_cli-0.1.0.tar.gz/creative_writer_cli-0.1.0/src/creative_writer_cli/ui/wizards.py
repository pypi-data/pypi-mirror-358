import questionary
from rich.console import Console

from ..core.models import Character, PlotPoint, WorldbuildingElement, Theme, NoteIdea, Reference, Chapter

console = Console()

def get_character_input(character_data=None):
    fields = [
        ("Name", "text"), ("Race", "text"), ("Class", "text"), ("Gender", "text"), 
        ("Background", "text"), ("Skills", "text"), ("Equipment", "text"), 
        ("Positive Traits", "text"), ("Negative Traits", "text")
    ]
    
    data = character_data if character_data else {}
    for field_name, field_type in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name}:", default=default_value).ask()
        # Add other field types if needed
        if answer is not None:
            data[field_name] = answer
    return data

def get_plot_point_input(plot_point_data=None):
    fields = [
        ("name", "text"), ("details", "text"), ("timeline_order", "text"), 
        ("characters_involved", "text"), ("location", "text"),
        ("status", "select", ["Idea", "Outline", "First Draft", "Completed"]) # Changed from "text" to "select"
    ]

    data = plot_point_data if plot_point_data else {}
    for field_name, field_type, *options in fields:
        current_value = data.get(field_name, "") # Get current value from data or empty string

        if field_type == "text":
            answer = questionary.text(f"Enter {field_name}:", default=current_value).ask()
        elif field_type == "select":
            choices = options[0]
            # Ensure default_value is one of the choices, or None
            default_value_for_select = current_value if current_value in choices else (choices[0] if choices else None)
            answer = questionary.select(f"Select {field_name}:", choices=choices, default=default_value_for_select).ask()

        if answer is not None:
            data[field_name] = answer
    return data

def get_worldbuilding_element_input(element_data=None):
    fields = [
        ("Name", "text"), 
        ("Type", "select", ["Location", "Culture", "Technology", "Magic System", "Other"]),
        ("Description", "text"), ("History/Lore", "text"), ("Connections", "text")
    ]

    data = element_data if element_data else {}
    for field_name, field_type, *options in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name}:", default=default_value).ask()
        elif field_type == "select":
            answer = questionary.select(f"Select {field_name}:", choices=options[0], default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_theme_input(theme_data=None):
    fields = [
        ("Theme Name", "text"), ("Description", "text"), 
        ("Motifs/Symbols", "text"), ("Related Elements", "text")
    ]

    data = theme_data if theme_data else {}
    for field_name, field_type in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name}:", default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_note_idea_input(note_data=None):
    fields = [
        ("Title", "text"), ("Content", "text"), ("Tags", "text")
    ]

    data = note_data if note_data else {}
    for field_name, field_type in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name}:", default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_reference_input(reference_data=None):
    fields = [
        ("Author(s)", "text"), ("Year", "text"), ("Title", "text"), 
        ("Journal/Conference", "text"), ("DOI/URL", "text")
    ]

    data = reference_data if reference_data else {}
    for field_name, field_type in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name}:", default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_chapter_input(chapter_data=None):
    fields = [
        ("Chapter Title", "text"), ("Content Summary", "text"), 
        ("Key Concepts", "text"), ("Status", "select", ["Outline", "Drafting", "Review", "Completed"])
    ]

    data = chapter_data if chapter_data else {}
    for field_name, field_type, *options in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name}:", default=default_value).ask()
        elif field_type == "select":
            answer = questionary.select(f"Select {field_name}:", choices=options[0], default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_simple_text_input(prompt, default_value=""):
    return questionary.text(prompt, default=default_value, multiline=True).ask()