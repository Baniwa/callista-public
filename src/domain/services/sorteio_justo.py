import random
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CandidatoSorteio:
    usuario_id: int
    percentual_meta: float


class SorteioJustoService:
    """
    Distribui demandas priorizando quem está mais atrás na meta mensal.

    Regras (replicadas do sistema CEPEL/Senado):
    - Se todos ≥ 90% da meta → sorteia entre os abaixo da média do grupo
    - Caso contrário → sorteia entre os com percentual ≤ mínimo + 10 p.p.
    """

    def selecionar(self, candidatos: Sequence[CandidatoSorteio]) -> int:
        if not candidatos:
            raise ValueError("Nenhum candidato disponível para o sorteio")

        percentuais = [c.percentual_meta for c in candidatos]
        todos_acima_90 = all(p >= 0.9 for p in percentuais)

        if todos_acima_90:
            media = sum(percentuais) / len(percentuais)
            elegiveis = [c for c in candidatos if c.percentual_meta < media]
            if not elegiveis:
                elegiveis = list(candidatos)
        else:
            minimo = min(percentuais)
            elegiveis = [c for c in candidatos if c.percentual_meta <= minimo + 0.10]

        return random.choice(elegiveis).usuario_id
