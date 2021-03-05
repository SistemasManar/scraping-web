import pyodbc

conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=localhost;"
    "Database=SCRAPING_PEGASO;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()


def insert_t_cep(unq_cep, nom_completo, cr_aportacion, flg_estado):
    insert_records = '''INSERT INTO T_CEP VALUES(?,?,?,?,?) '''
    cursor.execute(insert_records, unq_cep, unq_cep, nom_completo, cr_aportacion, flg_estado)
    conn.commit()


def insert_t_detalle_cep(id_cep, ape_paterno, ape_materno, nom_primer, nom_segundo, condicion,
                         nom_consejo, direccion, nu_telefono, nom_correo, url_image):
    insert_records = '''INSERT INTO T_DETALLE_CEP VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
    cursor.execute(insert_records, id_cep, ape_paterno, ape_materno, nom_primer, nom_segundo, condicion, nom_consejo,
                   direccion, nu_telefono, nom_correo, "" + url_image)
    conn.commit()


def close_conn():
    conn.close()
