import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
)
cursor = conn.cursor()
cursor.execute("SHOW PROCESSLIST")
cols = [col[0] for col in cursor.description]
rows = cursor.fetchall()
print("\n=== Active MySQL Processes ===")
for row in rows:
    process = dict(zip(cols, row))
    if process['db'] == 'earthconsulters' or process['Command'] != 'Sleep':
        print(process)
cursor.close()
conn.close()
