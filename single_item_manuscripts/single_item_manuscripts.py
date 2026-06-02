from pymarc import MARCReader, Record, Field, Subfield
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tqdm import tqdm
from pathlib import Path
import time, re

class RecordProcessor:
    def __init__(self, record):
        """Creates an object based on an individual record in a marc file."""
        self.record = record
            
    def ctrl_ldr(self):
        """Updates the 06-08 positions in the LDR.
        1. If LDR Type of Record (06) = 'p' → change to 't'
        2. If LDR Bibliographic Level (07) = 'c' → change to 'm'
        3. If LDR Type of Control (08) = 'a' → change to space
        """
        ldr = self.record.leader
        if ldr[6:8] == 'pc':
            ldr = ldr[:6] + 'tm' + ldr[8:]
        if ldr[8] == 'a':
            ldr = ldr[:8] + ' ' + ldr[9:]
        self.record.leader = ldr

    def ctrl_008(self):
        """Updates the 008 control field's publication status, Date 1, and Date 2.
        1. If Publication Status is i and the values of Date1 and Date 2 are identical → Publication status changed to s and delete the Date2 value.
        2. Else If Publication status is i → change Publication Status to q
        """
        f008 = self.record['008']
        pub = f008.data[6]
        date1 = f008.data[7:11]
        date2 = f008.data[11:15]
        data = list(f008.data)

        if pub == 'i' and date1 == date2:
            data[6] = 's'
            data[11:15] = list('    ')
        elif pub == 'i':
            data[6] = 'q'

        f008.data = ''.join(data)
        self.record.remove_field(f008)
        self.record.add_field(Field(tag='008', data=''.join(data)))

    def ctrl_006(self):
        """Updates the 006 control field's position 0 as needed.
        1. If the Form of Material is t - Manuscript Language Material → Delete Form of Material.
        """
        f006 = self.record.get_fields('006')
        for field in f006:
            if field.data.startswith('t'):
                self.record.remove_field(field)


    def field_655(self):
        """Adds a 655 field if it is not already present.
        1. If not present → Add 655 _7 ‡a Manuscripts. ‡2 lcgft
        """
        # Checks if 655 Manuscripts exists.
        has_655 = any(
            f.tag == '655' and
            f.indicator1 == ' ' and f.indicator2 == '7' and
            f.get_subfields('a') == ['Manuscripts.'] and
            f.get_subfields('2') == ['lcgft']
            for f in self.record.get_fields('655')
        )

        # Add 655 Manuscripts if needed.
        if not has_655:
            self.record.add_field(Field(
                tag='655',
                indicators=[' ', '7'],
                subfields=[
                    Subfield(code='a', value='Manuscripts.'),
                    Subfield(code='2', value='lcgft')
                ]
            ))

    def field_500s(self):
        """Adds a 655 for Academic Theses if any 500 field contains the word 'thesis'.
        1. If a 655 for Academic Theses is not already present and any 5xx field contains 'thesis' → Add 655 _7 ‡a Academic theses. ‡2 lcgft
        """
        # Check if any 5XX field mentions 'thesis'
        has_thesis = any(
            f.tag.startswith('5') and
            re.search(r'\bthesis(es)?\b', f.value().lower())
            for f in self.record.get_fields()
        )

        # Check if 655 Academic theses already exists
        has_655 = any(
            f.tag == '655' and
            f.indicator1 == ' ' and f.indicator2 == '7' and
            f.get_subfields('a') == ['Academic theses.'] and
            f.get_subfields('2') == ['lcgft']
            for f in self.record.get_fields('655')
        )

        # Add field if needed
        if has_thesis and not has_655:
            self.record.add_field(Field(
                tag='655',
                indicators=[' ', '7'],
                subfields=[
                    Subfield(code='a', value='Academic theses.'),
                    Subfield(code='2', value='lcgft')
                ]
            ))

    def field_502(self):
        """Adds 655 for Academic Theses if a 502 field is present.
        1. If a 655 for Academic Theses is not already present and a 502 field exists → Add 655 _7 ‡a Academic theses. ‡2 lcgft
        """
        # Check if 502 field exists.
        has_502 = any(
            f.tag == '502'
            for f in self.record.get_fields()
        )

        # Check is 655 for Academic theses exists.
        has_655 = any(
            f.tag == '655' and
            f.indicator1 == ' ' and f.indicator2 == '7' and
            f.get_subfields('a') == ['Academic theses.'] and
            f.get_subfields('2') == ['lcgft']
            for f in self.record.get_fields('655')
        )

        # Add 655 Academic Thesis if needed.
        if has_502 and not has_655:
                self.record.add_field(Field(
                tag='655',
                indicators=[' ', '7'],
                subfields=[
                    Subfield(code='a', value='Academic theses.'),
                    Subfield(code='2', value='lcgft')
                ]
                ))

    def field_079(self):
        """Removes 079 field if it exists in an 035.
        1. If 079 in 035 → remove field 079.
        """
        def extract_digits(value):
            """Return only the numeric digits from a subfield string."""
            match = re.search(r'\d+', value)
            return match.group(0) if match else None

        # Collect numbers from all 035$a values
        f035_numbers = {
            extract_digits(a)
            for f in self.record.get_fields('035')
            for a in f.get_subfields('a')
            if extract_digits(a)
        }

        # Compare numbers from 035 with all 079$a numbers
        for f079 in list(self.record.get_fields('079')):
            for a in f079.get_subfields('a'):
                num = extract_digits(a)
                if num and num in f035_numbers:
                    self.record.remove_field(f079)
                    break

    def rda_fix(self):
        """Updates RDA fields 336 and 337 if they are unspecified.
        1. If 336‡a is unspecified → update to 'text'.
        2. If 337‡a is unspecified → update to 'unmediated.
        """
        # Field and replacement text.
        replacements = {
            '336': 'text',
            '337': 'unmediated'
        }

        # Runs through same code for both 336 and 337, grabbing subfields a and 2 in variables.
        for tag, new_a_value in replacements.items():
            for field in self.record.get_fields(tag):
                a_values = field.get_subfields('a')
                two_values = field.get_subfields('2')

                # Lowercases the grabbed subfield a for comparison purposes, and if 'unspecified' it removes the old field and replaces it with an updated subfield a.
                if a_values and a_values[0].lower() == 'unspecified':
                    new_subfields = [Subfield('a', new_a_value)]
                    if two_values:
                        new_subfields.append(Subfield('2', two_values[0]))

                    new_field = Field(
                        tag=tag,
                        indicators=field.indicators,
                        subfields=new_subfields
                    )

                    self.record.remove_field(field)
                    self.record.add_field(new_field)
    
    def sammelbands(self):
        """Adds 655 for Sammelbands if a 773 is present.
        1. If a 655 for Sammelbands is not already present and a 773 field exists → Add 655 _7 ‡a Sammelbands. ‡2 rbmscv
        """
        # Check if a 774 exists.
        has_hostbib = any(
            f.tag == '773' 
            for f in self.record.get_fields('773')
        )

        # Check if a 655 Sammelbands already exists in the record.
        has_655 = any(
            f.tag == '655' and
            f.indicator1 == ' ' and f.indicator2 == '7' and
            f.get_subfields('a') == ['Sammelbands.'] and
            f.get_subfields('2') == ['rbmscv']
            for f in self.record.get_fields('655')
        )

        # Add 655 Sammelbands if needed.
        if has_hostbib and not has_655:
            self.record.add_field(Field(
                tag='655',
                indicators=[' ', '7'],
                subfields=[
                    Subfield(code='a', value='Sammelbands.'),
                    Subfield(code='2', value='rbmscv')
                ]
                ))

    def f773_list(self):
        """Checks for 773 fields and returns the subfield w in a list."""
        w_values = []

        for f in self.record.get_fields('773'):
            w_values.extend(f.get_subfields('w'))

        return w_values

    def finding_aid(self):
        """Checks if a finding aid exists, and skips any record with them.
        1. If 035 (YUL) exists → pass record.
        """
        has_findingaid = any(
            f.tag == '035' and 
            any(sf.startswith('(YUL)ead') for sf in f.get_subfields('a'))
            for f in self.record.get_fields('035')
        )

        return has_findingaid
    
    def process(self):
        """Processes the Record.
        1. Check for finding aid and pass if present using finding_aid()
        2. Update the LDR using ctrl_ldr()
        3. Update 008 using ctrl_008()
        4. Remove 006 as needed using ctrl_006()
        5. Remove 079 as needed using field_079()
        6. Update RDA fields 336 and 337 using rda_fix()
        7. Add 655 Manuscripts using field_655()
        8. Add 655 Academic Theses using field_502()
        9. Add 655 Sammelbands using sammelbands()
        """
        if self.finding_aid():
            return self
        self.ctrl_ldr()
        self.ctrl_008()
        self.ctrl_006()
        self.field_079()
        self.rda_fix()
        self.field_655()
        self.field_502()
        self.sammelbands()
        w_values = self.f773_list()

        return self, w_values

def marc_read(input):
    """Open and read a MARC file, returning each record in a list.
    Requires the path to file."""
    with open(input, 'rb') as fh:
        reader = MARCReader(fh, force_utf8=True)
        return list(reader)

def get_unique_filename(directory, base_filename):
    """Adds a number to the end of a filename in the case of repeat files. (e.g. backups.json, backups1.json, backups2.json, etc.)
    Requires the folder and the filename."""

    directory = Path(directory)
    name, ext = Path(base_filename).stem, Path(base_filename).suffix
    new_path = directory / base_filename
    counter = 1

    while new_path.exists():
        counter += 1
        new_path = directory / f"{name}_{counter}{ext}"

    return new_path

def marc_write(path, records):
    """Open and write a MARC file.
    Requires folder path and a set of all the records to be written to the mrc file.
    """
    date_str = time.strftime("%y%m%d")
    file = get_unique_filename(path, f"{date_str}_updatedmrc.mrc")
    with open(file, 'wb') as out_fh:
        for record in records:
            out_fh.write(record.as_marc())

def text_file(path, w_values):
    """
    Writes the collected 773$w values to a text file,
    ensuring one value per line and avoiding duplicate filenames.
    """
    # Deduplicate while preserving order
    seen = set()
    unique_values = []
    for w in w_values:
        if w not in seen:
            seen.add(w)
            unique_values.append(w)

    # Add newline to each line
    lines = [w + "\n" for w in unique_values]

    date_str = time.strftime("%y%m%d")
    file = get_unique_filename(path, f"{date_str}_773s.txt")

    with open(file, 'w', encoding='utf-8') as out:
        out.writelines(lines)


def run_gui():
    """Creates a pop up menu that has the user select an input file and an output folder."""
    def browse_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            folder_var.set(folder_selected)

    def browse_file():
        file_selected = filedialog.askopenfilename()
        if file_selected:
            file_var.set(file_selected)

    def submit():
        nonlocal input_file, output_file
        output_file = folder_var.get()
        input_file = file_var.get()

        if not output_file:
            messagebox.showerror("Missing Input", "Please select a folder.")
            return
        if not input_file:
            messagebox.showerror("Missing Input", "Please select a folder.")
            return

        root.quit()
        root.destroy()

    output_file = input_file = None

    root = tk.Tk()
    root.title("Script Configuration")

    # Folder picker
    folder_var = tk.StringVar()
    ttk.Label(root, text="Folder Path:").grid(row=3, column=0, sticky="e")
    ttk.Entry(root, textvariable=folder_var, width=40).grid(row=3, column=1)
    ttk.Button(root, text="Browse...", command=browse_folder).grid(row=3, column=2)

    # File picker
    file_var = tk.StringVar()
    ttk.Label(root, text="Input File:").grid(row=4, column=0, sticky="e")
    ttk.Entry(root, textvariable=file_var, width=40).grid(row=4, column=1)
    ttk.Button(root, text="Browse...", command=browse_file).grid(row=4, column=2)

    # Submit button
    ttk.Button(root, text="Submit", command=submit).grid(row=6, column=1, pady=10)

    root.mainloop()

    return input_file, output_file

def main():
    input, output = run_gui()
    reader = marc_read(input)
    processed_records = []
    all_773w = ["mms ids"]
    for record in tqdm(reader, desc="Processing Records", unit="record"):
        updated_record, w_values = RecordProcessor(record).process()
        processed_records.append(updated_record.record)
        all_773w.extend(w_values)

    marc_write(output, processed_records)
    text_file(output, all_773w)


if __name__ == "__main__":
    main()