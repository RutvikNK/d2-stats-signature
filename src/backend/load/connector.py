from mysql import connector

class SQLConnector:
    """
    Utility class that creates a MySQL database connection. Allows for executing queries, as well as commits and rollbacks
    """
    def __init__(self, db_name: str, port: int) -> None:
        self.db = connector.connect(
            host="localhost",
            user="root",
            password="pass",
            database=db_name,
            port = port
        )

    def execute(self, query, params=None):
        cursor = self.db.cursor(buffered=True)

        if params == None:
            params = []

        try:
            cursor.execute(query, params)
            self.commit()
            print(f"Query executed successfully\n")
            
            try:
                result = cursor.fetchall()
                if result:
                    return result
            except Exception:
                pass
        except Exception as e:
            self.rollback()
            print(f"{e}")
            print(f"Query execution failed\n")

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def retrieve_all(self, table_name: str):
        """
        Debug function to view all tuples in a table
        """
        result = self.execute(f"SELECT * FROM {table_name}")

        if result:
            return result
def main():
    db = SQLConnector("test", 33061)
    sql = "SELECT * FROM Armor"

    result = db.execute(sql)
    
    if result:
        for x in result:
            print(x)
    
if __name__ == "__main__":
    main()