import conn as sql
import pandas as pd
import time

QUERY = """
SELECT bt.BIB_ID, bv.CREATE_DATE, bt.BEGIN_PUB_DATE, bt.END_PUB_DATE, bt.PUB_DATES_COMBINED, bt.DATE_TYPE_STATUS, bt.AUTHOR, bt.TITLE, getbibsubfield(bt.bib_id, '245', 'k'), bt.BIB_FORMAT, getbibtag(bt.bib_id, '006'), bt.FIELD_008, getbibsubfield(bt.bib_id, '040', 'e'), bt.DESCRIP_FORM, getbibsubfield(bt.bib_id, '300', 'a'), bt.RDA_CONTENT, bt.RDA_MEDIA, bt.RDA_CARRIER, bv.NORMALIZED_CALL_NO, getmfhdsubfield(bv.mfhd_id, '852', 'h'), getmfhdsubfield(bv.mfhd_id, '852', 'i'), bv.MFHD_ID, bv.MFHD_LOCATION_CODE, getbibtag(bt.bib_id, '655')
FROM BIB_TEXT bt
WHERE bt.BIB_FORMAT LIKE 'pc'
AND getbibtag(bt.bib_id, '006') like 't%'
AND (getbibsubfield(bt.bib_id, '040', 'e') like 'amremm'
OR getbibsubfield(bt.bib_id, '040', 'e') like 'appm'
OR getbibsubfield(bt.bib_id, '040', 'e') like 'CtY-BA'
OR getbibsubfield(bt.bib_id, '040', 'e') like 'dcrmmss')
"""

if sql.conn():
    print("Connected successfully.")
    cursor = sql.connection.cursor()
    print("Executing Query...")
    cursor.execute(QUERY)
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=['bib_id', 'record_creation_date', 'begin_pub_date', 'end_pub_date', 'pub_dates_combined', 'date_type', 'author', 'title', 'field_245_k', 'bib_format', 'field_006', 'field_008', 'field_040_e', 'description_form', 'field_300_a', 'RDA_Content', 'RDA_Media', 'RDA_Carrier', 'Normalized_Call_Number', 'field_852_h', 'field_852_i', 'mfhd_id', 'location', '655'])
    date_str = time.strftime("%y%m%d")
    df.to_excel(f"files/{date_str}_simanuscripts_full.xlsx",engine='xlsxwriter', index=False)
    print("Query Completed.")
else:
    print("Connection failed.")