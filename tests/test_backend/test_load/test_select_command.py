import unittest
from unittest.mock import MagicMock

from backend.load.commands import SelectCommand

class SelectCommandTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.db_conn = MagicMock()
        self.empty_command = SelectCommand(self.db_conn)

        self.fields = ["col_1", "col_2", "col_3"]
        self.table_name = "test_table"
        self.pre_set_command = SelectCommand(self.db_conn, self.table_name, self.fields)

    def test_select_command_init_all_data(self):
        assert self.pre_set_command._SelectCommand__obj == self.db_conn
        assert self.pre_set_command._SelectCommand__table_name == self.table_name
        assert self.pre_set_command._SelectCommand__fields == self.fields
        assert self.pre_set_command._SelectCommand__conditions == {}

    def test_select_command_init_no_fields(self):
        partial_command = SelectCommand(self.db_conn, self.table_name)

        assert partial_command._SelectCommand__obj == self.db_conn
        assert partial_command._SelectCommand__table_name == self.table_name
        assert partial_command._SelectCommand__fields == []
        assert partial_command._SelectCommand__conditions == {}

    def test_select_commond_init_empty(self):
        assert self.empty_command._SelectCommand__obj == self.db_conn
        assert self.empty_command._SelectCommand__table_name == ""
        assert self.empty_command._SelectCommand__fields == []
        assert self.empty_command._SelectCommand__conditions == {}

    def test_select_command_successful_execute_no_conditions(self):
        mock_result = [1, 2, 3]
        self.db_conn.execute.return_value = mock_result
        actual_result = self.pre_set_command.execute()

        query = "SELECT col_1, col_2, col_3 FROM test_table"
        self.db_conn.execute.assert_called_once_with(query)
        assert actual_result == mock_result

    def test_select_command_unsuccessful_execute(self):
        self.db_conn.execute.side_effect = Exception
        with self.assertRaises(Exception):
            self.pre_set_command.execute()

        query = "SELECT col_1, col_2, col_3 FROM test_table"
        self.db_conn.execute.assert_called_once_with(query)

    def test_select_command_successful_set(self):
        table_name = "table_name"
        fields = ["col_1"]
        condition = {"col_2": 3}
        self.empty_command.set_command(table_name, fields, condition)

        assert self.empty_command._SelectCommand__obj == self.db_conn
        assert self.empty_command._SelectCommand__table_name == table_name
        assert self.empty_command._SelectCommand__fields == fields
        assert self.empty_command._SelectCommand__conditions == condition

    def test_select_command_successful_execute_with_conditions(self):
        table_name = "table_name"
        fields = ["col_1"]
        condition = {"col_2": 3}
        self.empty_command.set_command(table_name, fields, condition)

        mock_result = [1]
        self.db_conn.execute.return_value = mock_result
        actual_result = self.empty_command.execute()

        query = "SELECT col_1 FROM table_name WHERE col_2 = 3"
        self.db_conn.execute.assert_called_with(query)
        assert actual_result == mock_result

        table_name = "table_name"
        fields = ["col_3"]
        condition = {"col_1": "abc"}
        self.empty_command.set_command(table_name, fields, condition)

        mock_result = ["ret"]
        self.db_conn.execute.return_value = mock_result
        actual_result = self.empty_command.execute()

        query = 'SELECT col_3 FROM table_name WHERE col_1 = "abc"'
        self.db_conn.execute.assert_called_with(query)
        assert actual_result == mock_result

    def test_select_command_successful_execute_no_fields(self):
        simple_command = SelectCommand(self.db_conn, "table_name")
        
        mock_result = [
            [1, 2, "3"],
            [12, 222, "34"],
            [98, 22, "10"],
            [11, 80, "76"]
        ]
        self.db_conn.execute.return_value = mock_result
        result = simple_command.execute()

        query = "SELECT * FROM table_name"
        self.db_conn.execute.assert_called_once_with(query)
        assert result == mock_result
