import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="earthconsulters"
)
cursor = conn.cursor()

cursor.execute("SELECT MAX(LENGTH(empresa)) FROM empresas")
print("Max length in empresas:", cursor.fetchone()[0])

cursor.execute("SELECT MAX(LENGTH(empresa)) FROM formandos")
print("Max length in formandos:", cursor.fetchone()[0])

cursor.close()
conn.close()
