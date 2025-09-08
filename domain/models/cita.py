from dataclasses import dataclass
from domain.models.enums import EstadoCita

@dataclass
class Cita:
    id: str
    paciente_id: str
    medico_id: str
    fecha: str
    prioridad: int
    estado: EstadoCita = EstadoCita.PENDIENTE
