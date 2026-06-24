import mysql.connector

def prepare_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="earthconsulters"
        )
        cursor = conn.cursor()
        
        tables = ["acoes", "empresas", "formadores", "formandos", "inscricoes"]
        
        for table in tables:
            print(f"Preparing table: {table}")
            
            # Add Soft Delete and Metadata columns if they don't exist
            cols_to_add = [
                ("is_deleted", "TINYINT(1) DEFAULT 0"),
                ("deleted_at", "DATETIME NULL"),
                ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            ]
            
            cursor.execute(f"DESCRIBE {table}")
            existing_cols = [col[0] for col in cursor.fetchall()]
            
            for col_name, col_def in cols_to_add:
                if col_name not in existing_cols:
                    print(f"  Adding column {col_name} to {table}...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
            
        # Ensure id columns are BIGINT for Django
        mapping = {
            "acoes": "id_acao",
            "empresas": "id_empresa",
            "formadores": "id_formador",
            "formandos": "id_formando",
            "inscricoes": "id_inscricao"
        }
        
        for table, pk in mapping.items():
            print(f"Ensuring {pk} in {table} is BIGINT...")
            cursor.execute(f"ALTER TABLE {table} MODIFY COLUMN {pk} BIGINT NOT NULL")
            # Ensure it is Primary Key if not already
            cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
            if not cursor.fetchone():
                 print(f"  Setting {pk} as PRIMARY KEY for {table}...")
                 cursor.execute(f"ALTER TABLE {table} ADD PRIMARY KEY ({pk})")
            
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database prepared for Django migration.")
        
    except Exception as e:
        print(f"❌ Error preparing database: {e}")

if __name__ == "__main__":
    prepare_db()
