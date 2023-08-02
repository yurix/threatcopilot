MATCH (n:ThreatModel) DETACH DELETE(n);
MATCH (n:Interactor) DETACH DELETE(n);
MATCH (n:DataFlow) DETACH DELETE(n);
MATCH (n:Process) DETACH DELETE(n);
MATCH (n:Store) DETACH DELETE(n);

