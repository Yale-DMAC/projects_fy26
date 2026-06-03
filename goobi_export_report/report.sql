SELECT
  CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) AS aspace_uri,
  ao.id AS refID,
  CONCAT_WS(
  '-',
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[0]')), 'null'),
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[1]')), 'null'),
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[2]')), 'null'),
  NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[3]')), 'null')
) AS callNumber,
  tc.indicator AS `container(Indicator)`,
  CASE
    WHEN type_enum.value IN ('folder', 'slide', 'item', 'volume', 'page', 'reel', 'frame', 'file')
    THEN sc.indicator_2
  END AS `subcontainer(Child Indicator)`,
  CASE
    WHEN type_enum.value = 'item_barcode'
    THEN sc.indicator_2
  END AS item_barcode,
  r.title AS hostTitle,
  hd.creation_date AS hostDate,
  physical_containers.container_statement AS sourceNote,
  ao.display_string AS Title,
  d.creation_date AS date,
  e.phys_desc AS physDesc,
  GROUP_CONCAT(DISTINCT CASE
  	WHEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.type')) NOT IN ('scopecontent', 'accessrestrict', 'prefercite')
  	THEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.subnotes[0].content'))
  END) AS note,
  GROUP_CONCAT(DISTINCT CASE
  	WHEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.type')) = 'scopecontent'
  	THEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.subnotes[0].content'))
  END) AS abstract,
  tc.barcode AS aspace_barcode,
  'ArchivalObject' AS pubType,
  'DefaultCollection' AS collection,
  'TRUE' AS useOPAC,
  'ArchivesSpace' AS opacName,
  GROUP_CONCAT(DISTINCT CASE
  	WHEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.type')) = 'accessrestrict'
  	THEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.subnotes[0].content'))
  END) AS yaleRestriction,
  GROUP_CONCAT(DISTINCT CASE
  	WHEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.type')) = 'userestrict'
  	THEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.subnotes[0].content'))
  END) AS yaleUse,
  GROUP_CONCAT(DISTINCT CASE
  	WHEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.type')) = 'acqinfo'
  	THEN JSON_UNQUOTE(JSON_EXTRACT(CAST(n.notes AS CHAR CHARACTER SET utf8), '$.subnotes[0].content'))
  END) AS yaleOwner
FROM sub_container sc
LEFT JOIN instance i
  ON i.id = sc.instance_id
LEFT JOIN archival_object ao
  ON ao.id = i.archival_object_id
LEFT JOIN resource r
  ON r.id = ao.root_record_id
LEFT JOIN top_container_link_rlshp tclr
  ON tclr.sub_container_id = sc.id
LEFT JOIN top_container tc
  ON tc.id = tclr.top_container_id
LEFT JOIN enumeration_value lev
  ON lev.id = ao.level_id
LEFT JOIN enumeration_value type_enum
  ON type_enum.id = sc.type_2_id
LEFT JOIN note n
	ON ao.id = n.archival_object_id
LEFT JOIN (
  SELECT
    archival_object_id,
    GROUP_CONCAT(
      COALESCE(expression, CONCAT_WS(' - ', `begin`, `end`))
      SEPARATOR ' | '
    ) AS creation_date
  FROM date
  WHERE archival_object_id IS NOT NULL
  GROUP BY archival_object_id
) d ON d.archival_object_id = ao.id
LEFT JOIN (
  SELECT
    resource_id,
    GROUP_CONCAT(
      COALESCE(expression, CONCAT_WS(' - ', `begin`, `end`))
      SEPARATOR ' | '
    ) AS creation_date
  FROM date
  WHERE resource_id IS NOT NULL
  GROUP BY resource_id
) hd ON hd.resource_id = r.id
LEFT JOIN (
  SELECT
    e.archival_object_id,
    GROUP_CONCAT(
      CONCAT(e.number, ' ', et.value)
      SEPARATOR ' | '
    ) AS phys_desc
  FROM extent e
  LEFT JOIN enumeration_value et
    ON et.id = e.extent_type_id
  GROUP BY e.archival_object_id
) e ON e.archival_object_id = ao.id
      LEFT JOIN (SELECT ao.id as ao_id
                  , GROUP_CONCAT(DISTINCT CONCAT(IFNULL(ev.value, '')
                                                      , IF(tc.indicator IS NOT NULL, ' ', '')
                                                      , IFNULL(tc.indicator, '')
                                                      , IF(cp.name IS NOT NULL, ' [', '')
                                                      , IFNULL(cp.name, '')
                                                      , IF(cp.name IS NOT NULL, '] ', ' ')
                                                      , IFNULL(ev2.value, '')
                                                      , IF(sc.indicator_2 IS NOT NULL, ' ', '')
                                                      , IFNULL(sc.indicator_2, ''))
                  ORDER BY CAST(tc.indicator as UNSIGNED), CAST(sc.indicator_2 as UNSIGNED)
                  SEPARATOR '; ') as container_statement
                FROM archival_object ao
                JOIN resource on resource.id = ao.root_record_id
                JOIN instance on instance.archival_object_id = ao.id
                JOIN sub_container sc on sc.instance_id = instance.id
                JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
                JOIN top_container tc on tc.id = tclr.top_container_id
                LEFT JOIN top_container_profile_rlshp tcpr on tcpr.top_container_id = tc.id
                LEFT JOIN container_profile cp on tcpr.container_profile_id = cp.id
                LEFT JOIN enumeration_value ev on ev.id = tc.type_id
                LEFT JOIN enumeration_value ev2 on ev2.id = sc.type_2_id
                LEFT JOIN enumeration_value ev3 on ev3.id = instance.instance_type_id
                WHERE ao.repo_id = 11
                AND (ev3.value is NULL or ev3.value != 'digital_object')
                GROUP BY ao.id) as physical_containers on physical_containers.ao_id = ao.id
WHERE ao.root_record_id = '13973'
GROUP BY ao.id
ORDER BY ao.id