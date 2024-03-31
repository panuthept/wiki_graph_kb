from typing import Dict, List
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Entity:
    id: str | None = None
    name: str | None = None
    description: str | None = None
    aliases: List[str] | None = None
    wikipedia_title: str | None = None
    entity_relations: Dict[str, str] | None = None
    entity_values: Dict[str, str] | None = None
    qualifiers: Dict[str, str] | None = None

    @classmethod
    def from_json(self, data: Dict) -> 'Entity':
        entity_relations = {values["claim_id"]: {"property_id": values["property_id"], "value": values["value"]} for values in data["entity_rels"]}
        entity_values = {values["claim_id"]: {"property_id": values["property_id"], "value": values["value"]} for values in data["entity_values"]}
        qualifiers = defaultdict(dict)
        for values in data["qualifiers"]:
            qualifiers[values["claim_id"]][values["qualifier_id"]] = {"property_id": values["property_id"], "value": values["value"]}

        return Entity(
            id=data["qid"],
            name=data["label"],
            description=data["description"],
            aliases=data["alias"],
            wikipedia_title=data["wikipedia_title"].lower() if data["wikipedia_title"] else None,
            entity_relations=entity_relations,
            entity_values=entity_values,
            qualifiers=qualifiers,
        )
    

@dataclass
class Property:
    id: str
    name: str
    description: str
    entity_relations: Dict[str, str]
    entity_values: Dict[str, str]
    qualifiers: Dict[str, str]

    @classmethod
    def from_json(self, data: Dict) -> 'Property':
        entity_relations = {values["claim_id"]: {"property_id": values["property_id"], "value": values["value"]} for values in data["entity_rels"]}
        entity_values = {values["claim_id"]: {"property_id": values["property_id"], "value": values["value"]} for values in data["entity_values"]}
        qualifiers = defaultdict(dict)
        for values in data["qualifiers"]:
            qualifiers[values["claim_id"]][values["qualifier_id"]] = {"property_id": values["property_id"], "value": values["value"]}

        return Property(
            id=data["qid"],
            name=data["label"],
            description=data["description"],
            entity_relations=entity_relations,
            entity_values=entity_values,
            qualifiers=qualifiers,
        )


@dataclass
class Hyperlink:
    start: int
    length: int
    mention_surface: str
    wikipedia_title: str

    @classmethod
    def from_json(self, data: Dict) -> 'Hyperlink':
        return Hyperlink(
            start=data["start"],
            length=data["length"],
            mention_surface=data["mention_surface"],
            wikipedia_title=data["wikipedia_title"].lower() if data["wikipedia_title"] else None,
        )


@dataclass
class Passage:
    id: str
    text: str
    hyperlinks: List[Hyperlink]
    
    @classmethod
    def from_json(self, data: Dict) -> 'Passage':
        return Passage(
            id=data["id"],
            text=data["text"],
            hyperlinks=[Hyperlink.from_json(h) for h in data["hyperlink"]]
        )


@dataclass
class Document:
    id: str
    title: str
    description: str
    paragraphs: List[Passage]

    @classmethod
    def from_json(self, data: Dict) -> 'Document':
        return Document(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            paragraphs=[Passage.from_json(p) for p in data["paragraph"]]
        )