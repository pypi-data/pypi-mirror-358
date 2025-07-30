# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

from typing import TypedDict

import boto3
from botocore.exceptions import ClientError


class RedshiftCreds(TypedDict):
    username: str
    password: str


def get_redshift_creds(secret_name: str, region_name: str) -> RedshiftCreds:
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as exc:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise exc

    secret_string = get_secret_value_response["SecretString"]
    return secret_string.encode("utf-8").decode("unicode-escape")


if __name__ == "__main__":
    secret_name = "redshift!qoreai-datawarehouse-stage-admin"
    region_name = "us-east-1"
    print(get_redshift_creds(secret_name, region_name))
