from domain.models.consulta import Consulta

class HistorialService:
    """Alta de consultas y lectura de historial (lista doble)."""
    def __init__(self, pacientes_repo): self.pacientes=pacientes_repo

    def agregar(self, paciente_id, diag, tratamiento, fecha, medico_id):
        p=self.pacientes.get(paciente_id)
        if not p: raise ValueError("Paciente no existe")
        c=Consulta(id=fecha.replace(" ","_"), diag=diag, tratamiento=tratamiento, fecha=fecha, medico_id=medico_id)
        p.historial.append(c); return c

    def ver(self, paciente_id):
        p=self.pacientes.get(paciente_id); return p.historial if p else None
