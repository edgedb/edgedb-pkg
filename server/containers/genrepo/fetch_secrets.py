#!/usr/bin/env python3
from __future__ import annotations
from typing import *

import functools
import os
import pathlib

import boto3
from botocore.exceptions import ClientError
import click


APP_PREFIX = "edbcloud/app/edgedbeng/pkg/"


def list_secret_ids_by_prefix(
    client: boto3.SecretsManagerClient, secret_id_prefix: str,
) -> Set[str]:
    paginator = client.get_paginator("list_secrets")
    secret_ids = set()

    try:
        for page in paginator.paginate(
            Filters=[
                {
                    "Key": "name",
                    "Values": [
                        f"{APP_PREFIX}{secret_id_prefix}"
                    ],
                },
            ],
        ):
            for secret in page["SecretList"]:
                secret_ids.add(secret["Name"])
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using
            # the provided KMS key.
            raise e
        elif code == "InternalServiceErrorException":
            # An error occurred on the server side.
            raise e
        elif code == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            raise e
        elif code == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current
            # state of the resource.
            raise e
        elif code == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            raise e
        else:
            # Other issues
            raise e
    else:
        return secret_ids


def get_secret_string(
    client: boto3.SecretsManagerClient, secret_id: str
) -> str:
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_id)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using
            # the provided KMS key.
            raise e
        elif code == "InternalServiceErrorException":
            # An error occurred on the server side.
            raise e
        elif code == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            raise e
        elif code == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current
            # state of the resource.
            raise e
        elif code == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            raise e
        else:
            # Other issues
            raise e
    else:
        if "SecretString" not in get_secret_value_response:
            raise ValueError(
                f"Secret {secret_id!r} does not contain a secret string."
            )

        return get_secret_value_response["SecretString"]


@click.command()
@click.argument("secret_id_prefix")
@click.argument("target_directory")
def main(secret_id_prefix: str, target_directory: str) -> None:
    region = os.environ.get("AWS_REGION", "us-east-2")
    session = boto3.session.Session(region_name=region)
    secretsmanager = session.client(service_name="secretsmanager")
    secret_ids = list_secret_ids_by_prefix(
        secretsmanager, secret_id_prefix=secret_id_prefix
    )
    if not secret_ids:
        raise click.ClickException(
            f"No secrets with the prefix {secret_id_prefix!r} can be found in"
            f" region {region!r}"
        )

    target_dir_path = pathlib.Path(target_directory)
    os.makedirs(target_directory, exist_ok=True)

    click.echo(
        f"{len(secret_ids)} secrets with prefix {secret_id_prefix!r} in region"
        f" {region!r} to copy from AWS SecretsManager to {target_directory}"
    )

    for secret_id in secret_ids:
        try:
            secret = get_secret_string(secretsmanager, secret_id)
        except ClientError as e:
            click.echo(f"Reading {secret_id} failed:", err=True)
            click.echo(str(e), err=True)
            continue

        if secret_id.startswith(APP_PREFIX):
            secret_id = secret_id[len(APP_PREFIX):]
        with open(target_dir_path / secret_id, "w") as target_file:
            target_file.write(secret)


if __name__ == "__main__":
    main()
