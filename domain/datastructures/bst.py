class _Node:
    __slots__ = ("key","val","l","r")
    def __init__(self, key, val): self.key, self.val, self.l, self.r = key, val, None, None

class BST:
    """Árbol Binario de Búsqueda para ordenar por 'key' (nombre).
    in_order() devuelve los valores en orden alfabético.
    """
    def __init__(self): self.root = None

    def insert(self, key, val):
        def _ins(n, key, val):
            if not n: return _Node(key, val)
            if key.lower() < n.key.lower(): n.l = _ins(n.l, key, val)
            elif key.lower() > n.key.lower(): n.r = _ins(n.r, key, val)
            else: n.val = val
            return n
        self.root = _ins(self.root, key, val)

    def in_order(self):
        out = []
        def _dfs(n):
            if not n: return
            _dfs(n.l); out.append(n.val); _dfs(n.r)
        _dfs(self.root)
        return out
