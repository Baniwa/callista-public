from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TipoAtribuicao(str, Enum):
    RESPOSTA = "RES"
    REVISAO = "REV"


@dataclass
class HistoricoAtribuicao:
    id: Optional[int]
    demanda_id: int
    usuario_id: int
    tipo: TipoAtribuicao
    data_atribuicao: datetime = field(default_factory=datetime.now)
    valido: bool = True
