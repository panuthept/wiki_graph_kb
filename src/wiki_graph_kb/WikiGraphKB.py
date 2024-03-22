import os
import json
from tqdm import tqdm
from typing import List, Set
from neo4j import GraphDatabase
from wiki_graph_kb.data_types import Entity, Document, Property


class WikiGraphKB:
    def __init__(self, uri, auth, collection: str = "neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.driver.verify_connectivity()
        self.collection = collection

    # def new_collection(self, collection: str) -> None:
    #     with self.driver.session(database="system") as session:
    #         session.run(f"CREATE DATABASE {collection}")
    #     self.collection = collection

    # def select_collection(self, collection: str) -> None:
    #     self.collection = collection
        
    def get_locked_entities(self) -> Set[str]:
        transactions = kb.query("SHOW TRANSACTIONS YIELD parameters, currentQuery")
        transactions = [t for t in transactions if "e:Entity" in t["currentQuery"]]

        locked_entities = set()
        for t in transactions:
            if "id" in t["parameters"]:
                locked_entities.add(t["parameters"]["id"])
            if "sub_id" in t["parameters"]:
                locked_entities.add(t["parameters"]["sub_id"])
            if "obj_id" in t["parameters"]:
                locked_entities.add(t["parameters"]["obj_id"])
        return locked_entities

    def update_collection(
            self, 
            wikipedia_corpus_path: str | None = None, 
            wikidata_corpus_path: str | None = None,
            wikipedia_range: tuple[int, int] = (0, -1),
            wikidata_range: tuple[int, int] = (0, -1),

    ) -> None:
        # Get paths for wikipedia's documents
        wikipedia_file_paths = []
        if wikipedia_corpus_path is not None:
            for folder in tqdm(os.listdir(wikipedia_corpus_path)):
                if os.path.isdir(os.path.join(wikipedia_corpus_path, folder)):
                    for file in os.listdir(os.path.join(wikipedia_corpus_path, folder)):
                        if file.startswith("wiki_"):
                            wikipedia_file_paths.append(os.path.join(wikipedia_corpus_path, folder, file))
            wikipedia_file_paths = sorted(wikipedia_file_paths)
            wikipedia_file_paths = wikipedia_file_paths[wikipedia_range[0]:wikipedia_range[1]] if wikipedia_range[1] != -1 else wikipedia_file_paths[wikipedia_range[0]:]

        # Get paths for wikidata's entities and properties
        entities_file_paths = []
        if wikidata_corpus_path is not None:
            properties_file_paths = [os.path.join(wikidata_corpus_path, "properties", file) for file in os.listdir(os.path.join(wikidata_corpus_path, "properties")) if file.endswith(".jsonl")]
            entities_file_paths = sorted([os.path.join(wikidata_corpus_path, "entities", file) for file in os.listdir(os.path.join(wikidata_corpus_path, "entities")) if file.endswith(".jsonl")])
            entities_file_paths = entities_file_paths[wikidata_range[0]:wikidata_range[1]] if wikidata_range[1] != -1 else entities_file_paths[wikidata_range[0]:]

            # Get property mapping qid to name
            properties = {}
            for file_path in tqdm(properties_file_paths):
                with open(file_path, "r") as f:
                    for line in f:
                        property = Property.from_json(json.loads(line))
                        properties[property.id] = property
                    
        # # Create contrains
        # self.query(
        #     """
        #     CREATE CONSTRAINT FOR (d:Document) REQUIRE (d.id) IS UNIQUE
        #     CREATE CONSTRAINT FOR (p:Passage) REQUIRE (p.id) IS UNIQUE
        #     CREATE CONSTRAINT FOR (e:Entity) REQUIRE (e.id) IS UNIQUE
        #     CREATE CONSTRAINT FOR (v:Value) REQUIRE (v.value) IS UNIQUE
        #     """
        # )
                    
        # # Create indexes
        # self.query(
        #     """
        #     CREATE INDEX FOR (d:Document) ON (d.title)
        #     CREATE INDEX FOR (e:Entity) ON (e.name)
        #     """
        # )

        # Create graph for wikipedia corpus
        for file_path in tqdm(wikipedia_file_paths):
            with open(file_path, "r") as f:
                for line in f:
                    doc = Document.from_json(json.loads(line))
                    # Create a document node
                    self.query(
                        """
                        MERGE (d:Document {id: $id, title: $title, description: $description})
                        """,
                        {
                            "id": doc.id,
                            "title": doc.title,
                            "description": doc.description,
                        }
                    )

        # Create graph for wikidata corpus
        for file_path in tqdm(entities_file_paths):
            with open(file_path, "r") as f:
                for line in f:
                    entity = Entity.from_json(json.loads(line))
                    if entity.name is None:
                        continue
                    # Create an entity node and links to the document
                    if entity.wikipedia_title:
                        self.query(
                            """
                            MERGE (e:Entity {id: $id})
                            SET e.name = $name 
                            SET e.description = $description
                            SET e.aliases = $aliases
                            WITH e
                            MATCH (d:Document {title: $wikipedia_title})
                            MERGE (e)-[:DESCRIBED_IN]->(d)
                            """,
                            {
                                "id": entity.id,
                                "name": entity.name,
                                "description": entity.description,
                                "aliases": entity.aliases,
                                "wikipedia_title": entity.wikipedia_title,
                            }
                        )
                    else:
                        self.query(
                            """
                            MERGE (e:Entity {id: $id})
                            SET e.name = $name 
                            SET e.description = $description
                            SET e.aliases = $aliases
                            """,
                            {
                                "id": entity.id,
                                "name": entity.name,
                                "description": entity.description,
                                "aliases": entity.aliases,
                            }
                        )
                    for claim_id, values in entity.entity_relations.items():
                        self.query(
                            """
                            MATCH (sub_e:Entity {id: $sub_id})
                            MERGE (obj_e:Entity {id: $obj_id})
                            MERGE (sub_e)-[:%s {claim_id: $claim_id, name: $name}]->(obj_e)
                            """ % values["property_id"],
                            {
                                "sub_id": entity.id,
                                "obj_id": values["value"],
                                "claim_id": claim_id,
                                "name": properties[values["property_id"]].name,
                            }
                        )
                    for claim_id, values in entity.entity_values.items():
                        self.query(
                            """
                            MATCH (sub_e:Entity {id: $sub_id})
                            MERGE (v:Value {value: $value})
                            MERGE (sub_e)-[:%s {claim_id: $claim_id, name: $name}]->(v)
                            """ % values["property_id"],
                            {
                                "sub_id": entity.id,
                                "value": values["value"],
                                "claim_id": claim_id,
                                "name": properties[values["property_id"]].name,
                            }
                        )
                    
        # Create graph for wikipedia corpus
        for file_path in tqdm(wikipedia_file_paths):
            with open(file_path, "r") as f:
                for line in f:
                    doc = Document.from_json(json.loads(line))
                    # Create passage nodes
                    for paragraph in doc.paragraphs:
                        self.query(
                            """
                            MATCH (d:Document {id: $doc_id})
                            MERGE (p:Passage {id: $passage_id, text: $text})
                            MERGE (d)-[:CONTAINS]->(p)
                            """,
                            {
                                "passage_id": paragraph.id,
                                "doc_id": doc.id,
                                "text": paragraph.text,
                            }
                        )
                        # Create links to entities
                        for hyperlink in paragraph.hyperlinks:
                            self.query(
                                """
                                MATCH (p:Passage {id: $passage_id})
                                MATCH (d:Document {title: $document_title})
                                MERGE (p)-[:MENTIONS {start: $start, mention_surface: $mention_surface}]->(d)
                                WITH d, p
                                MATCH (e:Entity)-[:DESCRIBED_IN]->(d)
                                MERGE (p)-[:MENTIONS {start: $start, mention_surface: $mention_surface}]->(e)
                                """,
                                {
                                    "passage_id": paragraph.id,
                                    "document_title": hyperlink.wikipedia_title,
                                    "start": hyperlink.start,
                                    "mention_surface": hyperlink.mention_surface,
                                }
                            )

    def query(self, query: str, parameters: dict | None = None) -> List[dict]:
        with self.driver.session(database=self.collection) as session:
            return session.run(query, parameters).data()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", type=str, default="bolt://localhost:7687") # bolt://ist-compute-1-001:7687
    parser.add_argument("--username", type=str, default="neo4j")
    parser.add_argument("--password", type=str, default="panuthept")
    args = parser.parse_args()

    URI = args.uri
    AUTH = (args.username, args.password)
    kb = WikiGraphKB(uri=URI, auth=AUTH)
    # response = kb.query("MATCH (n) RETURN count(n)")
    response = kb.get_locked_entities()
    print(response)