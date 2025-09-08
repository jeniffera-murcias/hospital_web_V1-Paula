"""RBAC mínimo: contexto de sesión y validador de rol."""

from dataclasses import dataclass


@dataclass
class Context:
    """Guarda el usuario y rol activo de la sesión."""
    user_id: str | None
    role: str | None  # "PACIENTE" | "MEDICO"

    @staticmethod
    def validate_role(role: str) -> None:
        """Valida que el rol sea uno de los permitidos."""
        if role not in ("PACIENTE", "MEDICO"):
            raise ValueError("Rol inválido")
