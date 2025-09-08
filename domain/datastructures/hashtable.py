class _Entry:
    __slots__ = ("k", "v")
    def __init__(self, k, v): self.k, self.v = k, v

class HashTable:
    """Hash table con encadenamiento separado y rehash simple.
    - put/get/remove O(1) promedio
    - sin usar dict para el índice (solo para nodos propios)
    """
    def __init__(self, cap=53, load_factor=0.75):
        self._cap = cap
        self._buckets = [[] for _ in range(self._cap)]
        self._size = 0
        self._lf = load_factor

    def _idx(self, k): return (hash(k) & 0x7FFFFFFF) % self._cap

    def _rehash(self):
        old = self._buckets
        self._cap = self._cap * 2 + 1
        self._buckets = [[] for _ in range(self._cap)]
        self._size = 0
        for b in old:
            for e in b:
                self.put(e.k, e.v)

    def put(self, k, v):
        i = self._idx(k)
        b = self._buckets[i]
        for e in b:
            if e.k == k:
                e.v = v
                return
        b.append(_Entry(k, v))
        self._size += 1
        if self._size / self._cap > self._lf:
            self._rehash()

    def get(self, k):
        b = self._buckets[self._idx(k)]
        for e in b:
            if e.k == k:
                return e.v
        return None

    def remove(self, k):
        b = self._buckets[self._idx(k)]
        for i, e in enumerate(b):
            if e.k == k:
                del b[i]
                self._size -= 1
                return e.v
        return None

    def values(self):
        for b in self._buckets:
            for e in b:
                yield e.v
