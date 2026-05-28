"""
Adapter para a API de Dados Abertos do Senado Federal.

Endpoint ativo: https://legis.senado.leg.br/dadosabertos/processo
Documentado em: docs/architecture/senado-api.md

Notas:
- API pública, sem autenticação
- Cache server-side de 30 minutos — não consultar com intervalo menor
- /processo/{id}/tramitacao retorna 404 — histórico de passos não disponível
"""
import logging
from datetime import date, datetime
from typing import Optional

import httpx

from src.domain.entities.projeto_lei import ProjetoLei

logger = logging.getLogger(__name__)

_BASE_URL = "https://legis.senado.leg.br/dadosabertos"
_TIMEOUT = 15.0


class SenadoAdapter:
    """Implementa SenadoPort consultando a API /processo do Senado Federal."""

    def __init__(self, timeout: float = _TIMEOUT) -> None:
        self._client = httpx.Client(
            base_url=_BASE_URL,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )

    def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]:
        try:
            resp = self._client.get(
                "/processo",
                params={"sigla": sigla, "numero": str(numero), "ano": str(ano)},
            )
            resp.raise_for_status()
            dados = resp.json()
            itens = self._extrair_lista(dados)
            if not itens:
                return None
            item = itens[0]
            id_senado = item.get("id")
            if not id_senado:
                return None
            return self._buscar_detalhe(int(id_senado))
        except httpx.HTTPError as exc:
            logger.error("Erro HTTP ao buscar PL %s %s/%s: %s", sigla, numero, ano, exc)
            return None

    def buscar_por_id(self, id_senado: int) -> Optional[ProjetoLei]:
        return self._buscar_detalhe(id_senado)

    def _buscar_detalhe(self, id_senado: int) -> Optional[ProjetoLei]:
        try:
            resp = self._client.get(f"/processo/{id_senado}")
            resp.raise_for_status()
            dados = resp.json()
            return self._parse_pl(id_senado, dados)
        except httpx.HTTPError as exc:
            logger.error("Erro HTTP ao buscar detalhe do processo %s: %s", id_senado, exc)
            return None

    def _extrair_lista(self, dados: dict) -> list:
        """Navega a resposta JSON da API, que pode ter wrappers variados."""
        if isinstance(dados, list):
            return dados
        for chave in ("dados", "Dados", "processos", "Processos", "items"):
            valor = dados.get(chave)
            if isinstance(valor, list):
                return valor
            if isinstance(valor, dict):
                for sub in ("Processo", "processo", "items"):
                    sub_valor = valor.get(sub)
                    if isinstance(sub_valor, list):
                        return sub_valor
                    if isinstance(sub_valor, dict):
                        return [sub_valor]
        return []

    def _parse_pl(self, id_senado: int, dados: dict) -> Optional[ProjetoLei]:
        try:
            conteudo = dados.get("conteudo") or {}
            documento = dados.get("documento") or {}

            ementa = (
                conteudo.get("ementa")
                or dados.get("ementa")
                or documento.get("ementa")
                or ""
            )
            sigla = dados.get("sigla", "")
            numero_raw = dados.get("numero", "0")
            numero = int(numero_raw) if str(numero_raw).isdigit() else 0
            ano = int(dados.get("ano", 0))
            identificacao = dados.get("identificacao") or f"{sigla} {numero}/{ano}"

            tramitando_raw = dados.get("tramitando", "Não")
            tramitando = str(tramitando_raw).lower() in ("sim", "true", "1")

            situacao_atual = dados.get("situacaoAtual", "")
            sigla_situacao = dados.get("siglaSituacaoAtual", "")

            dat_situacao = self._parse_date(
                dados.get("dataSituacaoAtual") or dados.get("dat_situacao")
            )
            dat_ultima_atualizacao = self._parse_datetime(
                dados.get("dthUltimaAtualizacao") or dados.get("dataUltimaAtualizacao")
            )

            url_documento = (
                dados.get("urlDocumento")
                or documento.get("url")
                or ""
            )
            autoria = (
                dados.get("autoria")
                or documento.get("resumoAutoria")
                or dados.get("resumoAutoria")
                or ""
            )

            return ProjetoLei(
                id=None,
                id_senado=id_senado,
                identificacao=identificacao,
                sigla=sigla,
                numero=numero,
                ano=ano,
                ementa=ementa,
                tramitando=tramitando,
                situacao_atual=situacao_atual,
                sigla_situacao=sigla_situacao,
                dat_situacao=dat_situacao or date.today(),
                url_documento=url_documento,
                autoria=autoria,
                dat_ultima_atualizacao=dat_ultima_atualizacao or datetime.now(),
            )
        except Exception as exc:
            logger.error("Erro ao parsear processo %s: %s", id_senado, exc)
            return None

    @staticmethod
    def _parse_date(valor: Optional[str]) -> Optional[date]:
        if not valor:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(valor[:10], fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_datetime(valor: Optional[str]) -> Optional[datetime]:
        if not valor:
            return None
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(valor[:26], fmt)
            except ValueError:
                continue
        return None
