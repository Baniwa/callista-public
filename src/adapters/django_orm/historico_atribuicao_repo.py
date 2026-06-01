from typing import Sequence

from src.adapters.django_orm.models import HistoricoAtribuicaoModel


class DjangoHistoricoAtribuicaoRepository:
    def registrar(self, demanda_id: int, usuario_id: int, tipo: str) -> None:
        HistoricoAtribuicaoModel.objects.create(
            demanda_id=demanda_id,
            usuario_id=usuario_id,
            tipo=tipo,
        )

    def listar_por_demanda(self, demanda_id: int) -> Sequence[HistoricoAtribuicaoModel]:
        return list(
            HistoricoAtribuicaoModel.objects.filter(demanda_id=demanda_id)
            .select_related("usuario")
        )
