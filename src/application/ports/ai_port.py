from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass
class FonteOficial:
    titulo: str
    url: str
    orgao: str
    resumo_trecho: str


class IAPort(Protocol):
    def buscar_fontes(self, texto: str) -> Sequence[FonteOficial]: ...
    def gerar_resumo(self, texto: str) -> str: ...
    def sugerir_rascunho(self, texto_demanda: str, respostas_anteriores: Sequence[str]) -> str: ...