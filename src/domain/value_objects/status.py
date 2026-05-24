from enum import Enum


class StatusDemanda(str, Enum):
    PENDENTE_RESPOSTA = "PR"
    PENDENTE_REVISAO = "PF"
    PENDENTE_EXTERNA = "PE"
    CONCLUIDA = "C"

    def label(self) -> str:
        labels = {
            "PR": "Pendente de resposta",
            "PF": "Pendente de revisão",
            "PE": "Pendente externa",
            "C": "Concluída",
        }
        return labels[self.value]
