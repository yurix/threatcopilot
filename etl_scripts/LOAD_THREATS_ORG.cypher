WITH "/scripts/threats-custom.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

UNWIND value AS t
MERGE (n:Threat { ThreatID: t.ThreatID, Catalog: 'Org Database', ThreatCategory: t.ThreatCategory, ThreatDescription: t.ThreatDescription, STRIDE: t.STRIDE, Name: t.Threat, ThreatOrigin: t.ThreatOrigin, ExploitExample: [value IN t.ExploitExample | coalesce(toStringOrNull(value),' NOT SET ')], CVEExample: [value IN t.CVEExample | coalesce(toStringOrNull(value),' NOT SET ')] });