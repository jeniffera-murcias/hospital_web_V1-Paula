# create_db.py
import sqlite3
from werkzeug.security import generate_password_hash

DB = "hospital.db"

schema = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_documento TEXT NOT NULL,
    numero_documento TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL,
    celular TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('PACIENTE','MEDICO','ADMIN')),
    edad INTEGER,
    genero TEXT,
    especialidad TEXT,
    tarjeta_profesional TEXT,
    password TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_doc ON usuarios(tipo_documento, numero_documento);

CREATE TABLE IF NOT EXISTS citas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    medico_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,   -- YYYY-MM-DD
    hora TEXT NOT NULL,    -- HH:MM
    tipo TEXT NOT NULL CHECK(tipo IN ('CONSULTA','EMERGENCIA')),
    estado TEXT NOT NULL DEFAULT 'PENDIENTE', -- PENDIENTE, ATENDIDA, CANCELADA
    FOREIGN KEY(paciente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY(medico_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS historial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    medico_id INTEGER,
    fecha TEXT NOT NULL,
    diagnostico TEXT,
    tratamiento TEXT,
    FOREIGN KEY(paciente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY(medico_id) REFERENCES usuarios(id) ON DELETE SET NULL
);
CREATE TABLE recomendaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parte TEXT NOT NULL,
    recomendacion TEXT NOT NULL
);
"""

def seed(conn):
    cur = conn.cursor()
    # Usuarios demo (si no existen)
    # paciente 1001
    cur.execute("SELECT id FROM usuarios WHERE numero_documento='1001'")
    if not cur.fetchone():
        cur.execute("""INSERT INTO usuarios
            (tipo_documento, numero_documento, nombre, correo, celular, rol, edad, genero, password)
            VALUES (?, ?, ?, ?, ?, 'PACIENTE', ?, ?, ?)""",
            ("CC","1001","Ana Paciente","ana@demo.com","3001234567",25,"F",
             generate_password_hash("paciente123"))
        )
    # medico 2001
    cur.execute("SELECT id FROM usuarios WHERE numero_documento='2001'")
    if not cur.fetchone():
        cur.execute("""INSERT INTO usuarios
            (tipo_documento, numero_documento, nombre, correo, celular, rol, especialidad, tarjeta_profesional, password)
            VALUES (?, ?, ?, ?, ?, 'MEDICO', ?, ?, ?)""",
            ("CC","2001","Dr. Carlos","carlos@demo.com","3017654321",
             "Medicina General","TP-9999", generate_password_hash("medico123"))
        )
    # sample cita (solo si no existe)
    # obtener ids
    cur.execute("SELECT id FROM usuarios WHERE numero_documento='1001'")
    p = cur.fetchone()
    cur.execute("SELECT id FROM usuarios WHERE numero_documento='2001'")
    m = cur.fetchone()
    if p and m:
        paciente_id = p[0]
        medico_id = m[0]
        cur.execute("SELECT id FROM citas WHERE paciente_id=? AND medico_id=? LIMIT 1", (paciente_id, medico_id))
        if not cur.fetchone():
            cur.execute("""INSERT INTO citas
                (paciente_id, medico_id, fecha, hora, tipo, estado)
                VALUES (?, ?, ?, ?, 'CONSULTA', 'PENDIENTE')""",
                (paciente_id, medico_id, "2025-09-15", "10:00")
            )

    conn.commit()

def seed(conn):
    cur = conn.cursor()

    # Ejemplo de recomendaciones por parte del cuerpo
    recomendaciones = [
        ("Cabeza", "Mantén buena hidratación para prevenir dolores de cabeza."),
        ("Cabeza", "Duerme al menos 7-8 horas diarias para reducir migrañas."),
        ("Espalda", "Haz estiramientos diarios para mejorar la postura."),
        ("Espalda", "Evita cargar peso excesivo sin protección."),
        ("Estómago", "Consume comidas ligeras y evita exceso de grasas."),
        ("Estómago", "Toma agua con frecuencia para facilitar la digestión."),
        ("Piernas", "Caminar 30 minutos al día ayuda a la circulación."),
        ("Piernas", "Evita estar sentado por períodos prolongados."),
    ]

    cur.executemany(
        "INSERT INTO recomendaciones (parte, recomendacion) VALUES (?, ?)",
        recomendaciones
    )

    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect(DB)
    conn.executescript(schema)
    seed(conn)
    conn.close()
    print("BD creada/actualizada: hospital.db (tablas y seed ok)")
