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
from src.home.threatmodel_service import ThreatModelService
from src.home.weakness_service import WeaknessService


import src.home.util as util

config.DATABASE_URL = Config.NEO4J_URL

class Report:
    def __init__(self):
        self.product = None
        self.threatmodel = None
        self.threats = []
        self.elements_with_threats = []
        self.elements_without_threats = []
        self.flows = []

def as_array(neomodel_list):
    arr = []
    for var in neomodel_list:
        item = var[0]
        arr.append(item)
    return arr
def as_object(neomodel_single_item):
    if len (neomodel_single_item) > 0:
        return neomodel_single_item[0]
    else:
        return None

class ReportService:
    def __init__(self):
        db.set_connection(config.DATABASE_URL)
        self.node_type = "Report"

    def get_threat_report(self, threat_model_uid):
        report = Report()
        elements = as_array(ThreatModelService().find_threatmodel_elements(threat_model_uid))
        threat_keys = set()

        for element in elements:
            if element['dtype'] != 'DataFlow':
                threats = as_array(ElementService().find_element_threats(element['dtype'], element['uid']))
                if len(threats) > 0:
                    report.elements_with_threats.append(element)
                    for threat in threats:
                        if threat['ThreatID'] not in threat_keys:
                            threat_keys.add(threat['ThreatID'])
                            weaknesses = as_array(ThreatService().find_threat_weaknesses(threat['ThreatID']))
                            for weakness in weaknesses:
                                weakness.number = weakness['Name'].replace('CWE-','')
                            threat.cwes = weaknesses
                            report.threats.append(threat)
                else:
                    report.elements_without_threats.append(element)
            else:
                report.flows.append(element)

        for threat in report.threats:
            t_elements = []
            for element in elements:
                if element['dtype'] != 'DataFlow':
                    print (element['full_name'])
                    element_threats = as_array(ElementService().find_element_threats(element['dtype'], element['uid']))
                    if len(element_threats) > 0:
                        for element_threat in element_threats:
                            print (threat['ThreatID']+'=='+element_threat['ThreatID'])
                            if threat['ThreatID'] == element_threat['ThreatID']:
                                t_elements.append(element)
                                print('true')
                                
            threat.elements = t_elements


        return report

    
    

    