"""Servicio de pacientes: alta/baja/consulta, búsqueda por prefijo y directorio A–Z."""

from domain.models.paciente import Paciente


class PacientesService:
    def __init__(self, tabla, trie, bst, context):
        self.tabla = tabla
        self.trie = trie
        self.bst = bst
        self.context = context

    def crear_paciente(self, id, nombre, edad):
        """Crea paciente y actualiza índices secundarios (Trie/BST)."""
        p = Paciente(id=id, nombre=nombre, edad=edad)
        self.tabla.put(id, p)
        self.trie.insert(nombre, ref=id)
        self.bst.insert(p)
        return p

    def obtener_por_id(self, id):
        """Devuelve un paciente por ID (o None)."""
        return self.tabla.get(id)

    def buscar(self, q):
        """Busca por ID exacto o por prefijo de nombre en el Trie."""
        p = self.tabla.get(q)
        if p:
            return p
        return [self.tabla.get(pid) for pid in self.trie.search_prefix(q)]

    def listar_alfabetico(self):
        """Listado A–Z usando BST (o lista ordenada en este stub)."""
        return self.bst.in_order()

    def seed_basico(self):
        """Carga datos mínimos para pruebas manuales."""
        if not self.tabla.get("p1"):
            self.crear_paciente("p1", "Andrea", 27)
            self.crear_paciente("p2", "Juliana", 26)
            self.crear_paciente("p3", "Paula", 26)
            self.crear_paciente("p4", "Ana", 27)
            self.crear_paciente("p5", "Ashley", 27)
