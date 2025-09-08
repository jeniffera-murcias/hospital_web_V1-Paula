class Stack:
    """Pila LIFO para deshacer acciones."""
    def __init__(self): self._s = []
    def push(self, x): self._s.append(x)
    def pop(self): return self._s.pop() if self._s else None
