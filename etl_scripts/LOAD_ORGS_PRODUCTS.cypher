WITH "/scripts/orgs_and_products.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

UNWIND value.organizations AS organizations
CREATE (org:Organization { Name: organizations.name, Acronym: organizations.acronym})
WITH org, organizations
FOREACH (organization IN organizations | 
  FOREACH (product IN organization.products |
    MERGE (org)-[:OWNS]->(:Product {  ProductID: product.productid, Name: product.name, Description: product.description })
  )
)
