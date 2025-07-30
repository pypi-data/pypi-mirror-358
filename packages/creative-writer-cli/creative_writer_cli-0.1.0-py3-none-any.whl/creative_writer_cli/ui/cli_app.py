import questionary
from rich.console import Console
import json

from ..data.repositories.project_repository import ProjectRepository
from ..core.templates import TEMPLATES
from ..core.models import Character, PlotPoint, WorldbuildingElement, Theme, NoteIdea, Reference, Chapter
from .display.tables import (
    display_character_table, display_plot_table, display_worldbuilding_table,
    display_themes_table, display_notes_table, display_references_table,
    display_chapters_table
)
from .display.views import view_details, display_text_content, project_overview
from .wizards.novel_wizards import (
    get_character_input, get_plot_point_input, get_worldbuilding_element_input,
    get_theme_input, get_note_idea_input
)
from .wizards.scientific_wizards import (
    get_reference_input, get_chapter_input
)
from .wizards.generic_wizards import get_simple_text_input
from .ascii_art import get_ascii_art

console = Console()

class CLIApp:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository
        self.console = Console()

    def main_menu(self):
        self.console.print(get_ascii_art())
        while True:
            choice = questionary.select(
                "What do you want to do?",
                choices=["Create New Project", "View Existing Projects", "Delete Project", "Exit"]
            ).ask()

            if choice == "Create New Project":
                self.create_project()
            elif choice == "View Existing Projects":
                self.view_projects()
            elif choice == "Delete Project":
                self.delete_project()
            elif choice == "Exit" or choice is None:
                if questionary.confirm("Are you sure you want to exit? This will close the application.").ask():
                    break
                else:
                    continue # If user says no, continue the loop and show main menu again

    def create_project(self):
        project_type = questionary.select(
            "What type of writing?",
            choices=list(TEMPLATES.keys())
        ).ask()

        if project_type is None:
            return

        project_name = questionary.text("Enter project name:").ask()

        if not project_name:
            self.console.print("[bold red]Project name cannot be empty.[/bold red]")
            return

        success, message = self.project_repository.create_project(project_name, project_type)

        if success:
            self.console.print(f"[bold green]{message}[/bold green]")
            # Initial input for Novel projects
            if project_type == "Novel":
                initial_input_choice = questionary.select(
                    "Initial input",
                    choices=["Plot", "Characters", "skip to template overview"]
                ).ask()

                if initial_input_choice and initial_input_choice != "skip to template overview":
                    self.edit_section(project_name, initial_input_choice)
        else:
            self.console.print(f"[bold red]{message}[/bold red]")

    def view_projects(self):
        projects = self.project_repository.get_projects()
        if not projects:
            self.console.print("[bold yellow]No projects found.[/bold yellow]")
            return

        project_choices = []
        for project_name in projects:
            project_meta = self.project_repository.get_project_meta(project_name)
            project_type = project_meta.get('type', 'Unknown Type')
            project_choices.append(f"{project_name} ({project_type})")

        project_to_view_display = questionary.select(
            "Select a project to view:",
            choices=project_choices
        ).ask()

        if project_to_view_display:
            # Extract the actual project name from the display string
            project_to_view = project_to_view_display.split(' (')[0]

        if project_to_view:
            self.project_menu(project_to_view)

    def delete_project(self):
        projects = self.project_repository.get_projects()
        if not projects:
            self.console.print("[bold yellow]No projects found.[/bold yellow]")
            return

        project_to_delete = questionary.select(
            "Select a project to delete:",
            choices=projects
        ).ask()

        if project_to_delete:
            if questionary.confirm(f"Are you sure you want to delete the project '{project_to_delete}'?").ask():
                success, message = self.project_repository.delete_project(project_to_delete)
                if success:
                    self.console.print(f"[bold green]{message}[/bold green]")
                else:
                    self.console.print(f"[bold red]{message}[/bold red]")

    def project_menu(self, project_name):
        while True:
            self.console.print(f"\n[bold cyan]Project: {project_name}[/bold cyan]")
            sections = self.project_repository.get_project_sections(project_name)
            choice = questionary.select(
                "What do you want to do?",
                choices=["View/Edit Sections", "Rename Project", "Project Overview", "Export Project", "Back to Main Menu"]
            ).ask()

            if choice == "View/Edit Sections":
                self.view_edit_sections(project_name, sections)
            elif choice == "Project Overview":
                project_meta = self.project_repository.get_project_meta(project_name)
                project_type = project_meta.get('type')
                sections = self.project_repository.get_project_sections(project_name)
                project_overview(project_name, sections, project_type, self.project_repository)
            elif choice == "Rename Project":
                self.rename_project(project_name)
                # After renaming, the project_name variable in this scope is outdated.
                # We need to break and let the main_menu re-list projects.
                break
            elif choice == "Export Project":
                self.export_project_menu(project_name)
            elif choice == "Back to Main Menu" or choice is None:
                break

    def rename_project(self, old_project_name):
        new_project_name = questionary.text(f"Enter new name for project '{old_project_name}':").ask()
        if not new_project_name:
            self.console.print("[bold red]New project name cannot be empty.[/bold red]")
            return

        if new_project_name == old_project_name:
            self.console.print("[bold yellow]Project name is the same. No change made.[/bold yellow]")
            return

        success, message = self.project_repository.rename_project(old_project_name, new_project_name)
        if success:
            self.console.print(f"[bold green]{message}[/bold green]")
        else:
            self.console.print(f"[bold red]{message}[/bold red]")

    def view_edit_sections(self, project_name, sections):
        section_to_edit = questionary.select(
            "Select a section to view/edit:",
            choices=sections
        ).ask()

        if section_to_edit:
            self.edit_section(project_name, section_to_edit)

    def export_project_menu(self, project_name):
        export_format = questionary.select(
            "Select export format:",
            choices=["Markdown", "JSON", "TXT"]
        ).ask()

        if export_format:
            message = self.project_repository.export_project(project_name, export_format)
            self.console.print(f"[bold green]{message}[/bold green]")

    def edit_section(self, project_name, section_name):
        while True:
            data = self.project_repository.get_section_content(project_name, section_name)
            self.console.print(f"\n[bold]Editing: {section_name}[/bold]")

            # Determine choices based on section_name and project_type
            project_meta = self.project_repository.get_project_meta(project_name)
            project_type = project_meta.get('type')

            choices = ["Back to Project Menu"]
            add_action = None
            edit_action = None
            delete_action = None
            view_details_action = None

            if section_name == "Characters":
                display_character_table(data)
                add_action = "Add Character"
                edit_action = "Edit Character"
                delete_action = "Delete Character"
                view_details_action = "View Character Details"
            elif section_name == "Plot":
                display_plot_table(data)
                add_action = "Add Plot Point"
                edit_action = "Edit Plot Point"
                delete_action = "Delete Plot Point"
                view_details_action = "View Plot Point Details"
            elif section_name == "Worldbuilding":
                display_worldbuilding_table(data)
                add_action = "Add Worldbuilding Element"
                edit_action = "Edit Worldbuilding Element"
                delete_action = "Delete Worldbuilding Element"
                view_details_action = "View Worldbuilding Element Details"
            elif section_name == "Themes":
                display_themes_table(data)
                add_action = "Add Theme"
                edit_action = "Edit Theme"
                delete_action = "Delete Theme"
                view_details_action = "View Theme Details"
            elif section_name == "Notes/Ideas":
                display_notes_table(data)
                add_action = "Add Note/Idea"
                edit_action = "Edit Note/Idea"
                delete_action = "Delete Note/Idea"
                view_details_action = "View Note/Idea Details"
            elif section_name == "References":
                display_references_table(data)
                add_action = "Add Reference"
                edit_action = "Edit Reference"
                delete_action = "Delete Reference"
                view_details_action = "View Reference Details"
                if project_type == "Scientific Article":
                    choices.insert(0, "Export References") # Add export option for scientific articles
            elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                display_chapters_table(data)
                add_action = "Add Chapter Content"
                edit_action = "Edit Chapter Content"
                delete_action = "Delete Chapter Content"
                view_details_action = "View Chapter Details"
            elif project_type in ["Scientific Article", "Scientific Book"] and section_name in ["Title", "Abstract", "Introduction", "Methods", "Results", "Discussion"]:
                display_text_content(data)
                add_action = "Add Content"
                edit_action = "Edit Content"
                delete_action = "Delete Content"
            else:
                self.console.print(json.dumps(data, indent=2))
                add_action = "Add Item"
                edit_action = "Edit Item"
                delete_action = "Delete Item"
            
            if add_action: choices.insert(0, add_action)
            if edit_action: choices.insert(1, edit_action)
            if delete_action: choices.insert(2, delete_action)
            if view_details_action: choices.insert(3, view_details_action)

            action = questionary.select(
                "What do you want to do?",
                choices=choices
            ).ask()

            if action == "Back to Project Menu" or action is None:
                break

            # Handle actions
            if action == add_action:
                if section_name == "Characters":
                    new_item_data = get_character_input()
                    if new_item_data: data.append(new_item_data)
                elif section_name == "Plot":
                    new_item_data = get_plot_point_input()
                    if new_item_data: data.append(new_item_data)
                elif section_name == "Worldbuilding":
                    new_item_data = get_worldbuilding_element_input()
                    if new_item_data: data.append(new_item_data)
                elif section_name == "Themes":
                    new_item_data = get_theme_input()
                    if new_item_data: data.append(new_item_data)
                elif section_name == "Notes/Ideas":
                    new_item_data = get_note_idea_input()
                    if new_item_data: data.append(new_item_data)
                elif section_name == "References":
                    new_item_data = get_reference_input()
                    if new_item_data: data.append(new_item_data)
                elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                    new_item_data = get_chapter_input()
                    if new_item_data: data.append(new_item_data)
                elif project_type in ["Scientific Article", "Scientific Book"] and section_name in ["Title", "Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion"]:
                    new_content = get_simple_text_input("Enter content:")
                    if new_content: data = [new_content]
                else:
                    new_item = questionary.text("Enter new item (in JSON format or simple text):").ask()
                    if new_item:
                        try: data.append(json.loads(new_item))
                        except json.JSONDecodeError: data.append(new_item)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print(f"[green]{add_action.replace('Add ', '')} added.[/green]")

            elif action == edit_action:
                if not data:
                    self.console.print("[yellow]No items to edit.[/yellow]")
                    continue
                
                selected_item_name = None
                if section_name == "Characters": selected_item_name = questionary.select("Select character to edit:", choices=[item.get("name", f"Character {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Plot": selected_item_name = questionary.select("Select plot point to edit:", choices=[item.get("name", f"Plot Point {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Worldbuilding": selected_item_name = questionary.select("Select worldbuilding element to edit:", choices=[item.get("name", f"Worldbuilding Element {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Themes": selected_item_name = questionary.select("Select theme to edit:", choices=[item.get("theme_name", f"Theme {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Notes/Ideas": selected_item_name = questionary.select("Select note/idea to edit:", choices=[item.get("title", f"Note/Idea {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "References": selected_item_name = questionary.select("Select reference to edit:", choices=[item.get("title", f"Reference {i}") for i, item in enumerate(data)]).ask()
                elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                    selected_item_name = questionary.select("Select chapter to edit:", choices=[item.get("chapter_title", f"Chapter {i}") for i, item in enumerate(data)]).ask()
                elif project_type in ["Scientific Article", "Scientific Book"] and section_name in ["Title", "Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion"]:
                    new_content = get_simple_text_input("Edit content:", default_value=data[0] if data else "")
                    if new_content:
                        data = [new_content]
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Content updated.[/green]")
                        continue
                else:
                    selected_item_name = questionary.select("Select item to edit:", choices=[f"{i}: {json.dumps(item)}" for i, item in enumerate(data)]).ask()

                if selected_item_name:
                    index = -1
                    if section_name == "Characters": index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                    elif section_name == "Plot": index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                    elif section_name == "Worldbuilding": index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                    elif section_name == "Themes": index = next((i for i, item in enumerate(data) if item.get("theme_name") == selected_item_name), None)
                    elif section_name == "Notes/Ideas": index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                    elif section_name == "References": index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                    elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                        index = next((i for i, item in enumerate(data) if item.get("chapter_title") == selected_item_name), None)
                    else: index = int(selected_item_name.split(':')[0])

                    if index is not None and index != -1:
                        updated_item_data = {}
                        if section_name == "Characters": updated_item_data = get_character_input(data[index])
                        elif section_name == "Plot": updated_item_data = get_plot_point_input(data[index])
                        elif section_name == "Worldbuilding": updated_item_data = get_worldbuilding_element_input(data[index])
                        elif section_name == "Themes": updated_item_data = get_theme_input(data[index])
                        elif section_name == "Notes/Ideas": updated_item_data = get_note_idea_input(data[index])
                        elif section_name == "References": updated_item_data = get_reference_input(data[index])
                        elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                            updated_item_data = get_chapter_input(data[index])
                        else: 
                            new_value = questionary.text("Enter new value:", default=json.dumps(data[index])).ask()
                            try: updated_item_data = json.loads(new_value)
                            except json.JSONDecodeError: updated_item_data = new_value
                        
                        if updated_item_data:
                            data[index] = updated_item_data
                            self.project_repository.save_section_content(project_name, section_name, data)
                            self.console.print(f"[green]{edit_action.replace('Edit ', '')} updated.[/green]")

            elif action == delete_action:
                if not data:
                    self.console.print("[yellow]No items to delete.[/yellow]")
                    continue

                selected_item_name = None
                if section_name == "Characters": selected_item_name = questionary.select("Select character to delete:", choices=[item.get("name", f"Character {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Plot": selected_item_name = questionary.select("Select plot point to delete:", choices=[item.get("name", f"Plot Point {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Worldbuilding": selected_item_name = questionary.select("Select worldbuilding element to delete:", choices=[item.get("name", f"Worldbuilding Element {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Themes": selected_item_name = questionary.select("Select theme to delete:", choices=[item.get("theme_name", f"Theme {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "Notes/Ideas": selected_item_name = questionary.select("Select note/idea to delete:", choices=[item.get("title", f"Note/Idea {i}") for i, item in enumerate(data)]).ask()
                elif section_name == "References": selected_item_name = questionary.select("Select reference to delete:", choices=[item.get("title", f"Reference {i}") for i, item in enumerate(data)]).ask()
                elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                    selected_item_name = questionary.select("Select chapter to delete:", choices=[item.get("chapter_title", f"Chapter {i}") for i, item in enumerate(data)]).ask()
                elif project_type in ["Scientific Article", "Scientific Book"] and section_name in ["Title", "Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion"]:
                    if questionary.confirm("Are you sure you want to delete the content?").ask():
                        data = []
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Content deleted.[/green]")
                        continue
                else:
                    selected_item_name = questionary.select("Select item to delete:", choices=[f"{i}: {json.dumps(item)}" for i, item in enumerate(data)]).ask()

                if selected_item_name:
                    index = -1
                    if section_name == "Characters": index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                    elif section_name == "Plot": index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                    elif section_name == "Worldbuilding": index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                    elif section_name == "Themes": index = next((i for i, item in enumerate(data) if item.get("theme_name") == selected_item_name), None)
                    elif section_name == "Notes/Ideas": index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                    elif section_name == "References": index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                    elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                        index = next((i for i, item in enumerate(data) if item.get("chapter_title") == selected_item_name), None)
                    else: index = int(selected_item_name.split(':')[0])

                    if index is not None and index != -1:
                        del data[index]
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print(f"[green]{delete_action.replace('Delete ', '')} deleted.[/green]")
            
            elif action == view_details_action:
                if section_name == "Characters": view_details(data, "Name")
                elif section_name == "Plot": view_details(data, "name")
                elif section_name == "Worldbuilding": view_details(data, "name")
                elif section_name == "Themes": view_details(data, "theme_name")
                elif section_name == "Notes/Ideas": view_details(data, "title")
                elif section_name == "References": view_details(data, "title")
                elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                    view_details(data, "chapter_title")
            elif action == "Export References":
                self.export_references_menu(project_name)

    def export_references_menu(self, project_name):
        export_format = questionary.select(
            "Select reference export format:",
            choices=["BibTeX", "RIS", "Zotero RDF"]
        ).ask()

        if export_format:
            message = self.project_repository.export_project(project_name, export_format)
            self.console.print(f"[bold green]{message}[/bold green]")