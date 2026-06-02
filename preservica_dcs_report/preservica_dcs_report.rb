class PreservicaDcsReport < AbstractReport
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
        MAX(r.name) AS 'Repository Name',
        MAX(r.id) AS 'Repository ID',
        ao.id AS 'Archival Object ID',
        MAX(resource.title) AS 'Collection Title',
        MAX(ao.title) AS 'Archival Object Title',
        MAX(do.title) AS 'Digital Object Title',
        JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) AS call_number,
        COUNT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.id END) AS preservica_count,
        COUNT(DISTINCT CASE WHEN fv.file_uri LIKE '%hdl.handle.net%' THEN do.id END) AS handle_count,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.id END) AS preservica_object_ids,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%hdl.handle.net%' THEN do.id END) AS handle_object_ids,
        GROUP_CONCAT(DISTINCT CASE WHEN fv.file_uri LIKE '%preservica.library%' THEN do.digital_object_id END) AS preservica_identifiers
      FROM digital_object do
      LEFT JOIN file_version fv ON fv.digital_object_id = do.id
      LEFT JOIN instance_do_link_rlshp idlr ON idlr.digital_object_id = do.id
      LEFT JOIN instance i ON i.id = idlr.instance_id
      LEFT JOIN archival_object ao ON ao.id = i.archival_object_id
      LEFT JOIN repository r ON r.id = do.repo_id
      LEFT JOIN resource ON resource.id = ao.root_record_id
      WHERE r.id = #{db.literal(@repo_id)}
    SOME_SQL

    if @call_number.present?
      query += " AND JSON_UNQUOTE(JSON_EXTRACT(resource.identifier, '$[0]')) LIKE #{db.literal("%#{@call_number}%")}"
    end

    query += <<~SOME_SQL
      GROUP BY ao.id
      HAVING preservica_count > 0 AND handle_count > 0
      ORDER BY r.name, ao.title
    SOME_SQL
    query
  end

  def page_break
    false
  end
end
