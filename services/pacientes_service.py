from domain.models.paciente import Paciente

class PacientesService:
    """Registro/Búsqueda de pacientes (Hash + Trie + BST)."""
    def __init__(self, tabla, trie, bst):
        self.tabla=tabla; self.trie=trie; self.bst=bst

    def crear(self, id, nombre, edad):
        if self.tabla.get(id):
            raise ValueError(f"Paciente con ID '{id}' ya existe")
        p=Paciente(id=id, nombre=nombre, edad=edad)
        self.tabla.put(id,p); self.trie.insert(nombre, ref=id); self.bst.insert(nombre,p)
        return p

    def get(self, id): return self.tabla.get(id)

    def buscar(self, q):
        exact=self.tabla.get(q)
        if exact: return exact
        return [self.tabla.get(pid) for pid in self.trie.search_prefix(q)]

    def listar_az(self): return self.bst.in_order()

    def seed(self):
        if not self.tabla.get("p1"):
            self.crear("p1","Andrea",27)
            self.crear("p2","Juliana",26)
            self.crear("p3","Paula",26)
            self.crear("p4","Ana",27)
            self.crear("p5","Ashley",27)