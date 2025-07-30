import re
from functools import cached_property, wraps

from loguru import logger


class QueryProcessorImplementationError(Exception):
    """Query processor implementation error."""


class ChatBotSQLQuery:
    """SQL query processing tool."""

    def __init__(self, sql: str, llm_limit_value: str | None = None) -> None:
        """
        Initialize the SQLQuery object.

        :param sql: The SQL query string.
        :param llm_limit_value: pattern of limit value added by the LLM.
        """
        self.sql: str = sql.strip().rstrip(";").rstrip()
        self.llm_limit_pat = (
            re.compile(rf"LIMIT\s+({llm_limit_value}(?::(\d+))?)")
            if llm_limit_value
            else None
        )

        self.select_pat = re.compile(r"\bSELECT\b")
        self.limit_at_end = re.compile(r"LIMIT\s+(\d+)(?:\s+OFFSET\s+\d+)?$")
        self.offset_at_end = re.compile(r"OFFSET\s+(\d+)(?:\s+LIMIT\s+\d+)?$")
        self.sql_prefix_path = re.compile(
            r"^(?:\s*SET\b.*?;\s*\n?)+\s*(?!SET)"
        )

    def __str__(self) -> str:
        return self.sql

    def llm_limit(
        self, limit: int = 10, check_is_select_sql: bool = True
    ) -> str:
        """
        Adjust LIMIT statement in a SQL query.

        Adjusts SQL based on the LIMIT pattern included by the LLM.
        If it is not found, the `manual_limit` method is called.

        Args:
        :param limit: The maximum number of rows to return.
        """
        if not self.llm_limit_pat:
            return self.manual_limit(limit, check_is_select_sql)

        if check_is_select_sql and not self.select_pat.search(self.sql):
            logger.error("The query must contain a SELECT statement.")
            return self.sql

        def replace_limit(match):
            if match.group(2) and int(match.group(2)) < limit:
                return f"LIMIT {match.group(2)}"
            return f"LIMIT {limit}"

        sql, num_subs = self.llm_limit_pat.subn(replace_limit, self.sql)
        if num_subs > 0:
            return sql

        logger.warning(f"The SQL was not limited by the LLM: {self.sql}")
        return self.manual_limit(limit, check_is_select_sql=False)

    def manual_limit(
        self, limit: int = 10, check_is_select_sql: bool = False
    ) -> str:
        """
        Manually append/adjust a LIMIT statement to/in a SQL query.

        If the LIMIT is already there and less than `limit`, no change is made.
        If `limit` is less than 1, no limit is applied.
        """
        if limit < 1:
            logger.warning("The provided limit is less than 1.")
            return self.sql

        if check_is_select_sql and not self.select_pat.search(self.sql):
            logger.error("The query must contain a SELECT statement.")
            return self.sql

        def replace_limit(match):
            if int(match.group(1)) < limit:
                return f"LIMIT {match.group(1)}"
            return f"LIMIT {limit}"

        sql, num_subs = self.limit_at_end.subn(replace_limit, self.sql)
        if num_subs > 1:
            raise QueryProcessorImplementationError(
                'The query contains more than one LIMIT "at the end".'
            )
        if num_subs > 0:
            return sql

        return f"{sql}\nLIMIT {limit}"

    def manual_offset(self, offset: int = 0) -> str:
        """Manually append/adjust an OFFSET statement to/in a SQL query."""
        sql, num_subs = self.offset_at_end.subn(f"OFFSET {offset}", self.sql)
        if num_subs > 1:
            raise QueryProcessorImplementationError(
                'The query contains more than one OFFSET "at the end".'
            )
        if num_subs > 0:
            return sql

        return f"{sql}\nOFFSET {offset}"

    @cached_property
    def no_llm_limit_sql(self) -> str:
        """Remove the LLM's "LIMIT" statement from the SQL query."""
        if not self.llm_limit_pat:
            return self.sql

        def replace_limit(match):
            if match.group(2):
                return f"LIMIT {match.group(2)}"
            return ""

        return self.llm_limit_pat.sub(replace_limit, self.sql)

    @cached_property
    def count_sql(self) -> str:
        """Count the rows in the result set of the original query."""
        if not self.select_pat.search(self.no_llm_limit_sql):
            raise ValueError("The query must contain a SELECT statement.")

        if sets_match := self.sql_prefix_path.search(self.no_llm_limit_sql):
            sets = sets_match.group(0)
            target_sql = self.no_llm_limit_sql[len(sets) :]
            return f"{sets}\nSELECT COUNT(*) FROM ({target_sql}) AS subquery"

        return f"SELECT COUNT(*) FROM ({self.no_llm_limit_sql}) AS subquery"

    @cached_property
    def explain_sql(self) -> str:
        """Get the execution plan of the original query."""
        if sets_match := self.sql_prefix_path.search(self.no_llm_limit_sql):
            sets = sets_match.group(0)
            return f"{sets}\nEXPLAIN\n{self.no_llm_limit_sql[len(sets):]}"

        return f"EXPLAIN\n{self.no_llm_limit_sql}"

    @property
    def chain(self) -> "_ChainProxy":
        """
        Return a development proxy instance.

        When methods are called on this proxy and they return a string,
        the string is wrapped in a new ChatBotSQLQuery with `llm_limit_value`
        set to None.
        """
        return _ChainProxy(self)


class _ChainProxy:
    """
    A proxy for ChatBotSQLQuery that intercepts method calls.

    If a method call returns a string, the proxy wraps it in a new
    ChatBotSQLQuery with llm_limit_value set to None.
    """

    def __init__(self, query: ChatBotSQLQuery) -> None:
        self._query = query

    def __getattr__(self, attr_name):
        attr = getattr(self._query, attr_name)
        if callable(attr):

            @wraps(attr)
            def wrapped(*args, **kwargs):
                result = attr(*args, **kwargs)
                if isinstance(result, str):
                    return ChatBotSQLQuery(result, llm_limit_value=None)
                return result

            return wrapped
        return attr


sql = """SET search_path TO dg1;
WITH ranked_results AS (
    SELECT
        c.contact_id,
        c.first_name,
        c.last_name,
        ic.auto_in_market_aim_propensity_score AS propensity_score,
        ic.economiccohortscode,
        coh.description AS cohort_description,
        r.make,
        r.model,
        r.year,
        r.trim,
        r.body,
        r.stock AS stock_number,
        i.new_used AS vehicle_condition,
        ROW_NUMBER() OVER (PARTITION BY c.contact_id ORDER BY ic.auto_in_market_aim_propensity_score DESC) AS rank
    FROM
        dg1.recommendations r
    JOIN
        dg1.contacts c ON r.contact_id = c.contact_id
    JOIN
        ixi.consumers ic ON c.consumer_key = ic.consumer_key
    LEFT JOIN
        ixi.cohorts coh ON ic.economiccohortscode = coh.id
    JOIN
        dg1.inventory i ON r.vin = i.vin
    WHERE
        r.make ILIKE 'KIA'
        AND i.new_used = 'New' -- Filter for new vehicles
        AND ic.auto_in_market_aim_propensity_score > 750 -- Filter for in-market customers
)
SELECT
    contact_id,
    first_name,
    last_name,
    propensity_score,
    make,
    model,
    year,
    trim,
    body,
    stock_number,
    vehicle_condition,
    economiccohortscode,
    cohort_description
FROM
    ranked_results
WHERE
    rank = 1 -- Select only the top result per contact_id
ORDER BY
    propensity_score DESC;"""

query = ChatBotSQLQuery(sql)
print(query.llm_limit(5))
