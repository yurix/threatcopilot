import yaml
from datetime import datetime
import pytz
from neomodel import config
from time import sleep
from src.config import Config
from src.home.vocabulary_model import Vocabulary, DataFlowVocabulary, StoreVocabulary, InteractorVocabulary, ProcessVocabulary, DataFlowTerm, StoreTerm, InteractorTerm, ProcessTerm
from neomodel import db

config.DATABASE_URL = Config.NEO4J_URL


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

    def display_tree(self, node, level=0):
        if node is not None:
            print("  " * level + str(node.name))
            for child in node.children:
                self.display_tree(child, level + 1)


class VocabularyService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)

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
            

    def walk(self):
        
        #print (results)
        
        #tore_v = v.store_vocabulary
        store_tree = Tree()
        store_root_node = Node(0,'Store')
        store_tree.set_root(store_root_node)
        query = f"MATCH (t:StoreTerm) WHERE NOT EXISTS(()-[:CHILD_OF_STORE_TERM]->(t:StoreTerm)) RETURN t"
        results, columns = db.cypher_query(query, resolve_objects=True)
        for store_terms in results: 
            store_term = store_terms[0]
            new_node = Node(store_term.id,store_term.name)
            self.build_child_nodes('StoreTerm','CHILD_OF_STORE_TERM',new_node)
            store_root_node.add_child(new_node)
            
        
        store_tree.display_tree(store_tree.root)
    
    def load(self, node_type, limit=100):
        query = f"MATCH (n:{node_type}) RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        self.walk()

        return results 

    def save(self, content):
        self.vocabulary_data = None
        vocabulary_data = yaml.safe_load(content)
        self.vocabulary = Vocabulary(name=vocabulary_data['name'],version=vocabulary_data['version']).save()
        flows = vocabulary_data['flows']
        managed_flow_vocabulary = []
        print("Processando vocabulário...")
        print("Name: " + self.vocabulary.name)
        print("Version: " + str(self.vocabulary.version))
        print('Processando vocabulário de flows...')
        self.dfv = DataFlowVocabulary(name='DataFlowVocabulary').save()
        self.dfv.vocabulary.connect(self.vocabulary)
        self.vocabulary.dataflow_vocabulary.connect(self.dfv)
        self.parse_flows(self.dfv, flows, None, managed_flow_vocabulary)
        print('Finalizado! Processando vocabulário de stores...')          
        stores = vocabulary_data['stores']
        managed_store_vocabulary = []
        self.sv = StoreVocabulary(name='StoreVocabulary').save()
        self.sv.vocabulary.connect(self.vocabulary)
        self.vocabulary.store_vocabulary.connect(self.sv)
        self.parse_stores(self.sv, stores, None, managed_store_vocabulary)
        print('Finalizado! Processando vocabulário de interactors...')
        interactors = vocabulary_data['interactors']
        managed_interactor_vocabulary = []     
        self.iv = InteractorVocabulary(name='InteractorVocabulary').save()
        self.iv.vocabulary.connect(self.vocabulary)
        self.vocabulary.interactor_vocabulary.connect(self.iv)
        self.parse_interactors(self.iv, interactors, None, managed_interactor_vocabulary)
        print('Finalizado! Processando vocabulário de processes...')
        processes = vocabulary_data['processes']
        managed_process_vocabulary = []
        self.pv = ProcessVocabulary(name='ProcessVocabulary').save()
        self.pv.vocabulary.connect(self.vocabulary)
        self.vocabulary.process_vocabulary.connect(self.pv)
        self.parse_processes(self.pv, processes, None, managed_process_vocabulary)
        print("Finalizado! Processamento do vocabulário encerrado.")

    def parse_flows(self, dataflow_vocabulary, flows, parent, managed_flow_vocabulary):
        if flows:
            for flow in flows:
                current_obj = DataFlowTerm(name=flow['name']).save()
                managed_flow_vocabulary.append(current_obj)
                current_obj.dataflow_vocabulary.connect(dataflow_vocabulary)
                dataflow_vocabulary.dataflow_terms.connect(current_obj)
                if parent is not None:
                    current_obj.parent.connect(parent)
                    parent.children.connect(current_obj)
                if 'children' in flow:
                    self.parse_flows(dataflow_vocabulary, flow['children'], current_obj, managed_flow_vocabulary)
        
    def parse_stores(self, store_vocabulary, stores, parent, managed_store_vocabulary):
        if stores:
            for store in stores:
                current_obj = StoreTerm(name=store['name']).save()
                managed_store_vocabulary.append(current_obj)
                current_obj.store_vocabulary.connect(store_vocabulary)
                store_vocabulary.store_terms.connect(current_obj)
                if parent is not None:
                    current_obj.parent.connect(parent)
                    parent.children.connect(current_obj)
                if 'children' in store:
                    self.parse_stores(store_vocabulary, store['children'], current_obj, managed_store_vocabulary)

    def parse_interactors(self, interactor_vocabulary, interactors, parent, managed_interactor_vocabulary):
        if interactors:
            for interactor in interactors:
                current_obj = InteractorTerm(name=interactor['name']).save()
                managed_interactor_vocabulary.append(current_obj)
                current_obj.interactor_vocabulary.connect(interactor_vocabulary)
                interactor_vocabulary.interactor_terms.connect(current_obj)

                if parent is not None:
                    current_obj.parent.connect(parent)
                    parent.children.connect(current_obj)

                if 'children' in interactor:
                    self.parse_interactors(self.iv, interactor['children'], current_obj, managed_interactor_vocabulary)
    def parse_processes(self, process_vocabulary, processes, parent, managed_process_vocabulary):
        if processes:
            for process in processes:
                current_obj = ProcessTerm(name=process['name']).save()
                managed_process_vocabulary.append(current_obj)
                current_obj.process_vocabulary.connect(process_vocabulary)
                process_vocabulary.process_terms.connect(current_obj)

                if parent is not None:
                    current_obj.parent.connect(parent)
                    parent.children.connect(current_obj)

                if 'children' in process:
                    self.parse_processes(process_vocabulary, process['children'], current_obj, managed_process_vocabulary)