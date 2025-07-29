from django.apps import AppConfig


class PostgresExtraAppConfig(AppConfig):
    name = "psql_partition"
    verbose_name = "PostgreSQL Extra"

    def ready(self) -> None:
        from .lookups import InValuesLookup  # noqa
