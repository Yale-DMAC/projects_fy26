from datetime import datetime
from collections import defaultdict
import json, re, string


def parse_acc(acc_value, seen):
    """Gets and cleans up Accession Dates."""

    dupe_acc = ''
    unknown_acc = ''
    
    acc_value = acc_value.strip()
    
    match_six = re.search(r'\b(\d{6})\b', acc_value)
    match_eight = re.search(r'\b(\d{8})\b', acc_value)
    match_month = re.search(r'\b(\d{1,2})[-/]?([A-Za-z]{3})[-/]?(\d{2})\b', acc_value, re.IGNORECASE)
    
    if acc_value.startswith('y'):
        acc_value = acc_value[1:]
    
    acc_value = re.sub(r'\(.*\)$', '', acc_value)
    acc_value = re.sub(r'^\[(.*?)\]$', r'\1', acc_value)
    
    if acc_value.endswith('?'):
        acc_value = acc_value[:-1]
    
    def fixMMDD(value):
        """Fixes Common Issues with Dates."""

        if len(value) != 8:
            if value == "000000":
                value = "010101"
            elif value[:2] == "00":
                value = "01" + value[2:]
            elif value[2:4] == "00":
                value = value[:2] + "01" + value[4:]
            elif value[4:] == "00":
                value = value[:4] + "01"

        if value == "00000000":
            value = "19010101"
        elif value[4:8] == "0000":
            value = value[:4] + "0101" + value[8:]
        elif value[4:6] == "00":
            value = value[:4] + "01" + value[6:]
        elif value[6:8] == "00":
            value = value[:6] + "01" + value[8:]

        return value
   
    def get_suffix(n):
        """Adds a suffix to the accession number if it already exists in the file."""

        chars = string.ascii_lowercase
        base = len(chars)
        suffix = ''

        while n >= 0:
            suffix = chars[n % base] + suffix
            n = n // base - 1
            if n < 0:
                break
            
        return '-' + suffix.rjust(3, 'a')

    if match_six:
        date_str = match_six.group(1)
        try:
            date_str = fixMMDD(date_str)
            if len(date_str) == 6:
                try:
                    yy = int(date_str[:2])
                    mm = int(date_str[2:4])
                    dd = int(date_str[4:6])
                    year = 1900 + yy  # Force 1900s
                    acc_accession_date = datetime(year, mm, dd).strftime('%Y-%m-%d')
                    acc_id_0 = year
                    acc_id_2 = f"{mm}{dd}" + acc_value[6:]
                except ValueError:
                    try:
                        mm = int(date_str[:2])
                        dd = int(date_str[2:4])
                        yy = int(date_str[4:6])
                        year = 1900 + yy  # Force 1900s
                        acc_accession_date = datetime(year, mm, dd).strftime('%Y-%m-%d')
                        acc_id_0 = year
                        acc_id_2 = f"{mm}{dd}" + acc_value[6:]
                    except ValueError as e:
                        print(f"ValueError parsing date from accession value '{acc_value}': {e}")
        except ValueError as e:
            print(f"ValueError parsing date from accession value '{acc_value}': {e}")
    elif match_eight:
        date_str = match_eight.group(1)
        try:
            date_str = fixMMDD(date_str)
            try: 
                acc_accession_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
            except ValueError:
                acc_accession_date = datetime.strptime(date_str, '%m%d%Y').strftime('%Y-%m-%d')
            acc_id_0 = date_str[:4]
            acc_id_2 = acc_value[4:]
        except ValueError as e:
            print(f"ValueError parsing date from accession value '{acc_value}': {e}")
    elif match_month:
        day, mon_str, year = match_month.groups()
        try:
            date_obj = datetime.strptime(f'{day}-{mon_str}-{year}', '%d-%b-%y')
            acc_accession_date = date_obj.strftime('%Y-%m-%d')
            acc_id_0 = date_str[:4]
            acc_id_2 = acc_value[4:]
        except ValueError as e:
            print(f"ValueError parsing date from accession value '{acc_value}': {e}")
    else:
        acc_accession_date = '1901-01-01'
        acc_id_0 = '1901'
        acc_id_2 = '0101'
        unknown_acc = "Actual date of accession unknown. Accession date 1901-01-01 and accession identifier created at time of import into ArchivesSpace."
    
    key = f"{acc_id_0}/{acc_id_2}"
    count = seen[key]
    seen[key] += 1
    
    if count > 0:
        acc_id_2 += get_suffix(count - 1)
        dupe_acc = "Accession identifier created at time of import into ArchivesSpace."
    
    return acc_accession_date, acc_id_0, acc_id_2, dupe_acc, unknown_acc

def fieldFUN(entry, fundcodes):
    """Removes funding codes not present in ArchivesSpace."""

    FUN = entry.get('FUN', '').upper()

    if FUN in fundcodes:
        entry['FUN'] = FUN
        return entry
    else:
        entry['PAY_NOTE'] = f'Fund Code (FUN) = {FUN}'
        del entry['FUN']
        return entry

def fieldPRI(entry):
    """Determines the currency type and cleans up any pricing errors such as decimal misplacement."""

    PRI = entry.get('PRI', '').strip()
    total_price = currency = pri_note = ''
    PRI = re.sub(r'(\d+\.\d+)\.\d+', r'\1', PRI)

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

    no_digits = not bool(re.search(r'\d', PRI))
    has_parentheses = '(' in PRI or ')' in PRI
    alpha_after_num = bool(re.search(r'\d+\.\d{2}[a-zA-Z]+', PRI))
    if no_digits or has_parentheses or alpha_after_num:
        pri_note = PRI
    return pri_note, lot, total_price, currency

def fieldACQTYPE(entry):
    """Determines the acquistion type based on conditions in the record."""

    VNA = entry.get('VNA')
    DON = entry.get('DON')

    if VNA and not DON:
        type = "purchase"
    elif DON and not VNA:
        type = "gift"
    else:
        type = ""

    return type	

def date_norm(entry):
    """Normalizes dates."""

    formats_to_try = [
        '%Y %b %d',
        '%d %b %Y',
        '%Y-%m-%d',
    ]

    for key in ['PDT', 'DTE', 'DTB']:
        date_str = entry.get(key)
        if isinstance(date_str, str):
            for fmt in formats_to_try:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt)
                    entry[key] = parsed_date.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
                
    return entry

def remove_empty_fields(obj):
    """Removes empty fields from record."""

    if isinstance(obj, dict):
        return {k: remove_empty_fields(v) for k, v in obj.items() if v != ''}
    elif isinstance(obj, list):
        return [remove_empty_fields(item) for item in obj]
    else:
        return obj

def normalize_template(record, seen, fundcodes):
    """Cleans up fields and adds in necessary fields for normalization."""

    acc_date, acc_id_0, acc_id_2, dupe_acc, unknown_acc = parse_acc(record.get('ACC', ''), seen)
    
    record['dupe_acc'] = dupe_acc
    record['unknown_acc'] = unknown_acc
    record['acc_accession_date'] = acc_date
    record['acc_id_0'] = acc_id_0
    record['acc_id_2'] = acc_id_2
    record = fieldFUN(record, fundcodes)
    record = date_norm(record)

    pri_note, lot, total_price, currency = fieldPRI(record)
    acqtype = fieldACQTYPE(record)

    record['pri_note'] = pri_note
    record['in_lot'] = lot
    record['total_price'] = total_price
    record['currency'] = currency
    record['acquisition_type'] = acqtype

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

    seen = defaultdict(int)
    fundcodes_result = get('config/enumerations/66', env)
    fundcodes = fundcodes_result['values']
    updated_records = {}
    
    for entry_id, entry in record.items():
        updated_entry = normalize_template(entry, seen, fundcodes)
        updated_records[entry_id] = updated_entry
    return updated_records

