WITH RECURSIVE hierarchies
AS (SELECT ao.id as id
		, ao.display_string as display_string
		, ao.parent_id as parent_id
		, ao.root_record_id as root_record_id
        , replace(resource.title, '"', "'") as resource_title
        , JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) AS call_number
		, ao.repo_id as repo_id
		, 0 as lvl
		, IF(ev.value = 'series', ao.component_id, NULL) as series_cuid
		, IF(ev.value = 'series', ao.display_string, NULL) as series_title
		, IF(ev.value = 'series', ao.id, NULL) as series_id
        , CONCAT(ao.display_string, ' (', CONCAT(UPPER(SUBSTRING(ev.value,1,1)),LOWER(SUBSTRING(ev.value,2))), ' ', IF(ao.component_id is not NULL, CAST(ao.component_id as CHAR), "N/A"), ')') as path
    FROM archival_object ao
    LEFT JOIN enumeration_value ev on ev.id = ao.level_id
    JOIN resource on resource.id  = ao.root_record_id
    WHERE ao.parent_id is NULL
    AND resource.id = '2819'
    UNION ALL
    SELECT ao.id as id
		, ao.display_string as display_string
        , ao.parent_id as parent_id
        , ao.root_record_id as root_record_id
        , replace(resource.title, '"', "'") as resource_title
        , JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) AS call_number
        , ao.repo_id as repo_id
        , h.lvl + 1 as lvl
        , h.series_cuid
        , h.series_title
        , h.series_id
        , CONCAT(h.path ,' > ', CONCAT(ao.display_string, ' (', CONCAT(UPPER(SUBSTRING(ev.value,1,1)),LOWER(SUBSTRING(ev.value,2))), ' ', IF(ao.component_id is not NULL, CAST(ao.component_id as CHAR), "N/A"), ')')) AS path
    FROM hierarchies h
    JOIN archival_object ao on h.id = ao.parent_id
	JOIN resource on resource.id  = ao.root_record_id
    LEFT JOIN enumeration_value ev on ev.id = ao.level_id
    WHERE resource.id = '2819')
SELECT 
CONCAT('/repositories', r.repo_id, '/archival_objects/', ao.id) as uri
, CONCAT_WS(
  '-',
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[0]')), 'null'),
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[1]')), 'null'),
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[2]')), 'null'),
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[3]')), 'null')
) AS resource_id
, r.title AS resource_title
, ao.display_string AS archival_object_title
, d.expression AS date_expression
, ao.component_id AS cuid
, tc.`indicator` AS top_container_box_number
, tc.barcode AS top_container_barcode
, type_enum.value AS child_type
, sc.indicator_2 AS child_indicator
, CONCAT(h.resource_title, ' (Resource ', h.call_number, ') > ', h.path) as full_path
FROM archival_object ao 
LEFT JOIN resource r ON r.id = ao.root_record_id
LEFT JOIN date d ON d.archival_object_id = ao.id
LEFT JOIN instance i ON ao.id = i.archival_object_id
LEFT JOIN sub_container sc ON sc.instance_id = i.id
LEFT JOIN top_container_link_rlshp tclr ON tclr.sub_container_id = sc.id
LEFT JOIN top_container tc ON tc.id = tclr.top_container_id
LEFT JOIN enumeration_value type_enum ON type_enum.id = sc.type_2_id
LEFT JOIN hierarchies h ON h.id = ao.id
WHERE r.id = '2819'