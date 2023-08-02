WITH "/scripts/assets.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

UNWIND value.assets AS a
CREATE (n:Asset { Name: a.name, Host: a.host, Type: a.type, Description: a.description })
