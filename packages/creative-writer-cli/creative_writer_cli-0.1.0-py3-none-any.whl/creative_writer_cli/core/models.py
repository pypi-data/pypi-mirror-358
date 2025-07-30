from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Character:
    name: str
    race: Optional[str] = None
    character_class: Optional[str] = None
    gender: Optional[str] = None
    background: Optional[str] = None
    skills: Optional[str] = None
    equipment: Optional[str] = None
    positive_traits: Optional[str] = None
    negative_traits: Optional[str] = None

@dataclass
class PlotPoint:
    name: str
    details: Optional[str] = None
    timeline_order: Optional[str] = None
    characters_involved: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

@dataclass
class WorldbuildingElement:
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    history_lore: Optional[str] = None
    connections: Optional[str] = None

@dataclass
class Theme:
    theme_name: str
    description: Optional[str] = None
    motifs_symbols: Optional[str] = None
    related_elements: Optional[str] = None

@dataclass
class NoteIdea:
    title: str
    content: Optional[str] = None
    tags: Optional[str] = None

@dataclass
class Reference:
    title: str
    authors: Optional[str] = None
    year: Optional[str] = None
    journal_conference: Optional[str] = None
    doi_url: Optional[str] = None

@dataclass
class Chapter:
    chapter_title: str
    content_summary: Optional[str] = None
    key_concepts: Optional[str] = None
    status: Optional[str] = None

@dataclass
class ProjectSection:
    name: str
    content: List[Any] = field(default_factory=list)

@dataclass
class Project:
    name: str
    type: str
    created: str
    sections: Dict[str, ProjectSection] = field(default_factory=dict)
