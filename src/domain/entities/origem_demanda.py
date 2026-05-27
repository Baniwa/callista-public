from dataclasses import dataclass
from datetime import timedelta
from typing import Optional


@dataclass
class OrigemDemanda:
    id: Optional[int]
    sigla: str
    nome: str
    prazo_padrao_dias: int
    tem_numero: bool
