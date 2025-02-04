import unittest
from unittest.mock import patch

from backend.load.connector import SQLConnector

class SQLConnectorTestCase(unittest.TestCase):
    @patch("backend.load.connector.connector")
    def test_successful_db_connector_execute_fetchall(self, mock_connector):
        db_conn = SQLConnector("test DB", 1111)

        mock_fetchall = ["col 1", "col 2", "col 3"]
        mock_connector.connect.return_value.cursor.return_value.fetchall.return_value = mock_fetchall
        actual_result = db_conn.execute("query")

        mock_connector.connect.return_value.cursor.return_value.execute.assert_called_once_with("query", [])
        assert actual_result == mock_fetchall

    @patch("backend.load.connector.connector")
    def test_successful_db_connector_execute_no_fetchall(self, mock_connector):
        db_conn = SQLConnector("test DB", 1111)
        mock_connector.connect.return_value.cursor.return_value.fetchall.return_value = None

        actual_result = db_conn.execute("query")

        mock_connector.connect.return_value.cursor.return_value.execute.assert_called_once_with("query", [])
        assert actual_result is None

    @patch("backend.load.connector.connector")
    def test_unsuccessful_db_connector_execute(self, mock_connector):
        mock_connector.connect.return_value = None
        db_conn = SQLConnector("test DB", 1111)

        assert db_conn.db is None

        with self.assertRaises(AttributeError):
            db_conn.execute("query")

    @patch("backend.load.connector.connector")
    def test_successful_db_connector_commit(self, mock_connector):
        db_conn = SQLConnector("test DB", 1111)

        db_conn.commit()
        mock_connector.connect.return_value.commit.assert_called_once()

    @patch("backend.load.connector.connector")
    def test_successful_db_connector_rollback(self, mock_connector):
        db_conn = SQLConnector("test DB", 1111)

        db_conn.rollback()
        mock_connector.connect.return_value.rollback.assert_called_once()

    @patch("backend.load.connector.connector")
    def test_successful_db_connector_retrieve_all(self, mock_connector):
        db_conn = SQLConnector("test DB", 1111)

        mock_fetchall = ["col 1", "col 2", "col 3"]
        mock_connector.connect.return_value.cursor.return_value.fetchall.return_value = mock_fetchall

        result = db_conn.retrieve_all("table name")

        mock_connector.connect.return_value.cursor.return_value.execute.assert_called_once_with("SELECT * FROM table name", [])
        assert result == mock_fetchall


    @patch("backend.load.connector.connector")
    def test_unsuccessful_db_connector_retrieve_all(self, mock_connector):
        db_conn = SQLConnector("test DB", 1111)

        mock_connector.connect.return_value.cursor.return_value.fetchall.return_value = None

        result = db_conn.retrieve_all("table name")

        mock_connector.connect.return_value.cursor.return_value.execute.assert_called_once_with("SELECT * FROM table name", [])
        assert result is None
    
    @patch("backend.load.connector.connector")
    def test_unsuccessful_db_connector_execute_cursor_error(self, mock_connector):
        db_conn = SQLConnector("test DB", 1111)
        mock_connector.connect.return_value.cursor.return_value.fetchall.side_effect = Exception()
        
        db_conn.execute("Query")
        mock_connector.connect.return_value.rollback.assert_called_once()
        