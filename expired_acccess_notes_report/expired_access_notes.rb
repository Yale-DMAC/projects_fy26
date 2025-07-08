class ExpiredAccessNotes < AbstractReport
  register_report(
    params: [['from', Date, 'The start of report range'],
    ['to', Date, 'The start of report range'],
    ["call_number", "callnumber", "The resource identifier"]]
  )

  def initialize(params, job, db)
    super
    @from = DateTime.parse(params['from']).to_time.strftime('%Y-%m-%d') if params['from'].present?
    @to = DateTime.parse(params['to']).to_time.strftime('%Y-%m-%d') if params['to'].present?
    @call_number = params["call_number"].to_s
  end

  def query
    results = db.fetch(query_string)
    info[:total_count] = results.count
    results
  end

  def query_string
    query = <<~SOME_SQL
      SELECT CONCAT('/repositories/', ao.repo_id, '/archival_objects/', n.archival_object_id) as uri, ao.display_string as resource_title, ao.id as id, re.name as repository, 
      CONCAT_WS('-', 
          JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[0]')),
          JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[1]')),
          JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[2]'))
      ) AS identifier,
      JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')) AS expiration_date
      FROM note n 
      LEFT JOIN archival_object ao on ao.id = n.archival_object_id 
      LEFT JOIN repository re on re.id = ao.repo_id 
      LEFT JOIN resource r on r.id = ao.root_record_id 
      WHERE JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.type')) like 'accessrestrict%'
      AND JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')) is not null
      AND n.archival_object_id is not NULL
      AND ao.repo_id = #{db.literal(@repo_id)} 
    SOME_SQL
    if @to && @from
      query += " AND (STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')), '%Y-%m-%d') BETWEEN #{db.literal(@from)} AND #{db.literal(@to)}) "
    elsif @from
      query += " AND (STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')), '%Y-%m-%d') >= #{db.literal(@from)}) "
    elsif @to
      query += " AND (STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')), '%Y-%m-%d') <= #{db.literal(@to)}) "
    end
    if @call_number.present?
      query += " AND r.identifier like #{db.literal("%#{@call_number}%")} "
    end
    query += <<~SOME_SQL
      UNION ALL
      SELECT CONCAT('/repositories/', r.repo_id, '/resources/', n.resource_id) as uri, r.title as resource_title, r.id as id, re.name as repository,
      CONCAT_WS('-', 
          JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[0]')),
          JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[1]')),
          JSON_UNQUOTE(JSON_EXTRACT(r.identifier, '$[2]'))
      ) AS identifier,
      JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')) AS expiration_date
      FROM note n 
      LEFT JOIN resource r on r.id = n.resource_id 
      LEFT JOIN repository re on re.id = r.repo_id
			WHERE JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.type')) like 'accessrestrict%'
      AND JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')) is not null
      AND n.resource_id is not NULL
      AND r.repo_id = #{db.literal(@repo_id)}
			SOME_SQL
      if @to && @from
        query += " AND (STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')), '%Y-%m-%d') BETWEEN #{db.literal(@from)} AND #{db.literal(@to)}) "
      elsif @from
        query += " AND (STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')), '%Y-%m-%d') >= #{db.literal(@from)}) "
      elsif @to
        query += " AND (STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(CONVERT(n.notes USING utf8), '$.rights_restriction.end')), '%Y-%m-%d') <= #{db.literal(@to)}) "
      end
      if @call_number.present?
        query += " AND r.identifier like #{db.literal("%#{@call_number}%")}"
      end
    query
  end

  def page_break
    false
  end
end
