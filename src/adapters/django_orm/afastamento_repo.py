from datetime import date
from typing import Sequence

from src.domain.entities.afastamento import Afastamento
from .models import AfastamentoModel


class DjangoAfastamentoRepository:
    def listar_ativos_na_data(self, data: date) -> Sequence[Afastamento]:
        # Busca todos os afastamentos cujo período possa cobrir a data
        # A lógica de antecipação de 2 dias úteis é aplicada pela entidade Afastamento.cobre_data()
        return [
            self._to_entity(obj)
            for obj in AfastamentoModel.objects.filter(
                dat_final__gte=data
            ).select_related("usuario")
        ]

    def _to_entity(self, obj: AfastamentoModel) -> Afastamento:
        return Afastamento(
            id=obj.id,
            usuario_id=obj.usuario_id,
            dat_inicial=obj.dat_inicial,
            dat_final=obj.dat_final,
            motivo=obj.motivo,
        )
