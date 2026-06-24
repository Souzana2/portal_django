import mysql.connector

def inspect_table(cursor, table_name):
    print(f"\n--- Columns in {table_name} ---")
    cursor.execute(f"DESCRIBE {table_name}")
    for col in cursor.fetchall():
        print(f"  {col[0]} ({col[1]})")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="earthconsulters"
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    
    for table in ["acoes", "empresas", "formadores", "formandos", "inscricoes"]:
        if table in tables:
            inspect_table(cursor, table)
        else:
            print(f"Table {table} not found!")
            
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
