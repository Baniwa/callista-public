from typing import Sequence

from src.domain.entities.feriado import Feriado
from .models import FeriadoModel


class DjangoFeriadoRepository:
    def listar(self) -> Sequence[Feriado]:
        return [
            Feriado(data=obj.data, nome=obj.nome)
            for obj in FeriadoModel.objects.all()
        ]
