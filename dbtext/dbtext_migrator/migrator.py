import xml.etree.ElementTree as ET
import connections.API as api
from tqdm import tqdm
import csv, time, json, yaml, copy, sys
import normalize.acq_norm as dbacq
import normalize.catmss_norm as dbcatmss
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
 

# 01. FILE CONFIGURATION AND CREATION FUNCTIONS

def load_config(file_path):
    """Load a yaml file. 
    Called in the main function."""

    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
    
def process_xml(xml_path):
    """Process an xml file into a dictionary. 
    Called in the Main function."""

    records = {}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespaces = {'inm':'http://www.inmagic.com/webpublisher/query'}

    for record in root.findall('.//inm:Record', namespaces):
        entry_id = record.get('setEntry')
        record_data = {}

        for child in record:
            tag = child.tag.split('}')[-1]
            text = child.text if child.text is not None else ""
            if tag in record_data:
                record_data[tag] = record_data[tag] + '; ' + text
            else:
                record_data[tag] = text

        record_data['entry_id'] = entry_id
        records[entry_id] = record_data

    return records

def get_unique_filename(directory, base_filename):
    """Adds a number to the end of a filename in the case of repeat files. (e.g. backups.json, backups1.json, backups2.json, etc.)
    Called in the Main function."""

    directory = Path(directory)
    name, ext = Path(base_filename).stem, Path(base_filename).suffix
    new_path = directory / base_filename
    counter = 1

    while new_path.exists():
        counter += 1
        new_path = directory / f"{name}_{counter}{ext}"

    return new_path

def csv_config(path):
    """Create CSV files for successful migrations and errors. Should be saved to two variables (e.g. writer, err_writer = csv_config(yourpathhere))
    Called in the Main function."""

    date_str = time.strftime("%y%m%d")
    Path(path).mkdir(parents=True, exist_ok=True)
    
    def make_writer(suffix):
        file = get_unique_filename(path, f"{date_str}_{suffix}.csv")
        writer = csv.DictWriter(file.open('a', encoding='utf8', newline=''),
                                fieldnames=['id', 'uri', 'results', 'record'])
        writer.writeheader()
        return writer

    return make_writer('migration'), make_writer('errors')

def to_csv(writer, uri, results, record, id):
    """Records variables to one of the earlier created CSV files.
    Called in References and Events classes and the post_record function."""

    writer.writerow({
        'id': id,
        'uri': uri,
        'results': results,
        'record': record
    })


# 02. API FUNCTIONS

def post(uri, data):
    """Posts to the ArchivesSpace API with the supplied uri and json data. Makes use of the global env variable to determine whether to post to production or test environments.
    Called in References and Events classes, and the post_record function."""

    if api.connect(env):
        response = api.client.post(uri, json=data)
        if response.status_code == 200:
            result = response.json()
            return result, True
        else:
            try:
                error = json.loads(response.text)
                if not isinstance(error, dict):
                    error = {'error': error}
            except json.JSONDecodeError:
                error = {'error': response.text}
            return error, False
    else:
        return 'No connection.', False

def suppress(uri):
    """Suppresses the provided uri in ArchivesSpace by using the post function.
    Called in the post_record function."""

    if api.connect(env):
        suppress = api.client.post(f"{uri}/suppressed",
                                 params={"suppressed": True}) 


# 03. GUI AND NORMALIZATION FUNCTIONS

def normalize(database, jsonfile):
    """Processes json files using python scripts specific to each database.
    Called in the Main function."""

    if database == 'acq':
        print("ACQ mapping being used.")
        return dbacq.normalize(jsonfile, env)
    elif database == 'catacq':
        print("CATACQ mapping being used.")
        return dbacq.normalize(jsonfile, env)
    elif database == 'catmss':
        print("CATMSS mapping being used.")
        return dbcatmss.normalize(jsonfile, env)
    elif database == 'deposit':
        print("Deposit mapping being used.")
        return remove_empty_fields(jsonfile)
    else: 
        print("No database found.")
        sys.exit(1)

def remove_empty_fields(obj):
    """Removes empty fields from the jsonfile.
    Called in the Normalize function."""

    if isinstance(obj, dict):
        return {k: remove_empty_fields(v) for k, v in obj.items() if v != ''}
    elif isinstance(obj, list):
        return [remove_empty_fields(item) for item in obj]
    else:
        return obj

class ScriptConfigGUI:
    """Called in the Main function."""

    def __init__(self):
        self.env = None
        self.database = None
        self.path = None
        self.xml_file = None
        self.backups = None

        self.root = tk.Tk()
        self.root.title("Script Configuration")

        self._create_widgets()

    def _create_widgets(self):
        """Creates GUI design look."""

        # Use Method dropdown
        self.use_method_var = tk.StringVar(value="test")
        ttk.Label(self.root, text="Use Method:").grid(row=0, column=0, sticky="e")
        ttk.Combobox(
            self.root,
            textvariable=self.use_method_var,
            values=["test", "production"],
            state="readonly"
        ).grid(row=0, column=1)

        # Database dropdown
        self.database_var = tk.StringVar(value="deposit")
        ttk.Label(self.root, text="Database:").grid(row=1, column=0, sticky="e")
        ttk.Combobox(
            self.root,
            textvariable=self.database_var,
            values=["deposit", "catmss", "acq", "catacq"],
            state="readonly"
        ).grid(row=1, column=1)

        # Folder picker
        self.folder_var = tk.StringVar()
        ttk.Label(self.root, text="Folder Path:").grid(row=2, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.folder_var, width=40).grid(row=2, column=1)
        ttk.Button(self.root, text="Browse...", command=self.browse_folder).grid(row=2, column=2)

        # File picker
        self.file_var = tk.StringVar()
        ttk.Label(self.root, text="Input XML File:").grid(row=3, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.file_var, width=40).grid(row=3, column=1)
        ttk.Button(self.root, text="Browse...", command=self.browse_file).grid(row=3, column=2)

        # Checkbox for backups
        self.backups_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.root, text="Save JSON backups", variable=self.backups_var
        ).grid(row=4, column=1, sticky="w")

        # Submit button
        ttk.Button(self.root, text="Submit", command=self.submit).grid(row=5, column=1, pady=10)

    def browse_folder(self):
        """Browse and Select folder path to save files in."""

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_var.set(folder_selected)

    def browse_file(self):
        """Browse and Select XML file to use."""

        file_selected = filedialog.askopenfilename(filetypes=[("XML and JSON files", "*.xml *.json")])
        if file_selected:
            self.file_var.set(file_selected)

    def submit(self):
        """Submit button sends each field to a specific variable."""

        use_method_display = self.use_method_var.get()
        self.env = {"test": "test", "production": "production"}.get(use_method_display, "test")
        self.database = self.database_var.get()
        self.path = self.folder_var.get()
        self.xml_file = self.file_var.get()
        self.backups = self.backups_var.get()

        if not self.path or not self.xml_file:
            messagebox.showerror("Missing Input", "Please select both a folder and an XML file.")
            return

        self.root.quit()
        self.root.destroy()

    def run(self):
        """Creates GUI and gathers infromation from it."""

        self.root.mainloop()
        return self.env, self.database, self.path, self.xml_file, self.backups


# 04. CREATE AGENTS, INSTANCES, AND EVENTS

class ReferenceCreator:
    """Called in main function."""

    def __init__(self, records, writer, err_writer, yaml_file):
        self.records = records
        self.writer = writer
        self.err_writer = err_writer
        config = load_config(yaml_file)
        self.repo_id = config.get('repo_id')

    def process(self):
        """Cycles through each entry in a record and requests agents and instances for them."""

        agent_fields = [
            ('AUT', 'AUT_URI'),
            ('OWNER', 'OWNER_URI'),
            ('DON', 'DON_URI'),
            ('VNA', 'VNA_URI'),
            ('PUB', 'PUB_URI')
        ]

        for record_id, entry in tqdm(self.records.items(), desc="Processing References", unit="record"):
            for field, uri_field in agent_fields:
                self.create_agent(record_id, entry, field, uri_field)
            self.create_instance(record_id, entry, 'TC_URI')

        return self.records

    def create_agent(self, record_id, entry, field, uri_field):
        """Creates and posts an agent by calling the build_agent_data function and the post functions. 
        Moves the Agent name to a note and uses a shortened version if the Agent name surpasses 255 characters."""

        name = entry.get(field)

        if not name:
            return

        full_note = None
        if len(name) > 255:
            full_note = name
            name = name[:250].rstrip() + '...'

        agent_data = self._build_agent_data(name, field, full_note)
        result, posted = post('agents/people', agent_data)

        uri = result.get('uri') if posted else (
            result.get('error', {}).get('conflicting_record', [None])[0]
        )
        if not posted:
            to_csv(self.err_writer, uri, result, entry, field)
        else:
            to_csv(self.writer, uri, result, agent_data, field)

        if uri:
            self.records[record_id][uri_field] = uri

    def _build_agent_data(self, name, role, full_note):
        """Structures Agent data into json."""

        agents = {
            'agent_type': 'agent_person',
            'display_name': {
                'authorized': False,
                'is_display_name': True,
                'jsonmodel_type': 'name_person',
                'lock_version': 0,
                'name_order': 'inverted',
                'primary_name': name,
                'sort_name': name,
                'sort_name_auto_generate': True
            },
            'is_linked_to_published_record': False,
            'is_slug_auto': False,
            'jsonmodel_type': 'agent_person',
            'linked_agent_roles': role,
            'lock_version': 22,
            'names': [{
                'authorized': False,
                'is_display_name': True,
                'jsonmodel_type': 'name_person',
                'name_order': 'inverted',
                'primary_name': name,
                'sort_name': name,
                'sort_name_auto_generate': True
            }],
            'publish': False,
            'title': name,
            'suppressed': True
        }
        if full_note:
                agents['notes'] = [{
                    'jsonmodel_type': 'note_general_context',
                    'publish': True,
                    'subnotes': [{
                        'content': full_note,
                        'jsonmodel_type': 'note_text',
                        'publish': True
                    }]
                }]
        return agents

    def create_instance(self, record_id, entry, uri_field):
        """Creates and Posts an Instance for the entry in the record set."""

        barcode_field = entry.get('BAR')
        indicator = entry.get('BCN')

        if not barcode_field:
            return

        barcodes = [b.strip() for b in barcode_field.split(';') if b.strip()]
        for barcode in barcodes:
            instance_data = {
                'indicator': f"{indicator}",
                'barcode': f"{barcode}",
                'jsonmodel_type': 'top_container',
                'restricted': True,
                'type': 'box'
            }
            uri_path = f'/repositories/{self.repo_id}/top_containers'
            result, posted = post(uri_path, instance_data)

            uri = result.get('uri') if posted else (
                result.get('error', {}).get('conflicting_record', [None])[0]
            )
            if not posted:
                to_csv(self.err_writer, uri, result, entry, 'instance')
            else:
                to_csv(self.writer, uri, result, instance_data, 'instance')

            if uri:
                existing = self.records[record_id].get(uri_field, "")
                if existing:
                    self.records[record_id][uri_field] = existing + ";" + uri
                else:
                    self.records[record_id][uri_field] = uri

class EventCreator:
    """Called upon by post_record function."""

    def __init__(self, entry, event_uri, writer, err_writer, config):
        self.entry = entry
        self.event_uri = event_uri
        self.writer = writer
        self.err_writer = err_writer
        self.config = config
        self.repo_id = config.get('repo_id')
        self.uri_path = f'/repositories/{self.repo_id}/events'

    def event_data(self, event_value, field_type):
        """Structures data into a json."""

        return {
                'date': {
                    'expression': event_value,
                    'date_type': 'single',
                    'jsonmodel_type': 'date',
                    'label': 'event'
                },
                'event_type': field_type,
                'jsonmodel_type': 'event',
                'repository': {'ref': f'/repositories/{self.repo_id}'},
                'suppressed': True,
                'linked_records': [{'role': 'transfer', 'ref': self.event_uri}],
                'linked_agents': [{'role': 'recipient', 'ref': '/agents/corporate_entities/923'}]
            }
    
    def create_event(self, data, event_value):
        """Creates an event using json data via the post function. Writes results to csv."""

        result, posted = post(self.uri_path, data)
        uri = result.get('uri') if posted else (
                result.get('error', {}).get('conflicting_record', [None])[0]
            )
        target_writer = self.writer if posted else self.err_writer
        to_csv(target_writer, uri, result, data, event_value)

    def proccess_event(self):
        """Maps, creates the json data, and then requests the event be posted."""

        event_map = {
            'DTB': 'date_to_beinecke',
            'DTC': 'date_to_cataloging'
        }
        for key, field_type in event_map.items():
            event_value = self.entry.get(key)
            data = self.event_data(event_value, field_type)
            self.create_event(data, event_value)


# 05. GENERATE FIELDS

def generate_material_types(record, config):
    """Provide entry and Yaml config in order to return the material type.
    Called in the create_record function."""

    MAT_CODE_MAP = {
        'ar': 'works_of_art',
        'av': 'audiovisual_materials',
        'cf': 'electronic_documents',
        'ga': 'games',
        'mi': 'microforms',
        'mp': 'maps',
        'ms': 'manuscripts',
        'ph': 'photographs',
        're': 'realia',
        'se': 'serials',
        }
    base = copy.deepcopy(config['material_types'])
    if not config.get('auto_generate_mat', True):
        return base

    mat_field = record.get('MAT', '').strip().lower()
    if not mat_field:
        base['books'] = True
    else:
        for code, key in MAT_CODE_MAP.items():
            if code in mat_field:
                base[key] = True
    return base

def generate_notes(record, config):
    """Provide entry and YAML config. Function will create a notefield with appropriate labels for each individual note. Also includes a "Migrated to ArchivesSpace." note.
    Called in the create_record function."""

    auto_generate = config.get('auto_generate_note', True) 
    note_fields = config.get('note_fields', [])
    migration_note = config.get('migration_note', {})

    notes = []
    if auto_generate:
        for field in note_fields:
            value = record.get(field['source'], '')
            if value:
                notes.append(f"{field['label']} = {value}")

    # Always append migration note
    notes.append(f"Migration Note = {migration_note.get('content', 'Migrated to ArchivesSpace.')}")
    return ' | '.join(notes)

def generate_subtemplates(type, record, config):
    """Provide the type of template you wish to create (ex_doc, dates, extents, instances, or references), the entry, and YAML config. This function will return the template.
    Called in the create_record function."""
    
    type_map = {
        'ex_doc': ('auto_generate_external_documents', 'external_doc_template'),
        'dates': ('auto_generate_dates', 'dates_template'),
        'extents': ('auto_generate_extents', 'extents_template'),
        'instances': ('auto_generate_instances', 'instances_template'),
        'references': ('auto_generate_references', 'references_template'),
    }

    auto_key, template_key = type_map.get(type, (None, None))
    if not auto_key or not config.get(auto_key, True):
        return []

    template = config.get(template_key, [])
    refs = []
    for field in template:
        source = field.get('source')
        if source and source not in record:
            continue
        if source and isinstance(record.get(source), str) and ';' in record[source]:
            values = [v.strip() for v in record[source].split(';') if v.strip()]
        else:
            values = [record.get(source)] if source else [None]

        for value in values:
            local_context = record.copy()
            if source:
                local_context[source] = value

            rendered = render_template(
                {k: v for k, v in field.items() if k != 'source'},
                local_context
            )

            if rendered:
                refs.append(rendered)
    return refs

def generate_payments(record, config):
    """Provide entry and YAML config and this function will return a payment template for the record. Makes use of the render_template function.
    Called in the create_record function."""

    if not config.get('auto_generate_payment', True):
        return None

    template = config.get('payment_template', [])
    record.setdefault('currency', '')
    record.setdefault('total_price', '')
    record.setdefault('in_lot', '')
    record.setdefault('FUN', '')
    record.setdefault('PAY_NOTE', '')

    for field in template:
        source = field.get('source')
        value = record.get(source, '') if source else ''
        if value or value == '':
            return render_template({k: v for k, v in field.items() if k != 'source'}, record)
    return None


# 06. TRANSFORMATIONS AND TEMPLATE RENDERING

def apply_transformations(record, transformations):
    """Applies transformations at the YAML level for simple normalization.
    See deposit.yml for example.
    Called in the create_record function."""

    enriched = {}
    context = {k: v for k, v in record.items()}
    context['time'] = time 
    for key, expr in transformations.items():
        try:
            enriched[key] = eval(f'f"""{expr}"""', {}, context)
        except Exception as e:
            print(f"[Transformation error] {key}: {e}")
    return {**record, **enriched}

def render_template(template, context):
    """Turns the template in the YAML file into json.
    Called in the create_record function."""

    if isinstance(template, dict):
        return {k: render_template(v, context) for k, v in template.items() if render_template(v, context) is not None}
    elif isinstance(template, list):
        rendered = [render_template(i, context) for i in template]
        return [i for i in rendered if i is not None]
    elif isinstance(template, str):
        try:
            return eval(f'f"""{template}"""', {}, context)
        except Exception:
            return None
    return template


# 07. CREATE RECORDS

def create_record(record, config):
    """Applies transformations, creates a template, and calls the generate fields.
    Fully creates the json data to be posted.
    Called in the main function."""

    full_record = apply_transformations(record, config.get('transformations', {}))	
    full_record['note_field'] = generate_notes(record, config)
    full_record['repo_id'] = config.get('repo_id')
    record_template = render_template(config.get('template', {}), full_record)
    record_template['linked_agents'] = generate_subtemplates('references', record, config)
    record_template['extents'] = generate_subtemplates('extents', record, config)
    record_template['material_types'] = generate_material_types(record, config)
    record_template['dates'] = generate_subtemplates('dates', record, config)
    record_template['instances'] = generate_subtemplates('instances', record, config)
    record_template['external_documents'] = generate_subtemplates('ex_doc', record, config)
    if record.get('PRI'):
        record_template['payment_summary'] = generate_payments(record, config)
    return record_template

def post_record(record, config, writer, err_writer):
    """Posts the record and events to ArchivesSpace.
    Called in the main function."""
    
    id = record['entry_id']
    suppression = config.get('suppression')
    uri = f'/repositories/{record["repo_id"]}/accessions'

    result, posted = post(uri, record)

    if posted:
        event_uri = result.get('uri')
        if suppression:
            suppress(event_uri)
        EventCreator(record, event_uri, writer, err_writer, config).proccess_event()
        to_csv(writer, event_uri, result, record, id)
    else:
        error_block = result.get('error', {})
        if isinstance(error_block, dict):
            conflicting_record = error_block.get('conflicting_record', [None])
            if isinstance(conflicting_record, list):
                event_uri = conflicting_record[0]
            else:
                event_uri = None
        else:
            event_uri = None
        to_csv(err_writer, event_uri, result, record, id)


# 08. MAIN

def main():
    global env

    # Run GUI and set up files selection.
    env, database, path, xml_file, backups = ScriptConfigGUI().run()
    current_dir = Path(__file__).resolve().parent
    yaml_file = load_config(current_dir / "mapping" / f"{database}.yml")

    # Set up CSV.
    writer, err_writer = csv_config(path)

    # Process XML into JSON and normalize the record.
    jsonfile = process_xml(xml_file)
    records = normalize(database, jsonfile)

    # Create Agents and Instances.
    records = ReferenceCreator(records, writer, err_writer, yaml_file).process()

    # Create Records.
    for entry_id, entry in tqdm(records.items(), desc="Processing Records", unit="record"):
        result = create_record(entry, yaml_file)
        post_record(result, yaml_file, writer, err_writer)
        backup_records[entry_id] = result

    # Backups.
    backup_records = {}
    if backups:
        backup_file = get_unique_filename(path, 'backups.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_records, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()


