import questionary

def get_character_input(character_data=None):
    fields = [
        ("name", "text"), ("race", "text"), ("character_class", "text"), ("gender", "text"), 
        ("background", "text"), ("skills", "text"), ("equipment", "text"), 
        ("positive_traits", "text"), ("negative_traits", "text")
    ]
    
    data = character_data if character_data else {}
    for field_name, field_type in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name.replace('_', ' ').title()}:", default=default_value).ask()
        # Add other field types if needed
        if answer is not None:
            data[field_name] = answer
    return data

def get_plot_point_input(plot_point_data=None):
    fields = [
        ("name", "text"), ("details", "text"), ("timeline_order", "text"), 
        ("characters_involved", "text"), ("location", "text"),
        ("status", "select", ["Idea", "Outline", "First Draft", "Completed"])
    ]

    data = plot_point_data if plot_point_data else {}
    for field_name, field_type, *options in fields:
        current_value = data.get(field_name, "")

        if field_type == "text":
            answer = questionary.text(f"Enter {field_name.replace('_', ' ').title()}:", default=current_value).ask()
        elif field_type == "select":
            choices = options[0]
            default_value_for_select = current_value if current_value in choices else (choices[0] if choices else None)
            answer = questionary.select(f"Select {field_name.replace('_', ' ').title()}:", choices=choices, default=default_value_for_select).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_worldbuilding_element_input(element_data=None):
    fields = [
        ("name", "text"), 
        ("type", "select", ["Location", "Culture", "Technology", "Magic System", "Other"]),
        ("description", "text"), ("history_lore", "text"), ("connections", "text")
    ]

    data = element_data if element_data else {}
    for field_name, field_type, *options in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name.replace('_', ' ').title()}:", default=default_value).ask()
        elif field_type == "select":
            answer = questionary.select(f"Select {field_name.replace('_', ' ').title()}:", choices=options[0], default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_theme_input(theme_data=None):
    fields = [
        ("theme_name", "text"), ("description", "text"), 
        ("motifs_symbols", "text"), ("related_elements", "text")
    ]

    data = theme_data if theme_data else {}
    for field_name, field_type in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name.replace('_', ' ').title()}:", default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data

def get_note_idea_input(note_data=None):
    fields = [
        ("title", "text"), ("content", "text"), ("tags", "text")
    ]

    data = note_data if note_data else {}
    for field_name, field_type in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name.replace('_', ' ').title()}:", default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data
