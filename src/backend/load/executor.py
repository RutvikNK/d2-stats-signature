from backend.load.connector import SQLConnector
from backend.load.commands import InsertCommand, SelectCommand
from backend.data.bng_data import BungieData

class DatabaseExecutor:
    """
    Handles executing basic queries on the D2 stats database. 
    """
    def __init__(self, db: SQLConnector) -> None:
        self.__db = db
        self.__insert_command: InsertCommand = InsertCommand(db)
        self.__select_command: SelectCommand = SelectCommand(db)

    def insert_row(self, table_name: str, data: BungieData):
        """
        Insert row(s) into a table
        """
        self.__insert_command.set_command(table_name, data)
        self.__insert_command.execute()

    def select_rows(self, table_name: str, fields: list[str], condition: dict):
        """
        Retrieve rows or sepcfifc columns of a row from a table
        """
        self.__select_command.set_command(table_name, fields, condition)
        return self.__select_command.execute()

    def update_row(self, table_name: str, data: dict, conditions: dict):
        """
        Update a row in a table
        """
        query = "UPDATE " + table_name + " SET "
        for key, value in data.items():
            if isinstance(value, str):
                query += key + " = '" + value + "', "
            else:
                query += key + " = " + str(value) + ", "
        
        query = query[:-2] + " WHERE "
        for key, value in conditions.items():
            query += key + " = " + str(value) + " AND "
        query = query[:-5]

        return self.__db.execute(query)

    def delete_row(self, table_name: str, conditions: dict):
        """
        Delete a row from a table
        """
        query = "DELETE FROM " + table_name + " WHERE "
        for key, value in conditions.items():
            query += key + " = " + str(value) + " AND "
        query = query[:-5]
        
        return self.__db.execute(query)

    def retrieve_all(self, table_name: str):
        return self.__db.retrieve_all(table_name)
    
# def main():
#     conn = SQLConnector("test", 33061)
#     executor = DatabaseExecutor(conn)

#     result = executor.select_rows("`Weapon`", ["weapon_id"], {"bng_weapon_id": 1916287826})
#     print(result)

# if __name__ == "__main__":
#     main()
