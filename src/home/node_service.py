import yaml
from datetime import datetime
import pytz
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty)
from time import sleep
from src.config import Config
from neomodel import db
from neo4j import GraphDatabase

config.DATABASE_URL = Config.NEO4J_URL

class NodeService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)
        self.driver = GraphDatabase.driver(Config.NEO4J_URI, auth=(Config.NEO4J_USER, Config.NEO4J_PASS))


    def find(self, node_type, property_name, id):
        query = f"MATCH (n:{node_type}) WHERE n.{property_name} = '{id}' RETURN n"

        with self.driver.session() as session:
            result = session.run(query)
            return result.data()

    def count_nodes_by_property(self, node_type, property_name, order="DESC"):
        query = f"MATCH (n:{node_type}) RETURN n.{property_name}, COUNT(n) AS count ORDER BY count {order}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        print (results)
        return results