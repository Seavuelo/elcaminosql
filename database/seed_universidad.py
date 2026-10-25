import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "universidad.db")

def add_practice_data(conn):
    """Casos de uno-a-muchos, ausencia de relaciones y valores pendientes."""
    conn.execute("UPDATE profesores SET nombre='Profesor Marco' WHERE nombre='Dr. Alan Turing'")
    if conn.execute("SELECT 1 FROM sqlite_master WHERE name='tutorias'").fetchone():
        return
    conn.execute("CREATE TABLE tutorias (id INTEGER PRIMARY KEY, estudiante_id INTEGER NOT NULL, tema TEXT NOT NULL, asistencia INTEGER, FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id))")
    conn.executemany("INSERT INTO tutorias VALUES (?, ?, ?, ?)", [
        (1, 1, "Filtros", 1), (2, 1, "Ordenamiento", 0),
        (3, 2, "Subconsultas", None), (4, 3, "Filtros", 1),
    ])

def create_and_seed_db(db_path=DB_PATH):
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Tabla Estudiantes
    cur.execute("""
    CREATE TABLE estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        carrera TEXT NOT NULL,
        semestre INTEGER NOT NULL,
        promedio REAL NOT NULL,
        estado TEXT NOT NULL
    );
    """)

    estudiantes_data = [
        ("Ignacio Perez", "Ingenieria Informatica", 2, 6.2, "Activo"),
        ("Sofia Miranda", "Ingenieria Informatica", 3, 6.8, "Activo"),
        ("Carlos Munoz", "Ciencia de Datos", 1, 3.8, "Activo"),
        ("Valentina Rojas", "Ingenieria Informatica", 2, 5.5, "Activo"),
        ("Matias Silva", "Ciberseguridad", 4, 4.1, "Activo"),
        ("Camila Castro", "Ciencia de Datos", 2, 6.5, "Activo"),
        ("Felipe Morales", "Ingenieria Informatica", 1, 3.5, "Suspendido"),
        ("Daniela Herrera", "Ciberseguridad", 3, 5.9, "Activo"),
        ("Lucas Gonzalez", "Ingenieria Informatica", 2, 4.8, "Activo"),
        ("Constanza Soto", "Ciencia de Datos", 3, 6.9, "Activo"),
        ("Diego Espinoza", "Ingenieria Informatica", 1, 3.2, "Activo"),
        ("Javiera Diaz", "Ingenieria Informatica", 3, 5.7, "Activo"),
    ]
    cur.executemany("INSERT INTO estudiantes (nombre, carrera, semestre, promedio, estado) VALUES (?, ?, ?, ?, ?);", estudiantes_data)

    # 2. Tabla Materias
    cur.execute("""
    CREATE TABLE materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        creditos INTEGER NOT NULL,
        cupos INTEGER NOT NULL
    );
    """)

    materias_data = [
        ("BD101", "Bases de Datos I", 4, 8),
        ("PROG101", "Algoritmos y Estructuras", 5, 0),
        ("SO201", "Sistemas Operativos", 4, 12),
        ("RED301", "Redes y Comunicaciones", 4, 3),
        ("MAT102", "Calculo Diferencial", 5, 0),
        ("SEG202", "Fundamentos de Seguridad", 3, 15),
    ]
    cur.executemany("INSERT INTO materias (codigo, nombre, creditos, cupos) VALUES (?, ?, ?, ?);", materias_data)

    # 3. Tabla Notas del Parcial
    cur.execute("""
    CREATE TABLE notas_parcial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER NOT NULL,
        estudiante_nombre TEXT NOT NULL,
        materia_codigo TEXT NOT NULL,
        nota REAL NOT NULL,
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
    );
    """)

    notas_data = [
        (1, "Ignacio Perez", "BD101", 6.0),
        (2, "Sofia Miranda", "BD101", 6.8),
        (3, "Carlos Munoz", "BD101", 3.2),
        (4, "Valentina Rojas", "BD101", 5.4),
        (5, "Matias Silva", "BD101", 3.9),
        (6, "Camila Castro", "BD101", 6.1),
        (7, "Felipe Morales", "BD101", 2.8),
        (8, "Daniela Herrera", "BD101", 5.9),
        (9, "Lucas Gonzalez", "BD101", 4.2),
        (10, "Constanza Soto", "BD101", 7.0),
        (11, "Diego Espinoza", "BD101", 3.4),
        (12, "Javiera Diaz", "BD101", 5.6),
    ]
    cur.executemany("INSERT INTO notas_parcial (estudiante_id, estudiante_nombre, materia_codigo, nota) VALUES (?, ?, ?, ?);", notas_data)

    # 4. Tabla Profesores
    cur.execute("""
    CREATE TABLE profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        departamento TEXT NOT NULL,
        oficina TEXT NOT NULL
    );
    """)

    profesores_data = [
        ("Profesor Marco", "Ciencias de la Computacion", "Lab 204"),
        ("Dra. Ada Lovelace", "Arquitectura de Software", "Lab 201"),
        ("Prof. Edgar Codd", "Sistemas de Informacion", "Lab 105"),
    ]
    cur.executemany("INSERT INTO profesores (nombre, departamento, oficina) VALUES (?, ?, ?);", profesores_data)

    add_practice_data(conn)
    conn.commit()
    conn.close()
    print(f"Base de datos creada exitosamente en: {db_path}")

if __name__ == "__main__":
    create_and_seed_db()
