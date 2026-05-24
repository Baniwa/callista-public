from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Resposta:
    id: Optional[int]
    demanda_id: int
    usuario_id: int
    texto: str
    dat_resposta: datetime = field(default_factory=datetime.now)
    editado: bool = False
