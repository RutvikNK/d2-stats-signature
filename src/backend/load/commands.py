from abc import ABC, abstractmethod

from backend.load.connector import SQLConnector
from backend.data.bng_data import BungieData

class Command(ABC):
    """
    Command interface
    """
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def set_command(self):
        pass

class InsertCommand(Command):
    """
    Insert command, handles adding rows to the given table. Allows for multiple rows to be added
    """
    def __init__(self, obj: SQLConnector, table_name: str="", data: list[dict]=[{}]) -> None:
        self.__obj = obj
        self.__data = data
        self.__table_name = table_name

    def execute(self):
        """
        Executes an insert query based on the class' attributes.
        """
        query = f"INSERT INTO {self.__table_name}("  # construct base query by populating the column names
        for k in self.__data[0].keys():
            query += f"{k}, "

        query = f"{query[:-2]}) VALUES"

        for value in self.__data:  # populate the query with all rows in the data list
            query += "("
            for attr in value.values():
                if isinstance(attr, float) or isinstance(attr, int):
                    query += f"{attr}, "
                else:
                    query += f'"{attr}", '
            else:
                query = f"{query[:-2]}), "
        else:
            query = f"{query[:-2]}"
        
        print(query)  # print to debug
        self.__obj.execute(query)  # execute

    def set_command(self, table_name: str, data: BungieData) -> None:
        """
        Allows setting the command attributes: table name and insertion data
        """
        # query details
        self.__table_name = table_name
        self.__data = [data.data]  # add empty dictionary for new row

class SelectCommand(Command):
    """
    Select command, handles retrieving specific columns or entire rows from the given table.
    """
    def __init__(self, obj: SQLConnector, table_name: str="", fields: list[str]=[]) -> None:
        self.__obj = obj
        self.__table_name = table_name
        self.__fields = fields
        self.__conditions = dict()
    
    def execute(self):
        """
        Executes the select query based on the given class' attributes
        """
        query = "SELECT "
        if self.__fields:
            for field in self.__fields:
                query += f"{field}, "
            else:
                query = f"{query[:-2]} FROM {self.__table_name}"
        else:
            query += f"* FROM {self.__table_name}"

        if self.__conditions:
            query += " WHERE "
            for k, v, in self.__conditions.items():
                if isinstance(v, int) or isinstance(v, float):
                    query += f"{k} = {v}"
                else:
                    query += f'{k} = "{v}"'
                query += " AND "
            query = query[:-5]  # remove last AND

        print(query)
        result = self.__obj.execute(query)
        return result

    def set_command(self, table_name: str, fields: list[str], condition: dict) -> None:
        """
        Allows setting the attributes for the select command
        """
        self.__table_name = table_name
        self.__fields = fields
        self.__conditions = condition

class DeleteCommand(Command):
    """
    Delete command, handles deleting specified rows from the given table.
    """
    def __init__(self, obj: SQLConnector, table_name: str="", data: dict={}) -> None:
        self.__obj = obj
        self.__table_name = table_name
        self.__data = data

    def execute(self):
        """
        Executes the delete command based on the class' attributes
        """
        query = "DELETE FROM " + self.__table_name + " WHERE "
        for key, value in self.__data.items():
            query += key + " = " + str(value) + " AND "
        query = query[:-5]
        print(query)
        return self.__obj.execute(query)

    def set_command(self):
        """
        Allows ssetting the attribtues of the delete command
        """
        self.__table_name = input("Enter the name of the table you want to delete from: ")

        condition = input("Enter the column and its value for the delete condition, separate by a semicolon (;). Include \"\" for any TEXT data types!: ")
        self.__data[condition.split(";")[0]] = condition.split(";")[1]
