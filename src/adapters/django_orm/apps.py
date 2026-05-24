from django.apps import AppConfig


class DjangoOrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.adapters.django_orm"
    verbose_name = "CALLISTA — ORM"
