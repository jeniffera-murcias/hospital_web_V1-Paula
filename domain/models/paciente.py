from dataclasses import dataclass, field
from domain.datastructures.doubly_linked_list import DoublyLinkedList

@dataclass
class Paciente:
    id: str
    nombre: str
    edad: int
    historial: DoublyLinkedList = field(default_factory=DoublyLinkedList)
