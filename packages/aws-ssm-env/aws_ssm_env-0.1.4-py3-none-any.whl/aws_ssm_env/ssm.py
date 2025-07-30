# aws_ssm_env/ssm.py

import boto3
import json
from typing import Dict
from botocore.exceptions import ClientError

def get_env_parameters_from_ssm(
    account_id: str,
    region: str,
    role_name: str,
    parameter_name: str,
    with_decryption: bool = True
) -> "json":
    """
    Fetch parameters from AWS SSM Parameter Store, optionally assuming an IAM role.

    This function retrieves a parameter from AWS SSM Parameter Store, optionally
    assuming a specified IAM role in the given AWS account. The parameter is expected
    to be a JSON string representing a dictionary of environment variables.

    Args:
        account_id (str): AWS Account ID where the parameter is stored. (optinal if using default credentials)
        region (str): AWS region where the parameter is stored.
        role_name (str): IAM role name to assume in the target account. If empty, uses default credentials.
        parameter_name (str): Name of the SSM parameter to fetch.
        with_decryption (bool): Whether to decrypt SecureString parameters (default: True).

    Returns:
        json: The parsed JSON object stored in the SSM parameter.

    Raises:
        Exception: If the parameter cannot be fetched or parsed as JSON.

    Example:
        >>> get_env_parameters_from_ssm(
        ...     account_id="123456789012",
        ...     region="us-west-2",
        ...     role_name="MyRole",
        ...     parameter_name="/my/app/env",
        ... )
        {'DB_HOST': 'localhost', 'DB_USER': 'admin', ...}
    """

    def create_ssm_client() -> boto3.client:
        """
        Creates an SSM client using either default credentials or by assuming the specified IAM role.

        Returns:
            boto3.client: An SSM client object.
        """
        if role_name:
            # Assume the specified IAM role in the target AWS account
            sts_client = boto3.client("sts")
            response = sts_client.assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/{role_name}",
                RoleSessionName="SSMParameterSession"
            )
            creds = response["Credentials"]
            # Use temporary credentials from the assumed role to create the SSM client
            return boto3.client(
                "ssm",
                region_name=region,
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
            )
        else:
            # Use default credentials (e.g., from environment or EC2 instance profile)
            return boto3.client("ssm", region_name=region)

    # Create the SSM client (with or without assumed role)
    ssm_client = create_ssm_client()

    # Fetch the parameter value from SSM
    response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=with_decryption)

    try:
        value = response["Parameter"]["Value"]

        # The parameter value is expected to be a JSON string representing a dict
        return json.loads(value)

    except json.JSONDecodeError as je:
        # Raised if the parameter value is not valid JSON
        raise Exception(f"Failed to parse parameter '{parameter_name}' as JSON: {je}")
    except ClientError as ce:
        # Raised if there is an error fetching the parameter from SSM
        raise Exception(f"Error fetching parameter '{parameter_name}': {ce}")

