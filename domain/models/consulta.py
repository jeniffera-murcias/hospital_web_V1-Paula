from dataclasses import dataclass
@dataclass
class Consulta:
    id: str
    diag: str
    tratamiento: str
    fecha: str
    medico_id: str
