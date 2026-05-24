from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    id: Optional[int]
    nome: str
    email: str
    matricula: str
    cargo: str = ""
    is_ativo: bool = True
    is_oculto: bool = False

    @property
    def elegivel_para_demandas(self) -> bool:
        return self.is_ativo and not self.is_oculto
