"""
Gera um banco SQLite que simula o Callista 1.0 com dados fictícios.

Uso:
    python scripts/gerar_db_callista1_fake.py
    python scripts/gerar_db_callista1_fake.py --output D:/outro/caminho/fake.sqlite3

O arquivo gerado pode ser usado diretamente com importar_callista1:
    python manage.py importar_callista1 --db-path scripts/callista1_fake.sqlite3 --dry-run
    python manage.py importar_callista1 --db-path scripts/callista1_fake.sqlite3
"""
import argparse
import sqlite3
from pathlib import Path

DEFAULT_OUTPUT = Path(__file__).parent / "callista1_fake.sqlite3"


def criar_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE origem_demanda (
            id_origem     INTEGER PRIMARY KEY,
            nom_origem    TEXT NOT NULL,
            tmp_resposta  INTEGER NOT NULL,  -- em segundos
            ind_origem    INTEGER DEFAULT 0  -- bool: tem número de origem
        );

        CREATE TABLE configuracoes_feriado (
            id          INTEGER PRIMARY KEY,
            dat_feriado TEXT NOT NULL UNIQUE,
            nom_feriado TEXT NOT NULL
        );

        CREATE TABLE auth_user (
            id         INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name  TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            is_active  INTEGER DEFAULT 1,
            is_staff   INTEGER DEFAULT 0
        );

        CREATE TABLE usuarios_userprofile (
            id         INTEGER PRIMARY KEY,
            user_id    INTEGER NOT NULL REFERENCES auth_user(id),
            is_hidden  INTEGER DEFAULT 0,
            matricula  TEXT,
            cargo      TEXT
        );

        CREATE TABLE configuracoes_motivoafastamento (
            id        INTEGER PRIMARY KEY,
            descricao TEXT NOT NULL
        );

        CREATE TABLE configuracoes_afastamento (
            id             INTEGER PRIMARY KEY,
            id_usuario_id  INTEGER NOT NULL REFERENCES auth_user(id),
            dat_inicial    TEXT NOT NULL,
            dat_final      TEXT NOT NULL,
            motivo_id      INTEGER REFERENCES configuracoes_motivoafastamento(id)
        );

        CREATE TABLE cadastro_demanda (
            id_demanda                  INTEGER PRIMARY KEY,
            num_origem                  INTEGER,
            des_demanda                 TEXT NOT NULL,
            dat_chegada                 TEXT NOT NULL,
            prazo                       INTEGER NOT NULL,  -- em segundos
            status                      TEXT NOT NULL,
            id_usuario_id               INTEGER REFERENCES auth_user(id),
            usuario_resposta_id         INTEGER REFERENCES auth_user(id),
            data_atribuicao_resposta    TEXT,
            usuario_revisao_id          INTEGER REFERENCES auth_user(id),
            data_atribuicao_revisao     TEXT,
            dat_cadastro                TEXT NOT NULL,
            id_origem_id                INTEGER REFERENCES origem_demanda(id_origem)
        );

        CREATE TABLE resposta_demanda (
            id_resposta         INTEGER PRIMARY KEY,
            des_resposta        TEXT NOT NULL,
            id_demanda_id       INTEGER NOT NULL REFERENCES cadastro_demanda(id_demanda),
            id_usuario_id       INTEGER NOT NULL REFERENCES auth_user(id),
            dat_resposta        TEXT NOT NULL,
            editado             INTEGER DEFAULT 0,
            dat_edicao          TEXT,
            id_usuario_edicao_id INTEGER REFERENCES auth_user(id)
        );

        CREATE TABLE feedback_demandas (
            id_feedback          INTEGER PRIMARY KEY,
            des_feedback         TEXT NOT NULL,
            id_resposta_id       INTEGER NOT NULL REFERENCES resposta_demanda(id_resposta),
            id_usuario_id        INTEGER NOT NULL REFERENCES auth_user(id),
            dat_feedback         TEXT NOT NULL,
            editado              INTEGER DEFAULT 0,
            dat_edicao           TEXT,
            id_usuario_edicao_id INTEGER REFERENCES auth_user(id)
        );

        CREATE TABLE demandas_historicoatribuicao (
            id               INTEGER PRIMARY KEY,
            id_demanda_id    INTEGER NOT NULL REFERENCES cadastro_demanda(id_demanda),
            id_usuario_id    INTEGER NOT NULL REFERENCES auth_user(id),
            tipo_atribuicao  TEXT NOT NULL,   -- 'RES' ou 'REV'
            data_atribuicao  TEXT NOT NULL,
            atribuicao_valida INTEGER DEFAULT 1
        );

        CREATE TABLE pendencia_externa (
            id                    INTEGER PRIMARY KEY,
            id_demanda_id         INTEGER NOT NULL REFERENCES cadastro_demanda(id_demanda),
            justificativa         TEXT NOT NULL,
            data_inicio           TEXT NOT NULL,
            data_fim              TEXT,
            id_usuario_criacao_id INTEGER NOT NULL REFERENCES auth_user(id)
        );
    """)


def popular(conn: sqlite3.Connection) -> None:
    # --- Origens ---
    conn.executemany(
        "INSERT INTO origem_demanda VALUES (?, ?, ?, ?)",
        [
            (1, "Secretaria Geral da Mesa", 5 * 86400, 1),
            (2, "Lei de Acesso à Informação", 20 * 86400, 1),
            (3, "Imprensa / Assessoria de Comunicação", 3 * 86400, 0),
            (4, "Gabinete da Presidência", 5 * 86400, 1),
            (5, "Consultoria Legislativa Interna", 10 * 86400, 0),
        ],
    )

    # --- Feriados (2025-2026) ---
    conn.executemany(
        "INSERT INTO configuracoes_feriado (dat_feriado, nom_feriado) VALUES (?, ?)",
        [
            ("2025-01-01", "Confraternização Universal"),
            ("2025-04-21", "Tiradentes"),
            ("2025-05-01", "Dia do Trabalho"),
            ("2025-09-07", "Independência do Brasil"),
            ("2025-10-12", "Nossa Senhora Aparecida"),
            ("2025-11-02", "Finados"),
            ("2025-11-15", "Proclamação da República"),
            ("2025-12-25", "Natal"),
            ("2026-01-01", "Confraternização Universal"),
            ("2026-04-21", "Tiradentes"),
            ("2026-05-01", "Dia do Trabalho"),
        ],
    )

    # --- Usuários ---
    conn.executemany(
        "INSERT INTO auth_user VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1, "Ana",    "Silveira",   "ana.silveira@senado.leg.br",    1, 0),
            (2, "Bruno",  "Carvalho",   "bruno.carvalho@senado.leg.br",  1, 0),
            (3, "Carla",  "Mendonça",   "carla.mendonca@senado.leg.br",  1, 0),
            (4, "Diego",  "Ferreira",   "diego.ferreira@senado.leg.br",  0, 0),  # inativo
            (5, "Elisa",  "Torres",     "elisa.torres@senado.leg.br",    1, 0),
            (99, "Admin", "Sistema",    "admin@senado.leg.br",           1, 1),  # staff/admin
        ],
    )

    conn.executemany(
        "INSERT INTO usuarios_userprofile (user_id, is_hidden, matricula, cargo) VALUES (?, ?, ?, ?)",
        [
            (1,  0, "10001", "Pesquisadora Legislativa"),
            (2,  0, "10002", "Consultor Legislativo"),
            (3,  0, "10003", "Analista de Pesquisa"),
            (4,  0, "10004", "Pesquisador Legislativo"),
            (5,  1, "10005", "Estagiária"),          # oculta
        ],
    )

    # --- Motivos de afastamento ---
    conn.executemany(
        "INSERT INTO configuracoes_motivoafastamento VALUES (?, ?)",
        [
            (1, "Férias"),
            (2, "Licença Médica"),
            (3, "Capacitação"),
        ],
    )

    # --- Afastamentos ---
    conn.executemany(
        "INSERT INTO configuracoes_afastamento (id_usuario_id, dat_inicial, dat_final, motivo_id) VALUES (?, ?, ?, ?)",
        [
            (1, "2025-07-14", "2025-07-25", 1),  # Ana em férias
            (2, "2025-06-02", "2025-06-06", 2),  # Bruno em licença
            (3, "2026-01-05", "2026-01-09", 3),  # Carla em capacitação
        ],
    )

    # Prazo em segundos: n_dias * 86400
    cinco  = 5  * 86400
    vinte  = 20 * 86400
    tres   = 3  * 86400
    dez    = 10 * 86400

    # --- Demandas ---
    # status: PR=Pendente Resposta, PF=Pendente Revisão, PE=Pendente Externa, C=Concluída
    conn.executemany("""
        INSERT INTO cadastro_demanda VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        # id, num_orig, texto, dat_chegada, prazo, status, criador, relator, dat_atrib_relator, revisor, dat_atrib_revisor, dat_cadastro, origem_id
        (1, 1234, "Qual é a composição atual da Comissão de Constituição e Justiça do Senado?",
         "2025-03-10", cinco, "C", 99, 1, "2025-03-10 09:00:00", 2, "2025-03-12 10:30:00", "2025-03-10 08:45:00", 1),

        (2, 5678, "Quantas propostas de emenda constitucional foram aprovadas desde 1988?",
         "2025-04-02", vinte, "C", 99, 2, "2025-04-02 14:00:00", 3, "2025-04-15 16:00:00", "2025-04-02 13:50:00", 2),

        (3, None, "Quais são os critérios para convocação de sessão extraordinária no Congresso?",
         "2025-05-20", tres, "C", 99, 3, "2025-05-20 10:00:00", 1, "2025-05-22 11:00:00", "2025-05-20 09:55:00", 3),

        (4, 9012, "Qual o histórico de votações nominais do PL 1234/2024?",
         "2025-06-01", cinco, "PF", 99, 1, "2025-06-01 09:00:00", 2, "2025-06-03 14:00:00", "2025-06-01 08:50:00", 1),

        (5, None, "Resumo das atividades da CPI dos Combustíveis.",
         "2025-06-10", dez, "PR", 99, 3, "2025-06-10 11:00:00", None, None, "2025-06-10 10:58:00", 5),

        (6, 3344, "Quais senadores integram a bancada ruralista?",
         "2025-06-15", cinco, "PE", 99, 2, "2025-06-15 09:00:00", None, None, "2025-06-15 08:55:00", 4),

        (7, None, "Existe precedente para cassação de mandato por quebra de decoro parlamentar?",
         "2025-07-01", cinco, "PR", 99, None, None, None, None, "2025-07-01 10:00:00", 5),
    ])

    # --- Respostas (apenas para demandas concluídas ou PF) ---
    conn.executemany("""
        INSERT INTO resposta_demanda VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        # id_resposta, texto, demanda_id, usuario_id, dat, editado, dat_edicao, editor_id
        (1, "A CCJ do Senado é composta por 27 senadores titulares, eleitos no início de cada legislatura. "
            "Atualmente é presidida pelo Sen. Rodrigo Pacheco (PSD-MG). Fonte: Portal do Senado Federal.",
         1, 1, "2025-03-11 16:30:00", 0, None, None),

        (2, "Desde a promulgação da Constituição de 1988, foram aprovadas 132 emendas constitucionais. "
            "A EC 132/2023 (Reforma Tributária) foi a mais recente. Fonte: STF e Senado Federal.",
         2, 2, "2025-04-10 14:00:00", 1, "2025-04-11 09:00:00", 3),

        (3, "A convocação de sessão extraordinária pode ser feita pelo Presidente do Senado, da Câmara, "
            "ou pelo Presidente da República, conforme art. 57 §6º da CF/88.",
         3, 3, "2025-05-21 17:00:00", 0, None, None),

        (4, "O PL 1234/2024 foi votado em três sessões plenárias: 10/03, 25/03 e 02/04/2025. "
            "Aprovado por 45 votos a 32 na votação final.",
         4, 1, "2025-06-02 17:00:00", 0, None, None),
    ])

    # --- Revisões (feedback) para demandas concluídas ---
    conn.executemany("""
        INSERT INTO feedback_demandas VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        # id_feedback, texto, id_resposta_id, usuario_id, dat, editado, dat_edicao, editor_id
        (1, "Resposta completa e bem fundamentada. Aprovado.", 1, 2, "2025-03-12 11:00:00", 0, None, None),
        (2, "Inclui informação sobre a EC 133 que ainda não foi promulgada. Corrigido e aprovado.", 2, 3, "2025-04-16 10:00:00", 1, "2025-04-17 08:30:00", 1),
        (3, "Boa citação constitucional. Aprovado sem ressalvas.", 3, 1, "2025-05-22 12:00:00", 0, None, None),
    ])

    # --- Histórico de atribuições ---
    conn.executemany("""
        INSERT INTO demandas_historicoatribuicao
        (id_demanda_id, id_usuario_id, tipo_atribuicao, data_atribuicao, atribuicao_valida)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 1, "RES", "2025-03-10 09:00:00", 1),
        (1, 2, "REV", "2025-03-12 10:30:00", 1),
        (2, 2, "RES", "2025-04-02 14:00:00", 1),
        (2, 3, "REV", "2025-04-15 16:00:00", 1),
        (3, 3, "RES", "2025-05-20 10:00:00", 1),
        (3, 1, "REV", "2025-05-22 11:00:00", 1),
        (4, 1, "RES", "2025-06-01 09:00:00", 1),
        (4, 2, "REV", "2025-06-03 14:00:00", 1),
        (5, 3, "RES", "2025-06-10 11:00:00", 1),
        (6, 2, "RES", "2025-06-15 09:00:00", 1),
        # atribuição anterior inválida (foi reatribuída):
        (2, 1, "RES", "2025-04-01 10:00:00", 0),
    ])

    # --- Pendência externa (demanda 6 está PE) ---
    conn.execute("""
        INSERT INTO pendencia_externa
        (id_demanda_id, justificativa, data_inicio, data_fim, id_usuario_criacao_id)
        VALUES (6, 'Aguardando retorno da liderança do partido para confirmar composição atual da bancada.', '2025-06-16 09:00:00', NULL, 2)
    """)

    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera banco SQLite falso do Callista 1.0")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output = Path(args.output)
    if output.exists():
        output.unlink()

    conn = sqlite3.connect(str(output))
    try:
        criar_schema(conn)
        popular(conn)
        print(f"Banco criado em: {output}")
        print("\nResumo dos dados inseridos:")
        for tabela in [
            "origem_demanda", "configuracoes_feriado", "auth_user",
            "usuarios_userprofile", "configuracoes_afastamento",
            "cadastro_demanda", "resposta_demanda", "feedback_demandas",
            "demandas_historicoatribuicao", "pendencia_externa",
        ]:
            count = conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            print(f"  {tabela:40s}: {count} registros")
    finally:
        conn.close()

    print(f"\nPróximo passo:")
    print(f"  python manage.py importar_callista1 --db-path {output} --dry-run")
    print(f"  python manage.py importar_callista1 --db-path {output}")


if __name__ == "__main__":
    main()
