from __future__ import annotations

import secrets
import string

import relationalai as rai

from pandas import DataFrame
from typing import Any, Union, cast, Optional

from .. import Compiler
from relationalai.early_access.metamodel.util import ordered_set
from relationalai.early_access.metamodel import ir, executor as e, factory as f

class SnowflakeExecutor(e.Executor):
    """Executes SQL using the RAI client."""

    def __init__(
            self,
            database: str,
            schema: str,
            dry_run: bool = False,
            skip_denormalization: bool = False,
            config: rai.Config | None = None,
    ) -> None:
        super().__init__()
        self.database = database
        self.schema = schema
        self.dry_run = dry_run
        self.config = config or rai.Config()
        self.compiler = Compiler(skip_denormalization)
        self.provider = cast(rai.clients.snowflake.Provider, rai.Provider(config=config))

    def execute(self, model: ir.Model, task:ir.Task, result_cols:Optional[list[str]]=None,
                export_to:Optional[str]=None, update:bool=False) -> Union[DataFrame, Any]:
        """ Execute the SQL query directly. """
        if self.dry_run:
            return DataFrame()

        db_name = f"{self.database}_{self._generate_unique_id()}"
        db_query = f"CREATE OR REPLACE DATABASE {db_name};"
        schema_query = f"CREATE OR REPLACE SCHEMA {db_name}.{self.schema};"
        use_schema_query = f"USE SCHEMA {db_name}.{self.schema};"
        model_sql = self.compiler.compile(model)

        full_sql_model = f"{db_query}\n{schema_query}\n{use_schema_query}\n{model_sql}"

        # TODO: find the way how to compile task instead of building model with one root task
        query_model = f.model(ordered_set(), ordered_set(), ordered_set(), task)
        query_sql = self.compiler.compile(query_model)

        try:
            self.provider.resources._session.connection.execute_string(full_sql_model) # type: ignore
            result = cast(DataFrame, self.provider.sql(query_sql, format='pandas'))
            return result
        finally:
            self.provider.sql(f"DROP DATABASE IF EXISTS {db_name};")

    def _generate_unique_id(self, length=7):
        alphabet = string.ascii_letters + string.digits  # a-zA-Z0-9
        return ''.join(secrets.choice(alphabet) for _ in range(length))