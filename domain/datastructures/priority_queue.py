import heapq

class PriorityQueue:
    """Max-heap de citas (mayor prioridad primero)."""
    def __init__(self): self._h=[]; self._c=0
    def push(self, item, prio): self._c+=1; heapq.heappush(self._h, (-prio, self._c, item))
    def pop_max(self): return heapq.heappop(self._h)[2] if self._h else None
    def __len__(self): return len(self._h)
