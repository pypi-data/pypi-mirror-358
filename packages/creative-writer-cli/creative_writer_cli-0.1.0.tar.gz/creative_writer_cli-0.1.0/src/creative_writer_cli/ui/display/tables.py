from rich.console import Console
from rich.table import Table

console = Console()

def display_character_table(data):
    if not data:
        console.print("[yellow]No characters found.[/yellow]")
        return

    table = Table(title="Characters Summary")
    table.add_column("Name", style="cyan")
    table.add_column("Race", style="magenta")
    table.add_column("Class", style="green")

    for character in data:
        table.add_row(
            character.get("name", "N/A"),
            character.get("race", "N/A"),
            character.get("character_class", "N/A"),
        )
    console.print(table)

def display_plot_table(data):
    if not data:
        console.print("[yellow]No plot points found.[/yellow]")
        return

    table = Table(title="Plot Summary")
    table.add_column("Order", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Status", style="green")

    sorted_data = sorted(data, key=lambda x: int(x.get("timeline_order", 0) or 0) if str(x.get("timeline_order", 0) or 0).isdigit() else 0)

    for plot_point in sorted_data:
        table.add_row(
            plot_point.get("timeline_order", "N/A"),
            plot_point.get("name", "N/A"),
            plot_point.get("status", "N/A"),
        )
    console.print(table)

def display_worldbuilding_table(data):
    if not data:
        console.print("[yellow]No worldbuilding elements found.[/yellow]")
        return

    table = Table(title="Worldbuilding Summary")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")

    for element in data:
        table.add_row(
            element.get("name", "N/A"),
            element.get("type", "N/A"),
        )
    console.print(table)

def display_themes_table(data):
    if not data:
        console.print("[yellow]No themes found.[/yellow]")
        return

    table = Table(title="Themes Summary")
    table.add_column("Theme Name", style="cyan")

    for theme in data:
        table.add_row(theme.get("theme_name", "N/A"))
    console.print(table)

def display_notes_table(data):
    if not data:
        console.print("[yellow]No notes/ideas found.[/yellow]")
        return

    table = Table(title="Notes/Ideas Summary")
    table.add_column("Title", style="cyan")
    table.add_column("Tags", style="magenta")

    for note in data:
        table.add_row(note.get("title", "N/A"), note.get("tags", "N/A"))
    console.print(table)

def display_references_table(data):
    if not data:
        console.print("[yellow]No references found.[/yellow]")
        return

    table = Table(title="References Summary")
    table.add_column("Title", style="cyan")
    table.add_column("Author(s)", style="magenta")
    table.add_column("Year", style="green")

    for ref in data:
        table.add_row(
            ref.get("title", "N/A"),
            ref.get("authors", "N/A"),
            ref.get("year", "N/A"),
        )
    console.print(table)

def display_chapters_table(data):
    if not data:
        console.print("[yellow]No chapters found.[/yellow]")
        return

    table = Table(title="Chapters Summary")
    table.add_column("Chapter Title", style="cyan")
    table.add_column("Status", style="magenta")

    for chapter in data:
        table.add_row(
            chapter.get("chapter_title", "N/A"),
            chapter.get("status", "N/A"),
        )
    console.print(table)
