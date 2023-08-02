import yaml
from datetime import datetime
import pytz
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty)
from time import sleep
from src.config import Config
from src.home.vocabulary_model import Vocabulary, DataFlowTerm
from neomodel import db

config.DATABASE_URL = Config.NEO4J_URL

class WeaknessService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)

    def load(self, limit=100):
        #db.set_connection(config.DATABASE_URL)
        node_type = 'Weakness'
        query = f"MATCH (n:{node_type}) RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        print (meta)
        return results
    
    def find_weakness_attacks(self, CWE):
        query = f"MATCH (w:Weakness {{ Name: '{CWE}' }})-[:RelatedAttackPattern]->(att:Attack) RETURN att"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def find_weakness_by_likelihood_of_attack(self, likelihood):
        query = f"MATCH (w:Weakness)-[:RelatedAttackPattern]->(att:Attack) Where att.Likelihood_Of_Attack = '{likelihood}' RETURN w"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
    
    def find_weakness_by_likelihood_of_exploits(self, likelihood_of_exploit):
        query = f"MATCH (w:Weakness {{ Likelihood_Of_Exploit: '{likelihood_of_exploit}' }}) RETURN w"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def find(self, user_query):
        node_type = 'Weakness'
        query = f"MATCH (n:{node_type}) WHERE {user_query} RETURN n"
        results, meta = db.cypher_query(query, resolve_objects=False)
        print (meta)
        return results

    def count_nodes_by_property(self, node_type, property_name, order="DESC"):
        query = f"MATCH (n:{node_type}) RETURN n.{property_name}, COUNT(n) AS count ORDER BY count {order}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        print (results)
        return results