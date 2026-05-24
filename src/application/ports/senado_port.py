from dataclasses import dataclass
from typing import Optional, Protocol, Sequence


@dataclass
class EtapaTramitacao:
    descricao: str
    data: Optional[str]
    concluida: bool


@dataclass
class ProjetoLei:
    sigla: str
    numero: int
    ano: int
    ementa: str
    autor: str
    tramitacao: Sequence[EtapaTramitacao]
    url_texto_integral: str


class SenadoPort(Protocol):
    def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]: ...
    def pesquisar_pls(self, termo: str) -> Sequence[ProjetoLei]: ...
