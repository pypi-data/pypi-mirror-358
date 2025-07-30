# aws-ssm-env

Fetch environment configurations from **AWS SSM Parameter Store** as JSON.
Supports both AWS environments and local development via IAM role assumption.

## Installation

```bash
pip install aws-ssm-env
```

## Prerequisites

* The SSM parameter **must be of type `String`** (not `StringList` or `SecureString` unless you're decrypting).
* The value of the parameter **must be a valid JSON object string**. For example:

```json
{
  "DB_HOST": "localhost",
  "DB_USER": "admin",
  "DB_PASS": "secret"
}
```

## Usage

### 1. In AWS environment (e.g., EC2, Lambda)

If your code is running in an AWS environment with appropriate IAM permissions, you only need to provide the region and parameter name:

```python
from aws_ssm_env.ssm import get_env_parameters_from_ssm

env_config = get_env_parameters_from_ssm(
    account_id="",  # Optional
    region="us-west-2",
    role_name="",  # Optional
    parameter_name="/my/app/env"
)

print(env_config["DB_HOST"])
```

---

### 2. From local environment (with role assumption)

Use this method when working locally and you need to access parameters from another AWS account:

```python
from aws_ssm_env.ssm import get_env_parameters_from_ssm

env_config = get_env_parameters_from_ssm(
    account_id="123456789012",
    region="us-west-2",
    role_name="MyRole",
    parameter_name="/my/app/env"
)

print(env_config["DB_HOST"])
```

---

## License

MIT

