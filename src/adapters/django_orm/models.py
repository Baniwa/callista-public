from django.db import models


class UsuarioModel(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=100, blank=True, default="")
    is_ativo = models.BooleanField(default=True)
    is_oculto = models.BooleanField(default=False)

    class Meta:
        db_table = "callista_usuario"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self) -> str:
        return self.nome


class FeriadoModel(models.Model):
    data = models.DateField(unique=True)
    nome = models.CharField(max_length=100)

    class Meta:
        db_table = "callista_feriado"
        ordering = ["data"]

    def __str__(self) -> str:
        return f"{self.nome} ({self.data})"


class AfastamentoModel(models.Model):
    usuario = models.ForeignKey(
        UsuarioModel, on_delete=models.CASCADE, related_name="afastamentos"
    )
    dat_inicial = models.DateField()
    dat_final = models.DateField()
    motivo = models.CharField(max_length=200)

    class Meta:
        db_table = "callista_afastamento"
        unique_together = [("usuario", "dat_inicial", "dat_final")]

    def __str__(self) -> str:
        return f"{self.usuario.nome}: {self.dat_inicial} → {self.dat_final}"


class OrigemDemandaModel(models.Model):
    """Origem/órgão de uma demanda, com prazo padrão configurável.
    Equivale ao model OrigemDemanda do Callista 1.0 (tabela origem_demanda).
    No 2.0 a sigla ainda existe como CharField em DemandaModel para compatibilidade
    retroativa — este model permite a normalização completa.
    """
    sigla = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=255)
    prazo_padrao_dias = models.PositiveSmallIntegerField(default=5)
    tem_numero = models.BooleanField(default=False)

    class Meta:
        db_table = "callista_origem_demanda"
        verbose_name = "Origem de Demanda"
        verbose_name_plural = "Origens de Demandas"

    def __str__(self) -> str:
        return f"{self.sigla} — {self.nome}"


class DemandaModel(models.Model):
    STATUS_CHOICES = [
        ("PR", "Pendente de Resposta"),
        ("PF", "Pendente de Revisão"),
        ("PE", "Pendente Externa"),
        ("C", "Concluída"),
    ]

    origem = models.CharField(max_length=50)
    origem_ref = models.ForeignKey(
        OrigemDemandaModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="demandas",
    )
    num_origem = models.IntegerField(null=True, blank=True)
    texto = models.TextField()
    dat_chegada = models.DateField()
    dias_prazo = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PR")
    relator = models.ForeignKey(
        UsuarioModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="demandas_como_relator",
    )
    dat_atribuicao_relator = models.DateTimeField(null=True, blank=True)
    revisor = models.ForeignKey(
        UsuarioModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="demandas_como_revisor",
    )
    dat_atribuicao_revisor = models.DateTimeField(null=True, blank=True)
    criador = models.ForeignKey(
        UsuarioModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="demandas_criadas",
    )
    dat_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "callista_demanda"
        ordering = ["-dat_chegada"]

    def __str__(self) -> str:
        return f"[{self.status}] {self.origem} #{self.num_origem or self.pk}"


class RespostaModel(models.Model):
    demanda = models.ForeignKey(
        DemandaModel, on_delete=models.CASCADE, related_name="respostas"
    )
    usuario = models.ForeignKey(
        UsuarioModel, on_delete=models.PROTECT, related_name="respostas"
    )
    texto = models.TextField()
    dat_resposta = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    dat_edicao = models.DateTimeField(null=True, blank=True)
    editado_por = models.ForeignKey(
        UsuarioModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="respostas_editadas",
    )

    class Meta:
        db_table = "callista_resposta"
        ordering = ["dat_resposta"]

    def __str__(self) -> str:
        return f"Resposta de {self.usuario.nome} para demanda #{self.demanda_id}"


class RevisaoModel(models.Model):
    """Revisão de uma demanda — entidade separada da Resposta.
    Equivale ao model FeedbackDemandas do Callista 1.0 (tabela feedback_demandas).
    """
    demanda = models.OneToOneField(
        DemandaModel, on_delete=models.CASCADE, related_name="revisao"
    )
    usuario = models.ForeignKey(
        UsuarioModel, on_delete=models.PROTECT, related_name="revisoes"
    )
    texto = models.TextField()
    dat_revisao = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    dat_edicao = models.DateTimeField(null=True, blank=True)
    editado_por = models.ForeignKey(
        UsuarioModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revisoes_editadas",
    )

    class Meta:
        db_table = "callista_revisao"
        ordering = ["dat_revisao"]

    def __str__(self) -> str:
        return f"Revisão de {self.usuario.nome} para demanda #{self.demanda_id}"


class HistoricoAtribuicaoModel(models.Model):
    """Rastreia cada atribuição de relator ou revisor a uma demanda.
    Equivale ao model HistoricoAtribuicao do Callista 1.0.
    """
    TIPO_CHOICES = [
        ("RES", "Resposta"),
        ("REV", "Revisão"),
    ]

    demanda = models.ForeignKey(
        DemandaModel, on_delete=models.CASCADE, related_name="historico_atribuicoes"
    )
    usuario = models.ForeignKey(
        UsuarioModel, on_delete=models.PROTECT, related_name="historico_atribuicoes"
    )
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES)
    data_atribuicao = models.DateTimeField(auto_now_add=True)
    valido = models.BooleanField(default=True)

    class Meta:
        db_table = "callista_historico_atrib"
        ordering = ["data_atribuicao"]

    def __str__(self) -> str:
        return f"{self.tipo} — demanda #{self.demanda_id} → {self.usuario.nome}"


class PendenciaExternaModel(models.Model):
    """Justificativa e controle de tempo para demandas com status PE.
    Equivale ao model PendenciaExterna do Callista 1.0 (tabela pendencia_externa).
    """
    demanda = models.OneToOneField(
        DemandaModel, on_delete=models.CASCADE, related_name="pendencia_externa"
    )
    justificativa = models.TextField()
    criador = models.ForeignKey(
        UsuarioModel, on_delete=models.PROTECT, related_name="pendencias_criadas"
    )
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "callista_pendencia_externa"

    def __str__(self) -> str:
        return f"Pendência externa — demanda #{self.demanda_id}"


class ProjetoLeiModel(models.Model):
    """Snapshot de um Projeto de Lei rastreado via API do Senado Federal.

    Cada vez que o use case RastrearPL é executado, este registro é atualizado
    com os dados mais recentes da API. A comparação com o snapshot anterior
    permite detectar mudanças de status.
    """
    id_senado = models.IntegerField(unique=True)
    identificacao = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    numero = models.IntegerField()
    ano = models.IntegerField()
    ementa = models.TextField()
    tramitando = models.BooleanField()
    situacao_atual = models.CharField(max_length=200)
    sigla_situacao = models.CharField(max_length=20, blank=True)
    dat_situacao = models.DateField()
    url_documento = models.CharField(max_length=500, blank=True)
    autoria = models.CharField(max_length=500, blank=True)
    dat_ultima_atualizacao = models.DateTimeField()
    demanda = models.ForeignKey(
        DemandaModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="projetos_lei",
    )
    dat_snapshot = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "callista_projeto_lei"
        ordering = ["-dat_ultima_atualizacao"]

    def __str__(self) -> str:
        return self.identificacao
