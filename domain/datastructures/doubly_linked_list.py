class _Node:
    def __init__(self, v): self.v=v; self.prev=None; self.next=None

class DoublyLinkedList:
    def __init__(self): self.head=None; self.tail=None
    def append(self, v):
        n=_Node(v)
        if not self.head: self.head=self.tail=n
        else: self.tail.next=n; n.prev=self.tail; self.tail=n
    def iter_forward(self):
        cur=self.head
        while cur: yield cur.v; cur=cur.next
