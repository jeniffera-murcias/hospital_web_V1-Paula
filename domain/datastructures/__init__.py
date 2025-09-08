"""Tabla hash mínima usando dict interno.

Sustituye/expande esto con tu propia implementación 'desde cero'
si tu taller lo requiere (manejo de colisiones, factor de carga, etc.).
"""

class HashTable:
    def __init__(self, cap=128):
        self._d = {}

    def put(self, k, v):
        """Inserta o actualiza un elemento."""
        self._d[k] = v

    def get(self, k):
        """Obtiene un elemento por clave (o None si no existe)."""
        return self._d.get(k)

    def remove(self, k):
        """Elimina y devuelve el valor por clave (o None)."""
        return self._d.pop(k, None)

    def values(self):
        """Itera los valores almacenados."""
        return self._d.values()
