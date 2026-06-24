import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="earthconsulters"
)
cursor = conn.cursor()

# Get database collation
cursor.execute("SELECT @@character_set_database, @@collation_database")
print("DB defaults:", cursor.fetchone())

# Get tables collation
for table in ["acoes", "empresas", "formadores", "formandos", "inscricoes", "cursos"]:
    cursor.execute(f"SHOW CREATE TABLE `{table}`")
    print(f"\n=== Create table: {table} ===")
    print(cursor.fetchone()[1])

cursor.close()
conn.close()
