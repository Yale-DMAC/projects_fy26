import csv, json, time
from connections import API as api
from tqdm import tqdm

def get(uri):
	if api.connect(env):
		response = api.client.get(uri)
		code = response.status_code
		if code == 200:
			result = response.json()
			return result
		else:
			error = response.text
			error = json.loads(error)
			to_csv(uri, code, error)
			return

def post(uri, data):
    if api.connect(env):
        response = api.client.post(uri, json=data)
        code = response.status_code
        if code == 200:
            result = response.json()
            to_csv(uri, code, result)
            return result, True
        else:
            try:
                error = response.text
                error = json.loads(error)
                to_csv(uri, code, error)
            except json.JSONDecodeError:
                error = response.text
                to_csv(uri, code, error)
            return error, False

def csv_config(path):
	date_str = date_str = time.strftime("%y%m%d")
	updatefile = open(f'{path}/{date_str}_results.csv', 'a', encoding='utf8', newline='')
	writer = csv.DictWriter(updatefile, fieldnames=['uri', 'code', 'result'])
	writer.writeheader()
	return writer

def to_csv(uri, code, result):
	row_dict = {}
	row_dict['uri'] = uri
	row_dict['code'] = code
	row_dict['result'] = result
	writer.writerow(row_dict)	
      
def proccess_csv(file):
    values = {}
    with open(file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for i, row in enumerate(reader, start=1):
            if row:
                values[i] = {
                    'uri': row[0],
                    'note': row[11],
                    'code': row[12],
                    'indicator': row[13],
                    'location': row[16]
                }
    return values

def create_tc(value):
    instance = {
        'indicator': value['indicator'],
        'jsonmodel_type': 'top_container',
        'restricted': True,
        'type': 'box'
    }
    if value['location']:
        instance['container_locations'] = [{
            'jsonmodel_type': 'container_location',
            'ref': '/locations/207',
            'status': 'current',
            'start_date': "2025-07-29" 
        }]
    result, posted = post('/repositories/11/top_containers', instance)
    uri = result.get('uri') if posted else (
        result.get('error', {}).get('conflicting_record', [None])[0]
    )
    if uri:
        value['tc_uri'] = uri
    return value

def backup(uri, data):
	with open(f"{path}/backups/{uri.replace('/','_')}.json", 'w', encoding='utf8') as outfile:
	    json.dump(data, outfile, sort_keys=True, indent=4)

def update_ao(value):
    uri = value['uri']
    tc_uri = value['tc_uri']
    record = get(uri)
    backup(uri, record)
    if value['note']:
        record['notes'].append({
                "jsonmodel_type": "note_multipart",
                "publish": True,
                "rights_restriction": {
                    "local_access_restriction_type": [
                        "RestrictedFragileSpecColl"
                    ]
                },
                "subnotes": [
                    {
                        "content": value['note'],
                        "jsonmodel_type": "note_text",
                        "publish": True
                    }
                ],
                "type": "accessrestrict"
            })
    instance_template = {
        "instance_type": "mixed_materials",
        "jsonmodel_type": "instance",
        "lock_version": 0,
        "sub_container": {
            "jsonmodel_type": "sub_container",
            "lock_version": 0,
            "top_container": {
                "ref": tc_uri
            }}}
    if 'instances' in record:
         record['instances'].append(instance_template)
    else:
        record['instances'] = [instance_template]
    post(uri, record)

def main():
    global env, writer, path
    env = 'production'
    path = 'files/papyri_containers_restrictions'
    writer = csv_config(path)
    file = f'{path}/papyri_containers_and_restrictions.csv'
    values = proccess_csv(file)
    last_tc_uri = None 

    for i in tqdm(values, desc="Processing Records", unit="record"):
        value = values[i]
        
        if value['indicator']:
            value = create_tc(value)
            last_tc_uri = value.get('tc_uri')
        elif last_tc_uri:
            value['tc_uri'] = last_tc_uri
        else:
            print(f"Skipping row {i}: No indicator and no previously created top container.")

        update_ao(value)


if __name__ == "__main__":
    main()
