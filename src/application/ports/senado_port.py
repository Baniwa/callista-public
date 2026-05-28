from typing import Optional, Protocol

from src.domain.entities.projeto_lei import ProjetoLei


class SenadoPort(Protocol):
    def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]: ...
    def buscar_por_id(self, id_senado: int) -> Optional[ProjetoLei]: ...
