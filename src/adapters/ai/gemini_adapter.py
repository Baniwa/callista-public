"""
Adapter Gemini para o IAPort.

Traduz as chamadas do domínio (buscar_fontes, gerar_resumo, sugerir_rascunho)
em requisições à API Gemini (Google). Toda lógica de prompt fica aqui —
o domínio não sabe que existe IA, modelo ou API key.
"""
import json
import logging
from typing import Sequence

from google import genai
from google.genai import types

from src.application.ports.ai_port import FonteOficial, IAPort

logger = logging.getLogger(__name__)

_MODELO = "gemini-2.5-flash-lite"

_PROMPT_FONTES = """Você é um assistente especializado em legislação e pesquisa parlamentar brasileira.

A seguinte demanda chegou para uma assessoria de pesquisa do Senado Federal:
"{texto}"

Liste até 5 fontes oficiais onde um pesquisador legislativo deve buscar informação sobre este tema.
Responda APENAS com um array JSON válido. Cada objeto deve ter exatamente estes campos:
- "titulo": nome da fonte ou documento
- "url": URL oficial (use string vazia se não souber a URL exata)
- "orgao": órgão responsável (ex: "Senado Federal", "STF", "TCU")
- "resumo_trecho": uma frase explicando por que esta fonte é relevante para a demanda

Exemplo de formato esperado:
[
  {{
    "titulo": "Regimento Interno do Senado Federal",
    "url": "https://www25.senado.leg.br/web/atividade/regimento-interno",
    "orgao": "Senado Federal",
    "resumo_trecho": "Regula os procedimentos e quóruns para votações no Senado."
  }}
]

Retorne apenas o JSON, sem markdown, sem texto adicional."""

_PROMPT_RESUMO = """Você é um pesquisador legislativo do Senado Federal.

Resuma a seguinte demanda em até 3 frases objetivas, destacando:
1. O que está sendo pedido
2. O contexto legislativo relevante
3. O tipo de fonte que deve ser consultada

Demanda:
"{texto}"

Responda apenas com o resumo, sem título, sem marcadores."""

_PROMPT_RASCUNHO = """Você é um pesquisador legislativo sênior do Senado Federal.

Redija um rascunho de resposta técnica para a seguinte demanda:{contexto_anterior}

Demanda:
"{texto_demanda}"

O rascunho deve:
- Ser formal e objetivo, adequado para uso institucional
- Citar tipos de fontes que devem ser consultadas (Regimento Interno, Diário do Senado, etc.)
- Ter entre 3 e 5 parágrafos
- NÃO inventar dados, leis ou números específicos — use termos como "conforme levantamento a ser realizado"

Responda apenas com o texto do rascunho."""


class GeminiAdapter:
    """Implementa IAPort usando o modelo Gemini 2.5 Flash Lite (Google)."""

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    def buscar_fontes(self, texto: str) -> Sequence[FonteOficial]:
        prompt = _PROMPT_FONTES.format(texto=texto)
        try:
            response = self._client.models.generate_content(
                model=_MODELO,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            dados = json.loads(response.text)
            return [
                FonteOficial(
                    titulo=item.get("titulo", ""),
                    url=item.get("url", ""),
                    orgao=item.get("orgao", ""),
                    resumo_trecho=item.get("resumo_trecho", ""),
                )
                for item in dados
                if isinstance(item, dict)
            ]
        except (json.JSONDecodeError, Exception) as exc:
            logger.error("Erro ao buscar fontes no Gemini: %s", exc)
            return []

    def gerar_resumo(self, texto: str) -> str:
        prompt = _PROMPT_RESUMO.format(texto=texto)
        try:
            response = self._client.models.generate_content(
                model=_MODELO,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3),
            )
            return response.text.strip()
        except Exception as exc:
            logger.error("Erro ao gerar resumo no Gemini: %s", exc)
            return ""

    def sugerir_rascunho(
        self, texto_demanda: str, respostas_anteriores: Sequence[str]
    ) -> str:
        if respostas_anteriores:
            exemplos = "\n\nRespostas anteriores como referência de tom e formato:\n"
            exemplos += "\n---\n".join(respostas_anteriores[:3])
        else:
            exemplos = ""

        prompt = _PROMPT_RASCUNHO.format(
            texto_demanda=texto_demanda,
            contexto_anterior=exemplos,
        )
        try:
            response = self._client.models.generate_content(
                model=_MODELO,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.5),
            )
            return response.text.strip()
        except Exception as exc:
            logger.error("Erro ao sugerir rascunho no Gemini: %s", exc)
            return ""
