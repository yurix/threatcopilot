WITH "/scripts/capec.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

FOREACH (reference IN value.Attack_Pattern_Catalog.External_References.External_Reference |
  MERGE (r:Attack_External_Reference {Reference_ID: reference.Reference_ID})
  SET r.Author = [value IN reference.Author | value], r.Title = reference.Title,
  r.Edition = reference.Edition, r.URL = reference.URL,
  r.Publication_Year = reference.Publication_Year, r.Publisher = reference.Publisher
);

WITH "/scripts/capec.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value
UNWIND value.Attack_Pattern_Catalog.Attack_Patterns.Attack_Pattern AS capec

MERGE (i:CAPEC {
  Name: value.Attack_Pattern_Catalog.Name, Version: value.Attack_Pattern_Catalog.Version,
  Date: value.Attack_Pattern_Catalog.Date, Schema: 'http://capec.mitre.org/data/xsd/ap_schema_v3.4.xsd'
})

MERGE (cp:Attack {
  Name: 'CAPEC-' + capec.ID
})

SET cp.ExtendedName = capec.Name, cp.Abstraction = capec.Abstraction,
cp.Status = capec.Status, cp.Description = coalesce(toStringOrNull(capec.Description), ' NOT SET '),
cp.Likelihood_Of_Attack = capec.Likelihood_Of_Attack, cp.Typical_Severity = capec.Typical_Severity,
cp.Alternate_Terms = [value IN capec.Alternate_Terms.Alternate_Term | value.Term],

cp.Submission_Date = capec.Content_History.Submission.Submission_Date,
cp.Submission_Name = capec.Content_History.Submission.Submission_Name,
cp.Submission_Organization = capec.Content_History.Submission.Submission_Organization
MERGE (cp)-[:belongsTo]->(i)

FOREACH (skill IN capec.Skills_Required.Skill |
  MERGE (con:AttackSkillRequired { Description: coalesce(toStringOrNull(skill.text),' NOT SET ')})
  SET con.Level = [value IN skill.Level | value] 
  MERGE (cp)-[rel:hasSkillRequired]->(con)
)
//Required Resources
FOREACH (resource IN capec.Resources_Required.Resource |
  MERGE (res:AttackResourceRequired { Description: coalesce(toStringOrNull(resource),' NOT SET ')})
  MERGE (cp)-[rel:hasResourceRequired]->(res)
)
//Indicators
FOREACH (indicator IN capec.Indicators.Indicator |
  MERGE (ind:AttackIndicator { Description: coalesce(toStringOrNull(indicator),' NOT SET ')})
  MERGE (cp)-[rel:hasIndicator]->(ind)
)
//Prerequisites
FOREACH (prerequisite IN capec.Prerequisites.Prerequisite |
  MERGE (pre:AttackPreRequisite { Description: coalesce(toStringOrNull(prerequisite),' NOT SET ')})
  MERGE (cp)-[rel:hasIndicator]->(pre)
)

// Consequences
FOREACH (consequence IN capec.Consequences.Consequence |
  MERGE (con:AttackConsequence {Scope: [value IN consequence.Scope | value]})
  MERGE (cp)-[rel:hasConsequence]->(con)
  SET rel.Impact = [value IN consequence.Impact | value],
  rel.Note = consequence.Note, rel.Likelihood = consequence.Likelihood
)
// Mitigations
FOREACH (mit IN capec.Mitigations.Mitigation |
  MERGE (m:AttackMitigation {
    Description: coalesce(toStringOrNull(mit), ' NOT SET ')
  })
  MERGE (cp)-[:hasMitigation]->(m)
)

FOREACH (executionflow IN capec.ExecutionFlow.Attack_Step |
  MERGE (con:AttackExecutionFlow {Step: [value IN executionflow.Step | value]})
  MERGE (cp)-[rel:hasExecutionFlow]->(con)
  SET rel.Phase = executionflow.Phase,
  rel.Description = executionflow.Description
)
//ExecutionFlow TODO
//FOREACH (executionflow IN capec.ExecutionFlow |
//  MERGE (pre:AttacExecutionFlow { Description: coalesce(toStringOrNull(prerequisite),' NOT SET ')})
//  MERGE (cp)-[rel:hasIndicator]->(pre)
//)

// Related Attack Patterns
WITH cp, capec
UNWIND (
CASE capec.Related_Attack_Patterns.Related_Attack_Pattern WHEN [] THEN [ null ]
  ELSE capec.Related_Attack_Patterns.Related_Attack_Pattern
  END) AS Rel_AP
OPTIONAL MATCH (pec:Attack {
  Name: 'CAPEC-' + Rel_AP.CAPEC_ID
})
MERGE (cp)-[:RelatedAttackPattern {Nature: Rel_AP.Nature}]->(pec)

// Public References
WITH cp, capec
UNWIND (
CASE capec.References.Reference WHEN [] THEN [ null ]
  ELSE capec.References.Reference
  END) AS ExReference
OPTIONAL MATCH (Ref:Attack_External_Reference {Reference_ID: ExReference.External_Reference_ID})
MERGE (cp)-[rel:hasExternal_Reference {CAPEC_ID: cp.Name}]->(Ref)
SET rel.Section = ExReference.Section;

// ------------------------------------------------------------------------
// Insert Categories
WITH "/scripts/capec.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

UNWIND value.Attack_Pattern_Catalog.Categories.Category AS category
MERGE (c:Attack {Name: 'CAPEC-' + category.ID})
SET c.Extended_Name = category.Name, c.Status = category.Status, c.Summary = coalesce(toStringOrNull(category.Summary), ' NOT SET '),
c.Submission_Name = category.Content_History.Submission.
  Submission_Name,
c.Submission_Date = category.Content_History.Submission.Submission_Date,
c.Submission_Organization = category.Content_History.Submission.Submission_Organization
//c.Modification = [value IN category.Content_History.Modification | coalesce(toStringOrNull(value), ' NOT SET ')]

// Insert Members for each Category
WITH c, category
UNWIND (
CASE category.Relationships.Has_Member WHEN [] THEN [ null ]
  ELSE category.Relationships.Has_Member
  END) AS members
OPTIONAL MATCH (MemberAP:CAPEC {Name: 'CAPEC-' + members.CAPEC_ID})
MERGE (c)-[:hasMember]->(MemberAP);

// ------------------------------------------------------------------------
// Insert Public References for each Category
WITH "/scripts/capec.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

UNWIND value.Attack_Pattern_Catalog.Categories.Category AS category
UNWIND (
CASE category.References.Reference WHEN [] THEN [ null ]
  ELSE category.References.Reference
  END) AS categoryExReference
MATCH (c:Attack)
  WHERE c.Name = 'CAPEC-' + category.ID
OPTIONAL MATCH (catRef:Attack_External_Reference {Reference_ID: categoryExReference.External_Reference_ID})
MERGE (c)-[rel:hasExternal_Reference]->(catRef)
SET rel.Section = categoryExReference.Section;

// ------------------------------------------------------------------------
// Insert Views for CAPECs
WITH "/scripts/capec.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

// Views
UNWIND value.Attack_Pattern_Catalog.Views.View AS view
MERGE (v:AttackView {ViewID: view.ID})
SET v.Name = view.Name, v.Type = view.Type, v.Status = view.Status,
v.Objective = coalesce(toStringOrNull(view.Objective), ' NOT SET '), v.Filter = view.Filter,
v.Filter = view.Filter,
v.Notes = coalesce(toStringOrNull(view.Notes), ' NOT SET '),
v.Submission_Name = view.Content_History.Submission.Submission_Name,
v.Submission_Date = view.Content_History.Submission.Submission_Date,
v.Submission_Organization = view.Content_History.Submission.Submission_Organization
//v.Modification = [value IN view.Content_History.Modification | coalesce(toStringOrNull(value), ' NOT SET ')]

// Insert Stakeholders for each View
FOREACH (value IN view.Audience.Stakeholder |
  MERGE (st:Stakeholder {Type: value.Type})
  MERGE (v)-[rel:usefulFor]->(st)
  SET rel.Description = value.Description
)

// Insert Members for each View
WITH v, view
UNWIND (
CASE view.Members.Has_Member WHEN [] THEN [ null ]
  ELSE view.Members.Has_Member
  END) AS members
OPTIONAL MATCH (MemberAP:Attack {Name: 'CAPEC-' + members.CAPEC_ID})
MERGE (v)-[:hasMember]->(MemberAP);

// ------------------------------------------------------------------------
// Insert Public References for each View
WITH "/scripts/capec.json" as filesToImport
UNWIND [filesToImport] AS files
CALL apoc.load.json(files) YIELD value

UNWIND value.Attack_Pattern_Catalog.Views.View AS view
UNWIND (
CASE view.References.Reference WHEN [] THEN [ null ]
  ELSE view.References.Reference
  END) AS viewExReference
MATCH (v:CAPEC_VIEW)
  WHERE v.ViewID = view.ID
OPTIONAL MATCH (viewRef:Attack_External_Reference {Reference_ID: viewExReference.External_Reference_ID})
MERGE (v)-[:hasExternal_Reference]->(viewRef);