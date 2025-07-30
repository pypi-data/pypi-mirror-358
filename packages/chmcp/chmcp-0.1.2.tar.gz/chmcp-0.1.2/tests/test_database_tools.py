"""Tests for ClickHouse database tools."""

import pytest
from unittest.mock import patch, Mock, MagicMock
from chmcp import (
    list_databases,
    list_tables,
    run_query,
    create_clickhouse_client,
)


class TestDatabaseTools:
    """Test suite for database operation tools."""

    @patch("chmcp.mcp_server.clickhouse_connect.get_client")
    def test_create_clickhouse_client_success(self, mock_get_client, clickhouse_config):
        """Test successful ClickHouse client creation."""
        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Call the function
        client = create_clickhouse_client()

        # Assertions
        mock_get_client.assert_called_once()
        assert client == mock_client

    def test_create_clickhouse_client_failure(self):
        """Test ClickHouse client creation with invalid config."""
        with patch("chmcp.mcp_env.get_config") as mock_config:
            mock_config.return_value.get_client_config.return_value = {
                "host": "invalid-host",
                "port": 9999,
                "username": "invalid",
                "password": "invalid",
                "secure": False,
                "verify": False,
                "connect_timeout": 1,
                "send_receive_timeout": 1,
                "client_name": "test",
            }

            with pytest.raises(Exception):
                create_clickhouse_client()

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_list_databases(self, clickhouse_client, test_database):
        """Test listing databases."""
        result = list_databases()

        assert isinstance(result, list)
        assert test_database in result
        assert "system" in result  # ClickHouse always has system database

    def test_list_databases_connection_error(self):
        """Test list_databases with connection error."""
        with patch("chmcp.mcp_server.create_clickhouse_client") as mock_client:
            mock_client.side_effect = Exception("Connection failed")

            with pytest.raises(Exception, match="Connection failed"):
                list_databases()

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_list_tables_basic(self, clickhouse_client, test_database, test_table):
        """Test basic table listing."""
        result = list_tables(test_database)

        assert isinstance(result, list)
        assert len(result) >= 1

        # Find our test table
        test_table_info = next((t for t in result if t["name"] == test_table), None)
        assert test_table_info is not None

        # Verify table structure
        assert test_table_info["database"] == test_database
        assert test_table_info["engine"] == "MergeTree"
        assert test_table_info["comment"] == "Test table for comprehensive unit testing"
        assert isinstance(test_table_info["columns"], list)
        assert len(test_table_info["columns"]) == 6

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_list_tables_with_like_filter(self, clickhouse_client, test_database, test_table):
        """Test table listing with LIKE filter."""
        result = list_tables(test_database, like=f"{test_table}%")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == test_table

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_list_tables_with_not_like_filter(self, clickhouse_client, test_database, test_table):
        """Test table listing with NOT LIKE filter."""
        result = list_tables(test_database, not_like="nonexistent%")

        assert isinstance(result, list)
        # Should include our test table since it doesn't match the NOT LIKE pattern
        table_names = [t["name"] for t in result]
        assert test_table in table_names

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_list_tables_column_details(self, clickhouse_client, test_database, test_table):
        """Test detailed column information in table listing."""
        result = list_tables(test_database)
        test_table_info = next((t for t in result if t["name"] == test_table), None)

        # Get columns by name for easier testing
        columns = {col["name"]: col for col in test_table_info["columns"]}

        # Verify column details
        assert "id" in columns
        assert columns["id"]["column_type"] == "UInt32"
        assert columns["id"]["comment"] == "Primary identifier"

        assert "name" in columns
        assert columns["name"]["column_type"] == "String"
        assert columns["name"]["comment"] == "User name field"

        assert "email" in columns
        assert columns["email"]["column_type"] == "String"

        assert "created_at" in columns
        assert columns["created_at"]["column_type"] == "DateTime"
        assert columns["created_at"]["default_kind"] == "DEFAULT"

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_list_tables_nonexistent_database(self, clickhouse_client):
        """Test listing tables for nonexistent database."""
        with pytest.raises(Exception):
            list_tables("nonexistent_database_12345")

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_run_query_success(self, clickhouse_client, test_database, test_table):
        """Test successful SELECT query execution."""
        query = f"SELECT id, name, email FROM {test_database}.{test_table} ORDER BY id"
        result = run_query(query)

        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "columns" in result
        assert "rows" in result

        # Verify columns
        expected_columns = ["id", "name", "email"]
        assert result["columns"] == expected_columns

        # Verify data
        assert len(result["rows"]) == 4
        assert result["rows"][0] == [1, "Alice Johnson", "alice@example.com"]
        assert result["rows"][1] == [2, "Bob Smith", "bob@example.com"]

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_run_query_with_filters(self, clickhouse_client, test_database, test_table):
        """Test SELECT query with WHERE clause."""
        query = f"SELECT name FROM {test_database}.{test_table} WHERE age > 30 ORDER BY name"
        result = run_query(query)

        assert result["status"] == "success"
        assert len(result["rows"]) == 2
        assert result["rows"][0][0] == "Bob Smith"
        assert result["rows"][1][0] == "Charlie Brown"

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_run_query_aggregation(self, clickhouse_client, test_database, test_table):
        """Test SELECT query with aggregation."""
        query = f"SELECT COUNT(*) as total, AVG(age) as avg_age FROM {test_database}.{test_table}"
        result = run_query(query)

        assert result["status"] == "success"
        assert len(result["rows"]) == 1
        assert result["rows"][0][0] == 4  # COUNT(*)
        assert result["rows"][0][1] == 33.75  # AVG(age)

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_run_query_syntax_error(self, clickhouse_client):
        """Test SELECT query with syntax error."""
        query = "SELECT * FROMM invalid_syntax"
        result = run_query(query)

        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "message" in result
        assert len(result["message"]) > 0

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_run_query_nonexistent_table(self, clickhouse_client, test_database):
        """Test SELECT query on nonexistent table."""
        query = f"SELECT * FROM {test_database}.nonexistent_table"
        result = run_query(query)

        assert result["status"] == "error"
        assert "message" in result

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_run_query_timeout(self, clickhouse_client):
        """Test SELECT query timeout handling."""
        # This test simulates a long-running query
        # In a real scenario, you'd use a query that takes longer than the timeout
        with patch("chmcp.mcp_server.SELECT_QUERY_TIMEOUT_SECS", 0.1):
            with patch("chmcp.mcp_server.execute_query") as mock_execute:
                import time

                def slow_query(query):
                    time.sleep(0.2)  # Simulate slow query
                    return {"status": "success", "columns": [], "rows": []}

                mock_execute.side_effect = slow_query

                result = run_query("SELECT sleep(1)")
                assert result["status"] == "error"
                assert "timed out" in result["message"]

    @pytest.mark.skip(reason="Requires live ClickHouse connection")
    def test_readonly_query_enforcement(self, clickhouse_client, test_database):
        """Test that only SELECT queries are allowed (readonly enforcement)."""
        # INSERT should fail due to readonly setting
        insert_query = f"INSERT INTO {test_database}.test_table VALUES (999, 'Hacker')"
        result = run_query(insert_query)

        assert result["status"] == "error"
        # Should contain message about readonly or permissions

    @pytest.mark.parametrize(
        "invalid_query",
        [
            "",  # Empty query
            "   ",  # Whitespace only
            "SELECT",  # Incomplete query
            "SELECT * FROM",  # Incomplete query
        ],
    )
    def test_run_query_invalid_input(self, invalid_query):
        """Test SELECT query with various invalid inputs."""
        result = run_query(invalid_query)
        assert result["status"] == "error"
