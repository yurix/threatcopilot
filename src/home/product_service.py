import yaml
from datetime import datetime
import pytz
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty)
from time import sleep
from src.config import Config
from src.home.vocabulary_model import Vocabulary, DataFlowTerm
from neomodel import db

config.DATABASE_URL = Config.NEO4J_URL

class ProductService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)

    def load(self, limit=100):
        #db.set_connection(config.DATABASE_URL)
        node_type = 'Product'
        query = f"MATCH (n:{node_type}) RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        print (meta)
        return results
    def find(self, user_query):
        #db.set_connection(config.DATABASE_URL)
        node_type = 'Product'
        query = f"MATCH (n:{node_type}) WHERE {user_query} RETURN n"
        results, meta = db.cypher_query(query, resolve_objects=False)
        print (meta)
        return results

    def find_product_assets(self, ProductID):
        query = f"MATCH (p:Product {{ ProductID: '{ProductID}' }})-[:related]->(a:Asset) RETURN a"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def bind_product_asset(self, ProductID, AssetID):
        query = f"MATCH (p:Product),(a:Asset) WHERE p.ProductID = '{ProductID}' AND a.Name = '{AssetID}' MERGE (p)-[:related]->(a)"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def delete_product_asset(self, ProductID, AssetID):
        query = f"MATCH (p:Product {{ ProductID: '{ProductID}' }})-[r:related]->(a:Asset) WHERE a.Name = '{AssetID}' DELETE(r)"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def find_product_threatmodels(self, ProductID):
        query = f"MATCH (p:Product {{ ProductID: '{ProductID}' }})-[:related]->(t:ThreatModel) RETURN t"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def bind_product_threatmodel(self, ProductID, threat_model_uid):
        query = f"MATCH (p:Product),(t:ThreatModel) WHERE p.ProductID = '{ProductID}' AND t.threat_model_uid = '{threat_model_uid}' MERGE (p)-[:related]->(t)"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def delete_product_threatmodel(self, ProductID, threat_model_uid):
        query = f"MATCH (p:Product {{ ProductID: '{ProductID}' }})-[r:related]->(t:ThreatModel) WHERE t.threat_model_uid = '{threat_model_uid}' DELETE(r)"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def count_nodes_by_property(self, node_type, property_name, order="DESC"):
        query = f"MATCH (n:{node_type}) RETURN n.{property_name}, COUNT(n) AS count ORDER BY count {order}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        print (results)
        return results