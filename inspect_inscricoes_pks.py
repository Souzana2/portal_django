import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="earthconsulters"
)
cursor = conn.cursor()

# Check counts of NULL vs non-NULL for FKs in inscricoes
for col in ["id_formando", "id_acao", "id_empresa"]:
    cursor.execute(f"SELECT COUNT(*), COUNT({col}) FROM inscricoes")
    total, non_null = cursor.fetchone()
    print(f"inscricoes.{col}: total rows = {total}, non-null = {non_null}, null/zero = {total - non_null}")

cursor.close()
conn.close()
