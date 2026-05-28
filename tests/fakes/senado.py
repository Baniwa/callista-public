from typing import Optional, Sequence

from src.domain.entities.projeto_lei import ProjetoLei


class FakeSenado:
    """Implementação in-memory do SenadoPort para testes unitários."""

    def __init__(self, pl: Optional[ProjetoLei] = None) -> None:
        self._pl = pl

    def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]:
        return self._pl

    def buscar_por_id(self, id_senado: int) -> Optional[ProjetoLei]:
        if self._pl and self._pl.id_senado == id_senado:
            return self._pl
        return None


class FakeSenadoVazio:
    """Sempre retorna None — simula PL não encontrado."""

    def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]:
        return None

    def buscar_por_id(self, id_senado: int) -> Optional[ProjetoLei]:
        return None
