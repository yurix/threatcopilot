import yaml
from datetime import datetime
import pytz


from neomodel import (StructuredNode, StringProperty, IntegerProperty, DateTimeProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom)

from src.home.vocabulary_model import Vocabulary, DataFlowVocabulary, StoreVocabulary, InteractorVocabulary, ProcessVocabulary, DataFlowTerm, StoreTerm, InteractorTerm, ProcessTerm


class ThreatModel(StructuredNode):
    threat_model_uid = StringProperty()
    name = StringProperty()
    package = StringProperty()
    creation_date = DateTimeProperty(
        default=lambda: datetime.now(pytz.utc),
        index=True
    )
    stores = RelationshipTo('Store', 'OWNS')
    interactors = RelationshipTo('Interactor', 'OWNS')
    processes = RelationshipTo('Process', 'OWNS')
    dataflows = RelationshipTo('DataFlow', 'OWNS')
    def get_full_name(self, name): 
        return self.package + "." + name

class Element(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty()
    package = StringProperty()
    full_name = StringProperty()
    term = StringProperty()
    input_sources = RelationshipFrom('DataFlow','CONNECTS_IN')
    output_destinations = RelationshipTo('DataFlow','CONNECTS_OUT')
    threat_model = RelationshipFrom('ThreatModel', 'OWNS')

class Interactor(Element):
    dtype = StringProperty(default="Interactor")
    interactor_term = RelationshipTo('InteractorTerm','ITS')

class Process(Element):
    dtype = StringProperty(default="Process")
    process_term = RelationshipTo('ProcessTerm','ITS')

class Store(Element):
    dtype = StringProperty(default="Store")
    store_term = RelationshipTo('StoreTerm','ITS')

class DataFlow(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  full_name = StringProperty()
  dtype = StringProperty(default="DataFlow")
  term = StringProperty()
  description = StringProperty()
  input_source = RelationshipFrom('Element', 'CONNECTS_OUT')
  output_destination = RelationshipTo('Element', 'CONNECTS_IN')
  threat_model = RelationshipFrom('ThreatModel', 'OWNS')
  dataflow_term = RelationshipTo('DataFlowTerm','ITS')
