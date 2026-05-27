from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Revisao:
    id: Optional[int]
    demanda_id: int
    usuario_id: int
    texto: str
    dat_revisao: datetime = field(default_factory=datetime.now)
    editado: bool = False
    editado_por_id: Optional[int] = None
    dat_edicao: Optional[datetime] = None
