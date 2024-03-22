"""Database module to interact with SQLite database.
"""

import sqlite3
import pickle
import matplotlib.pyplot as plt


class Database:
    """
    Represents a SQLite database.

    This class provides methods to interact with the database, such as creating tables,
    inserting data, retrieving data, and deleting data.

    Attributes:
        con (sqlite3.Connection): The connection to the SQLite database.
        cur (sqlite3.Cursor): The cursor object for executing SQL statements.
    """

    def __init__(self, data_base):
        """
        Initializes a Database object.

        Args:
            data_base (str): The name of the database.
        """
        self.con = sqlite3.connect(f'{data_base}.db')
        self.cur = self.con.cursor()
        self.create_table()

    def __del__(self):
        """
        Closes the database connection when the object is destroyed.

        This method is automatically called when the object is garbage collected.
        It ensures that the database connection is properly closed to avoid resource leaks.

        Note:
        - It is generally recommended to explicitly close the database connection 
            using the `close()` method
            instead of relying solely on the `__del__` method.
        - The `__del__` method is not guaranteed to be called in all cases, 
            so it should not be relied upon
            as the sole means of closing resources.
        """
        self.con.close()

    def create_table(self):
        """
        Creates a table named 'measurements' if it doesn't already exist in the database.

        The table has the following columns:
        - id: INTEGER (Primary Key)
        - chip_id TEXT,
        - measurement_type: TEXT
        - measurement_parameter1 TEXT
        - measurement_parameter2 TEXT,
        - measurement_data: TEXT
        - measurement_result: TEXT
        - time_stamp: TIMESTAMP (Default: CURRENT_TIMESTAMP)
        """
        self.cur.execute('''CREATE TABLE IF NOT EXISTS measurements
             (id INTEGER PRIMARY KEY,
             chip_id TEXT,
             measurement_type TEXT,
             measurement_parameter1 TEXT,
             measurement_parameter2 TEXT,
             measurement_data TEXT,
             measurement_result TEXT,
             time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    def insert(self, chip_id, measurement_type, measurements_data, measurement_result, measurement_parameter1="", measurement_parameter2=""):
        """
        Inserts a new measurement into the database.

        Args:
            chip_id (str): The ID of the chip.
            measurement_type (str): The type of measurement.
            measurement_parameter1 (str): The first parameter of the measurement.
            measurement_parameter2 (str): The second parameter of the measurement.
            measurements_data (object): The data associated with the measurement.
            measurement_result (float): The result of the measurement.

        Returns:
            None
        """
        self.cur.execute("INSERT INTO measurements (chip_id, measurement_type, measurement_data," +
                         " measurement_result, measurement_parameter1, measurement_parameter2) VALUES (?, ?, ?, ?, ?, ?)",
                         (chip_id, measurement_type, pickle.dumps(measurements_data), measurement_result, measurement_parameter1, measurement_parameter2))
        self.con.commit()

    def read(self):
        """
        Retrieves all the measurements from the database.

        Returns:
            A list of tuples representing the measurements.
        """
        self.cur.execute("SELECT * FROM measurements")
        return self.cur.fetchall()

    def print_table(self):
        """
        Prints the contents of the 'measurements' table in a formatted manner.

        This method executes a SELECT query to fetch all the rows from the 'measurements' table.
        It then calculates the maximum length of each column and formats the table accordingly.
        The column length for the third column is adjusted based on the length of the values.

        Args:
            None

        Returns:
            None
        """
        self.cur.execute("SELECT * FROM measurements")
        columns_name = [description[0] for description in self.cur.description]
        data_fetched = self.cur.fetchall()
        column_lengths = [len(column) for column in columns_name]
        for row in data_fetched:
            for i, value in enumerate(row):
                if i == 5:
                    if len(value) > 10:
                        column_lengths[i] = max(column_lengths[i], len("Data true"))
                    else:
                        column_lengths[i] = max(column_lengths[i], len("Data false"))
                else:
                    column_lengths[i] = max(column_lengths[i], len(str(value)))
        separator = "+--" + "+--".join(["-" * length for length in column_lengths]) + "+"
        print(separator)
        print("| " + " | ".join([column.ljust(column_lengths[i]) for i, column in
                                 enumerate(columns_name)]) + ' |')
        print(separator)
        for row in data_fetched:
            row_values = []
            for i, value in enumerate(row):
                formated_value = str(value).ljust(column_lengths[i])
                if i == 5:
                    if len(value) > 10:
                        formated_value = "Data true".ljust(column_lengths[i])
                    else:
                        formated_value = "Data false".ljust(column_lengths[i])
                row_values.append(formated_value)
            formated_row = "| " + " | ".join(row_values) + " |"
            print(formated_row)
        print(separator)

    def delete_entries(self, id_values, table_name="measurements", column_name="id"):
        """
        Delete entries from the specified table based on the given ID values.

        Args:
            id_values (list): A list of ID values to be deleted.
            table_name (str, optional): The name of the table to delete entries from.
                Defaults to "measurements".
            column_name (str, optional): The name of the column to match the ID values.
                Defaults to "id".
        """
        for id_value in id_values:
            self.cur.execute(f"DELETE FROM {table_name} WHERE {column_name}={id_value}")
        self.con.commit()

    def delete_measurement_before(self, timestamp_cutoff, table_name="measurements"):
        """
        Delete measurements from the specified table before the given timestamp cutoff.

        Args:
            timestamp_cutoff (str): The timestamp cutoff in the format 'YYYY-MM-DD HH:MM:SS'.
            table_name (str, optional): The name of the table to delete measurements from.
                Defaults to "measurements".
        """
        self.cur.execute(f"DELETE FROM {table_name} WHERE time_stamp < '{timestamp_cutoff}'")
        self.con.commit()

    def delete_oldest_measurements(self, measurement, column_name="measurement_type",
                                   table_name="measurements"):
        """
        Delete the oldest measurement of a specific type from the database.

        Args:
            measurement (str): The type of measurement to delete.
            column_name (str, optional): The name of the column to filter on.
                Defaults to "measurement_type".
            table_name (str, optional): The name of the table to delete from.
                Defaults to "measurements".
        """
        self.cur.execute(f"DELETE FROM {table_name} WHERE id = (SELECT id FROM {table_name}" +
                         f" WHERE {column_name} ='{measurement}' ORDER BY time_stamp LIMIT 1)")
        self.con.commit()

    def select_by_id(self, id_to_select, table_name="measurements"):
        """
        Retrieves a row from the specified table based on the given ID.

        Args:
            id_to_select (int): The ID of the row to retrieve.
            table_name (str, optional): The name of the table to select from.
                Defaults to "measurements".

        Returns:
            tuple: The row retrieved from the table.
        """
        self.cur.execute(f"SELECT * FROM {table_name} WHERE id={id_to_select}")
        row = self.cur.fetchone()
        return row

    def select_field_by_id(self, id_to_select, field_name="measurement_data",
                           table_name="measurements"):
        """
        Retrieves the value of a specific field from a row in the database table
        based on the given ID.

        Args:
            id_to_select (int): The ID of the row to select.
            field_name (str, optional): The name of the field to retrieve.
                Defaults to "measurement_data".
            table_name (str, optional): The name of the table to query.
                Defaults to "measurements".

        Returns:
            The value of the specified field in the selected row, or None if
            the row does not exist.
        """
        self.cur.execute(f"SELECT {field_name} FROM {table_name} WHERE id  = ?", (id_to_select,))
        row = self.cur.fetchone()
        return row[0] if row is not None else None
    def plot_last_n_entries(self, n=9):
        """
        Plots the efficiency.

        Args:
            n (int): The number of entries to plot.

        Returns:
            None
        """
        # Query the last n entries from the database
        # self.cur.execute("SELECT * FROM measurements ORDER BY time_stamp DESC LIMIT ?", (n,))
        # rows = self.cur.fetchall()
        measurement_type = "normal startup"
        self.cur.execute("SELECT * FROM measurements WHERE measurement_type = ? ORDER BY time_stamp DESC LIMIT ?", (measurement_type, n))
        rows = self.cur.fetchall()

        # Unpack the pickled data and create a plot
        for row in rows:
            index, chip_id, measurement_type, measurement_parameter1, measurement_parameter2, measurement_data, measurement_result, _ = row
            measurement_data = pickle.loads(measurement_data)
            if hasattr(measurement_data, 'efficiency'):
                plt.scatter(measurement_data.out_current, measurement_data.efficiency, label=measurement_data.title)
            else:
                print("Efficiency does not exist in measurement_data")
        plt.legend()
        plt.grid()
        plt.xlabel("Output Current (A)")
        plt.ylabel("Efficiency (%)")
        plt.title(f"Efficiency vs Output Current for {chip_id}")
        plt.tight_layout()
        plt.show()
if __name__ == "__main__":
    database = Database("measurements")
    database.print_table()
    database.plot_last_n_entries(9)
    # db=Database("test")
    # db.print_table()
    # db.insert("test", [1,2,3,4,5], "Failed")
    # db.print_table()
    # data= pickle.loads(db.select_field_by_id(1))
    # print(data)
    # # db.delete_entries([1])
    # db.delete_oldest_measurements("test")
