"""Connections to databases, buckets, and other services."""

import ast

from loguru import logger
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from lego.lego_types import JSONDict, OneOrMany


def settings_config(env_prefix: str | None, **kwargs) -> SettingsConfigDict:
    """Create a configuration for settings model."""
    if env_prefix:
        kwargs["env_prefix"] = env_prefix

    return SettingsConfigDict(
        env_file=kwargs.pop("env_file", ".env"),
        env_file_encoding=kwargs.pop("env_file_encoding", "utf-8"),
        extra=kwargs.pop("extra", "ignore"),
        ## With `extra="ignore"`, we can put many settings in one .env file.
        ## Thus, it won't raise an error if some of them are not used by a model
        **kwargs,
    )


def nonone_serialize(model_dict: JSONDict) -> JSONDict:
    """Serialize values that are not None."""
    return {
        key: value for key, value in model_dict.items() if value is not None
    }


class APIKeys:
    """API keys for some service provider."""

    def __init__(self, api_keys: OneOrMany[str]):
        self.api_keys: list[str] = (
            api_keys if isinstance(api_keys, list) else [api_keys]
        )
        self.api_key = self.api_keys[0]

    @classmethod
    def from_list_string(cls, api_keys: str) -> "APIKeys":
        """Create an APIKeys object from a string representing a list."""
        api_keys = api_keys.strip()
        if api_keys.startswith("[") and api_keys.endswith("]"):
            return APIKeys(ast.literal_eval(api_keys))
        if api_keys.startswith("'") and api_keys.endswith("'"):
            return APIKeys(ast.literal_eval(api_keys))
        try:
            return APIKeys(api_keys)
        except Exception as exc:
            logger.error(exc)
            raise ValueError(
                "Value is not enclosed with [] or ''."
                " It either can't be used directly as a string."
            ) from exc

    def __getitem__(self, idx: int) -> str:
        return self.api_keys[idx % len(self.api_keys)]

    def __len__(self) -> int:
        return len(self.api_keys)


class MilvusConnection(BaseSettings):
    """Settings to establish a connection with MilvusDB."""

    model_config = settings_config("milvus_")

    uri: str | None = None
    token: str | None = None
    host: str | None = None
    port: int | None = None

    @model_validator(mode="after")
    def validate_fields(self):
        """Validate the fields of the model."""
        if not self.uri and not (self.host and self.port):
            raise ValueError("Either 'uri' or 'host' and 'port' must be set.")
        return self


class S3Connection(BaseSettings):
    """Settings to establish a connection with an S3 bucket."""

    model_config = settings_config("s3_")

    access_key: str
    secret_key: str


class RedisConnection(BaseSettings):
    """Settings to establish a connection with a Redis database."""

    model_config = settings_config("redis_")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None

    def url(self) -> str:
        """Create a URL to connect to the Redis database.

        May require proper handling with `urllib.parse.unquote_plus`
        which is currently not implemented in the code.
        """
        url_after_pass = f"{self.host}:{self.port}/{self.db}"
        url = (
            f":{self.password}@{url_after_pass}"
            if self.password
            else url_after_pass
        )
        return f"redis://{url}"


class AmazonAccess(BaseSettings):
    """Settings for access to AWS services."""

    model_config = settings_config("aws_", env_file="~/.aws/credentials")

    access_key_id: str | None = None
    secret_access_key: str | None = None
    role_name: str | None = None
    session_name: str | None = None
    session_token: str | None = None
    profile_name: str | None = None
    region_name: str = "us-east-1"

    def serialize(self) -> dict[str, str]:
        """Serialize values that are not None."""
        return nonone_serialize(self.model_dump())


class RedshiftBoto3Connection(BaseSettings):
    """Settings to establish a connection with Boto3's 'redshift-data' API."""

    model_config = settings_config("redshift_")

    secret_arn: str
    workgroup: str
    database: str

    aws_region: str = "us-east-1"


class RedshiftConnection(BaseSettings):
    """Settings to establish a connection with a Redshift instance."""

    model_config = settings_config("redshift_")

    endpoint: str
    database: str
    port: int = 5439

    username: str
    password: str

    def uri(self) -> str:
        """Return the URI to connect to the Redshift instance."""
        return (
            f"redshift+psycopg2://{self.username}:{self.password}"
            f"@{self.endpoint}:{self.port}/{self.database}"
        )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """
        Validate the permissions scope of the username.
        """
        if value == "admin":
            logger.warning(
                "Mind the scope of the privileges!\n"
                "Using the 'admin' user is not recommended."
            )
        return value
