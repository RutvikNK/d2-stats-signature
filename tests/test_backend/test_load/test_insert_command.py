import unittest
from unittest.mock import MagicMock, patch

from backend.load.commands import InsertCommand
from backend.data.bng_data import PlayerData

class InsertCommandTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.db_conn = MagicMock()
        self.empty_command = InsertCommand(self.db_conn)

        self.cols = [
            {"col 1": 1, "col 2": "a"},
            {"col 1": 3, "col 2": "b"},
            {"col 1": 5, "col 2": "c"}
        ]
        self.table_name = "test_table"
        self.pre_set_command = InsertCommand(self.db_conn, self.table_name, self.cols)

    def test_insert_command_init_all_data(self):
        assert self.pre_set_command._InsertCommand__table_name == self.table_name
        assert self.pre_set_command._InsertCommand__obj == self.db_conn
        assert self.pre_set_command._InsertCommand__data == self.cols

    def test_insert_command_init_min_data(self):
        assert self.empty_command._InsertCommand__table_name == ""
        assert self.empty_command._InsertCommand__obj == self.db_conn
        assert self.empty_command._InsertCommand__data == [{}]

    @patch.object(PlayerData, "data", new={"col 1": 1, "col 2": "a"})
    def test_successful_insert_command_set(self):
        mock_bng_conn = MagicMock()
        data_to_set = PlayerData(mock_bng_conn, 1, 1)

        self.empty_command.set_command("table name", data_to_set)

        assert self.empty_command._InsertCommand__table_name == "table name"
        assert self.empty_command._InsertCommand__data == [self.cols[0]]

    def test_successful_insert_command_execute(self):
        self.pre_set_command.execute()

        query = 'INSERT INTO test_table(col 1, col 2) VALUES(1, "a"), (3, "b"), (5, "c")'
        self.db_conn.execute.assert_called_once_with(query)
    
    def test_successful_insert_command_execute_single_data(self):
        basic_insert_command = InsertCommand(self.db_conn, self.table_name, [{"col 1": 1, "col 2": "abc", "col 3": 2.33}])
        basic_insert_command.execute()

        query = 'INSERT INTO test_table(col 1, col 2, col 3) VALUES(1, "abc", 2.33)'
        self.db_conn.execute.assert_called_once_with(query)

    def test_insert_command_execute_no_data(self):
        self.empty_command.execute()

        query = "INSERT INTO) VALUE)"
        self.db_conn.execute.assert_called_once_with(query)
    
