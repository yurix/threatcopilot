WITH "/scripts/mtc-data.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

UNWIND value AS t
MERGE (n:Threat { ThreatID: t.ThreatID, Catalog: 'NIST MTC', ThreatCategory: t.ThreatCategory, Name: t.Threat, ThreatOrigin: t.ThreatOrigin, ExploitExample: [value IN t.ExploitExample | coalesce(toStringOrNull(value),' NOT SET ')], CVEExample: [value IN t.CVEExample | coalesce(toStringOrNull(value),' NOT SET ')] });

CREATE CONSTRAINT threatid_unique FOR (t:Threat) REQUIRE t.ThreatID IS UNIQUE;
