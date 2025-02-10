import unittest
from unittest.mock import MagicMock, patch

from backend.load.executor import DatabaseExecutor
from backend.load.commands import InsertCommand, SelectCommand
from backend.data.bng_data import PlayerData

class DBExecutorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.db_conn = MagicMock()

        self.db_exec = DatabaseExecutor(self.db_conn)

    def test_db_executor_init(self):
        assert self.db_exec._DatabaseExecutor__db == self.db_conn
        assert isinstance(self.db_exec._DatabaseExecutor__insert_command, InsertCommand)
        assert isinstance(self.db_exec._DatabaseExecutor__select_command, SelectCommand)

    @patch.object(PlayerData, "data", new={"col 1": 1, "col 2": "a"})
    def test_db_executor_successful_insert_row(self):
        mock_bng_conn = MagicMock()
        data_to_insert = PlayerData(mock_bng_conn, 1, 1)

        self.db_conn.execute.return_value = None
        result = self.db_exec.insert_row("table_name", data_to_insert)

        query = 'INSERT INTO table_name(col 1, col 2) VALUES(1, "a")'
        self.db_conn.execute.assert_called_with(query)
        assert result is None

    @patch.object(PlayerData, "data", new={"col 1": 1, "col 2": "a"})
    def test_db_executor_unsuccessful_insert_row(self):
        mock_bng_conn = MagicMock()
        data_to_insert = PlayerData(mock_bng_conn, 1, 1)

        self.db_conn.execute.side_effect = Exception
        with self.assertRaises(Exception):
            self.db_exec.insert_row("table_name", data_to_insert)

    def test_db_executor_successful_select_row(self):
        table_name = "table_name"
        fields = ["col_1", "col_2"]
        condition = {}
        
        mock_result = ["abc", 10]
        self.db_conn.execute.return_value = mock_result
        result = self.db_exec.select_rows(table_name, fields, condition)

        query = "SELECT col_1, col_2 FROM table_name"
        self.db_conn.execute.assert_called_with(query)
        assert result == mock_result

    def test_db_executor_successful_select_row_empty_set(self):
        table_name = "table_name"
        fields = ["col_1", "col_2"]
        condition = {}
        
        mock_result = []
        self.db_conn.execute.return_value = mock_result
        result = self.db_exec.select_rows(table_name, fields, condition)

        query = "SELECT col_1, col_2 FROM table_name"
        self.db_conn.execute.assert_called_with(query)
        assert result == mock_result

    def test_db_executor_unsuccessful_select_row(self):
        table_name = "table_name"
        fields = ["col_1", "col_2"]
        condition = {}
        
        self.db_conn.execute.side_effect = Exception
        with self.assertRaises(Exception):
            self.db_exec.select_rows(table_name, fields, condition)

        query = "SELECT col_1, col_2 FROM table_name"
        self.db_conn.execute.assert_called_with(query)

    def test_db_executor_successful_retrieve_all(self):
        mock_result = [
            [1, 2, 3],
            [10, 20, 30],
            [100, 200, 300]
        ]
        self.db_conn.retrieve_all.return_value = mock_result
        result = self.db_exec.retrieve_all("table_name")
        
        self.db_conn.retrieve_all.assert_called_with("table_name")
        assert result == mock_result
        
    def test_db_executor_unsuccessful_retrieve_all(self):
        self.db_conn.retrieve_all.side_effect = Exception
        with self.assertRaises(Exception):
            self.db_exec.retrieve_all("table_name")
        
        self.db_conn.retrieve_all.assert_called_with("table_name")
        