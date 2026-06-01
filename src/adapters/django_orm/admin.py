from django.contrib import admin

from .models import (
    AfastamentoModel,
    DemandaModel,
    FeriadoModel,
    HistoricoAtribuicaoModel,
    OrigemDemandaModel,
    ProjetoLeiModel,
    RespostaModel,
    UsuarioModel,
)

admin.site.site_header = "CALLISTA — Gestão SEPEL"
admin.site.site_title = "CALLISTA Admin"
admin.site.index_title = "Painel de Administração"


@admin.register(OrigemDemandaModel)
class OrigemDemandaAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nome", "prazo_padrao_dias", "tem_numero", "ativo")
    list_editable = ("prazo_padrao_dias", "tem_numero", "ativo")
    search_fields = ("sigla", "nome")
    list_filter = ("ativo", "tem_numero")
    ordering = ("sigla",)


@admin.register(UsuarioModel)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "matricula", "cargo", "is_ativo", "is_oculto")
    list_editable = ("is_ativo", "is_oculto")
    search_fields = ("nome", "email", "matricula")
    list_filter = ("is_ativo", "is_oculto", "cargo")
    ordering = ("nome",)
    fieldsets = (
        ("Identificação", {"fields": ("nome", "email", "matricula", "cargo")}),
        ("Status", {"fields": ("is_ativo", "is_oculto")}),
    )


@admin.register(AfastamentoModel)
class AfastamentoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "dat_inicial", "dat_final", "motivo")
    search_fields = ("usuario__nome", "motivo")
    list_filter = ("usuario",)
    ordering = ("-dat_inicial",)
    autocomplete_fields = ("usuario",)


@admin.register(FeriadoModel)
class FeriadoAdmin(admin.ModelAdmin):
    list_display = ("data", "nome")
    search_fields = ("nome",)
    ordering = ("data",)
    date_hierarchy = "data"


@admin.register(DemandaModel)
class DemandaAdmin(admin.ModelAdmin):
    list_display = ("__str__", "origem", "status", "dat_chegada", "relator", "revisor", "dat_cadastro")
    list_filter = ("status", "origem")
    search_fields = ("texto", "origem", "num_origem")
    ordering = ("-dat_chegada",)
    date_hierarchy = "dat_chegada"
    readonly_fields = ("dat_cadastro",)
    autocomplete_fields = ("relator", "revisor")
    fieldsets = (
        ("Identificação", {"fields": ("origem", "num_origem", "texto")}),
        ("Prazo e Status", {"fields": ("dat_chegada", "dias_prazo", "status", "dat_cadastro")}),
        ("Atribuição", {"fields": ("relator", "revisor")}),
    )


@admin.register(RespostaModel)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ("demanda", "usuario", "dat_resposta", "editado")
    list_filter = ("editado",)
    search_fields = ("demanda__texto", "usuario__nome", "texto")
    readonly_fields = ("dat_resposta",)
    ordering = ("-dat_resposta",)


@admin.register(HistoricoAtribuicaoModel)
class HistoricoAtribuicaoAdmin(admin.ModelAdmin):
    list_display = ("demanda", "usuario", "tipo", "data_atribuicao", "valido")
    list_filter = ("tipo", "valido")
    search_fields = ("demanda__texto", "usuario__nome")
    readonly_fields = ("data_atribuicao",)
    ordering = ("-data_atribuicao",)


@admin.register(ProjetoLeiModel)
class ProjetoLeiAdmin(admin.ModelAdmin):
    list_display = ("identificacao", "situacao_atual", "tramitando", "dat_situacao", "dat_ultima_atualizacao")
    list_filter = ("tramitando", "sigla")
    search_fields = ("identificacao", "ementa", "autoria")
    ordering = ("-dat_ultima_atualizacao",)
    readonly_fields = ("dat_snapshot", "dat_ultima_atualizacao")
