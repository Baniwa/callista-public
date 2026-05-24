from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from src.domain.value_objects.status import StatusDemanda
from src.domain.value_objects.prazo import Prazo


@dataclass
class Demanda:
    id: Optional[int]
    origem: str
    num_origem: Optional[int]
    texto: str
    dat_chegada: date
    prazo: Prazo
    status: StatusDemanda = StatusDemanda.PENDENTE_RESPOSTA
    id_relator: Optional[int] = None
    id_revisor: Optional[int] = None
    dat_cadastro: datetime = field(default_factory=datetime.now)

    @property
    def respondida(self) -> bool:
        return self.status in (StatusDemanda.PENDENTE_REVISAO, StatusDemanda.CONCLUIDA)

    @property
    def concluida(self) -> bool:
        return self.status == StatusDemanda.CONCLUIDA

    def marcar_respondida(self) -> None:
        if self.status != StatusDemanda.PENDENTE_RESPOSTA:
            raise ValueError("Demanda não está pendente de resposta")
        self.status = StatusDemanda.PENDENTE_REVISAO

    def marcar_concluida(self) -> None:
        if self.status != StatusDemanda.PENDENTE_REVISAO:
            raise ValueError("Demanda não está pendente de revisão")
        self.status = StatusDemanda.CONCLUIDA
