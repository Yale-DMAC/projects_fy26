SELECT
    CONCAT('https://archives.yale.edu/repositories/', ao.repo_id,'/archival_objects/', ao.id) AS aay_url,
    r.name AS `Repository Name`,
    r.id AS `Repository ID`,
    resource.title AS `Collection Title`,
    ao.display_string  AS `Archival Object Title`,
    JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) AS call_number,
    fv.file_uri as link,
    CONCAT('/repositories/', ao.repo_id,'/digital_objects/', ao.id) AS archivalobject_uri
FROM digital_object do
LEFT JOIN file_version fv ON fv.digital_object_id = do.id
LEFT JOIN instance_do_link_rlshp idlr ON idlr.digital_object_id = do.id
LEFT JOIN instance i ON i.id = idlr.instance_id
LEFT JOIN archival_object ao ON ao.id = i.archival_object_id
LEFT JOIN repository r ON r.id = do.repo_id
LEFT JOIN resource ON resource.id = ao.root_record_id
WHERE fv.file_uri like '%drive.google.com%'