import yaml
from datetime import datetime
import pytz
from neomodel import config
from time import sleep
from src.config import Config
from src.home.utml_model import ThreatModel, Element, Interactor,  Process, Store, DataFlow
from neomodel import db

from src.home.vocabulary_model import Vocabulary, DataFlowVocabulary, StoreVocabulary, InteractorVocabulary, ProcessVocabulary, DataFlowTerm, StoreTerm, InteractorTerm, ProcessTerm
from src.home.vocabulary_service import VocabularyService
from src.home.element_service import ElementService
from src.home.threat_service import ThreatService

import src.home.util as util

config.DATABASE_URL = Config.NEO4J_URL


class DFDRelation:
    def __init__(self, name, term, description, end_dfid, end_full_name, end_name, end_term, end_dtype):
        self.name = name
        self.term = term
        self.description = description
        self.end_dfid = end_dfid
        self.end_full_name = end_full_name
        self.end_name = end_name
        self.end_term = end_term
        self.end_dtype = end_dtype
        print (self.end_full_name)

class DFDNode:
    def __init__(self, dfid, full_name, name, dtype,term):
        self.dfid = dfid
        self.full_name = full_name
        self.name = name
        self.dtype = dtype
        self.term = term
        self.relations = []

    def add_relation(self, relation):
        self.relations.append(relation)

def get_letter_by_name(node_list, name):
    for node in node_list:
        if node.name == name: 
            return node.dfid
    return 'NULL'

def next_letter(sequencia):
    sequencia = sequencia.upper()
    
    num = 0
    for char in sequencia:
        num = num * 26 + (ord(char) - ord('A') + 1)
    num += 1
    nova_sequencia = ""
    while num > 0:
        num, rem = divmod(num - 1, 26)
        nova_sequencia = chr(rem + ord('A')) + nova_sequencia
    
    return nova_sequencia


class ThreatModelService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)
        self.node_type = "ThreatModel"
    
    def load(self, limit=100):
        query = f"MATCH (n:{self.node_type}) RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results 
    
    def load_except(self, threat_model_uid, limit=1000, resolve_objects=False):
        query = f"MATCH (n:ThreatModel) WHERE n.threat_model_uid <> '{threat_model_uid}' RETURN n LIMIT {limit}"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results 
    
    def find(self, user_query):
        query = f"MATCH (n:{self.node_type}) WHERE {user_query} RETURN n"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def find_by_id(self, threat_model_uid, resolve_objects=False):
        query = f"MATCH (p:ThreatModel {{ threat_model_uid: '{threat_model_uid}' }}) RETURN p"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results
    
    def delete(self, threat_model_uid):
        query = f"MATCH (p:ThreatModel {{ threat_model_uid: '{threat_model_uid}' }})-[r]-(g) DETACH delete g, r, p"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
    
    def finish(self, threat_model_uid):
        query = f"MATCH (p:ThreatModel {{ threat_model_uid: '{threat_model_uid}' }}) SET p.finished = true"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
    
    def reopen(self, threat_model_uid):
        query = f"MATCH (p:ThreatModel {{ threat_model_uid: '{threat_model_uid}' }}) SET p.finished = false"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results
    
    def find_threatmodel_elements(self, threat_model_uid, resolve_objects=False):
        query = f"MATCH (t:ThreatModel {{ threat_model_uid: '{threat_model_uid}' }})-[o:OWNS]->(w) RETURN w"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results
    
    def render_dfd(self, threat_model_uid):
        threatmodel = self.find_by_id(threat_model_uid,resolve_objects=True)
        dfdnodes = self.walk_elements(threat_model_uid)
        for dfdnode in dfdnodes:
            print (dfdnode.dfid)
        return dfdnodes

    def walk_elements(self, threat_model_uid):
        elements = self.find_threatmodel_elements(threat_model_uid, resolve_objects=True)
        dfdnodes = []
        sequence = 'A'
        for var in elements:
            for element in var: 
                if element.dtype != 'DataFlow':
                   dfdnode = DFDNode(sequence,element.full_name, element.name, element.dtype, element.term)
                   dfdnodes.append(dfdnode)
                   sequence = next_letter(sequence)
        
        
        self.create_dfd_relations(dfdnodes)
        return dfdnodes
    
    def create_dfd_relations(self, dfdnodes):
        for dfdnode in dfdnodes:

            output_dataflows = ElementService().find_element_outputs(dfdnode.full_name,resolve_objects=True)
            output_terms = []

            if util.safe_is_not_empty_list(output_dataflows):
                for var in output_dataflows:
                    for df in var: 
                        df_objs = ElementService().find_element_outputs_elements(df.full_name,True)
                        output_destination = df_objs[0][0]
                        dfdnode.add_relation ( DFDRelation(
                            df.name, 
                            df.term, 
                            df.description, 

                            get_letter_by_name(dfdnodes, output_destination.name), 
                            output_destination.full_name, 
                            output_destination.name, 
                            output_destination.term, 
                            output_destination.dtype) )       
        

    def find_threatmodel_elements_with_query(self, threat_model_uid, query):
        query = f"MATCH (t:ThreatModel {{ threat_model_uid: '{threat_model_uid}' }})-[o:OWNS]->(w) RETURN w"
        results, meta = db.cypher_query(query, resolve_objects=False)
        return results

    def save(self, content):
        #TODO: Implementar Transacoes
        self.utml = None
        utml_data = yaml.safe_load(content)
        self.threatmodel = ThreatModel(name=utml_data['name'],package=utml_data['package'], version=utml_data['version'], threat_model_uid=utml_data['threat_model_uid']).save()
        
        print("Processando threat model...")
        print("Name: " + self.threatmodel.name)
        print("Version: " + str(self.threatmodel.version))
        print('Processando interactors...')
        if 'interactors' in utml_data:      
            interactors = utml_data['interactors']
            managed_interactors = []
            self.parse_interactors(interactors, managed_interactors)
        
        print('Finalizado! Processando stores...')          

        if 'stores' in utml_data:
            stores = utml_data['stores']
            managed_stores = []
            self.parse_stores(stores, managed_stores)

        print('Finalizado! Processando processes...')          
        if 'processes' in utml_data:
            processes = utml_data['processes']
            managed_processes = []
            self.parse_processes(processes, managed_processes)

        print('Finalizado! Processando dataflows...')          
        if 'dataflows' in utml_data:
            dataflows = utml_data['dataflows']
            managed_dataflows = []
            self.parse_dataflows(dataflows, managed_dataflows)
            self.parse_relations(dataflows)
        
        print('Finalizado! Processando threats...')          
        if 'threatflows' in utml_data:
            threatflows = utml_data['threatflows']
            self.parse_threatflows(threatflows)

    def parse_relations(self, dataflows):
        if dataflows:
            for dataflow in dataflows:
                name = dataflow
                attr = dataflows[name]
                #print (attr)
                managed_df = DataFlow.nodes.get_or_none(full_name=self.threatmodel.package + '.' + name)
                source_node = self.find_in_all_dfd_nodes(attr['source_uid'])
               
                managed_df.input_source.connect(source_node)
                source_node.output_destinations.connect(managed_df)

                destination_node = self.find_in_all_dfd_nodes(attr['destination_uid'])
                managed_df.output_destination.connect(destination_node)
                destination_node.input_sources.connect(managed_df)

                #print ("Connecting input source " + attr['source_uid'] + " to "  + attr['destination_uid'])

    def parse_interactors(self, interactors, managed_interactors):
        if interactors:
            for interactor in interactors:
                name = interactor
                attr = interactors[name]
                current_obj = Interactor(name=name,package=self.threatmodel.package,full_name=self.threatmodel.get_full_name(name),description=attr['description'],term=attr['term']).save()
                managed_interactors.append(current_obj)
                current_obj.threat_model.connect(self.threatmodel)
                self.threatmodel.interactors.connect(current_obj)
                # bind with vocabulary term
                interactor_term = InteractorTerm.nodes.get_or_none(name=current_obj.term)
                if interactor_term is not None:
                    current_obj.interactor_term.connect(interactor_term)
    
    def parse_stores(self, stores, managed_stores):
        if stores:
            for store in stores:
                name = store
                attr = stores[name]
                current_obj = Store(name=name,package=self.threatmodel.package,full_name=self.threatmodel.get_full_name(name),description=attr['description'],term=attr['term']).save()
                managed_stores.append(current_obj)
                current_obj.threat_model.connect(self.threatmodel)
                self.threatmodel.stores.connect(current_obj)
                # bind with vocabulary term
                store_term = StoreTerm.nodes.get_or_none(name=current_obj.term)
                if store_term is not None:
                    current_obj.store_term.connect(store_term)

    def parse_processes(self, processes, managed_processes):
        if processes:
            for process in processes:
                name = process
                attr = processes[name]
                current_obj = Process(name=name,package=self.threatmodel.package,full_name=self.threatmodel.get_full_name(name),description=attr['description'],term=attr['term']).save()
                managed_processes.append(current_obj)
                current_obj.threat_model.connect(self.threatmodel)
                self.threatmodel.processes.connect(current_obj)
                # bind with vocabulary term
                process_term = ProcessTerm.nodes.get_or_none(name=current_obj.term)
                if process_term is not None:
                    current_obj.process_term.connect(process_term)

    def parse_dataflows(self, dataflows, managed_dataflows):
        if dataflows:
            for dataflow in dataflows:
                name = dataflow
                attr = dataflows[name]
                current_obj = DataFlow(name=name,package=self.threatmodel.package,full_name=self.threatmodel.get_full_name(name),description=attr['description'],term=attr['term']).save()
                managed_dataflows.append(current_obj)
                current_obj.threat_model.connect(self.threatmodel)
                self.threatmodel.dataflows.connect(current_obj)
                # bind with vocabulary term
                dataflow_term = DataFlowTerm.nodes.get_or_none(name=current_obj.term)
                if dataflow_term is not None:
                    current_obj.dataflow_term.connect(dataflow_term)
    
    def parse_threatflows(self, threatflows):
        if threatflows:
            for threatflow in threatflows:
                print ( threatflow )
                element = self.find_in_all_dfd_nodes(threatflow['element_uid'])
                print ( element )
                for threat in threatflow['threats']:
                    print ( threat ['threat_uid'] )
                    ElementService().bind_element_threat(element.dtype,element.uid,threat ['threat_uid'])

    def find_in_all_dfd_nodes(self, full_name):
        result = Interactor.nodes.get_or_none(full_name=full_name)
        if result is None:
            result = Process.nodes.get_or_none(full_name=full_name)
            if result is None:
                result = Store.nodes.get_or_none(full_name=full_name)

        return result
    
                