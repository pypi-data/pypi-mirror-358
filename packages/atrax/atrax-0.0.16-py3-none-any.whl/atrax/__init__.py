import io
import csv
from datetime import datetime
from typing import Union
import sqlite3
import psycopg2
from sqlalchemy import Engine, Connection, create_engine, text
# import pandas as pd
from .version import __version__


from .core.series import Series
from .core.dataset import DataSet
from .core.qcut import qcut
from .core.cut import cut
from .core.customdatetime import to_datetime, date_range

class Atrax:
    Series = Series
    DataSet = DataSet
    qcut = qcut
    cut = cut
    to_datetime = to_datetime
    date_range = date_range


    @staticmethod
    def read_csv(path_or_str, from_string=False, encoding='utf-8', converters=None, usecols=None, parse_dates=None):
        """Read a CSV file or string into a dataset.
        
        Parameters:
        -----------
            path_or_str: (str): Path to the CSV file or a CSV formatted string.
            from_string: (bool): If True, treats path_or_str as a string, otherwise as a file path.
            encoding: (str): Encoding to use when reading the file
            converters: (dict): Optional dict of colum: function
            usecols: (list): Optionaal list of columns to keep
            
        Returns:
        -----------
            DataSet: A DataSet object containing the data from the CSV.
        """
        if from_string:
            f = io.StringIO(path_or_str)
        else:
            f = open(path_or_str, newline='')

        reader = csv.DictReader(f)
        rows = []

        # attempt numeric conversion
        for row in reader:
            parsed_row = {}
            for k, v in row.items():
                if usecols and k not in usecols:
                    continue

                # Handle custom converter
                if converters and k in converters:
                    try:
                        parsed_row[k] = converters[k](v)
                        continue
                    except Exception:
                        parsed_row[k] = v
                        continue

                # Handle datetime parsing
                if parse_dates and k in parse_dates:
                    try:
                        parsed_row[k] = datetime.fromisoformat(v)
                        continue
                    except ValueError:
                        try:
                            parsed_row[k] = datetime.strptime(v, "%Y-%m-%d")
                        except:
                            parsed_row[k] = v
                        continue

                # Try numeric fallback
                try:
                    parsed_row[k] = float(v) if '.' in v else int(v)
                except:
                    parsed_row[k] = v

            rows.append(parsed_row)
                
        return DataSet(rows)
    
    @staticmethod
    def get_db(conn_str:str):
        """
        Get a database connection object from a connection string.

        Parameters:
            conn_str (str): Connection string for the database

        Returns:
            Database connection object
        """
        return create_engine(conn_str, echo=True)
    
    @staticmethod
    def read_sql(query: str, conn: Union[Engine, sqlite3.Connection, psycopg2.extensions.connection], index_col=None) -> "DataSet":
        """
        Execute SQL and convert result to Atrax DataSet, without using pandas.

        Parameters:
        -----------
        query : str
            SQL query to run.
        conn : SQLAlchemy engine/connection, sqlite3, or psycopg2 connection.
        index_col : str, optional
            Optional column to set as index.

        Returns:
        --------
        DataSet
        """
        try:
            # Handle SQLAlchemy connection
            if isinstance(conn, (Engine)):
                with conn.connect() as connection:
                    result = connection.execute(text(query))
                    columns = result.keys()
                    rows = result.fetchall()

            # Handle sqlite3 and psycopg2
            else:
                cursor = conn.cursor()
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

            # Convert rows into columns
            data = {col: [] for col in columns}
            for row in rows:
                for col, val in zip(columns, row):
                    data[col].append(val)

            # Set index if requested
            if index_col and index_col in data:
                index = data.pop(index_col)
                return DataSet(data, index=index_col, index_values=index)
            else:
                return DataSet(data)

        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {e}")
    