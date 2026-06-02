class PreservicaObjectReport < AbstractReport
  register_report(
    params: [["call_number", "callnumber", "The resource identifier(s)"]]
  )

  def initialize(params, job, db)
    super

    @call_number = params["call_number"].to_s

  end

  def query
    results = db.fetch(query_string)
    info[:total_count] = results.count
    results
  end

  def query_string
    query = <<~SOME_SQL
      SELECT 
        CONCAT('https://archives.yale.edu/repositories/', ao.repo_id,'/archival_objects/', ao.id) AS aay_url,
        MAX(r.name) AS 'Repository Name',
        MAX(r.id) AS 'Repository ID',
        MAX(resource.title) AS 'Collection Title',
        LTRIM(physical_containers.container_statement) as container_statement,
        JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) AS call_number,
        MAX(ao.display_string) AS 'Archival Object Title',
        COUNT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.id END) AS preservica_count,
        COUNT(DISTINCT CASE WHEN fv.file_uri LIKE '%collections.library.yale.edu%' THEN do.id END) AS dcs_count,
        COUNT(DISTINCT CASE WHEN fv.file_uri LIKE '%https://beineckelibrary.aviaryplatform.com%' THEN do.id END) AS aviary_count,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.title END) AS preservica_titles,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%collections.library.yale.edu%' THEN do.title END) AS dcs_titles,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%https://beineckelibrary.aviaryplatform.com%' THEN do.title END) AS aviary_titles,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.digital_object_id END) AS preservica_identifiers,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%collections.library.yale.edu%' THEN do.digital_object_id END) AS dcs_identifiers,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%https://beineckelibrary.aviaryplatform.com%' THEN do.digital_object_id END) AS aviary_identifiers,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN CONCAT('/repositories/', do.repo_id,'/digital_objects/', do.id) END) AS preservica_uris,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%collections.library.yale.edu%' THEN CONCAT('/repositories/', do.repo_id,'/digital_objects/', do.id) END) AS dcs_uris,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%https://beineckelibrary.aviaryplatform.com%'THEN CONCAT('/repositories/', do.repo_id,'/digital_objects/', do.id) END) AS aviary_uris,
        CONCAT('/repositories/', ao.repo_id,'/digital_objects/', ao.id) AS archivalobject_uri
      FROM digital_object do
      LEFT JOIN file_version fv ON fv.digital_object_id = do.id
      LEFT JOIN instance_do_link_rlshp idlr ON idlr.digital_object_id = do.id
      LEFT JOIN instance i ON i.id = idlr.instance_id
      LEFT JOIN archival_object ao ON ao.id = i.archival_object_id
      LEFT JOIN repository r ON r.id = do.repo_id
      LEFT JOIN resource ON resource.id = ao.root_record_id
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
                WHERE ao.repo_id = #{db.literal(@repo_id)}
                AND (ev3.value is NULL or ev3.value != 'digital_object')
                GROUP BY ao.id) as physical_containers on physical_containers.ao_id = ao.id
      WHERE r.id = #{db.literal(@repo_id)}
    SOME_SQL

    if @call_number.present?
      query += " AND JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) LIKE #{db.literal("%#{@call_number}%")}"
    end

    query += <<~SOME_SQL
      GROUP BY ao.id
      HAVING preservica_count > 0 OR dcs_count > 0 OR aviary_count > 0
      ORDER BY r.name, ao.title
    SOME_SQL
    query
  end

  def page_break
    false
  end
end
