# Creative Writer CLI Project Manager

A minimalistic command-line interface (CLI) tool designed to help writers organize their creative projects, capture ideas, and track progress.

## Features

-   **Main Menu:** Navigate easily through options to create, view, or delete projects.
-   **Idea Capture:** Quickly jot down ideas, structured by project type (Novel, Poem, Scientific Article, Scientific Book, Other).
-   **Project Management:** Organize your ideas and content within dedicated project structures.
-   **Templates:** Guided input based on predefined templates for different writing types.
-   **Progress Overview:** See what sections are complete, what's still missing, and the count of items (e.g., characters, plot points) at a glance. Includes a total word count for the project.
-   **Export Project:** Export your entire project content to Markdown, JSON, or TXT formats. (Note: BibTeX, RIS, and Zotero RDF export are currently under development and may not function as expected.)

### Enhanced Novel Project Sections

For 'Novel' projects, the following sections offer structured input, summary tables, and detailed views:

-   **Characters:** Add, edit, and delete characters with fields like Name, Race, Class, Gender, Background, Skills, Equipment, Positive Traits, and Negative Traits.
-   **Plot:** Manage plot points with fields for Name, Details, Timeline/Order, Characters Involved, Location, and Status.
-   **Worldbuilding:** Organize world elements by Name, Type (Location, Culture, Technology, Magic System, Other), Description, History/Lore, and Connections.
-   **Themes:** Define themes with fields for Theme Name, Description, Motifs/Symbols, and Related Elements.
-   **Notes/Ideas:** Capture general notes and ideas with a Title, Content, and Tags for easy categorization.

### Scientific Article Project Enhancements

-   **Dynamic Section Menus:** Menus adapt to the specific needs of scientific article sections.
-   **Content Snippets in Overview:** For sections like Title, Abstract, Introduction, Methods, Results, and Discussion, the project overview displays a snippet of the content.
-   **References Management:** A structured section for managing references with fields for Author(s), Year, Title, Journal/Conference, and DOI/URL. Now includes the ability to import reference data directly from a DOI URL using the CrossRef API.

## Development Status

**Please Note:** The 'Scientific Book' project type is currently under active development. While basic functionality is available, some sections may still be generic or lack the full structured input and detailed views present in the 'Novel' project type.

## Known Errors

No errors currently known.

## Tech Stack

-   **Language:** Python
-   **CLI Libraries:** `rich` (for rich text and tables), `questionary` (for interactive prompts)
-   **Data Storage:** Local JSON files

## Installation and Usage

To run the Creative Writer CLI Project Manager, follow these steps:

1.  **Clone or download the project:**
    Obtain the project files and navigate into the `creative_writer_cli_project_manager` directory.

2.  **Run the application:**
    Execute the provided `run.sh` script. This script will automatically create a Python virtual environment, install all necessary dependencies, and then start the CLI application.
    ```bash
    ./run.sh
    ```

    *(If `./run.sh` does not work, you might need to give it execute permissions first: `chmod +x ./run.sh`)*

## Portability

This project is designed to be fully portable. The `run.sh` script dynamically determines the project's location, meaning you can place the `creative_writer_cli_project_manager` folder anywhere on your system, and the application will run correctly without needing to modify any internal paths.

## Example Usage

Once the application starts, you will be presented with a main menu:

```
What do you want to do? 
❯ Create New Project
  View Existing Projects
  Delete Project
  Exit
```

Follow the prompts to create a new project, select its type, and start organizing your writing. For 'Novel' projects, explore the structured sections for Characters, Plot, Worldbuilding, Themes, and Notes/Ideas. For 'Scientific Article' projects, you can begin adding content to its specific sections and manage references.

## Project Structure

```
creative_writer_cli_project_manager/
├── .git/                               # Git version control directory
├── src/                                # Source code directory
│   ├── creative_writer_cli/            # Core application logic
│   │   ├── core/                       # Core logic/models
│   │   ├── data/                       # Data handling modules
│   │   │   └── repositories/           # Data repositories
│   │   │       ├── __init__.py
│   │   │       ├── json_store.py       # Handles low-level JSON file operations
│   │   │       └── project_repository.py # Manages project data (CRUD)
│   │   ├── ui/                         # User Interface modules
│   │   │   ├── cli_app.py              # Main CLI application logic and menus
│   │   │   ├── display/                # Modules for displaying data (tables, views)
│   │   │   │   ├── tables.py
│   │   │   │   └── views.py
│   │   │   ├── wizards/                # Modules for interactive user input (wizards)
│   │   │   │   ├── generic_wizards.py
│   │   │   │   ├── novel_wizards.py
│   │   │   │   └── scientific_wizards.py
│   │   │   ├── ascii_art.py
│   │   │   ├── display.py
│   │   │   └── wizards.py
│   │   └── utils/                      # Utility modules
│   │       ├── export_formatter.py
│   │       ├── path_helpers.py         # Utility for constructing file paths
│   │       ├── reference_export_formatter.py
│   │       └── word_counter.py         # Logic for calculating word counts
│   ├── main.py                         # Application entry point
│   └── projects/                       # Directory for storing user projects (initially empty)
├── .gitattributes                      # Git attributes configuration
├── .gitignore                          # Specifies intentionally untracked files to ignore
├── LICENSE                             # Project license file
├── README.md                           # Project documentation

├── run.sh                              # Script to set up environment and run the application
└── venv/                               # Python virtual environment (created by run.sh)
```
