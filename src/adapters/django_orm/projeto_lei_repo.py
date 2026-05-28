from typing import Optional, Sequence

from src.domain.entities.projeto_lei import ProjetoLei
from .models import ProjetoLeiModel


class DjangoProjetoLeiRepository:
    def salvar(self, pl: ProjetoLei) -> ProjetoLei:
        dados = {
            "id_senado": pl.id_senado,
            "identificacao": pl.identificacao,
            "sigla": pl.sigla,
            "numero": pl.numero,
            "ano": pl.ano,
            "ementa": pl.ementa,
            "tramitando": pl.tramitando,
            "situacao_atual": pl.situacao_atual,
            "sigla_situacao": pl.sigla_situacao,
            "dat_situacao": pl.dat_situacao,
            "url_documento": pl.url_documento,
            "autoria": pl.autoria,
            "dat_ultima_atualizacao": pl.dat_ultima_atualizacao,
            "demanda_id": pl.demanda_id,
        }
        if pl.id is None:
            obj = ProjetoLeiModel.objects.create(**dados)
        else:
            ProjetoLeiModel.objects.filter(pk=pl.id).update(**dados)
            obj = ProjetoLeiModel.objects.get(pk=pl.id)
        return self._to_entity(obj)

    def buscar_por_id(self, id: int) -> Optional[ProjetoLei]:
        try:
            return self._to_entity(ProjetoLeiModel.objects.get(pk=id))
        except ProjetoLeiModel.DoesNotExist:
            return None

    def buscar_por_id_senado(self, id_senado: int) -> Optional[ProjetoLei]:
        try:
            return self._to_entity(ProjetoLeiModel.objects.get(id_senado=id_senado))
        except ProjetoLeiModel.DoesNotExist:
            return None

    def listar_por_demanda(self, demanda_id: int) -> Sequence[ProjetoLei]:
        return [
            self._to_entity(obj)
            for obj in ProjetoLeiModel.objects.filter(demanda_id=demanda_id)
        ]

    def _to_entity(self, obj: ProjetoLeiModel) -> ProjetoLei:
        return ProjetoLei(
            id=obj.id,
            id_senado=obj.id_senado,
            identificacao=obj.identificacao,
            sigla=obj.sigla,
            numero=obj.numero,
            ano=obj.ano,
            ementa=obj.ementa,
            tramitando=obj.tramitando,
            situacao_atual=obj.situacao_atual,
            sigla_situacao=obj.sigla_situacao,
            dat_situacao=obj.dat_situacao,
            url_documento=obj.url_documento,
            autoria=obj.autoria,
            dat_ultima_atualizacao=obj.dat_ultima_atualizacao,
            demanda_id=obj.demanda_id,
        )
