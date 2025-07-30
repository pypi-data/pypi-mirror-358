# pyw-secret 🔑
[![PyPI](https://img.shields.io/pypi/v/pyw-secret.svg)](https://pypi.org/project/pyw-secret/)
[![CI](https://github.com/pythonWoods/pyw-secret/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-secret/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Back-end unificato per vari secret-store:

* `.env` locale (dotenv)
* AWS SSM Parameter Store
* HashiCorp Vault

```bash
pip install pyw-secret            # dotenv incluso
pip install pyw-secret[aws]       # + boto3
pip install pyw-secret[vault]     # + hvac
```

```python
from pyw.secret import SecretStore
store = SecretStore.from_uri("ssm://eu-west-1/")
db_pass = store.get("prod/db/password")
```


## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-secret/latest/

Issue tracker → https://github.com/pythonWoods/pyw-secret/issues

Changelog → https://github.com/pythonWoods/pyw-secret/releases

© pythonWoods — MIT License