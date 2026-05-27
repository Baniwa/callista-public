from typing import Optional, Sequence

from src.domain.entities.origem_demanda import OrigemDemanda
from .models import OrigemDemandaModel


class DjangoOrigemDemandaRepository:
    def listar(self) -> Sequence[OrigemDemanda]:
        return [self._to_entity(obj) for obj in OrigemDemandaModel.objects.all()]

    def buscar_por_sigla(self, sigla: str) -> Optional[OrigemDemanda]:
        try:
            return self._to_entity(OrigemDemandaModel.objects.get(sigla=sigla))
        except OrigemDemandaModel.DoesNotExist:
            return None

    def salvar(self, origem: OrigemDemanda) -> OrigemDemanda:
        obj, _ = OrigemDemandaModel.objects.update_or_create(
            sigla=origem.sigla,
            defaults={
                "nome": origem.nome,
                "prazo_padrao_dias": origem.prazo_padrao_dias,
                "tem_numero": origem.tem_numero,
            },
        )
        return self._to_entity(obj)

    def _to_entity(self, obj: OrigemDemandaModel) -> OrigemDemanda:
        return OrigemDemanda(
            id=obj.id,
            sigla=obj.sigla,
            nome=obj.nome,
            prazo_padrao_dias=obj.prazo_padrao_dias,
            tem_numero=obj.tem_numero,
        )
