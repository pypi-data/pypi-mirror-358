# this should not be here, but there are users depending
# on this being here, so let's leave it here so we don't
# break them
from psql_partition.query import PostgresQuerySet

from .manager import PostgresManager

__all__ = ["PostgresManager", "PostgresQuerySet"]
