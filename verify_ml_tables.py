import mysql.connector
try:
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="earthconsulters")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'modelos_previsao%'")
    print(cursor.fetchall())
    cursor.close()
    conn.close()
except Exception as e:
    print(e)
