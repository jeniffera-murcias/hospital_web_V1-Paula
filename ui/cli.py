"""UI por consola (CLI) mínima: login y ruteo por rol."""

from services.pacientes_service import PacientesService
from services.citas_service import CitasService
from services.historial_service import HistorialService
from services.reportes_service import ReportesService
from services.undo_service import UndoService

from domain.datastructures.hashtable import HashTable
from domain.datastructures.priority_queue import PriorityQueue
from domain.datastructures.trie import Trie
from domain.datastructures.bst import BST
from domain.datastructures.stack import Stack
from utils.rbac import Context

# Infra en memoria
_pacientes = HashTable()
_trie = Trie()
_bst = BST()
_pq = PriorityQueue()
_stack = Stack()

# Contexto de sesión
context = Context(user_id=None, role=None)

# Servicios
pacientes_service = PacientesService(_pacientes, _trie, _bst, context)
citas_service = CitasService(_pq, _pacientes, context)
historial_service = HistorialService(_pacientes, context)
reportes_service = ReportesService(context)
undo_service = UndoService(_stack, context)

def login() -> None:
    """Fija user/rol para la sesión y carga datos de prueba."""
    print("=== Login ===")
    user_id = input("User ID (ej: p1/m1): ").strip()
    role = input("Rol [PACIENTE/MEDICO]: ").strip().upper()
    Context.validate_role(role)
    context.user_id = user_id
    context.role = role
    try:
        pacientes_service.seed_basico()
    except Exception:
        pass

def menu_paciente() -> None:
    """Menú del paciente (demo)."""
    while True:
        print("\n=== MENÚ PACIENTE ===")
        print("1) Agendar cita")
        print("2) Ver mi historial")
        print("3) Recomendaciones")
        print("4) Buscar médicos/perfil")
        print("5) Directorio A–Z de médicos")
        print("6) Deshacer")
        print("0) Salir")
        op = input("> ").strip()
        if op == "1":
            mid = input("Médico ID: ").strip()
            fecha = input("Fecha/hora (YYYY-MM-DD HH:MM): ").strip()
            try:
                pr = int(input("Prioridad (1-5): ").strip())
            except ValueError:
                pr = 1
            print(citas_service.programar_cita(mid, fecha, pr))
        elif op == "2":
            h = historial_service.ver_historial(context.user_id)
            print(list(h.iter_forward()) if h else [])
        elif op == "3":
            print("Recomendaciones:", reportes_service.recomendaciones_personales(context.user_id))
        elif op == "4":
            q = input("Nombre o ID: ").strip()
            print(pacientes_service.buscar(q))
        elif op == "5":
            print([p.nombre for p in pacientes_service.listar_alfabetico()])
        elif op == "6":
            print("Deshacer:", undo_service.deshacer())
        elif op == "0":
            break

def menu_medico() -> None:
    """Menú del médico (demo)."""
    while True:
        print("\n=== MENÚ MÉDICO ===")
        print("1) Tomar siguiente cita")
        print("2) Ver historial de un paciente")
        print("3) Reportes")
        print("4) Recomendaciones clínicas")
        print("5) Buscar pacientes")
        print("6) Directorio A–Z")
        print("0) Salir")
        op = input("> ").strip()
        if op == "1":
            print(citas_service.tomar_siguiente())
        elif op == "2":
            pid = input("Paciente ID: ").strip()
            h = historial_service.ver_historial(pid)
            print(list(h.iter_forward()) if h else [])
        elif op == "3":
            print("Reportes:", reportes_service.metricas_basicas())
        elif op == "4":
            print("Sugerencias:", reportes_service.recomendaciones_clinicas())
        elif op == "5":
            q = input("Nombre o ID: ").strip()
            print(pacientes_service.buscar(q))
        elif op == "6":
            print([p.nombre for p in pacientes_service.listar_alfabetico()])
        elif op == "0":
            break

def main_menu() -> None:
    """Punto de entrada de la UI."""
    print("=== Sistema Hospitalario (demo) ===")
    login()
    if context.role == "PACIENTE":
        menu_paciente()
    else:
        menu_medico()
