import yaml
from datetime import datetime
import pytz
from neomodel import config
from time import sleep
from src.config import Config
from src.home.vocabulary_model import Vocabulary, DataFlowVocabulary, StoreVocabulary, InteractorVocabulary, ProcessVocabulary, DataFlowTerm, StoreTerm, InteractorTerm, ProcessTerm
from neomodel import db

config.DATABASE_URL = Config.NEO4J_URL
from src.home.threatmodel_service import ThreatModelService
from src.home.element_service import ElementService
import src.home.util as util
import src.home.util_similarity as util_similarity


from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from scipy.spatial import distance


class Node:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class Tree:
    def __init__(self):
        self.root = None

    def set_root(self, root_node):
        self.root = root_node
    
    def get_node_by_name(self, root_node, node_name):
        if root_node is not None:
            for child in root_node.children:
                if child.name == node_name:
                    return child
                else:
                    deep_search = self.get_node_by_name(child,node_name)
                    if deep_search is not None:
                        return deep_search
        return None
    
    def depth(self):
        return calculate_depth(self.root)
    
    def calculate_depth(self, node):
        if node is None:
            return 0
        else:
            max_depth = 0
            for child in node.children:
                child_depth = self.calculate_depth(child)
                max_depth = max(max_depth, child_depth)
            return max_depth + 1
    def calculate_weights(self):
        return self.build_wtree(self.root,0,[])
    
    def build_wtree(self, node, level, w_array):
        if node is None:
            return w_array
        else:
            for child in node.children:
                w_array.append(level)
                w_array = self.build_wtree(child, level + 1, w_array)
            return w_array

    def display_tree(self, node, level=0):
        if node is not None:
            print("  " * level + str(node.name))
            for child in node.children:
                self.display_tree(child, level + 1)
    
    def tree2array(self, term, arr=[], ws=[], node=None, level=0):
        if node is None:
            arr = []
            ws = []
            node = self.root
            for child in node.children:
                self.tree2array(term, arr, ws, child, level + 1)
            arr = arr[::-1]
            ws = ws[::-1]
            return 0, arr
        
        if node is not None:
            value = 0
            if node.name.lower() == term.lower():
                value = 1
                        
            for child in node.children:
                child_value, arr = self.tree2array(term, arr, ws, child, level + 1)
                if child_value == 1: 
                    value = 1
            ws.append(level)
            arr.append(value)
            return value, arr

class ThreatUnit:
    def __init__(self, uid, name, full_name, element_type, term, tree_term, dataflow_tree, brown_ic, input_terms, output_terms):
        self.uid = uid
        self.name = name
        self.full_name = full_name
        self.element_type = element_type
        self.tree_term = tree_term
        self.dataflow_tree = dataflow_tree
        self.term = term
        self.input_terms = input_terms
        self.output_terms = output_terms
        self.brown_ic = brown_ic

    def similarity(self, another_threat_unit): 
        aname = another_threat_unit.name
        sim_name = self.sim_name(self.name,aname)
        print( " Similarity name = " + str(sim_name))
        sim_term = self.sim_term(self.term, another_threat_unit.term)
        print( "Similarity term = " + str(sim_term))
        sim_io = self.sim_input_and_outputs(self.input_terms, another_threat_unit.input_terms, self.output_terms, another_threat_unit.output_terms)
        print( " Similarity io = " + str(sim_io))
        return  sim_name, sim_term, sim_io, (3 * sim_name + 7 * sim_term + 5 * sim_io)/15
    
    def sim_name(self, name_a, name_b):
        return util_similarity.compound_name_similarity(name_a,name_b)

    def sim_term(self, term_a, term_b):
        x, vector_a = self.tree_term.tree2array(term_a)
        y, vector_b = self.tree_term.tree2array(term_b)

        weights = self.tree_term.calculate_weights()
        cosine_sim = distance.cosine(vector_a,vector_b,weights)      

        return (1-cosine_sim)
    def sim_dataflow_term(self, term_a, term_b):
        x, vector_a = self.dataflow_tree.tree2array(term_a)
        y, vector_b = self.dataflow_tree.tree2array(term_b)
        weights = self.dataflow_tree.calculate_weights()

        cosine_sim = distance.cosine(vector_a,vector_b,weights)      

        return (1-cosine_sim)
    
    def sim_input_and_outputs(self, te1, te2, ts1, ts2):
        input_max = 0
        n = len(te1)
        m = len(te2)
        input_sim = 0
        if n > 0:
            for te1_x in te1:
                for te2_y in te2:
                    sim_value = self.sim_dataflow_term(te1_x, te2_y)
                    if sim_value > input_max:
                        input_max = sim_value
                input_sim = input_sim + input_max
            
            input_sim = input_sim / n

        output_n = len(ts1)
        output_m = len(ts2)
        output_sim = 0
        output_max = 0

        if output_n > 0:
            for ts1_x in ts1:
                for ts2_y in ts2:
                    sim_out_value = self.sim_dataflow_term(ts1_x, ts2_y)
                    if sim_out_value > output_max:
                        output_max = sim_out_value
                output_sim = output_sim + output_max
            
            output_sim = output_sim / output_n
        
        return (input_sim + output_sim)/2
    
    def __str__(self):
        return f"[Name: {self.name}, Element Type: {self.element_type}, Term: {self.term}]"



class RecommendationService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)
        self.brown_ic = wordnet_ic.ic('ic-brown.dat')
        self.store_tree = self.get_tree('StoreTerm',"CHILD_OF_STORE_TERM")
        self.dataflow_tree = self.get_tree('DataFlowTerm',"CHILD_OF_DATAFLOW_TERM")
        self.process_tree = self.get_tree('ProcessTerm',"CHILD_OF_PROCESS_TERM")
        self.interactor_tree = self.get_tree('InteractorTerm',"CHILD_OF_INTERACTOR_TERM")
      

    def build_child_nodes(self, node_type, relation, parent):
        query = f"MATCH (t:{node_type})-[:{relation}]->(ts:{node_type}) WHERE t.name = '{parent.name}' RETURN ts"
        results, columns = db.cypher_query(query, resolve_objects=True)
        for terms in results: 
            if terms is None:
                return
            term = terms[0]
            new_node = Node(term.id,term.name)
            parent.add_child(new_node)
            self.build_child_nodes(node_type,relation,new_node)
            
    def get_tree(self, node_type, relation):
        tree = Tree()
        root_node = Node(0,'Store')
        tree.set_root(root_node)
        query = f"MATCH (t:{node_type}) WHERE NOT EXISTS(()-[:{relation}]->(t:{node_type})) RETURN t"
        results, columns = db.cypher_query(query, resolve_objects=True)
        for terms in results: 
            term = terms[0]
            new_node = Node(term.id,term.name)
            self.build_child_nodes(node_type,relation,new_node)
            root_node.add_child(new_node)
        return tree
    
    def recommendation_threats(self, threat_model_uid):

        threatmodel = ThreatModelService().find_by_id(threat_model_uid,resolve_objects=True)
        threat_model_threat_units = self.threat_model_threat_units(threat_model_uid)
        all_threat_models = ThreatModelService().load_except(threat_model_uid,resolve_objects=True)
        
        print('Unidades de ameaças para pesquisa: ' + str(len(threat_model_threat_units)))

        all_threat_units = []
        for var in all_threat_models:
            for threat_model in var:
                threat_units = self.threat_model_threat_units(threat_model.threat_model_uid)
                for tu in threat_units:
                    all_threat_units.append(tu)

        print('Unidades de ameaças na base de conhecimento: ' + str(len(all_threat_units)))
        recommended_threats = list()
        for tm_tu in threat_model_threat_units:
            for x_tu in all_threat_units:
                if tm_tu.element_type == x_tu.element_type:
                    sim_name, sim_term, sim_io, similarity = tm_tu.similarity(x_tu)
                    print("Comparando " + str(tm_tu) + " com " + str(x_tu) + " : " + str(similarity))
                    if similarity>0.4:
                        threats = ElementService().find_element_threats(x_tu.element_type, x_tu.uid)
                        for x in threats:
                            for threat in x:
                                print ('Threat for: ' + tm_tu.uid)
                                recommended_threat = {
                                    "element_uid": tm_tu.uid, 
                                    "element_type": tm_tu.element_type, 
                                    "element_name": tm_tu.name, 
                                    "threat_uid": threat['ThreatID'], 
                                    "threat_name": threat['Name'], 
                                    "sim_name": sim_name,
                                    "sim_term": sim_term,
                                    "sim_io": sim_io,
                                    "similarity": similarity
                                }
                                recommended_threats.append(recommended_threat)

        recommended_threats = sorted(recommended_threats, key=lambda k: k['similarity'], reverse=True) 

        cleaned_threats = []
        if len(recommended_threats)>0:
            for rthreat in recommended_threats:
                exists = any(( item["threat_uid"] == rthreat['threat_uid'] and  item["element_uid"] == rthreat['element_uid']) for item in cleaned_threats)
                if not exists:
                    cleaned_threats.append(rthreat)

        
        return cleaned_threats
    
    def threat_model_threat_units(self, threat_model_uid):
        elements = ThreatModelService().find_threatmodel_elements(threat_model_uid, resolve_objects=True)
        threat_units = []
        for var in elements:
            for element in var: 
                if element.dtype != 'DataFlow':
                   threat_unit = self.build_threat_unit(element)
                   threat_units.append(threat_unit)
        return threat_units
                
    def build_threat_unit(self, element):
        input_dataflows = ElementService().find_element_inputs(element.full_name,resolve_objects=True)
        output_dataflows = ElementService().find_element_outputs(element.full_name,resolve_objects=True)
        input_terms = []
        if util.safe_is_not_empty_list(input_dataflows):
            for var in input_dataflows:
                for df in var: 
                    input_terms.append(df.term)
        output_terms = []
        if util.safe_is_not_empty_list(output_dataflows):
            for var in output_dataflows:
                for df in var: 
                    output_terms.append(df.term)
        threat_unit = ThreatUnit(element.uid, element.name, element.full_name, element.dtype, element.term, self.tree_term_factory(element.dtype), self.dataflow_tree, self.brown_ic, input_terms, output_terms)
        return threat_unit

    def tree_term_factory(self, name):
        
        if name == 'DataFlow':
            return self.dataflow_tree
        elif name == 'Process':
            return self.process_tree
        elif name == 'Interactor':
            return self.interactor_tree
        elif name == 'Store':
            return self.store_tree
        else:
            return None
    
    
    def load(self, node_type, limit=100):
        query = f"MATCH (n:{node_type}) RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        self.walk()

        return results 