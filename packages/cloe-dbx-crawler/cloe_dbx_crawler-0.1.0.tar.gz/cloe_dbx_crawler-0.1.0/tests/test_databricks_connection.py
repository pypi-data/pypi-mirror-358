import pytest
from cloe_dbx_connector import databricks_connection


def test_env_variable_loading(monkeypatch) -> None:
    """Ensure that credentials are correctly loaded from the environment and passed to WorkspaceClient"""
    monkeypatch.setenv("CLOE_DBX_HOST", "https://adb-1234567890123456.9.azuredatabricks.net")
    monkeypatch.setenv("CLOE_DBX_TOKEN", "test_token")
    monkeypatch.setenv("CLOE_DBX_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("CLOE_DBX_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("CLOE_DBX_TENANT_ID", "test_tenant_id")

    connector = databricks_connection.DatabricksConnector.from_env()
    assert connector.host == "https://adb-1234567890123456.9.azuredatabricks.net", f"{connector.host}"
    assert connector.token == "test_token"
    assert connector.client_id == "test_client_id"
    assert connector.client_secret == "test_client_secret"
    assert connector.tenant_id == "test_tenant_id"


def test_missing_credentials_host(monkeypatch):
    monkeypatch.setenv("CLOE_DBX_HOST", "https://adb-1234567890123456.9.azuredatabricks.net")
    monkeypatch.setenv("CLOE_DBX_TOKEN", "test_token")
    monkeypatch.setenv("CLOE_DBX_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("CLOE_DBX_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("CLOE_DBX_TENANT_ID", "test_tenant_id")

    monkeypatch.delenv("CLOE_DBX_HOST", raising=False)

    with pytest.raises(ValueError, match="Authentication credentials missing: Please provide a host.*"):
        databricks_connection.DatabricksConnector.from_env()


def test_missing_credentials_token_and_client_secret(monkeypatch):
    monkeypatch.setenv("CLOE_DBX_HOST", "https://adb-1234567890123456.9.azuredatabricks.net")
    monkeypatch.setenv("CLOE_DBX_TOKEN", "test_token")
    monkeypatch.setenv("CLOE_DBX_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("CLOE_DBX_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("CLOE_DBX_TENANT_ID", "test_tenant_id")

    monkeypatch.delenv("CLOE_DBX_TOKEN", raising=False)
    monkeypatch.delenv("CLOE_DBX_CLIENT_SECRET", raising=False)

    with pytest.raises(
        ValueError,
        match="Authentication credentials missing: Please provide either a token or service principal details.*",
    ):
        databricks_connection.DatabricksConnector.from_env()
