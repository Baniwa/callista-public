"""
Implementações fake do IAPort para uso em testes unitários.

Cada classe aqui é um adapter de teste — segue exatamente o mesmo contrato
de um adapter real (GeminiAdapter, ClaudeAdapter, etc.). Se o Callista 2.0
precisar trocar o provedor de IA, a única mudança é no container:
    ia=GeminiAdapter(...)  →  ia=ClaudeAdapter(...)

Nenhum teste, use case ou entidade precisa ser alterado.
"""
from typing import Sequence

from src.application.ports.ai_port import FonteOficial, IAPort


class FakeIA:
    """Adapter de teste que retorna dados fixos e previsíveis."""

    FONTE_PADRAO = FonteOficial(
        titulo="Regimento Interno do Senado Federal",
        url="https://www25.senado.leg.br/web/atividade/regimento-interno",
        orgao="Senado Federal",
        resumo_trecho="Regula os procedimentos e quóruns para votações no Senado.",
    )

    def buscar_fontes(self, texto: str) -> Sequence[FonteOficial]:
        return [self.FONTE_PADRAO]

    def gerar_resumo(self, texto: str) -> str:
        return f"Resumo de: {texto[:50]}"

    def sugerir_rascunho(
        self, texto_demanda: str, respostas_anteriores: Sequence[str]
    ) -> str:
        return "Rascunho gerado pelo adaptador fake."


class FakeIAVazia:
    """Simula provedor de IA que não retorna resultado (falha silenciosa)."""

    def buscar_fontes(self, texto: str) -> Sequence[FonteOficial]:
        return []

    def gerar_resumo(self, texto: str) -> str:
        return ""

    def sugerir_rascunho(
        self, texto_demanda: str, respostas_anteriores: Sequence[str]
    ) -> str:
        return ""


class FakeIAEspiao:
    """Registra todas as chamadas recebidas — útil para verificar que o
    use case repassa os argumentos corretos ao adapter."""

    def __init__(self) -> None:
        self.textos_busca: list[str] = []
        self.textos_resumo: list[str] = []
        self.textos_rascunho: list[str] = []
        self.contextos_rascunho: list[list[str]] = []

    def buscar_fontes(self, texto: str) -> Sequence[FonteOficial]:
        self.textos_busca.append(texto)
        return []

    def gerar_resumo(self, texto: str) -> str:
        self.textos_resumo.append(texto)
        return ""

    def sugerir_rascunho(
        self, texto_demanda: str, respostas_anteriores: Sequence[str]
    ) -> str:
        self.textos_rascunho.append(texto_demanda)
        self.contextos_rascunho.append(list(respostas_anteriores))
        return "Rascunho do espião."
