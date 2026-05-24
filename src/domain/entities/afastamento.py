from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Sequence


@dataclass(frozen=True)
class Afastamento:
    id: Optional[int]
    usuario_id: int
    dat_inicial: date
    dat_final: date
    motivo: str

    def cobre_data(self, data: date, feriados: Sequence[date] = ()) -> bool:
        """
        Retorna True se o membro deve ser considerado ausente para uma demanda
        com dat_chegada = data.

        Antecipa 2 dias úteis o início do afastamento para evitar atribuir
        demanda a quem está prestes a sair de licença.
        """
        feriados_set = set(feriados)
        inicio_efetivo = self._recuar_dias_uteis(self.dat_inicial, 2, feriados_set)
        return inicio_efetivo <= data <= self.dat_final

    def _recuar_dias_uteis(self, data: date, n: int, feriados: set) -> date:
        dias = n
        atual = data
        while dias > 0:
            atual -= timedelta(days=1)
            if atual.weekday() not in (5, 6) and atual not in feriados:
                dias -= 1
        return atual
