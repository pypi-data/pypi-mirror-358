import requests
from azure.identity import DefaultAzureCredential


def import_code_to_databricks(host, token, domain_name, target_path, filename, encoded_string):
    """
    Helper function to import jupyter notebook json content into Azure Databricks as a Notebook.
    Args:
        host: Databricks host URL.
        token: Databricks PAT (Personal Access Token).
        domain_name: your Databricks workspace name.
        target_path: Path in the workspace where the Notebook will be created.
        filename: Name of the Notebook you want.
        encoded_string: base64 encoded Jupyter notebook JSON content.
    """
    # First checking if the folder path exists, if so then skip, if not then create it.
    resp_1 = requests.post(
        f"{host}/api/2.0/workspace/mkdirs",
        headers={"Authorization": f"Bearer {token}"},
        json={"path": f"/Users/{domain_name}/{target_path}"}
    )

    if resp_1.status_code == 200:
        payload = {
            "path": f"/Users/{domain_name}/{target_path}/{filename}_notebook",
            "format": "JUPYTER",
            "language": "PYTHON",
            "content": encoded_string,
            "overwrite": True
        }

        resp_2 = requests.post(
            f"{host}/api/2.0/workspace/import",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        try:
            resp_2.raise_for_status()
            return {
                "status": resp_2.status_code,
                "message": resp_2.text,
                "location": f"/Users/{domain_name}/{target_path}/{filename}_notebook"
            }
        except requests.HTTPError as e:
            return {
                "error": e.errno,
                "message": f"Error in importing the notebook: {str(e)}-{resp_2.text}"
            }
    else:
        return{
            "error": resp_1.status_code,
            "message": resp_1.text
        }
    
def import_code_to_synapse(wName, target_path, filename, pool_name, notebook_json, api_version):
    """
    Helper function to import jupyter notebook json content as a Notebook into Azure Synapse Workspaces.
    Args:
        wName: Synapse Workspace name.
        target_path: Path in the workspace where the Notebook will be created.
        filename: Name of the Notebook you want.
        pool_name: Your Big Data pool name (Apache Spark Pool).
        notebook_json: Jupyter notebook JSON content.
        api_version: Synapse REST API Version.
    """
    creds = DefaultAzureCredential()
    token = creds.get_token("https://dev.azuresynapse.net/.default")

    notebook_name = f"{filename}_notebook"
    endpoint = f"https://{wName}.dev.azuresynapse.net"
    url = f"{endpoint}/notebooks/{notebook_name}?api-version={api_version}"

    props = {
        "nbformat": notebook_json["nbformat"],
        "nbformat_minor": notebook_json["nbformat_minor"],
        "cells": notebook_json["cells"],
        "metadata": notebook_json["metadata"],
        "bigDataPool": {
            "referenceName": pool_name,
            "type": "BigDataPoolReference"
        }
    }

    if target_path:
        props["folder"] = {"name": target_path}

    body = {
        "name": notebook_name,
        "properties": props
    }

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    resp = requests.put(url, headers=headers, json=body)
    
    try:
        resp.raise_for_status()
        return {
            "status": resp.status_code,
            "message": f"Imported notebook {notebook_name} successfully !",
            "location": f"/{target_path}/{notebook_name}" if target_path else f"/{notebook_name}",
            "id": resp.json()["recordId"]
        }
    except requests.HTTPError as e:
        return {
            "error": f"{resp.status_code}: {str(e)}",
            "message": f"Error in importing the notebook : {resp.text}"
        }