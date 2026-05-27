from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PendenciaExterna:
    id: Optional[int]
    demanda_id: int
    justificativa: str
    criador_id: int
    data_inicio: datetime = field(default_factory=datetime.now)
    data_fim: Optional[datetime] = None

    @property
    def encerrada(self) -> bool:
        return self.data_fim is not None
