import yaml
from datetime import datetime
import pytz
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty)
from time import sleep
from src.config import Config
from src.home.vocabulary_model import Vocabulary, DataFlowTerm
from neomodel import db

config.DATABASE_URL = Config.NEO4J_URL

class ThreatService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)

    def load(self, limit=100, resolve_objects=False):
        node_type = 'Threat'
        query = f"MATCH (n:{node_type}) RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def find(self, user_query, resolve_objects=False):
        node_type = 'Threat'
        query = f"MATCH (n:{node_type}) WHERE {user_query} RETURN n"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def find_by_id(self, ThreatID, resolve_objects=False):
        query = f"MATCH (t:Threat {{ ThreatID: '{ThreatID}' }}) RETURN t"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results
    
    def find_threat_weaknesses(self, ThreatID, resolve_objects=False):
        query = f"MATCH (t:Threat {{ ThreatID: '{ThreatID}' }})-[:related]->(w:Weakness) RETURN w"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def bind_threat_weakness(self, threat_name, weakness_name, resolve_objects=False):
        query = f"MATCH (o:Threat),(d:Weakness) WHERE o.ThreatID = '{threat_name}' AND d.Name = '{weakness_name}' MERGE (o)-[:related]->(d)"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def delete_threat_weakness(self, ThreatID, weakness_name, resolve_objects=False):
        query = f"MATCH (t:Threat {{ ThreatID: '{ThreatID}' }})-[r:related]->(w:Weakness) WHERE w.Name = '{weakness_name}' DELETE(r)"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def count_nodes_by_property(self, node_type, property_name, order="DESC", resolve_objects=False):
        query = f"MATCH (n:{node_type}) RETURN n.{property_name}, COUNT(n) AS count ORDER BY count {order}"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def create(self, threatid, catalog, category, stride, name, description, cve, resolve_objects=False):
        if cve is not None:
            cve = cve.split(",")
        else:
            cve = []
        
        query = f"CREATE (t:Threat {{ ThreatID: '{threatid}', Catalog: '{catalog}', ThreatCategory: '{category}', STRIDE: '{stride}', Name: '{name}', Description: '{description}', CVEExample: '[]'}}) "
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def delete(self, ThreatID, resolve_objects=False):
        query = f"MATCH (p:Threat {{ ThreatID: '{ThreatID}' }}) DETACH DELETE(p)"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results