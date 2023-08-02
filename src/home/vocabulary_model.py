import yaml
from datetime import datetime
import pytz

from neomodel import (StructuredNode, StringProperty, IntegerProperty, DateTimeProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom)

class Vocabulary(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  version = StringProperty()
  creation_date = DateTimeProperty(
        default=lambda: datetime.now(pytz.utc),
        index=True
  )
  dataflow_vocabulary = RelationshipTo('DataFlowVocabulary', 'OWNS_DATAFLOW_VOCABULARY')
  store_vocabulary = RelationshipTo('StoreVocabulary', 'OWNS_STORE_VOCABULARY')
  interactor_vocabulary = RelationshipTo('InteractorVocabulary', 'OWNS_INTERACTOR_VOCABULARY')
  process_vocabulary = RelationshipTo('ProcessVocabulary', 'OWNS_PROCESS_VOCABULARY')

  def get_dataflow_vocabulary(self):
        results, columns = self.cypher("MATCH (v:Vocabulary) WHERE id(v)=$self MATCH (v)-[:OWNS_DATAFLOW_VOCABULARY]->(b) RETURN b")
        return [self.inflate(row[0]) for row in results]

class DataFlowVocabulary(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  vocabulary = RelationshipFrom('Vocabulary', 'OWNS_DATAFLOW_VOCABULARY')
  dataflow_terms = RelationshipTo('DataFlowTerm', 'HAS_DATAFLOW_TERM')

class DataFlowTerm(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  children = RelationshipTo('DataFlowTerm', 'CHILD_OF_DATAFLOW_TERM')
  parent = RelationshipTo('DataFlowTerm', 'PARENT_OF_DATAFLOW_TERM')
  dataflow_vocabulary = RelationshipFrom('DataFlowVocabulary', 'HAS_DATAFLOW_TERM')

class StoreVocabulary(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  vocabulary = RelationshipFrom('Vocabulary', 'OWNS_STORE_VOCABULARY')
  store_terms = RelationshipTo('StoreTerm', 'HAS_STORE_TERM')

class StoreTerm(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  children = RelationshipTo('StoreTerm', 'CHILD_OF_STORE_TERM')
  parent = RelationshipTo('StoreTerm', 'PARENT_OF_STORE_TERM')
  store_vocabulary = RelationshipFrom('StoreVocabulary', 'OWNS_STORE_VOCABULARY')

class InteractorVocabulary(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  vocabulary = RelationshipFrom('Vocabulary', 'OWNS_INTERACTOR_VOCABULARY')
  interactor_terms = RelationshipTo('InteractorTerm', 'HAS_STORE_TERM')

class InteractorTerm(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  children = RelationshipTo('InteractorTerm', 'CHILD_OF_INTERACTOR_TERM')
  parent = RelationshipTo('InteractorTerm', 'PARENT_OF_INTERACTOR_TERM')
  interactor_vocabulary = RelationshipFrom('InteractorVocabulary', 'OWNS_INTERACTOR_VOCABULARY')

class ProcessVocabulary(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  vocabulary = RelationshipFrom('Vocabulary', 'OWNS_PROCESS_VOCABULARY')
  process_terms = RelationshipTo('ProcessTerm', 'HAS_PROCESS_TERM')

class ProcessTerm(StructuredNode):
  uid = UniqueIdProperty()
  name = StringProperty()
  children = RelationshipTo('ProcessTerm', 'CHILD_OF_PROCESS_TERM')
  parent = RelationshipTo('ProcessTerm', 'PARENT_OF_PROCESS_TERM')
  process_vocabulary = RelationshipFrom('ProcessVocabulary', 'OWNS_PROCESS_VOCABULARY')