import os
from creative_writer_cli.data.repositories.project_repository import ProjectRepository
from creative_writer_cli.ui.cli_app import CLIApp

def main():
    # Determine the absolute path to the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(script_dir) # Go up one level from src
    
    # Pass the project root directory to the ProjectRepository
    project_repository = ProjectRepository(base_dir=os.path.join(project_root_dir, "projects"))
    
    app = CLIApp(project_repository)
    app.main_menu()

if __name__ == "__main__":
    main()