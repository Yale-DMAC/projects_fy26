SELECT CONCAT('/repositories/', r.repo_id, '/resources/', n.resource_id) as uri,
r.title as title,
JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.rights_restriction.local_access_restriction_type')) as type,
JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.subnotes[0].content')) as content,
JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.rights_restriction.begin')) as begin_date,
JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.rights_restriction.end')) as end_date
FROM note n 
LEFT JOIN resource r on r.id = n.resource_id 
WHERE JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.type')) = "accessrestrict"
AND n.resource_id is not NULL 
AND (r.repo_id = 11 OR r.repo_id = 12)
AND JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.rights_restriction.local_access_restriction_type[0]')) IN ("RestrictedSpecColl", "RestrictedCurApprSpecColl", "RestrictedFragileSpecColl", "InProcessSpecColl", "ColdStorageBrbl", "UseSurrogate", "NoRequest", "BornDigital")