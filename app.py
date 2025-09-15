from flask import Flask, render_template, request, redirect, url_for, session, flash
from domain.datastructures.hashtable import HashTable
from domain.datastructures.trie import Trie
from domain.datastructures.bst import BST
from domain.datastructures.priority_queue import PriorityQueue
from domain.datastructures.stack import Stack

from services.pacientes_service import PacientesService
from services.medicos_service import MedicosService
from services.citas_service import CitasService
from services.historial_service import HistorialService
from services.reportes_service import ReportesService
from services.undo_service import UndoService

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime

app = Flask(__name__)
app.secret_key = "cambia-esta-clave"  # pon algo seguro
DB = "hospital.db"

# --- Helpers de BD ---
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_doc(tipo, numero):
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE tipo_documento=? AND numero_documento=?", (tipo, numero))
    user = cur.fetchone()
    con.close()
    return user

def get_user_by_id(uid):
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id=?", (uid,))
    u = cur.fetchone()
    con.close()
    return u

def get_medicos():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT id, nombre, especialidad FROM usuarios WHERE rol='MEDICO'")
    res = cur.fetchall()
    con.close()
    return res
# --- Rutas ---
@app.route("/")
def home():
    if "user" in session:
        rol = session["user"]["rol"]
        return redirect(url_for("dashboard_paciente" if rol=="PACIENTE" else "dashboard_medico"))
    return redirect(url_for("login_get"))

# LOGIN
@app.get("/login")
def login_get():
    return render_template("login.html")

@app.post("/login")
def login_post():
    tipo = request.form.get("tipo_documento")
    numero = request.form.get("numero_documento")
    password = request.form.get("password")

    user = get_user_by_doc(tipo, numero)
    if not user or not check_password_hash(user["password"], password):
        flash("Credenciales inválidas", "error")
        return redirect(url_for("login_get"))

    # guardar en sesión (lo mínimo necesario)
    session["user"] = {
        "id": user["id"],
        "nombre": user["nombre"],
        "rol": user["rol"],
        "tipo_documento": user["tipo_documento"],
        "numero_documento": user["numero_documento"],
    }

    # Redirección por rol
    if user["rol"] == "PACIENTE":
        return redirect(url_for("dashboard_paciente"))
    else:
        return redirect(url_for("dashboard_medico"))

# REGISTRO
@app.get("/register")
def register_get():
    return render_template("register.html")

@app.post("/register")
def register_post():
    role = request.form.get("role")  # 'PACIENTE' o 'MEDICO'
    tipo = request.form.get("tipo_documento")
    numero = request.form.get("numero_documento")
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    celular = request.form.get("celular")
    password = request.form.get("password")
    confirm = request.form.get("confirm_password")

    if password != confirm:
        flash("Las contraseñas no coinciden", "error")
        return redirect(url_for("register_get"))

    # Campos específicos
    edad = request.form.get("edad") if role == "PACIENTE" else None
    genero = request.form.get("genero") if role == "PACIENTE" else None
    especialidad = request.form.get("especialidad") if role == "MEDICO" else None
    tarjeta = request.form.get("tarjeta_profesional") if role == "MEDICO" else None

    # Validación básica
    if get_user_by_doc(tipo, numero):
        flash("Ya existe un usuario con ese documento", "error")
        return redirect(url_for("register_get"))

    # Guardar
    con = get_db()
    cur = con.cursor()
    cur.execute("""INSERT INTO usuarios 
        (tipo_documento, numero_documento, nombre, correo, celular, rol, edad, genero, especialidad, tarjeta_profesional, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (tipo, numero, nombre, correo, celular, role, edad, genero, especialidad, tarjeta,
         generate_password_hash(password))
    )
    con.commit()
    con.close()

    flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
    return redirect(url_for("login_get"))

# LOGOUT
@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_get"))

# DASHBOARDS
@app.get("/paciente")
def dashboard_paciente():
    if "user" not in session or session["user"]["rol"] != "PACIENTE":
        return redirect(url_for("login_get"))
    return render_template("dashboard_paciente.html", user=session["user"])

@app.route("/paciente/agendar", methods=["GET", "POST"])
def paciente_agendar():
    if "user" not in session or session["user"]["rol"] != "PACIENTE":
        return redirect(url_for("login_get"))
    medicos = get_medicos()
    if request.method == "POST":
        medico_id = request.form.get("medico_id")
        fecha = request.form.get("fecha")   # YYYY-MM-DD
        hora = request.form.get("hora")     # HH:MM
        tipo = request.form.get("tipo")     # CONSULTA / EMERGENCIA
        paciente_id = session["user"]["id"]
        # validaciones básicas
        if not (medico_id and fecha and hora and tipo):
            flash("Completa todos los campos", "error")
            return redirect(url_for("paciente_agendar"))
        con = get_db()
        cur = con.cursor()
        cur.execute("""INSERT INTO citas (paciente_id, medico_id, fecha, hora, tipo, estado)
                       VALUES (?, ?, ?, ?, ?, 'PENDIENTE')""",
                    (paciente_id, medico_id, fecha, hora, tipo))
        con.commit()
        con.close()
        flash("Cita agendada correctamente", "success")
        return redirect(url_for("paciente_citas"))
    return render_template("paciente_agendar.html", medicos=medicos)

@app.get("/paciente/citas")
def paciente_citas():
    if "user" not in session or session["user"]["rol"] != "PACIENTE":
        return redirect(url_for("login_get"))
    pid = session["user"]["id"]
    con = get_db()
    cur = con.cursor()
    cur.execute("""SELECT c.*, m.nombre as medico_nombre, m.especialidad as medico_especialidad
                   FROM citas c JOIN usuarios m ON c.medico_id = m.id
                   WHERE c.paciente_id = ? ORDER BY fecha, hora""", (pid,))
    citas = cur.fetchall()
    con.close()
    return render_template("paciente_citas.html", citas=citas)

@app.get("/paciente/historial")
def paciente_historial():
    if "user" not in session or session["user"]["rol"] != "PACIENTE":
        return redirect(url_for("login_get"))
    pid = session["user"]["id"]
    con = get_db()
    cur = con.cursor()
    cur.execute("""SELECT h.*, m.nombre as medico_nombre FROM historial h
                   LEFT JOIN usuarios m ON h.medico_id=m.id
                   WHERE h.paciente_id=? ORDER BY fecha DESC""", (pid,))
    rows = cur.fetchall()
    con.close()
    return render_template("paciente_historial.html", historial=rows)

@app.get("/buscar")
def buscar():
    if "user" not in session:
        return redirect(url_for("login_get"))

    query = request.args.get("q", "")
    resultados = []

    if query:
        con = get_db()
        cur = con.cursor()
        # ejemplo simple: buscar por nombre
        cur.execute("SELECT * FROM usuarios WHERE nombre LIKE ?", ('%' + query + '%',))
        resultados = cur.fetchall()
        con.close()

    return render_template("buscar.html", query=query, resultados=resultados)

#MEDICO
@app.get("/medico/dashboard")
def dashboard_medico():
    if "user" not in session or session["user"]["rol"] != "MEDICO":
        return redirect(url_for("login_get"))

    con = get_db()
    cur = con.cursor()

    # citas pendientes
    cur.execute("""SELECT c.id, u.nombre as paciente_nombre, c.fecha, c.hora, c.tipo
                   FROM citas c
                   JOIN usuarios u ON c.paciente_id = u.id
                   WHERE c.medico_id=? AND c.estado='PENDIENTE'
                   ORDER BY c.fecha, c.hora""", (session["user"]["id"],))
    citas = cur.fetchall()

    # historial atendido
    cur.execute("""SELECT h.fecha, u.nombre as paciente_nombre, h.diagnostico, h.tratamiento
                   FROM historial h
                   JOIN usuarios u ON h.paciente_id = u.id
                   WHERE h.medico_id=?
                   ORDER BY h.fecha DESC""", (session["user"]["id"],))
    historial = cur.fetchall()

    # estadísticas simples
    cur.execute("""SELECT tipo, COUNT(*) as total FROM citas 
                   WHERE medico_id=? AND estado='ATENDIDA'
                   GROUP BY tipo""", (session["user"]["id"],))
    rows = cur.fetchall()
    stats = {"consultas":0, "emergencias":0}
    for r in rows:
        if r["tipo"] == "CONSULTA":
            stats["consultas"] = r["total"]
        if r["tipo"] == "EMERGENCIA":
            stats["emergencias"] = r["total"]

    con.close()

    return render_template("dashboard_medico.html",
                           user=session["user"], citas=citas,
                           historial=historial, stats=stats)

@app.get("/medico/citas")
def medico_citas():
    if "user" not in session or session["user"]["rol"] != "MEDICO":
        return redirect(url_for("login_get"))
    mid = session["user"]["id"]
    con = get_db()
    cur = con.cursor()
    cur.execute("""SELECT c.*, p.nombre as paciente_nombre FROM citas c
                   JOIN usuarios p ON c.paciente_id=p.id
                   WHERE c.medico_id=? ORDER BY fecha, hora""", (mid,))
    citas = cur.fetchall()
    con.close()
    return render_template("medico_citas.html", citas=citas)

@app.route("/medico/atender/<int:cita_id>", methods=["GET", "POST"])
def medico_atender(cita_id):
    if "user" not in session or session["user"]["rol"] != "MEDICO":
        return redirect(url_for("login_get"))
    mid = session["user"]["id"]
    con = get_db()
    cur = con.cursor()
    cur.execute("""SELECT c.*, p.nombre as paciente_nombre FROM citas c
                   JOIN usuarios p ON c.paciente_id = p.id
                   WHERE c.id=? AND c.medico_id=?""", (cita_id, mid))
    cita = cur.fetchone()
    if not cita:
        con.close()
        flash("Cita no encontrada o no eres el médico asignado.", "error")
        return redirect(url_for("medico_citas"))
    if request.method == "POST":
        diagnostico = request.form.get("diagnostico")
        tratamiento = request.form.get("tratamiento")
        fecha = datetime.date.today().isoformat()
        # insertar historial
        cur.execute("""INSERT INTO historial (paciente_id, medico_id, fecha, diagnostico, tratamiento)
                       VALUES (?, ?, ?, ?, ?)""",
                    (cita["paciente_id"], mid, fecha, diagnostico, tratamiento))
        # marcar cita como atendida
        cur.execute("UPDATE citas SET estado='ATENDIDA' WHERE id=?", (cita_id,))
        con.commit()
        con.close()
        flash("Historial guardado y cita marcada como atendida.", "success")
        return redirect(url_for("medico_citas"))
    con.close()
    return render_template("medico_atender.html", cita=cita)

@app.get("/medico/cancelar/<int:cita_id>")
def cancelar_cita(cita_id):
    if "user" not in session or session["user"]["rol"] != "MEDICO":
        return redirect(url_for("login_get"))

    con = get_db()
    cur = con.cursor()

    # Verificar que la cita pertenece a este médico
    cur.execute("SELECT * FROM citas WHERE id=? AND medico_id=?", 
                (cita_id, session["user"]["id"]))
    cita = cur.fetchone()

    if not cita:
        con.close()
        flash("Cita no encontrada o no autorizada", "error")
        return redirect(url_for("dashboard_medico"))

    # Cambiar estado a CANCELADA
    cur.execute("UPDATE citas SET estado='CANCELADA' WHERE id=?", (cita_id,))
    con.commit()
    con.close()

    flash("Cita cancelada correctamente", "success")
    return redirect(url_for("dashboard_medico"))

#REPORTES
@app.get("/reportes")
def reportes():
    if "user" not in session:
        return redirect(url_for("login_get"))
    # Opcionalmente podemos restringir a MEDICO/ADMIN
    con = get_db()
    cur = con.cursor()
    # Citas por tipo (CONSULTA/EMERGENCIA)
    cur.execute("SELECT tipo, COUNT(*) as total FROM citas GROUP BY tipo")
    rows = cur.fetchall()  
    by_tipo = [dict(r) for r in rows] 

    # Citas por medico
    cur.execute("""SELECT u.nombre AS label, COUNT(c.id) AS total
                   FROM citas c JOIN usuarios u ON c.medico_id = u.id
                   GROUP BY c.medico_id""")
    rows = cur.fetchall()  
    by_medico = [dict(r) for r in rows] 
    # Pacientes por genero
    cur.execute("SELECT COALESCE(genero,'ND') AS genero, COUNT(*) AS total FROM usuarios WHERE rol='PACIENTE' GROUP BY genero")
    rows = cur.fetchall()  
    by_genero = [dict(r) for r in rows] 
    # Diagnósticos más comunes
    cur.execute("SELECT diagnostico, COUNT(*) AS total FROM historial GROUP BY diagnostico ORDER BY total DESC LIMIT 10")
    rows = cur.fetchall()  
    top_diag = [dict(r) for r in rows] 

    # Citas por estado
    cur.execute("SELECT estado, COUNT(*) as total FROM citas GROUP BY estado")
    rows = cur.fetchall()
    by_estado = [dict(r) for r in rows]

    con.close()
    return render_template("reportes.html",
                           by_tipo=by_tipo,
                           by_medico=by_medico,
                           by_genero=by_genero,
                           top_diag=top_diag,
                           by_estado=by_estado)

#RECOMENDACIONES
def recomendaciones_paciente(paciente_id):
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT diagnostico FROM historial WHERE paciente_id=?", (paciente_id,))
    diags = [r["diagnostico"] for r in cur.fetchall() if r["diagnostico"]]
    cur.execute("SELECT COUNT(*) as cnt FROM citas WHERE paciente_id=? AND fecha >= date('now','-6 months')", (paciente_id,))
    recent_count = cur.fetchone()["cnt"]
    con.close()
    recs = []
    # reglas simples
    if any("Hipertensión" in (d or "") for d in diags):
        recs.append("Tiene antecedentes de hipertensión. Recomendado control de presión arterial cada 3 meses.")
    if len(diags) >= 3:
        recs.append("Ha tenido múltiples diagnósticos. Considera una evaluación integral de salud.")
    if recent_count == 0:
        recs.append("No registra citas en los últimos 6 meses. Se recomienda chequeo preventivo.")
    if not recs:
        recs.append("Sin recomendaciones específicas. Mantener controles según indicaciones.")
    return recs

@app.route("/recomendaciones", methods=["GET", "POST"])
def recomendaciones():
    if "user" not in session or session["user"]["rol"] != "PACIENTE":
        return redirect(url_for("login_get"))

    pid = session["user"]["id"]
    recs_auto = recomendaciones_paciente(pid)

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT DISTINCT parte FROM recomendaciones")
    partes = [r[0] for r in cur.fetchall()]

    recomendacion = None
    parte = None

    if request.method == "POST":
        parte = request.form["parte"]
        cur.execute("SELECT recomendacion FROM recomendaciones WHERE parte=?", (parte,))
        recomendacion = [r[0] for r in cur.fetchall()]

    con.close()

    return render_template("recomendaciones.html",
                           recomendaciones=recs_auto,
                           partes=partes,
                           recomendacion=recomendacion,
                           parte=parte)


@app.route("/paciente/recomendaciones", methods=["GET", "POST"])
def paciente_recomendaciones():
    if "user" not in session or session["user"]["rol"] != "PACIENTE":
        return redirect(url_for("login_get"))

    con = get_db()
    cur = con.cursor()

    recomendacion = None

    # Convertimos a lista de strings
    cur.execute("SELECT DISTINCT parte FROM recomendaciones")
    partes = [r["parte"] for r in cur.fetchall()]

    if request.method == "POST":
        parte = request.form["parte"]
        cur.execute("SELECT recomendacion FROM recomendaciones WHERE parte=?", (parte,))
        rows = cur.fetchall()
        recomendacion = [r["recomendacion"] for r in rows]

    con.close()
    
    return render_template("recomendaciones.html",
                           partes=partes,
                           recomendacion=recomendacion)


def ensure_google_column():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("PRAGMA table_info(citas)")
    cols = [row[1] for row in cur.fetchall()]
    if 'google_event_id' not in cols:
        cur.execute("ALTER TABLE citas ADD COLUMN google_event_id TEXT")
        con.commit()
    con.close()

# Llama a esto una vez al inicio (después de definir DB)
ensure_google_column()


#EJECUTAR
if __name__ == "__main__":
    # crear BD si no existe
    if not os.path.exists(DB):
        import create_db  # crea y hace seed
    app.run(debug=True)
