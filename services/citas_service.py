from domain.models.cita import Cita
from domain.models.enums import EstadoCita
import uuid

class CitasService:
    """Programación y atención de citas (PriorityQueue)."""
    def __init__(self, pq):
        self.pq=pq

    def agendar(self, paciente_id, medico_id, fecha, prioridad:int):
        cid=str(uuid.uuid4())[:8]
        c=Cita(id=cid, paciente_id=paciente_id, medico_id=medico_id, fecha=fecha, prioridad=prioridad)
        self.pq.push(c, prioridad)
        return c

    def tomar_siguiente(self, medico_id:str|None=None):
        c=self.pq.pop_max()
        if not c: return None
        if medico_id and c.medico_id!=medico_id:
            # en demo simple se devuelve como "no asignada a este médico"
            c.estado=EstadoCita.PENDIENTE
        else:
            c.estado=EstadoCita.EN_CURSO
        return c
