from datetime import date
from typing import Optional, Sequence

from src.domain.entities.afastamento import Afastamento
from .models import AfastamentoModel


class DjangoAfastamentoRepository:
    def listar_todos(self) -> Sequence[Afastamento]:
        return [
            self._to_entity(obj)
            for obj in AfastamentoModel.objects.select_related("usuario").order_by("-dat_inicial")
        ]

    def buscar_por_id(self, id: int) -> Optional[Afastamento]:
        try:
            return self._to_entity(AfastamentoModel.objects.get(pk=id))
        except AfastamentoModel.DoesNotExist:
            return None

    def salvar(self, afastamento: Afastamento) -> Afastamento:
        dados = {
            "usuario_id": afastamento.usuario_id,
            "dat_inicial": afastamento.dat_inicial,
            "dat_final": afastamento.dat_final,
            "motivo": afastamento.motivo,
        }
        if afastamento.id is None:
            obj = AfastamentoModel.objects.create(**dados)
        else:
            AfastamentoModel.objects.filter(pk=afastamento.id).update(**dados)
            obj = AfastamentoModel.objects.get(pk=afastamento.id)
        return self._to_entity(obj)

    def excluir(self, id: int) -> None:
        AfastamentoModel.objects.filter(pk=id).delete()

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
