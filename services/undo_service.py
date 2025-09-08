class UndoService:
    """Deshacer usando pila de acciones inversas por sesión."""
    def __init__(self, stack): self.stack=stack
    def ejecutar(self, do, undo):
        do(); self.stack.push(undo)
    def deshacer(self):
        u=self.stack.pop()
        if not u: return False
        u(); return True
