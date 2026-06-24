import mysql.connector

def run_migration():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="earthconsulters"
    )
    cursor = conn.cursor()

    def get_columns(table):
        cursor.execute(f"DESCRIBE `{table}`")
        return {col[0]: col[1] for col in cursor.fetchall()}

    def get_indexes(table):
        cursor.execute(f"SHOW INDEX FROM `{table}`")
        return [idx[2] for idx in cursor.fetchall()]

    print("--- 1. Optimizing empresas and formandos tables ---")
    
    # 1. Convert empresas.empresa to VARCHAR(255) and index
    emp_cols = get_columns("empresas")
    empresa_col_type = emp_cols.get("empresa", b"")
    if isinstance(empresa_col_type, bytes):
        empresa_col_type = empresa_col_type.decode("utf-8")
    else:
        empresa_col_type = str(empresa_col_type)

    if "text" in empresa_col_type.lower():
        print("Altering empresas.empresa to VARCHAR(255)...")
        cursor.execute("ALTER TABLE empresas MODIFY COLUMN empresa VARCHAR(255) DEFAULT NULL")
    
    emp_indexes = get_indexes("empresas")
    if "empresa" not in emp_indexes and "idx_empresas_empresa" not in emp_indexes:
        print("Creating index on empresas(empresa)...")
        cursor.execute("CREATE INDEX idx_empresas_empresa ON empresas (empresa)")

    # 2. Convert formandos.empresa to VARCHAR(255) and index
    form_cols = get_columns("formandos")
    form_empresa_col_type = form_cols.get("empresa", b"")
    if isinstance(form_empresa_col_type, bytes):
        form_empresa_col_type = form_empresa_col_type.decode("utf-8")
    else:
        form_empresa_col_type = str(form_empresa_col_type)

    if "text" in form_empresa_col_type.lower():
        print("Altering formandos.empresa to VARCHAR(255)...")
        cursor.execute("ALTER TABLE formandos MODIFY COLUMN empresa VARCHAR(255) DEFAULT NULL")
    
    form_indexes = get_indexes("formandos")
    if "empresa" not in form_indexes and "idx_formandos_empresa" not in form_indexes:
        print("Creating index on formandos(empresa)...")
        cursor.execute("CREATE INDEX idx_formandos_empresa ON formandos (empresa)")

    # 3. Add and populate formandos.id_empresa
    if "id_empresa" not in form_cols:
        print("Adding column id_empresa to formandos...")
        cursor.execute("ALTER TABLE formandos ADD COLUMN id_empresa bigint(20) DEFAULT NULL")
    
    print("Populating formandos.id_empresa using index...")
    cursor.execute("""
        UPDATE formandos f 
        JOIN empresas e ON f.empresa = e.empresa 
        SET f.id_empresa = e.id_empresa 
        WHERE f.id_empresa IS NULL
    """)
    print(f"Affected rows (formandos.id_empresa): {cursor.rowcount}")

    print("--- 2. Populating cursos table ---")
    cursor.execute("SELECT COUNT(*) FROM cursos")
    if cursor.fetchone()[0] == 0:
        print("cursos table is empty. Populating from acoes...")
        cursor.execute("""
            INSERT IGNORE INTO cursos (codigo, nome, area_codigo, area_nome, id_etl, is_deleted)
            SELECT LEFT(cod_curso, 50), LEFT(MAX(curso), 500), LEFT(MAX(cod_area), 20), LEFT(MAX(curso_area), 255), '', 0
            FROM acoes
            WHERE cod_curso IS NOT NULL AND cod_curso != ''
            GROUP BY cod_curso
        """)
        print(f"Inserted courses: {cursor.rowcount}")
    else:
        print("cursos table is already populated.")

    print("--- 3. Optimizing and aligning acoes table ---")
    acoes_cols = get_columns("acoes")
    
    if "curso_id" not in acoes_cols:
        print("Adding column curso_id to acoes...")
        cursor.execute("ALTER TABLE acoes ADD COLUMN curso_id bigint(20) DEFAULT NULL")
    
    print("Populating acoes.curso_id...")
    cursor.execute("""
        UPDATE acoes a
        JOIN cursos c ON a.cod_curso = c.codigo
        SET a.curso_id = c.id
        WHERE a.curso_id IS NULL
    """)
    print(f"Affected rows (acoes.curso_id): {cursor.rowcount}")

    if "local_de_formacao" not in acoes_cols:
        print("Adding column local_de_formacao to acoes...")
        cursor.execute("ALTER TABLE acoes ADD COLUMN local_de_formacao varchar(255) DEFAULT NULL")
    
    print("Populating acoes.local_de_formacao...")
    cursor.execute("""
        UPDATE acoes
        SET local_de_formacao = LEFT(local_acao, 255)
        WHERE local_de_formacao IS NULL
    """)
    print(f"Affected rows (acoes.local_de_formacao): {cursor.rowcount}")

    if "data_acao" not in acoes_cols:
        print("Adding column data_acao to acoes...")
        cursor.execute("ALTER TABLE acoes ADD COLUMN data_acao varchar(20) DEFAULT NULL")
    
    print("Populating acoes.data_acao...")
    cursor.execute("""
        UPDATE acoes
        SET data_acao = LEFT(data_inicio_turma, 20)
        WHERE data_acao IS NULL
    """)
    print(f"Affected rows (acoes.data_acao): {cursor.rowcount}")

    print("--- 4. Aligning and modifying inscricoes table ---")
    insc_cols = get_columns("inscricoes")
    
    if "data_estado_profissional" not in insc_cols:
        print("Adding column data_estado_profissional to inscricoes...")
        cursor.execute("ALTER TABLE inscricoes ADD COLUMN data_estado_profissional varchar(50) DEFAULT NULL")
    
    if "no_de_certificado" not in insc_cols:
        print("Adding column no_de_certificado to inscricoes...")
        cursor.execute("ALTER TABLE inscricoes ADD COLUMN no_de_certificado varchar(200) DEFAULT NULL")
        
    print("Populating inscricoes.no_de_certificado...")
    cursor.execute("""
        UPDATE inscricoes
        SET no_de_certificado = LEFT(n_de_certificado, 200)
        WHERE no_de_certificado IS NULL
    """)
    print(f"Affected rows (inscricoes.no_de_certificado): {cursor.rowcount}")

    print("Converting foreign keys in inscricoes to BIGINT...")
    for fk in ["id_formando", "id_acao", "id_empresa"]:
        col_type = insc_cols.get(fk, "")
        if isinstance(col_type, bytes):
            col_type = col_type.decode("utf-8")
        else:
            col_type = str(col_type)
            
        if "double" in col_type.lower():
            print(f"Modifying inscricoes.{fk} type from double to bigint(20)...")
            cursor.execute(f"ALTER TABLE inscricoes MODIFY COLUMN {fk} bigint(20) DEFAULT NULL")

    print("--- 5. Aligning historical tables ---")
    hist_tables = {
        "entidades_historicalformando": [("id_etl", "varchar(50) NOT NULL DEFAULT ''"), ("id_empresa", "bigint(20) DEFAULT NULL")],
        "entidades_historicalcurso": [("id_etl", "varchar(50) NOT NULL DEFAULT ''")],
        "entidades_historicalacao": [("id_etl", "varchar(50) NOT NULL DEFAULT ''")],
        "entidades_historicalinscricao": [("id_etl", "varchar(50) NOT NULL DEFAULT ''")]
    }

    for table, cols in hist_tables.items():
        table_cols = get_columns(table)
        for col_name, col_def in cols:
            if col_name not in table_cols:
                print(f"Adding column {col_name} to {table}...")
                cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN {col_name} {col_def}")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All migrations completed successfully!")

if __name__ == "__main__":
    run_migration()
