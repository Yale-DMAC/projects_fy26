SELECT 
  CONCAT('https://archives.yale.edu/repositories/', ao.repo_id,'/archival_objects/', ao.id) AS aay_url,
  r.name AS `Repository Name`,
  r.id AS `Repository ID`,
  resource.title AS `Collection Title`,
  ao.display_string  AS `Archival Object Title`,
  JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) AS call_number,
  COUNT(DISTINCT CASE WHEN fv.file_uri LIKE '%drive.google.com%' THEN do.id END) AS google_count,
  COUNT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.id END) AS preservica_count,
  GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%drive.google.com%' THEN do.digital_object_id END) AS google_identifiers,
  GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%drive.google.com%' THEN fv.file_uri END) AS google_uris,
  GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.digital_object_id END) AS preservica_identifiers,
  GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN fv.file_uri END) AS preservica_uris,
  CONCAT('repositories/', r.id, '/archival_objects/', ao.id) as uri
FROM digital_object do
LEFT JOIN file_version fv ON fv.digital_object_id = do.id
LEFT JOIN instance_do_link_rlshp idlr ON idlr.digital_object_id = do.id
LEFT JOIN instance i ON i.id = idlr.instance_id
LEFT JOIN archival_object ao ON ao.id = i.archival_object_id
LEFT JOIN repository r ON r.id = do.repo_id
LEFT JOIN resource ON resource.id = ao.root_record_id
GROUP BY ao.id
HAVING google_count > 0