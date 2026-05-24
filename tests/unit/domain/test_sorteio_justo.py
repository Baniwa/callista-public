import pytest

from src.domain.services.sorteio_justo import CandidatoSorteio, SorteioJustoService


def _candidato(usuario_id: int, percentual: float) -> CandidatoSorteio:
    return CandidatoSorteio(usuario_id=usuario_id, percentual_meta=percentual)


def test_sem_candidatos_levanta_erro():
    servico = SorteioJustoService()
    with pytest.raises(ValueError, match="Nenhum candidato"):
        servico.selecionar([])


def test_unico_candidato_sempre_selecionado():
    servico = SorteioJustoService()
    resultado = servico.selecionar([_candidato(usuario_id=7, percentual=0.5)])
    assert resultado == 7


def test_todos_acima_90_sorteia_abaixo_da_media():
    # Todos >= 90%: sorteio entre os abaixo da média (0.95)
    # usuario 1 = 90%, usuario 2 = 100% → média = 95% → elegível: usuario 1
    servico = SorteioJustoService()
    candidatos = [_candidato(1, 0.90), _candidato(2, 1.00)]
    for _ in range(20):
        assert servico.selecionar(candidatos) == 1


def test_todos_acima_90_todos_iguais_sorteia_qualquer_um():
    # Todos iguais e acima de 90% → todos abaixo da média? Não, nenhum < média.
    # Nesse caso, elegiveis cai para a lista toda.
    servico = SorteioJustoService()
    candidatos = [_candidato(1, 1.0), _candidato(2, 1.0)]
    resultados = {servico.selecionar(candidatos) for _ in range(30)}
    assert resultados == {1, 2}


def test_nao_todos_acima_90_sorteia_dentro_de_minimo_mais_10pp():
    # usuario 1 = 0%, usuario 2 = 5%, usuario 3 = 20%
    # mínimo = 0%, limite = 10% → elegíveis: 1 e 2
    servico = SorteioJustoService()
    candidatos = [_candidato(1, 0.0), _candidato(2, 0.05), _candidato(3, 0.20)]
    for _ in range(30):
        assert servico.selecionar(candidatos) in {1, 2}


def test_nao_todos_acima_90_minimo_mais_10pp_exclui_avancados():
    # usuario 1 = 50%, usuario 2 = 80% → mínimo 50%, limite 60% → só elegível: usuario 1
    servico = SorteioJustoService()
    candidatos = [_candidato(1, 0.50), _candidato(2, 0.80)]
    for _ in range(20):
        assert servico.selecionar(candidatos) == 1


def test_resultado_e_sempre_um_usuario_id_valido():
    servico = SorteioJustoService()
    ids_validos = {1, 2, 3, 4}
    candidatos = [_candidato(uid, 0.3) for uid in ids_validos]
    for _ in range(40):
        assert servico.selecionar(candidatos) in ids_validos
