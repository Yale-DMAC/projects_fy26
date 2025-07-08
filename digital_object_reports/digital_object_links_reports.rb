class DigitalObjectLinksReport < AbstractReport
  register_report(
    params: [["url", "url"],
    ["parent", "parent", "Parent Object ID"],
    ["oid", "oid", "Digital Object Identifier"]]  
  )
  def initialize(params, job, db)
      super
      @url = params["url"].to_s
      @parent = params["parent"].to_s
      @oid = params["oid"].to_s
    end
  def query
    results = db.fetch(query_string)
    info[:total_count] = results.count
    results
  end

  def query_string
  query = <<~SOME_SQL
    SELECT r.name as 'Repository Name'
    , do.repo_id as 'Repository ID'
    , do.id as 'Digital Object ID'
    , do.title, fv.file_uri as URL
    , i.archival_object_id as 'Parent Archival Object'
    , do.digital_object_id as 'Identifier'
    , concat('repositories/', do.repo_id, '/digital_object/', do.id) as URI
    FROM digital_object do 
    LEFT JOIN file_version fv on fv.digital_object_id = do.id
    LEFT JOIN instance_do_link_rlshp idlr on idlr.digital_object_id = do.id
    LEFT JOIN instance i on i.id = idlr.instance_id
    LEFT JOIN repository r on r.id = do.repo_id
    WHERE do.repo_id = #{db.literal(@repo_id)}
  SOME_SQL
  if @url.present?
    query += " AND fv.file_uri LIKE #{db.literal("%#{@url}%")}"
  end
  if @parent.present?
    query += " AND i.archival_object_id LIKE #{db.literal("%#{@parent}%")}"
  end
  if @oid.present?
    query += " AND do.digital_object_id LIKE #{db.literal("%#{@oid}%")}"
  end
    query
  end

  def page_break
    false
  end
end
