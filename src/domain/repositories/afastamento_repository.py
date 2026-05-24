from datetime import date
from typing import Protocol, Sequence

from src.domain.entities.afastamento import Afastamento


class AfastamentoRepository(Protocol):
    def listar_ativos_na_data(self, data: date) -> Sequence[Afastamento]: ...
