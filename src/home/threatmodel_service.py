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

config.DATABASE_URL = Config.NEO4J_URL


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
    
    def find_threatmodel_elements(self, threat_model_uid, resolve_objects=False):
        query = f"MATCH (t:ThreatModel {{ threat_model_uid: '{threat_model_uid}' }})-[o:OWNS]->(w) RETURN w"
        results, meta = db.cypher_query(query, resolve_objects=resolve_objects)
        return results


    
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

    def parse_relations(self, dataflows):
        if dataflows:
            for dataflow in dataflows:
                name = dataflow
                attr = dataflows[name]
                print (attr)
                managed_df = DataFlow.nodes.get_or_none(full_name=self.threatmodel.package + '.' + name)
                source_node = self.find_in_all_dfd_nodes(attr['source_uid'])
               
                managed_df.input_source.connect(source_node)
                source_node.output_destinations.connect(managed_df)

                destination_node = self.find_in_all_dfd_nodes(attr['destination_uid'])
                managed_df.output_destination.connect(destination_node)
                destination_node.input_sources.connect(managed_df)

                print ("Connecting input source " + attr['source_uid'] + " to "  + attr['destination_uid'])

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

    def find_in_all_dfd_nodes(self, full_name):
        print(full_name)
        result = Interactor.nodes.get_or_none(full_name=full_name)
        if result is None:
            result = Process.nodes.get_or_none(full_name=full_name)
            if result is None:
                result = Store.nodes.get_or_none(full_name=full_name)

        return result


                