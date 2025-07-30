import questionary
import requests

def _fetch_reference_from_doi(doi):
    url = f"https://api.crossref.org/v1/works/{doi}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        item = data.get("message", {})

        authors = ", ".join([f"{author.get("given", "")} {author.get("family", "")}" for author in item.get("author", [])])
        year = item.get("published-print", {}).get("date-parts", [[None]])[0][0] or \
               item.get("published-online", {}).get("date-parts", [[None]])[0][0] or "N/A"
        title = item.get("title", [""])[0]
        journal_conference = item.get("container-title", [""])[0]
        doi_url = item.get("URL", "")

        return {
            "authors": authors,
            "year": str(year),
            "title": title,
            "journal_conference": journal_conference,
            "doi_url": doi_url
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching DOI: {e}")
        return None

def get_reference_input(reference_data=None):
    if reference_data is None:
        choice = questionary.select(
            "How do you want to add the reference?",
            choices=["Import from DOI URL", "Enter details manually"]
        ).ask()

        if choice == "Import from DOI URL":
            doi = questionary.text("Enter DOI URL:").ask()
            if doi:
                fetched_data = _fetch_reference_from_doi(doi)
                if fetched_data:
                    print("Reference fetched successfully!")
                    reference_data = fetched_data
                else:
                    print("Could not fetch reference from DOI. Please enter details manually.")
                    choice = "Enter details manually"
            else:
                print("DOI URL cannot be empty. Please enter details manually.")
                choice = "Enter details manually"
        elif choice is None:
            return None # User cancelled

    if reference_data is None or choice == "Enter details manually":
        fields = [
            ("authors", "text"), ("year", "text"), ("title", "text"), 
            ("journal_conference", "text"), ("doi_url", "text")
        ]

        data = reference_data if reference_data else {}
        for field_name, field_type in fields:
            default_value = data.get(field_name, "")
            if field_type == "text":
                answer = questionary.text(f"Enter {field_name.replace('_', ' ').title()}:", default=default_value).ask()
            
            if answer is not None:
                data[field_name] = answer
        return data
    return reference_data

def get_chapter_input(chapter_data=None):
    fields = [
        ("chapter_title", "text"), ("content_summary", "text"), 
        ("key_concepts", "text"), ("status", "select", ["Outline", "Drafting", "Review", "Completed"])
    ]

    data = chapter_data if chapter_data else {}
    for field_name, field_type, *options in fields:
        default_value = data.get(field_name, "")
        if field_type == "text":
            answer = questionary.text(f"Enter {field_name.replace('_', ' ').title()}:", default=default_value).ask()
        elif field_type == "select":
            answer = questionary.select(f"Select {field_name.replace('_', ' ').title()}:", choices=options[0], default=default_value).ask()
        
        if answer is not None:
            data[field_name] = answer
    return data
