from typing import Protocol, Sequence

from src.domain.entities.feriado import Feriado


class FeriadoRepository(Protocol):
    def listar(self) -> Sequence[Feriado]: ...
