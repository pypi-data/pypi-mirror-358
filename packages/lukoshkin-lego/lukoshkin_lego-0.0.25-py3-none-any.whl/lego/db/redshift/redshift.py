"""
Example usage:
redshift = RedshiftData(RedshiftBoto3Connection())
statement_id = redshift.execute_query("SELECT * FROM ixi.cohorts LIMIT 10")
result = asyncio.run(redshift.get_query_result(statement_id))
"""

import asyncio
from io import StringIO
from typing import Any

import boto3
import pandas as pd

from lego.db.redshift import errors
from lego.lego_types import OneOrMany
from lego.settings import RedshiftBoto3Connection


class RedshiftQueryResult:
    """A wrapper around the Redshift query result"""

    def __init__(self, desc: dict, result: dict):
        self.desc = desc
        self.result = result
        self.result_format = result.get("ResultFormat", "json").lower()

    def cast_to_records(self) -> list[dict[str, Any]]:
        """Convert the result to a list of dicts: [{column: value}, ...]"""
        if self.result_format == "csv":
            return self.cast_to_pandas().to_dict(orient="records")

        return [
            {
                column: next(iter(entry.values()))
                for column, entry in zip(
                    (col["name"] for col in self.result["ColumnMetadata"]),
                    record,
                )
            }
            for record in self.result["Records"]
        ]

    def cast_to_pandas(self) -> pd.DataFrame:
        """Convert the result to a pandas DataFrame"""
        if self.result_format == "json":
            return pd.DataFrame(self.cast_to_records())
        if self.result["Records"]:
            return pd.read_csv(
                StringIO(self.result["Records"][0]["CSVRecords"])
            )
        return pd.DataFrame(
            columns=[col["name"] for col in self.result["ColumnMetadata"]]
        )

    def __repr__(self) -> str:
        rows = self.desc["ResultRows"]
        cols = self.desc["ResultSize"] // rows
        return (
            "RedshiftQueryResult(\n"
            f"\tresult_format={self.result_format},\n"
            f"\tsize=(rows={rows}, cols={cols}),\n"
            ")"
        )


class RedshiftData:
    """Easier management of Boto3's Redshift Data API"""

    def __init__(
        self,
        connection: RedshiftBoto3Connection,
        query_timeout: int = 30,
        default_sub_ids: OneOrMany[int] = 0,
        use_v2: bool = True,
    ):
        """
        Args:
        :param connection: An instance of lego's RedshiftBoto3Connection class
        :param query_timeout: The maximum time to wait for a query to finish
        :param default_sub_ids: positional IDs of substatement results to collect
        :param use_v2: Use execute_statement/get_statement_result v2 version
            to get the results in CSV format instead of JSON
        """
        self.connection = connection
        self.query_timeout = query_timeout
        self.default_sub_ids = default_sub_ids
        self.client = boto3.client(
            "redshift-data", region_name=connection.aws_region
        )
        if use_v2:
            self._result_format = "CSV"
            self._get_statement_result = self.client.get_statement_result_v2
        else:
            self._result_format = "JSON"
            self._get_statement_result = self.client.get_statement_result

    def execute_query(self, query: OneOrMany[str]) -> str:
        """Execute a SQL query on Redshift"""
        if isinstance(query, str):
            query = [query]

        response = self.client.batch_execute_statement(
            Database=self.connection.database,
            WorkgroupName=self.connection.workgroup,
            Sqls=query,
            ResultFormat=self._result_format,
            SecretArn=self.connection.secret_arn,
            WithEvent=False,  # do not send an event to EventBridge event bus
        )
        return response["Id"]

    async def get_query_result(
        self,
        statement_id: str,
        substatement_pos_id: OneOrMany[int] | None = None,
        polling_period: float = 0.2,
        timeout: float | None = None,
    ) -> list[RedshiftQueryResult]:
        """
        Get the result of a submitted query by its statement ID

        Raises `TimeoutError` if the query takes longer
        than the specified timeout

        Args:
        :param statement_id: The ID of the submitted statement
        :param polling_period: The time between each poll in seconds
        :param timeout: The maximum time to wait for the query to finish
        """
        wait_time: float = 0
        timeout = timeout or self.query_timeout
        if substatement_pos_id is None:
            substatement_pos_id = self.default_sub_ids

        if polling_period <= 0:
            raise ValueError("Polling period must be positive")
        if timeout < polling_period:
            raise ValueError(
                f"The polling exceeds the timeout:"
                f" {polling_period} > {timeout}"
            )
        while wait_time < (timeout or self.query_timeout):
            desc = self.client.describe_statement(Id=statement_id)
            if desc["Status"] in ("FINISHED", "FAILED", "ABORTED"):
                break

            await asyncio.sleep(polling_period)
            wait_time += polling_period

        if desc["Status"] == "FINISHED":
            if isinstance(substatement_pos_id, int):
                substatement_pos_id = [substatement_pos_id]

            return [
                RedshiftQueryResult(
                    desc=desc["SubStatements"][pos],
                    result=self._get_statement_result(
                        Id=desc["SubStatements"][pos]["Id"]
                    ),
                )
                for pos in substatement_pos_id
            ]

        if desc["Status"] == "FAILED":
            raise errors.RedshiftDataError(desc)

        if desc["Status"] == "ABORTED":
            raise errors.RedshiftQueryAbortedError("Query was aborted")

        raise TimeoutError(f"Query {desc["QueryString"]} timed out")
