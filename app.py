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

app = Flask(__name__)
app.secret_key = "dev-secret"

# ---- Infra global (memoria) ----
_pacientes = HashTable(); _t_pac = Trie(); _bst_pac = BST()
_medicos   = HashTable(); _t_med = Trie(); _bst_med = BST()
_pq = PriorityQueue()
_stacks_por_usuario = {}  # id -> Stack

pacientes_service = PacientesService(_pacientes, _t_pac, _bst_pac)
medicos_service   = MedicosService(_medicos, _t_med, _bst_med)
citas_service     = CitasService(_pq)
historial_service = HistorialService(_pacientes)
reportes_service  = ReportesService()

# semillas
pacientes_service.seed()
medicos_service.seed()

def _stack():
    uid = session.get("user_id")
    if uid not in _stacks_por_usuario: _stacks_por_usuario[uid] = Stack()
    return _stacks_por_usuario[uid]

# ---------- Helpers ----------
def require_auth():
    if not session.get("user_id"):
        flash("Inicia sesión.")
        return False
    return True

# ---------- Rutas públicas ----------
@app.get("/")
def home():
    return render_template("home.html")

@app.get("/login")
def login_get():
    return render_template("auth_login.html")

@app.post("/login")
def login_post():
    session["user_id"] = request.form["user_id"].strip()
    session["role"]    = request.form["role"].strip().upper()
    flash("Sesión iniciada.")
    return redirect(url_for("dashboard"))

@app.get("/register")
def register_get():
    return render_template("auth_register.html")

@app.post("/register")
def register_post():
    role = request.form["role"].strip().upper()
    uid  = request.form["user_id"].strip()
    nombre = request.form["nombre"].strip()

    try:
        if role=="PACIENTE":
            edad = int(request.form.get("edad","0") or "0")
            pacientes_service.crear(uid, nombre, edad)
        else:
            esp = request.form.get("especialidad","General")
            medicos_service.crear(uid, nombre, esp)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("register_get"))

    flash("✅ Registro creado. Ya puedes iniciar sesión.")
    return redirect(url_for("login_get"))

@app.get("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for("home"))

# ---------- Dashboard ----------
@app.get("/dashboard")
def dashboard():
    if not require_auth(): return redirect(url_for("login_get"))
    if session["role"]=="PACIENTE":
        p = pacientes_service.get(session["user_id"])
        return render_template("dashboard_patient.html",
            paciente=p, medicos=medicos_service.listar_az())
    else:
        m = medicos_service.get(session["user_id"])
        return render_template("dashboard_doctor.html",
            medico=m, pacientes=pacientes_service.listar_az())

# ---------- Acciones PACIENTE ----------
@app.post("/paciente/agendar")
def paciente_agendar():
    if not require_auth(): return redirect(url_for("login_get"))
    pid = session["user_id"]
    mid = request.form["medico_id"].strip()
    fecha = request.form["fecha"].strip()
    prioridad = int(request.form.get("prioridad","1") or "1")

    # do/undo
    def do():
        c = citas_service.agendar(pid, mid, fecha, prioridad)
        session["last_cita_id"] = c.id
    def undo():
        # deshacer ≈ sacar de la cola si es la última (demo simple)
        pass
    UndoService(_stack()).ejecutar(do, undo)

    flash("Cita registrada.")
    return redirect(url_for("dashboard"))

@app.get("/paciente/historial")
def paciente_historial():
    if not require_auth(): return redirect(url_for("login_get"))
    h = historial_service.ver(session["user_id"])
    return render_template("dashboard_patient.html",
        paciente=pacientes_service.get(session["user_id"]),
        medicos=medicos_service.listar_az(),
        historial=list(h.iter_forward()) if h else [])

# ---------- Acciones MÉDICO ----------
@app.post("/medico/tomar")
def medico_tomar():
    if not require_auth(): return redirect(url_for("login_get"))
    c = citas_service.tomar_siguiente(medico_id=session["user_id"])
    flash("Sin citas." if not c else f"Cita en curso: {c.id} (paciente {c.paciente_id})")
    return redirect(url_for("dashboard"))

@app.post("/medico/consulta")
def medico_consulta():
    if not require_auth(): return redirect(url_for("login_get"))
    pid   = request.form["paciente_id"].strip()
    diag  = request.form["diag"].strip()
    trat  = request.form["trat"].strip()
    fecha = request.form["fecha"].strip()
    m_id  = session["user_id"]

    def do():
        historial_service.agregar(pid, diag, trat, fecha, m_id)
    def undo():
        # demo: no implementamos borrado en DLL; se puede con punteros al nodo
        pass
    UndoService(_stack()).ejecutar(do, undo)
    flash("Consulta agregada al historial.")
    return redirect(url_for("dashboard"))

# ---------- Búsqueda / Directorios ----------
@app.get("/buscar")
def buscar():
    q = request.args.get("q","").strip()
    tipo = request.args.get("tipo","paciente")
    if tipo=="medico":
        res = medicos_service.buscar(q)
    else:
        res = pacientes_service.buscar(q)
    if not isinstance(res, list): res = [res] if res else []
    names = [f"{getattr(x,'id','')} - {getattr(x,'nombre','')}" for x in res if x]
    flash("Resultados: " + "; ".join(names) if names else "Sin resultados")
    return redirect(url_for("dashboard"))

@app.get("/directorio/medicos")
def dir_medicos():
    return render_template("home.html", lista=medicos_service.listar_az())

@app.get("/directorio/pacientes")
def dir_pacientes():
    return render_template("home.html", lista=pacientes_service.listar_az())

# ---------- Undo ----------
@app.post("/undo")
def deshacer():
    ok = UndoService(_stack()).deshacer()
    flash("Acción revertida." if ok else "Nada para deshacer.")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
