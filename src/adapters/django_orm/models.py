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


class DemandaModel(models.Model):
    STATUS_CHOICES = [
        ("PR", "Pendente de Resposta"),
        ("PF", "Pendente de Revisão"),
        ("PE", "Pendente Externa"),
        ("C", "Concluída"),
    ]

    origem = models.CharField(max_length=50)
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
    revisor = models.ForeignKey(
        UsuarioModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="demandas_como_revisor",
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
    usuario = models.ForeignKey(UsuarioModel, on_delete=models.PROTECT)
    texto = models.TextField()
    dat_resposta = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)

    class Meta:
        db_table = "callista_resposta"
        ordering = ["dat_resposta"]

    def __str__(self) -> str:
        return f"Resposta de {self.usuario.nome} para demanda #{self.demanda_id}"
