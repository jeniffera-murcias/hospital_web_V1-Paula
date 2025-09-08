class ReportesService:
    """Reportes/recomendaciones (stub)."""
    def metricas(self):
        return {"citas_atendidas_aprox": 0, "diagnosticos_top": []}

    def recomendaciones_paciente(self, paciente_id):
        return ["Hidratación", "Chequeo anual"]

    def recomendaciones_clinicas(self):
        return ["Protocolo A", "Protocolo B"]
