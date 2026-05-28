from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class ProjetoLei:
    id: Optional[int]
    id_senado: int
    identificacao: str          # "PL 8/2025"
    sigla: str                  # "PL", "PEC", "PLP"
    numero: int
    ano: int
    ementa: str
    tramitando: bool
    situacao_atual: str
    sigla_situacao: str
    dat_situacao: date
    url_documento: str
    autoria: str
    dat_ultima_atualizacao: datetime
    demanda_id: Optional[int] = None
