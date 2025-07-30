from typing import Generic, Literal, TypeAlias, TypedDict, TypeVar

from pydantic import BaseModel, Field, create_model

from lego.llm.utils import json_compose
from lego.models import CamelModel


class SQLModelBaseComponent(BaseModel):
    """The base class for all components."""

    def convert_to_component(self) -> "SQLModelComponent":
        """Convert a child class to SQLModelComponent."""
        return SQLModelComponent(**self.model_dump(by_alias=True))


class SQLModelComponent(SQLModelBaseComponent, extra="allow"):  # type: ignore[call-arg]
    """The component of the common protocol."""

    nlq: str = Field(
        default="",
        description=(
            "The part of the whole user prompt that corresponds to a"
            " self-contained subquery given in the same natural language"
            " but reformulated for clarity and brevity. If there are no"
            " logical parts in the user prompt, the 'nlq' corresponds to"
            " the whole user prompt."
        ),
    )
    sql: str = Field(
        ...,
        title="Complete Redshift query",
        description=(
            "A Redshift SQL query corresponding to the 'nlq'"
            " that helps to answer the user prompt"
        ),
    )
    sampling_sql: str = Field(
        default="",
        description=(
            "The sampling SQL query corresponding to the generated Redshift"
            " SQL. It is used to randomly sample a small amount of data"
            " for the frontend visualization: without duplicates and"
            " unnecessary columns. Always limit the number of rows to"
            " a small number around 10."
        ),
    )
    selected_tables: list[str] = Field(
        default=[],
        description=(
            "List of the all table names used in the generated Redshift"
            " 'sql' query and given in the fully-qualified form:"
            " <schema_name>.<table_name>"
        ),
    )


class SQLBasePartition(BaseModel):
    """The base class for all components partition models."""

    def convert_to_smp(self) -> "SQLModelProtocol":
        """Convert a child class to SQLModelProtocol."""
        return SQLModelProtocol(
            components=[
                comp.convert_to_component() for comp in self.components
            ]
        )


class SQLModelProtocol(SQLBasePartition):
    """The common protocol for all models above."""

    components: list[SQLModelComponent] = Field(
        ...,
        description=(
            "List of Redshift SQL queries that help to answer the user prompt."
            " Each query is accompanied by the reformulated part of the"
            " user prompt and the sampling SQL query."
        ),
    )

    def __iter__(self):
        """Iterate over the components."""
        return iter(self.components)

    def sql_queries(self) -> list[str]:
        """Return the list of SQL queries."""
        return [component.sql for component in self.components]

    def observed_tables(self) -> list[str]:
        """Return the list of observed tables."""
        return list(
            {
                table
                for component in self.components
                for table in component.selected_tables
            }
        )


def extend_model(
    model_cls: type[BaseModel],
    with_tables: bool,
    with_partition: bool,
    partition_model_docstring: str = "",
    components_docstring: str = "",
) -> type[BaseModel]:
    """
    Extend the model with the selected tables and/or partition.

    Args:
        model_cls: the model class to extend.
        with_tables: whether to include the selected_tables field.
        with_partition: whether to wrap the model into the partition.
    """
    if not with_tables and not with_partition:
        return model_cls

    ExtendedClass = model_cls
    model_name = model_cls.__name__
    if with_tables:
        model_name += "WithSelectedTables"
        ExtendedClass = create_model(
            model_name,
            selected_tables=(
                list[str],
                Field(
                    ...,
                    description=(
                        "List of all table names used in the generated "
                        "Redshift SQL query(-ies) and given in the fully-qualified "
                        "form: <schema_name>.<table_name>"
                    ),
                ),
            ),
            __base__=model_cls,
        )
    if with_partition:
        model_name += "Partition"
        ExtendedModel = create_model(
            model_name,
            components=(
                list[ExtendedClass],
                Field(
                    ...,
                    description=components_docstring
                    or "List of reformulated logically separate parts of the user query",
                ),
            ),
            __base__=SQLBasePartition,
            __doc__=partition_model_docstring or ExtendedClass.__doc__,
        )
        return ExtendedModel

    return ExtendedClass


class SQLSingleton(SQLModelBaseComponent):
    """Generate the Redshift SQL query that helps to answer the user prompt."""

    sql: str = Field(
        ...,
        description=(
            "The Redshift query that is relevant to the user prompt and"
            " extracts all the information necessary to respond to the user."
        ),
    )


## NOTE: no guarantees to work with the same set of tables
## NOTE: currently is not used anywhere
class MendSQLSingleton(SQLModelBaseComponent):
    """Adjust the provided SQL query to the updated user prompt."""

    updated_sql: str = Field(
        ...,
        alias="sql",
        description=(
            "The updated Redshift SQL query which is build on top of the"
            " original with the adjustments made to retrieve the necessary"
            " information in the updated user prompt."
        ),
    )


## NOTE: Aimed to work with the fixed set of tables
class AdjustSQLSingleton(SQLModelBaseComponent):
    """Adjust the provided SQL query to the updated user prompt."""

    updated_sql: str = Field(
        ...,
        alias="sql",
        description=(
            "The updated Redshift SQL query which is equivalent to the"
            " original one in terms of the set of the selected tables but"
            " includes adjustments for retrieving the necessary information"
            " in the updated user prompt."
        ),
    )


class SQLDoublet(SQLModelBaseComponent):
    """Generate Redshift SQL queries that help to answer the user prompt."""

    main_sql: str = Field(
        ...,
        alias="sql",
        title="Complete Redshift query",
        description="The Redshift query that helps to fully answer the user prompt",
    )
    sampling_sql: str = Field(
        ...,
        title="Sampling Redshift query",
        description=(
            "A counterpart of the 'Complete Redshift query' needed to"
            " randomly sample a small amount of data for the frontend"
            " visualization and the further unbiased analysis with the LLM."
            " The visualization should be presented to the user without"
            " duplicates and unnecessary columns. Always limit the number of"
            " rows in the final result of the 'Sampling Redshift query'"
            " to about 10 rows. NOTE that for the fair analysis, it is better"
            " to sample rows randomly than just pick the first few ones if"
            " the user query does not imply any specific order."
        ),
    )


class NLQ2SQLPair(SQLModelBaseComponent):
    """Reformulated part of the user prompt and the corresponding SQL query."""

    nlq: str = Field(
        ...,
        description=(
            "Reformulated part (NLQ) of the user prompt"
            " that represents a separate request for the data extraction."
        ),
    )
    sql: str = Field(
        ..., description="The NLQ converted to the Redshift query."
    )

    def convert_to_smp(self) -> "SQLModelProtocol":
        """Convert the NLQ2SQLPair to SQLModelProtocol."""
        return SQLModelProtocol(
            components=[SQLModelComponent(sql=self.sql, nlq=self.nlq)]
        )


SQLGenResponseModel: TypeAlias = (
    SQLModelBaseComponent
    | SQLBasePartition
    | SQLModelComponent
    | SQLModelProtocol
)
PyModel = TypeVar("PyModel")


class FewShotExample(TypedDict, Generic[PyModel]):
    """The fixed structure of a few-shot example."""

    query: str
    pymodel: PyModel


class _DrillDownOption(CamelModel):
    """A drill-down action representation."""

    short_name: str = Field(
        ...,
        description=(
            "A super short name of the drill-down action, literally three or"
            " four words at maximum that will be displayed on the frontend."
            " When options require user input and the typed-in value will be"
            " used as a threshold, make it clear whether it is above or below"
        ),
    )
    description: str = Field(
        ...,
        description=(
            "A short description of the drill-down action to pass it to the"
            " next LLM prompt. If 'use_case' is 'java', the description may"
            " be omitted. NOTE: when 'user_input_type' is not None, the"
            " description should contain the placeholder '{placeholder}'"
            " for the user input."
        ),
    )
    user_input_type: Literal["str", "int", "float", "date"] | None = Field(
        ...,
        description=(
            "The expected type of the user clarification required for the"
            " filter: a string, an integer, a float, or a date. Differentiate"
            " between absolute and relative dates. The type for relative ones"
            " should be still 'str'. In general, the type can be determined"
            " by the respective column type in the database. Make it None (in"
            " JSON it is null) when the user input is not needed. Note that it"
            " is always None when the `use_case` is 'java'."
        ),
    )
    # comparison_operator: Literal["=", ">", "<"] | None = Field(
    #     ...,
    #     description=(
    #         "The comparison operator that will be applied in the selected"
    #         " drill down option to the user input. Whenever the"
    #         " user input is a string, the operator is always '='. For the"
    #         " numeric values and dates, the operator can be '=', '>', or '<'."
    #         " Make it None (null in JSON) when the user input is not needed."
    #     ),
    # )
    use_case: Literal["llm", "java"] = Field(
        ...,
        description=(
            "The use case of the selected drill-down action. Whether the"
            " selected action should be returned back to the LLM, on "
            " Python-backend ('llm' literal) for further processing or the"
            " frontend needs to send it to the Java-backend ('java' literal)."
            " Determining the use case is easy: if the drill down action "
            " requires modifications over the SQL query, it should be marked"
            " as 'llm', otherwise as 'java'."
        ),
    )


class DrillDownOptions(CamelModel):
    """Output possible drill-down options for the given SQL query."""

    accompanying_response: str = Field(
        ...,
        description=(
            "The response to the user accompanying the drill-down options."
            " It should make the short names of the drill-down actions more"
            " understandable."
        ),
    )
    drill_down_options: list[_DrillDownOption] = Field(
        ...,
        description=(
            "List of drill-down actions that a user can take to"
            " amend their original SQL query."
        ),
    )


if __name__ == "__main__":
    ext_model = extend_model(
        NLQ2SQLPair,
        with_tables=True,
        with_partition=True,
        components_docstring="test",
    )
    print(NLQ2SQLPair(nlq="test", sql="test").convert_to_smp())
    parsed_model = ext_model.model_validate({
        "components": [
            {
                "nlq": "test",
                "sql": "SELECT * FROM test",
                "selected_tables": ["schema.table"],
            }
        ]
    })
    print(parsed_model.convert_to_smp())
    print(ext_model.__fields__["components"])
    print(json_compose.response_format(ext_model))
