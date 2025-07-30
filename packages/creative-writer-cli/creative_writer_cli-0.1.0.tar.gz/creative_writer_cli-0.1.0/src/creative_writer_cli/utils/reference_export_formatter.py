def format_to_bibtex(reference):
    # Basic BibTeX formatting for an article
    # Assumes 'journal_conference' is the journal title
    # You might need to refine this based on specific BibTeX entry types and fields
    authors = reference.get("authors", "").replace(" and ", " and ")
    title = reference.get("title", "")
    year = reference.get("year", "")
    journal = reference.get("journal_conference", "")
    doi = reference.get("doi_url", "")

    bibtex_entry = f"""@article{{{reference.get("title", "").replace(" ", "").replace(":", "")}{year},
    author = {{{authors}}},
    title = {{{title}}},
    journal = {{{journal}}},
    year = {{{year}}},
    doi = {{{doi}}}
}}"""
    return bibtex_entry

def format_to_ris(reference):
    # Basic RIS formatting
    ris_entry = ""
    ris_entry += "TY  - JOUR\n"
    for author in reference.get("authors", "").split(" and "): # Assuming "and" separates authors
        ris_entry += f"AU  - {author.strip()}\n"
    ris_entry += f"PY  - {reference.get("year", "")}\n"
    ris_entry += f"TI  - {reference.get("title", "")}\n"
    ris_entry += f"JO  - {reference.get("journal_conference", "")}\n"
    ris_entry += f"DO  - {reference.get("doi_url", "")}\n"
    ris_entry += "ER  - \n"
    return ris_entry

def format_to_zotero_rdf(reference):
    # Zotero RDF is more complex and typically involves XML/RDF serialization.
    # For a simple text export, we'll provide a basic representation.
    # A full implementation would require an RDF library.
    rdf_entry = f"""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:bib="http://purl.org/net/biblio#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
  <bib:Article rdf:about="urn:doi:{reference.get("doi_url", "")}">
    <dc:title>{reference.get("title", "")}</dc:title>
    <dc:creator>{reference.get("authors", "")}</dc:creator>
    <dc:date>{reference.get("year", "")}</dc:date>
    <bib:journal>{reference.get("journal_conference", "")}</bib:journal>
    <bib:doi>{reference.get("doi_url", "")}</bib:doi>
  </bib:Article>
</rdf:RDF>"""
    return rdf_entry
