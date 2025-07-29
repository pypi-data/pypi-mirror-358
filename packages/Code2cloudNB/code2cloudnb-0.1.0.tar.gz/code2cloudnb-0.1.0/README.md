# Code2cloudNB

A Python package providing helper functions to programmatically import Jupyter notebook content into Azure Databricks and Azure Synapse workspaces via REST APIs.

## Features

- Create folders and import Jupyter notebooks into Azure Databricks workspace.
- Import Jupyter notebooks into Azure Synapse Analytics workspace with support for Big Data Pools.
- Handles authentication using Personal Access Tokens (PAT) for Databricks and Azure AD `DefaultAzureCredential` for Synapse.
- Returns detailed responses for success and error scenarios.

## Installation

Install via PyPI once published:

```bash
pip install Code2cloudNB
```

# Usage

## Importing a notebook into Azure Databricks

```python
import base64
from Code2cloudNB import import_code_to_databricks

# Your Databricks workspace info
host = "https://<databricks-instance>"
token = "<your-databricks-pat>"
domain_name = "<your-domain-or-username>"
target_path = "target/folder/path"
filename = "my_notebook"

# Load your notebook JSON file content and encode to base64
with open("notebook.ipynb", "rb") as f:
    notebook_content = f.read()
encoded_string = base64.b64encode(notebook_content).decode()

response = import_code_to_databricks(host, token, domain_name, target_path, filename, encoded_string)

print(response)
```

## Importing a notebook into Azure Synapse Analytics

```python
from Code2cloudNB import import_code_to_synapse
import json

wName = "<your-synapse-workspace-name>"
target_path = "target_folder"
filename = "my_notebook"
pool_name = "<your-big-data-pool-name>"
api_version = "2021-06-01" # example API version

# Load notebook JSON content as Python dict
with open("notebook.ipynb", "r") as f:
    notebook_json = json.load(f)

response = import_code_to_synapse(wName, target_path, filename, pool_name, notebook_json, api_version)

print(response)
```

# Prerequisites

- For Databricks import:
    - A valid **Personal Access Token (PAT)** with workspace permissions.
    - Databricks workspace URL.

- For Synapse import:
    - Azure CLI or environment configured for Azure authentication.
    - Appropriate **Azure AD role assignments** for accessing Synapse workspace.
    - `azure-identity` Python package installed for `DefaultAzureCredential` support.

```bash
pip install azure-identity requests
```

# Error Handling

Both functions return dictionaries including HTTP status codes and error messages if any operation fails. Use these to troubleshoot or log issues.

# License

This project is licensed under the MIT License - see the [LICENSE] (LICENSE) file for details.

# Contributing

Feel free to open issues or submit pull requests to improve the package.

# Author

Antick Mazumder — antick.majumder@gmail.com