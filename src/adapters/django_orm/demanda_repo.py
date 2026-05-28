from datetime import datetime
from typing import Optional, Sequence

from src.domain.entities.demanda import Demanda
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda
from .models import DemandaModel


class DjangoDemandaRepository:
    def salvar(self, demanda: Demanda) -> Demanda:
        dados = {
            "origem": demanda.origem,
            "num_origem": demanda.num_origem,
            "texto": demanda.texto,
            "dat_chegada": demanda.dat_chegada,
            "dias_prazo": demanda.prazo.dias_uteis,
            "status": demanda.status.value,
            "relator_id": demanda.id_relator,
            "revisor_id": demanda.id_revisor,
        }
        if demanda.id is None:
            obj = DemandaModel.objects.create(**dados)
        else:
            DemandaModel.objects.filter(pk=demanda.id).update(**dados)
            obj = DemandaModel.objects.get(pk=demanda.id)
        return self._to_entity(obj)

    def buscar_por_id(self, id: int) -> Optional[Demanda]:
        try:
            return self._to_entity(DemandaModel.objects.get(pk=id))
        except DemandaModel.DoesNotExist:
            return None

    def listar_por_status(self, status: StatusDemanda) -> Sequence[Demanda]:
        return [
            self._to_entity(obj)
            for obj in DemandaModel.objects.filter(status=status.value)
        ]

    def buscar_por_texto(self, q: str) -> Sequence[Demanda]:
        from django.db.models import Q
        return [
            self._to_entity(obj)
            for obj in DemandaModel.objects.filter(Q(texto__icontains=q) | Q(origem__icontains=q))
        ]

    def listar_ativas(self) -> Sequence[Demanda]:
        return [
            self._to_entity(obj)
            for obj in DemandaModel.objects.exclude(status="C")
        ]

    def contar_respostas_no_mes(self, usuario_id: int, mes: int, ano: int) -> int:
        return DemandaModel.objects.filter(
            relator_id=usuario_id,
            dat_chegada__month=mes,
            dat_chegada__year=ano,
            status__in=["PF", "C"],
        ).count()

    def contar_revisoes_no_mes(self, usuario_id: int, mes: int, ano: int) -> int:
        return DemandaModel.objects.filter(
            revisor_id=usuario_id,
            dat_chegada__month=mes,
            dat_chegada__year=ano,
            status="C",
        ).count()

    def _to_entity(self, obj: DemandaModel) -> Demanda:
        demanda = Demanda(
            id=obj.id,
            origem=obj.origem,
            num_origem=obj.num_origem,
            texto=obj.texto,
            dat_chegada=obj.dat_chegada,
            prazo=Prazo(dias_uteis=obj.dias_prazo),
            status=StatusDemanda(obj.status),
            id_relator=obj.relator_id,
            id_revisor=obj.revisor_id,
            dat_cadastro=obj.dat_cadastro or datetime.now(),
        )
        return demanda
