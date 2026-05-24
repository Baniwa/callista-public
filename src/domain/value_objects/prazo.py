from dataclasses import dataclass
from datetime import date, timedelta
from typing import Sequence


@dataclass(frozen=True)
class Prazo:
    dias_uteis: int

    def data_limite(self, a_partir_de: date, feriados: Sequence[date] = ()) -> date:
        dias = self.dias_uteis
        data = a_partir_de
        feriados_set = set(feriados)

        while dias > 0:
            data += timedelta(days=1)
            if data.weekday() not in (5, 6) and data not in feriados_set:
                dias -= 1

        return data

    def __post_init__(self) -> None:
        if self.dias_uteis <= 0:
            raise ValueError("Prazo deve ser maior que zero dias úteis")
