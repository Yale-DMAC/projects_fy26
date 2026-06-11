from datetime import datetime
import json, re

def parse_dates(entry, id):
    """Searches for a usuable accession date from ACC, ADT, or DTE. Adds a note if the date comes from DTE."""

    acc = entry.get('ACC')
    adt = entry.get('ADT')
    dte = entry.get('DTE')
    mem = entry.get('MEM') or ""

    acc_status = ''
    acc_date = None
    adt_date = None
    dte_date = None
    date_to_use = None
    suffix = ''

    def split_suffix(date_str):
        """Split date and suffix like 19881202-a → (19881202, -a)"""

        if not date_str:
            return None, ''
        
        parts = date_str.strip().split('-', 1)

        if len(parts) == 2 and parts[1].isalpha():
            return parts[0], '-' + parts[1]
        return date_str.strip(), ''

    def normalize_date(date_str):
        """Check the date string for different date formats then normalize it to YYYYMMDD."""

        if not date_str:
            return None

        FORMATS = [
            "%Y%m%d", "%m%d%Y", "%d%m%Y",
            "%y%m%d", "%m%d%y", "%d%m%y", "%Y%d%m",
            "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y",
            "%m-%d-%y", "%d-%m-%y",
            "%m/%d/%Y", "%d/%m/%Y",
            "%m/%d/%y", "%d/%m/%y",
            "%d %B %Y", "%d %b %Y",
            "%B %d, %Y", "%b %d, %Y",
            "%B %d %Y", "%b %d %Y",
        ]

        s = date_str.strip()

        for fmt in FORMATS:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y%m%d")
            except ValueError:
                continue

        return None

   # --- ACC ---
    if acc:
        acc = acc.strip()
        if acc:
            raw, acc_suffix = split_suffix(acc)
            if raw and raw[0].isalpha():
                acc_status = raw[0]
                acc_date = normalize_date(raw[1:])
            else:
                acc_date = normalize_date(raw)

    # --- ADT ---
    if adt:
        adt = adt.strip()
        if adt:
            raw, adt_suffix = split_suffix(adt)
            if raw and raw[0].isalpha() and raw[1:9].isdigit():
                acc_status = raw[0]
                adt_date = normalize_date(raw[1:9])
            elif raw[:8].isdigit():
                adt_date = normalize_date(raw[:8])
            else:
                adt_date = normalize_date(raw)

    # --- DTE ---
    if dte:
        raw, dte_suffix = split_suffix(dte)
        dte_date = normalize_date(raw)

    # --- Choose date ---
    if adt_date:
        date_to_use = adt_date
        suffix_to_use = adt_suffix
    elif acc_date and acc and len(acc) >= 6:
        date_to_use = acc_date
        suffix_to_use = acc_suffix
    else:
        date_to_use = dte_date
        suffix_to_use = dte_suffix
        if date_to_use:
            mem_note = "Accession date (ADT) value copied from record creation date (DTE) at time of import into ArchivesSpace."
            mem = mem + '; ' + mem_note

    # --- Build IDs ---
    id_0 = ''
    id_2 = ''

    if date_to_use and len(date_to_use) >= 8:
        try:
            year = int(date_to_use[:4])
            month = int(date_to_use[4:6])

            # July rollover rule
            if month >= 7:
                year += 1

            id_0 = str(year)
            id_2 = date_to_use[4:] + suffix_to_use
        except ValueError:
            pass

    id_3 = f'acq-{id}'

    return acc_status, id_2, id_0, date_to_use, mem, id_3

def fieldFUN(entry, fundcodes):
    """Removes funding codes not present in ArchivesSpace."""

    FUN = entry.get('FUN').upper()

    if FUN in fundcodes:
        entry['FUN'] = FUN
        return entry
    else:
        entry['PAY_NOTE'] = FUN
        del entry['FUN']
        return entry

def fieldACQTYPE(entry, acc_status):
    """Determines the acquistion type based on conditions in the record."""

    VNA = entry.get('VNA')
    DON = entry.get('DON')

    if VNA and not DON:
        type = "purchase"
    elif DON and not VNA:
        type = "gift"
    elif acc_status == 'T':
         type = "transfer"
    else:
        type = ""

    return type	

def fieldPRI(entry):
    """Determines the currency type and cleans up any pricing errors such as decimal misplacement."""

    PRI = entry.get('PRI', '').strip()
    total_price = currency = lot = ''

    if PRI.startswith('$'):
        currency = 'USD'
        match = re.search(r'\$\s*([\d,]+\.\d{2})', PRI)
        if match:
            total_price = match.group(1).replace(',', '')
    elif PRI.startswith('L'):
        currency = 'GBP'
        match = re.search(r'L\s*(\d+\.\d+\.\d+)', PRI)
        if match:
            total_price = match.group(1)
    else:
        currency  = ""
        match = re.search(r'(\d+\.\d{2})(?!.*\d+\.\d{2})', PRI)
        if match:
            total_price = match.group(1)

    if 'lot' in PRI.lower():
        lot = True
    else:
        lot = False

    return lot, total_price, currency

def fieldPLATE(entry): 
    """Returns a cleaned up text and identifies plate entries."""

    fields = ['DON', 'VNA', 'PRI']
    
    for key in fields:
        value = entry.get(key)
        if value:
            match = re.search(r'(.*?)(?:\s*PLATE:\s*(.*))$', value)
            if match:
                original_text = match.group(1).strip()
                plate_text = match.group(2).strip()
                entry[key] = original_text 
                return plate_text, entry
            
    return None, entry

def normbar(entry):
    """Cleans up barcode fields."""

    bar = entry.get('BAR')
    bar.strip()
    bar = bar.rstrip('\n')
    return bar

def ud_enum(entry):
    """Changes ORT codes into ArchivesSpace codes."""

    ort = entry.get('ORT')
    if ort == "so":
        ort = "standing_order"
    elif ort == "sub":
        ort = "subscription"

    return ort

def remove_empty_fields(obj):
    """Removes empty fields from record."""

    if isinstance(obj, dict):
        return {k: remove_empty_fields(v) for k, v in obj.items() if v != ''}
    elif isinstance(obj, list):
        return [remove_empty_fields(item) for item in obj]
    else:
        return obj

def normalize_template(record, fundcodes, id):
    """Cleans up fields and adds in necessary fields for normalization."""

    record = fieldFUN(record, fundcodes)
    lot, total_price, currency = fieldPRI(record)
    plate, record = fieldPLATE(record)
    acc_status, id_2, id_0, acc_date, mem, id_3 = parse_dates(record, id)
    acqtype = fieldACQTYPE(record, acc_status)

    record['acc_id_2'] = id_2
    record['acc_id_3'] = id_3
    record['adt_id_0'] = id_0
    record['PLATE'] = plate
    record['in_lot'] = lot
    record['total_price'] = total_price
    record['currency'] = currency
    record['acquisition_type'] = acqtype
    record['acc_date'] = acc_date
    record['MEM'] = mem
    record['ORT'] = ud_enum(record)
    record['BAR'] = normbar(record)

    cleaned_data = remove_empty_fields(record)

    return cleaned_data

def get(uri, env):
    """Uses the API connection in migrator.py to get information from ArchivesSpace."""

    if api.connect(env):
        response = api.client.get(uri)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            error = response.text
            error = json.loads(error)
            return error	

def normalize(record, env):
    """Gets funding codes from ArchivesSpace and normalizes records."""

    fundcodes_result = get('config/enumerations/66', env)
    fundcodes = fundcodes_result['values']
    updated_records = {}
    
    for entry_id, entry in record.items():
        updated_entry = normalize_template(entry, fundcodes, entry_id)
        updated_records[entry_id] = updated_entry

    return updated_records