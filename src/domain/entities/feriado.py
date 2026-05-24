from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Feriado:
    data: date
    nome: str
