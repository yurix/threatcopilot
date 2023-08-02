import yaml
from datetime import datetime
import pytz
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty)
from time import sleep
from src.config import Config
from src.home.vocabulary_model import Vocabulary, DataFlowTerm
from neomodel import db

config.DATABASE_URL = Config.NEO4J_URL

class DashboardService:
    def __init__(self):
        self.db = db.set_connection(config.DATABASE_URL)

    def count_nodes(self, node_type):
        db.set_connection(config.DATABASE_URL)
        query = f"MATCH (n:{node_type}) RETURN count(n) AS nodeCount"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results[0][0]

    def count_nodes_by_property(self, node_type, property_name, order="DESC"):
        query = f"MATCH (n:{node_type}) RETURN n.{property_name}, COUNT(n) AS count ORDER BY count {order}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        #print (results)
        return results