from psql_partition.types import PostgresPartitioningMethod, SQLWithParams


class PostgresPartitionedModelOptions:
    """Container for :see:PostgresPartitionedModel options.

    This is where attributes copied from the model's `PartitioningMeta`
    are held.
    """

    def __init__(self, method: PostgresPartitioningMethod, key: list[str]):
        self.method = method
        self.key = key
        self.original_attrs: dict[str, PostgresPartitioningMethod | list[str] | None] = (
            dict(method=method, key=key)
        )


class PostgresViewOptions:
    """Container for :see:PostgresView and :see:PostgresMaterializedView
    options.

    This is where attributes copied from the model's `ViewMeta` are
    held.
    """

    def __init__(self, query: SQLWithParams | None):
        self.query = query
        self.original_attrs: dict[str, SQLWithParams | None] = dict(query=self.query)
