"""Grafo no dirigido para relaciones (paciente-diagnóstico-tratamiento)."""

class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, a, b):
        """Crea arista bidireccional a<->b."""
        self.adj.setdefault(a, set()).add(b)
        self.adj.setdefault(b, set()).add(a)

    def neighbors(self, a):
        """Vecinos de un nodo (o lista vacía)."""
        return list(self.adj.get(a, []))
