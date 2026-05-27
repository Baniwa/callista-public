"""
Management command para importar dados do Callista 1.0 para o 2.0.

Lê o banco SQLite do sistema original e importa todos os registros históricos,
preservando integralmente datas, atribuições, respostas e revisões.

Uso:
    python manage.py importar_callista1 --db-path D:/Projetos/callista/db.sqlite3
    python manage.py importar_callista1 --db-path ... --dry-run   # simula sem salvar
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from src.adapters.django_orm.models import (
    DemandaModel,
    HistoricoAtribuicaoModel,
    OrigemDemandaModel,
    PendenciaExternaModel,
    RespostaModel,
    RevisaoModel,
    UsuarioModel,
    AfastamentoModel,
    FeriadoModel,
)


def _dt(value: str | None):
    """Converte string datetime do SQLite para datetime aware (UTC)."""
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


class Command(BaseCommand):
    help = "Importa dados históricos do Callista 1.0 (SQLite) para o Callista 2.0"

    def add_arguments(self, parser):
        parser.add_argument(
            "--db-path",
            required=True,
            help="Caminho para o arquivo db.sqlite3 do Callista 1.0",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula a importação sem salvar nenhum dado",
        )

    def handle(self, *args, **options):
        db_path = Path(options["db_path"])
        if not db_path.exists():
            raise CommandError(f"Arquivo não encontrado: {db_path}")

        self.dry_run = options["dry_run"]
        if self.dry_run:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN: nenhum dado será salvo"))

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        self.conn = conn

        try:
            with transaction.atomic():
                self._importar_origens()
                self._importar_feriados()
                self._importar_usuarios()
                self._importar_afastamentos()
                self._importar_demandas()
                self._importar_respostas()
                self._importar_revisoes()
                self._importar_historico_atribuicoes()
                self._importar_pendencias_externas()

                if self.dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("\nDry-run: transação revertida."))
                else:
                    self.stdout.write(self.style.SUCCESS("\nImportação concluída com sucesso."))
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    # Origens
    # ------------------------------------------------------------------ #

    def _importar_origens(self):
        rows = self.conn.execute(
            "SELECT id_origem, nom_origem, tmp_resposta, ind_origem FROM origem_demanda"
        ).fetchall()

        criados = 0
        for row in rows:
            sigla = row["nom_origem"][:10].upper().replace(" ", "_")
            prazo_dias = int(row["tmp_resposta"]) // 86400  # timedelta em segundos → dias

            if not self.dry_run:
                _, novo = OrigemDemandaModel.objects.get_or_create(
                    sigla=sigla,
                    defaults={
                        "nome": row["nom_origem"],
                        "prazo_padrao_dias": prazo_dias or 5,
                        "tem_numero": bool(row["ind_origem"]),
                    },
                )
                if novo:
                    criados += 1

        self.stdout.write(f"  -> Origens: {len(rows)} lidas, {criados} criadas")

    # ------------------------------------------------------------------ #
    # Feriados
    # ------------------------------------------------------------------ #

    def _importar_feriados(self):
        rows = self.conn.execute(
            "SELECT dat_feriado, nom_feriado FROM configuracoes_feriado"
        ).fetchall()

        criados = 0
        for row in rows:
            if not self.dry_run:
                _, novo = FeriadoModel.objects.get_or_create(
                    data=row["dat_feriado"],
                    defaults={"nome": row["nom_feriado"]},
                )
                if novo:
                    criados += 1

        self.stdout.write(f"  -> Feriados: {len(rows)} lidos, {criados} criados")

    # ------------------------------------------------------------------ #
    # Usuários
    # ------------------------------------------------------------------ #

    def _importar_usuarios(self):
        rows = self.conn.execute("""
            SELECT
                au.id,
                au.first_name || ' ' || au.last_name AS nome,
                au.email,
                au.is_active,
                up.is_hidden,
                CAST(up.matricula AS TEXT) AS matricula,
                up.cargo
            FROM auth_user au
            LEFT JOIN usuarios_userprofile up ON up.user_id = au.id
            WHERE au.is_staff = 0 OR up.id IS NOT NULL
        """).fetchall()

        self._mapa_usuario: dict[int, int] = {}
        criados = 0

        for row in rows:
            email = row["email"] or f"usuario_{row['id']}@callista.legado"
            matricula = row["matricula"] or str(row["id"])

            if not self.dry_run:
                obj, novo = UsuarioModel.objects.get_or_create(
                    matricula=matricula,
                    defaults={
                        "nome": row["nome"].strip() or f"Usuário {row['id']}",
                        "email": email,
                        "is_ativo": bool(row["is_active"]),
                        "is_oculto": bool(row["is_hidden"]) if row["is_hidden"] is not None else False,
                        "cargo": row["cargo"] or "",
                    },
                )
                self._mapa_usuario[row["id"]] = obj.id
                if novo:
                    criados += 1
            else:
                self._mapa_usuario[row["id"]] = row["id"]

        self.stdout.write(f"  -> Usuários: {len(rows)} lidos, {criados} criados")

    # ------------------------------------------------------------------ #
    # Afastamentos
    # ------------------------------------------------------------------ #

    def _importar_afastamentos(self):
        rows = self.conn.execute("""
            SELECT a.id_usuario_id, a.dat_inicial, a.dat_final, m.descricao AS motivo
            FROM configuracoes_afastamento a
            LEFT JOIN configuracoes_motivoafastamento m ON m.id = a.motivo_id
        """).fetchall()

        criados = 0
        for row in rows:
            usuario_id = self._mapa_usuario.get(row["id_usuario_id"])
            if not usuario_id:
                continue
            if not self.dry_run:
                _, novo = AfastamentoModel.objects.get_or_create(
                    usuario_id=usuario_id,
                    dat_inicial=row["dat_inicial"],
                    dat_final=row["dat_final"],
                    defaults={"motivo": row["motivo"] or "Não informado"},
                )
                if novo:
                    criados += 1

        self.stdout.write(f"  -> Afastamentos: {len(rows)} lidos, {criados} criados")

    # ------------------------------------------------------------------ #
    # Demandas
    # ------------------------------------------------------------------ #

    def _importar_demandas(self):
        rows = self.conn.execute("""
            SELECT
                cd.id_demanda,
                cd.num_origem,
                cd.des_demanda,
                cd.dat_chegada,
                cd.prazo,
                cd.status,
                cd.id_usuario_id AS criador_id,
                cd.usuario_resposta_id AS relator_id,
                cd.data_atribuicao_resposta,
                cd.usuario_revisao_id AS revisor_id,
                cd.data_atribuicao_revisao,
                cd.dat_cadastro,
                od.nom_origem
            FROM cadastro_demanda cd
            LEFT JOIN origem_demanda od ON od.id_origem = cd.id_origem_id
        """).fetchall()

        self._mapa_demanda: dict[int, int] = {}
        criados = 0

        for row in rows:
            sigla = (row["nom_origem"] or "OUT")[:10].upper().replace(" ", "_")
            prazo_dias = int(row["prazo"]) // 86400 if row["prazo"] else 5

            origem_ref = None
            if not self.dry_run:
                origem_ref = OrigemDemandaModel.objects.filter(sigla=sigla).first()

            relator_id = self._mapa_usuario.get(row["relator_id"]) if row["relator_id"] else None
            revisor_id = self._mapa_usuario.get(row["revisor_id"]) if row["revisor_id"] else None
            criador_id = self._mapa_usuario.get(row["criador_id"]) if row["criador_id"] else None

            if not self.dry_run:
                obj, novo = DemandaModel.objects.get_or_create(
                    pk=row["id_demanda"],
                    defaults={
                        "origem": sigla,
                        "origem_ref": origem_ref,
                        "num_origem": row["num_origem"],
                        "texto": row["des_demanda"],
                        "dat_chegada": row["dat_chegada"],
                        "dias_prazo": prazo_dias,
                        "status": row["status"],
                        "relator_id": relator_id,
                        "dat_atribuicao_relator": _dt(row["data_atribuicao_resposta"]),
                        "revisor_id": revisor_id,
                        "dat_atribuicao_revisor": _dt(row["data_atribuicao_revisao"]),
                        "criador_id": criador_id,
                    },
                )
                self._mapa_demanda[row["id_demanda"]] = obj.id
                if novo:
                    criados += 1
            else:
                self._mapa_demanda[row["id_demanda"]] = row["id_demanda"]

        self.stdout.write(f"  -> Demandas: {len(rows)} lidas, {criados} criadas")

    # ------------------------------------------------------------------ #
    # Respostas
    # ------------------------------------------------------------------ #

    def _importar_respostas(self):
        rows = self.conn.execute("""
            SELECT
                rd.id_resposta,
                rd.des_resposta,
                rd.id_demanda_id,
                rd.id_usuario_id,
                rd.dat_resposta,
                rd.editado,
                rd.dat_edicao,
                rd.id_usuario_edicao_id
            FROM resposta_demanda rd
        """).fetchall()

        criados = 0
        for row in rows:
            demanda_id = self._mapa_demanda.get(row["id_demanda_id"])
            usuario_id = self._mapa_usuario.get(row["id_usuario_id"])
            if not demanda_id or not usuario_id:
                self.stdout.write(
                    self.style.WARNING(f"  ! Resposta {row['id_resposta']}: demanda ou usuário não encontrado")
                )
                continue

            editado_por_id = self._mapa_usuario.get(row["id_usuario_edicao_id"]) if row["id_usuario_edicao_id"] else None

            if not self.dry_run:
                _, novo = RespostaModel.objects.get_or_create(
                    pk=row["id_resposta"],
                    defaults={
                        "demanda_id": demanda_id,
                        "usuario_id": usuario_id,
                        "texto": row["des_resposta"],
                        "editado": bool(row["editado"]),
                        "dat_edicao": _dt(row["dat_edicao"]),
                        "editado_por_id": editado_por_id,
                    },
                )
                if novo:
                    criados += 1

        self.stdout.write(f"  -> Respostas: {len(rows)} lidas, {criados} criadas")

    # ------------------------------------------------------------------ #
    # Revisões (FeedbackDemandas no 1.0)
    # ------------------------------------------------------------------ #

    def _importar_revisoes(self):
        rows = self.conn.execute("""
            SELECT
                fd.id_feedback,
                fd.des_feedback,
                rd.id_demanda_id,
                fd.id_usuario_id,
                fd.dat_feedback,
                fd.editado,
                fd.dat_edicao,
                fd.id_usuario_edicao_id
            FROM feedback_demandas fd
            JOIN resposta_demanda rd ON rd.id_resposta = fd.id_resposta_id
        """).fetchall()

        criados = 0
        for row in rows:
            demanda_id = self._mapa_demanda.get(row["id_demanda_id"])
            usuario_id = self._mapa_usuario.get(row["id_usuario_id"])
            if not demanda_id or not usuario_id:
                continue

            editado_por_id = self._mapa_usuario.get(row["id_usuario_edicao_id"]) if row["id_usuario_edicao_id"] else None

            if not self.dry_run:
                _, novo = RevisaoModel.objects.get_or_create(
                    demanda_id=demanda_id,
                    defaults={
                        "usuario_id": usuario_id,
                        "texto": row["des_feedback"],
                        "editado": bool(row["editado"]),
                        "dat_edicao": _dt(row["dat_edicao"]),
                        "editado_por_id": editado_por_id,
                    },
                )
                if novo:
                    criados += 1

        self.stdout.write(f"  -> Revisões: {len(rows)} lidas, {criados} criadas")

    # ------------------------------------------------------------------ #
    # Histórico de Atribuições
    # ------------------------------------------------------------------ #

    def _importar_historico_atribuicoes(self):
        rows = self.conn.execute("""
            SELECT
                ha.id_demanda_id,
                ha.id_usuario_id,
                ha.tipo_atribuicao,
                ha.data_atribuicao,
                ha.atribuicao_valida
            FROM demandas_historicoatribuicao ha
        """).fetchall()

        criados = 0
        for row in rows:
            demanda_id = self._mapa_demanda.get(row["id_demanda_id"])
            usuario_id = self._mapa_usuario.get(row["id_usuario_id"])
            if not demanda_id or not usuario_id:
                continue

            if not self.dry_run:
                HistoricoAtribuicaoModel.objects.create(
                    demanda_id=demanda_id,
                    usuario_id=usuario_id,
                    tipo=row["tipo_atribuicao"],
                    valido=bool(row["atribuicao_valida"]),
                )
                criados += 1

        self.stdout.write(f"  -> Histórico de atribuições: {len(rows)} lidos, {criados} criados")

    # ------------------------------------------------------------------ #
    # Pendências Externas
    # ------------------------------------------------------------------ #

    def _importar_pendencias_externas(self):
        rows = self.conn.execute("""
            SELECT
                pe.id_demanda_id,
                pe.justificativa,
                pe.data_inicio,
                pe.data_fim,
                pe.id_usuario_criacao_id
            FROM pendencia_externa pe
        """).fetchall()

        criados = 0
        for row in rows:
            demanda_id = self._mapa_demanda.get(row["id_demanda_id"])
            criador_id = self._mapa_usuario.get(row["id_usuario_criacao_id"])
            if not demanda_id or not criador_id:
                continue

            if not self.dry_run:
                _, novo = PendenciaExternaModel.objects.get_or_create(
                    demanda_id=demanda_id,
                    defaults={
                        "justificativa": row["justificativa"],
                        "criador_id": criador_id,
                        "data_fim": row["data_fim"],
                    },
                )
                if novo:
                    criados += 1

        self.stdout.write(f"  -> Pendências externas: {len(rows)} lidas, {criados} criadas")
