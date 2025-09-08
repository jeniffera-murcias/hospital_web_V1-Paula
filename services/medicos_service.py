from domain.models.medico import Medico

class MedicosService:
    """Registro/Búsqueda de médicos (Hash + Trie + BST)."""
    def __init__(self, tabla, trie, bst):
        self.tabla=tabla; self.trie=trie; self.bst=bst

    def crear(self, id, nombre, especialidad):
        if self.tabla.get(id):
            raise ValueError(f"Médico con ID '{id}' ya existe")
        m=Medico(id=id, nombre=nombre, especialidad=especialidad)
        self.tabla.put(id,m); self.trie.insert(nombre, ref=id); self.bst.insert(nombre,m)
        return m

    def get(self, id): return self.tabla.get(id)
    def buscar(self, q):
        exact=self.tabla.get(q)
        if exact: return exact
        return [self.tabla.get(mid) for mid in self.trie.search_prefix(q)]
    def listar_az(self): return self.bst.in_order()

    def seed(self):
        if not self.tabla.get("m1"):
            self.crear("m1","Dr. Rivera","Medicina General")
            self.crear("m2","Dra. Torres","Pediatría")
            self.crear("m3","Dr. Díaz","Cardiología")