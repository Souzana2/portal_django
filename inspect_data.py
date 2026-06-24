import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="earthconsulters"
)
cursor = conn.cursor()

def show_samples(table, limit=3):
    cursor.execute(f"SELECT * FROM `{table}` LIMIT {limit}")
    cols = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    print(f"\n=== Table: {table} ({len(rows)} samples) ===")
    for row in rows:
        print(dict(zip(cols, row)))

# Show tables counts
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]
for t in ["acoes", "empresas", "formadores", "formandos", "inscricoes", "cursos"]:
    if t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
        print(f"Count of {t}: {cursor.fetchone()[0]}")

show_samples("acoes")
show_samples("inscricoes")
show_samples("formandos")

cursor.close()
conn.close()
