from __future__ import annotations

import duckdb
from pandas import DataFrame
from typing import Any, Union

from .. import Compiler
from relationalai.early_access.metamodel import ir, executor as e, factory as f

class DuckDBExecutor(e.Executor):

    def __init__(self, skip_denormalization: bool = False) -> None:
        super().__init__()
        self.compiler = Compiler(skip_denormalization)

    def execute(self, model: ir.Model, task:ir.Task) -> Union[DataFrame, Any]:
        """ Execute the SQL query directly. """
        model = f.compute_model(f.logical([model.root, task]))

        connection = duckdb.connect()
        try:
            result = connection.query(self.compiler.compile(model)).to_df()
            return result
        finally:
            connection.close()