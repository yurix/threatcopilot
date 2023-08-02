import yaml
from datetime import datetime
import pytz
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty)
from time import sleep
from src.config import Config
from src.home.vocabulary_model import Vocabulary, DataFlowTerm
from neomodel import db

config.DATABASE_URL = Config.NEO4J_URL

class ElementService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)

    def load(self, node_type, limit=100):
        query = f"MATCH (n:{node_type}) RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def find(self, node_type, user_query):
        query = f"MATCH (n:{node_type}) WHERE {user_query} RETURN n"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
    
    def bind_element_threat(self, element_type, element_id, threat_id):
        query = f"MATCH  (e:{element_type} {{ uid: '{element_id}'}}), (t:Threat {{ ThreatID: '{threat_id}' }}) MERGE (e)-[:related]->(t)"
        print(query)
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
    
    def find_element_threats(self, element_type, uid,resolve_objects=False):
        query = f"MATCH (e:{element_type} {{ uid: '{uid}' }})-[:related]->(t:Threat) RETURN t"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def delete_element_threat(self, element_type, element_id, threat_id):
        query = f"MATCH  (e:{element_type} {{ uid: '{element_id}'}})-[r:related]->(t:Threat) WHERE t.ThreatID = '{threat_id}' DELETE(r)"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def bind_element_asset(self, element_type, element_id, asset_id):
        query = f"MATCH  (e:{element_type} {{ uid: '{element_id}'}}), (a:Asset {{ Name: '{asset_id}' }}) MERGE (e)-[:related]->(a)"
        print(query)
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
    
    def find_element_assets(self, element_type, uid):
        query = f"MATCH (e:{element_type} {{ uid: '{uid}' }})-[:related]->(a:Asset) RETURN a"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def delete_element_asset(self, element_type, element_id, threat_id):
        query = f"MATCH  (e:{element_type} {{ uid: '{element_id}'}})-[r:related]->(a:Asset) WHERE a.Name = '{threat_id}' DELETE(r)"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def find_element_inputs(self, element_full_name, resolve_objects=False):
        query = f"MATCH (e:Element {{ full_name: '{element_full_name}' }})<-[o:CONNECTS_IN]-(d:DataFlow) RETURN d"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def find_element_outputs(self, element_full_name, resolve_objects=False):
        query = f"MATCH (e:Element {{ full_name: '{element_full_name}' }})-[o:CONNECTS_OUT]->(d:DataFlow) RETURN d"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results

    def count_nodes_by_property(self, node_type, property_name, order="DESC"):
        query = f"MATCH (n:{node_type}) RETURN n.{property_name}, COUNT(n) AS count ORDER BY count {order}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def delete(self, ThreatID):
        query = f"MATCH (p:Threat {{ ThreatID: '{ThreatID}' }}) DETACH DELETE(p)"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
