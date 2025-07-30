import os
import json
import shutil
from datetime import datetime

from ...core.models import Character, PlotPoint, WorldbuildingElement, Theme, NoteIdea, Reference, Chapter, Project
from ...core.templates import TEMPLATES
from .json_store import JsonStore
from ...utils import export_formatter, reference_export_formatter
from ...utils.word_counter import calculate_word_count

from ...utils.path_helpers import get_section_filepath

class ProjectRepository:
    def __init__(self, base_dir="projects"):
        self.base_dir = base_dir
        self.json_store = JsonStore(base_dir)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def create_project(self, project_name: str, project_type: str) -> tuple[bool, str]:
        project_path = os.path.join(self.base_dir, project_name)
        if os.path.exists(project_path):
            return False, "Project with this name already exists."

        os.makedirs(project_path)

        meta_data = {"name": project_name, "type": project_type, "created": datetime.now().isoformat()}
        self.json_store.write_json(os.path.join(project_name, "meta.json"), meta_data)

        for section in TEMPLATES[project_type]:
            self.json_store.write_json(get_section_filepath(project_name, section), [])
        
        return True, f"Project '{project_name}' of type '{project_type}' created successfully."

    def get_projects(self) -> list[str]:
        # List directories directly within the base_dir
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def delete_project(self, project_name: str) -> tuple[bool, str]:
        project_path = os.path.join(self.base_dir, project_name)
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
            return True, f"Project '{project_name}' deleted."
        return False, "Project not found."

    def get_project_meta(self, project_name: str) -> dict:
        return self.json_store.read_json(os.path.join(project_name, "meta.json"))

    def get_project_sections(self, project_name: str) -> list[str]:
        meta = self.get_project_meta(project_name)
        return TEMPLATES[meta['type']]

    def get_section_content(self, project_name: str, section_name: str) -> list[dict]:
        return self.json_store.read_json(get_section_filepath(project_name, section_name))

    def save_section_content(self, project_name: str, section_name: str, data: list[dict]):
        self.json_store.write_json(get_section_filepath(project_name, section_name), data)

    def export_project(self, project_name: str, export_format: str) -> str:
        project_abs_path = os.path.join(self.base_dir, project_name)
        output_content = ""

        if export_format == "Markdown" or export_format == "TXT":
            output_content += f"# {project_name}\n\n"
            project_meta = self.get_project_meta(project_name)
            project_type = project_meta.get('type')
            sections = self.get_project_sections(project_name)

            for section_name in sections:
                content = self.get_section_content(project_name, section_name)
                
                if section_name == "Characters":
                    output_content += export_formatter.format_characters_to_markdown(content)
                elif section_name == "Plot":
                    output_content += export_formatter.format_plot_points_to_markdown(content)
                elif section_name == "Worldbuilding":
                    output_content += export_formatter.format_worldbuilding_to_markdown(content)
                elif section_name == "Themes":
                    output_content += export_formatter.format_themes_to_markdown(content)
                elif section_name == "Notes/Ideas":
                    output_content += export_formatter.format_notes_to_markdown(content)
                elif section_name == "References":
                    output_content += export_formatter.format_references_to_markdown(content)
                elif project_type == "Scientific Book" and section_name in ["Chapter 1", "Chapter 2", "Chapter 3", "Conclusion"]:
                    output_content += export_formatter.format_chapters_to_markdown(content)
                elif project_type in ["Scientific Article", "Scientific Book"] and section_name in ["Title", "Abstract", "Introduction", "Methods", "Results", "Discussion"]:
                    output_content += export_formatter.format_generic_text_section_to_markdown(content, section_name)
                else:
                    # Fallback for any other sections not explicitly handled, or generic sections
                    if content:
                        output_content += f"## {section_name}\n\n"
                        if isinstance(content, list) and len(content) == 1 and isinstance(content[0], str):
                            output_content += f"{content[0]}\n\n"
                        else:
                            output_content += f"```json\n{json.dumps(content, indent=2)}\n```\n\n"
                    else:
                        output_content += f"## {section_name}\n\nNo content found.\n\n"

            if export_format == "TXT":
                # Convert Markdown to plain text for TXT export
                # This is a very basic conversion, a proper Markdown parser would be better
                output_content = output_content.replace("## ", "").replace("# ", "").replace("**", "").replace("```json", "").replace("```", "").replace("\n", "\n").replace("- ", "")

        elif export_format == "JSON":
            all_data = {}
            project_meta = self.get_project_meta(project_name)
            all_data["meta"] = project_meta
            sections = self.get_project_sections(project_name)
            for section_name in sections:
                content = self.get_section_content(project_name, section_name)
                all_data[section_name.lower().replace(' ', '_')] = content
            output_content = json.dumps(all_data, indent=4)
        elif export_format in ["BibTeX", "RIS", "Zotero RDF"]:
            references_content = self.get_section_content(project_name, "References")
            if not references_content:
                return f"No references found in project '{project_name}' to export to {export_format}."

            formatted_references = []
            for ref in references_content:
                if export_format == "BibTeX":
                    formatted_references.append(reference_export_formatter.format_to_bibtex(ref))
                elif export_format == "RIS":
                    formatted_references.append(reference_export_formatter.format_to_ris(ref))
                elif export_format == "Zotero RDF":
                    formatted_references.append(reference_export_formatter.format_to_zotero_rdf(ref))
            output_content = "\n\n".join(formatted_references)

        export_extension = export_format.lower()
        if export_extension == "markdown":
            export_extension = "md"
        elif export_extension == "bibtex":
            export_extension = "bib"
        elif export_extension == "ris":
            export_extension = "ris"
        elif export_extension == "zotero rdf":
            export_extension = "rdf"
        export_filename = f"{project_name}_export.{export_extension}"
        if export_format in ["BibTeX", "RIS", "Zotero RDF"]:
            export_filename = f"{project_name}_references_export.{export_extension}"
        with open(export_filename, "w") as f:
            f.write(output_content)
        return f"Project exported to {export_filename}"

    def rename_project(self, old_project_name: str, new_project_name: str) -> tuple[bool, str]:
        old_project_path = os.path.join(self.base_dir, old_project_name)
        new_project_path = os.path.join(self.base_dir, new_project_name)

        if not os.path.exists(old_project_path):
            return False, "Original project not found."

        if os.path.exists(new_project_path):
            return False, "A project with the new name already exists."

        try:
            shutil.move(old_project_path, new_project_path)

            # Update the project name in the meta.json file
            meta_filepath = os.path.join(new_project_path, "meta.json")
            meta_data = self.json_store.read_json(os.path.join(new_project_name, "meta.json")) # Read from new path
            meta_data["name"] = new_project_name
            self.json_store.write_json(os.path.join(new_project_name, "meta.json"), meta_data) # Write to new path

            return True, f"Project '{old_project_name}' renamed to '{new_project_name}' successfully."
        except Exception as e:
            return False, f"Error renaming project: {e}"

    def get_project_word_count(self, project_name: str) -> int:
        project_meta = self.get_project_meta(project_name)
        sections = self.get_project_sections(project_name)
        return calculate_word_count(project_name, project_meta, sections, self.get_section_content)
