from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

class Status(Enum):
    SUCESSO = "sucesso"
    ERRO = "erro"
    AVISO = "aviso"


@dataclass
class ServiceResult:
    status: Status
    mensagem: str = ""
    dados: Optional[Any] = None

    @property
    def sucesso(self) -> bool:
        return self.status == Status.SUCESSO

    @property
    def erro(self) -> bool:
        return self.status == Status.ERRO

    @property
    def aviso(self) -> bool:
        return self.status == Status.AVISO
