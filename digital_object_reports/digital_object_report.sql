SELECT r.name as 'Repository Name', do.repo_id as 'Repository ID', do.id as 'Digital Object ID', do.title, fv.file_uri as URL, i.archival_object_id as 'Parent Archival Object', do.digital_object_id as 'Identifier', concat('repositories/', do.repo_id, '/digital_object/', do.id) as URI
FROM digital_object do 
LEFT JOIN file_version fv on fv.digital_object_id = do.id
LEFT JOIN instance_do_link_rlshp idlr on idlr.digital_object_id = do.id
LEFT JOIN instance i on i.id = idlr.instance_id
LEFT JOIN repository r on r.id = do.repo_id