from typing import Sequence

from src.adapters.django_orm.models import OrigemDemandaModel


class DjangoOrigemDemandaRepository:
    def listar(self) -> Sequence[OrigemDemandaModel]:
        return list(OrigemDemandaModel.objects.filter(ativo=True))

    def buscar_por_sigla(self, sigla: str) -> OrigemDemandaModel | None:
        return OrigemDemandaModel.objects.filter(sigla=sigla, ativo=True).first()
