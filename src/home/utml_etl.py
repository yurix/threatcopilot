import yaml
from utml_model import *
from neomodel import config

config.DATABASE_URL = 'bolt://neo4j:your_password@localhost:7687'

data = None
with open('sis1.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

interactors = data['interactors']
processes = data['processes']
stores = data['stores']
assets = interactors + processes + stores

dataflows = data['dataflows']

tm = ThreatModel(name=data['name'],threat_model_uid=data['threat_model_uid']).save()

managed_assets = []
managed_dataflows = []

def find_asset(asset_uid=None):
  if (asset_uid == None):
    return None
  for xasset in managed_assets:
    print (xasset)
    if (asset_uid == xasset.asset_uid):
      return xasset
  return None

for asset_name in assets:
  asset = assets[asset_name]
  new_asset = Asset(name=asset_name,asset_uid=asset['asset_uid'], parent_uid=asset['parent_uid'], dtype=asset['type'], clazz=asset['class']).save()
  managed_assets.append(new_asset)
  tm.assets.connect(new_asset)

for dataflow_name in dataflows:
  dataflow = dataflows[dataflow_name]
  new_dataflow = DataFlow(name=dataflow_name,dataflow_uid=dataflow['dataflow_uid'],clazz=dataflow['class']).save()
  managed_dataflows.append(new_dataflow)
  tm.dataflows.connect(new_dataflow)
  new_dataflow.source.connect(find_asset(asset_uid=dataflow['source_asset_uid']))
  new_dataflow.destination.connect(find_asset(asset_uid=dataflow['destination_asset_uid']))