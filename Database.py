# -*- coding: utf-8 -*-
# _____________________________________________________________________________
# _____________________________________________________________________________
#
#                       Coded by: Daniel Gonzalez-Duque
#                               Last revised 2022-10-11
# _____________________________________________________________________________
# _____________________________________________________________________________
"""
______________________________________________________________________________

 DESCRIPTION:
    This class creates and saves the information in the datbabase.

______________________________________________________________________________
"""
# ----------------
# Import packages
# ----------------
import pandas as pd
import psycopg2


# -----------------
# Class
# -----------------
class Database:
    """
    The trials table
    """

    def __init__(self, db):
        """
        Takes a db connection.
        """
        self.table_meander = "meander_database"
        self.db = db
        self.variables = ['id', 'id_reach', 'huc04_n', 'huc_n',
                          'start_comid', 'scale', 'x_st', 'y_st', 'translate',
                          'id_meander', 'ind_start', 'ind_end', 'x_start',
                          'x_end', 'y_start', 'y_end', 'lambda', 'l',
                          'sinuosity', 'dif_z', 'j_x', 'so']
        self.input = {'id': self.convert_string,
                      'id_reach': self.convert_string,
                      'huc04_n': self.convert_string,
                      'huc_n': self.convert_string,
                      'start_comid': self.convert_float,
                      'scale': self.convert_int,
                      'x_st': self.convert_float, 'y_st': self.convert_float,
                      'translate': self.convert_bool,
                      'id_meander': self.convert_int,
                      'ind_start': self.convert_int,
                      'ind_end': self.convert_int,
                      'x_start': self.convert_float,
                      'x_end': self.convert_float,
                      'y_start': self.convert_float,
                      'y_end': self.convert_float,
                      'lambda': self.convert_float, 'l': self.convert_float,
                      'sinuosity': self.convert_float,
                      'dif_z': self.convert_float,
                      'j_x': self.convert_float,
                      'so': self.convert_int,
                      }

    @staticmethod
    def convert_string(value):
        return f"'{value}'"

    @staticmethod
    def convert_int(value):
        return f"{int(value)}"

    @staticmethod
    def convert_float(value):
        return f"{float(value)}"

    @staticmethod
    def convert_bool(value):
        return f"'{value}'"

    def execute_query(self, query):
        c = self.db.cursor()
        c.execute(query)
        self.db.commit()

    def close(self):
        self.db.close()
        return

    def create_meander_table(self):
        query = f"CREATE TABLE IF NOT EXISTS {self.table_meander} ("
        query += "id_database SERIAL PRIMARY KEY,"
        query += "id VARCHAR(42),"
        query += "id_reach VARCHAR(36),"
        query += "huc04_n VARCHAR(6),"
        query += "huc_n INTEGER,"
        query += "start_comid FLOAT,"
        query += "scale FLOAT,"
        query += "x_st FLOAT,"
        query += "y_st FLOAT,"
        query += "translate BOOLEAN,"
        query += "id_meander INTEGER,"
        query += "ind_start BIGINT,"
        query += "ind_end BIGINT,"
        query += "x_start FLOAT,"
        query += "x_end FLOAT,"
        query += "y_start FLOAT,"
        query += "y_end FLOAT,"
        query += "lambda FLOAT,"
        query += "l FLOAT,"
        query += "sinuosity FLOAT,"
        query += "dif_z FLOAT,"
        query += "j_x FLOAT,"
        query += "so INTEGER"
        query += ")"
        try:
            self.execute_query(query)
        except psycopg2.errors.UniqueViolation:
            print("Table already exists?")
            pass

    def new_entry(self, data):
        for i in range(len(data)):
            values = [f"'{data.index[i]}'"] + [
                self.input[var](data.iloc[i, ivar])
                for ivar, var in enumerate(self.variables[1:])]
            query = f"INSERT INTO {self.table_meander} "
            query += f"({','.join(self.variables)}) "
            query += f"VALUES ({','.join(values)});"
            print(query)
            if query != '':
                self.execute_query(query)
        return

    def fetchall_meanders(self):
        cursor = self.db.cursor()
        query = f'SELECT * from {self.table_meander}'
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        records_pd = pd.DataFrame(
            records, columns=['id_database'] + self.variables)
        records_pd.drop(columns=['id_database'], inplace=True)
        records_pd.set_index('id', inplace=True)
        return records_pd

    def truncate_table_meander(self):
        query = f'TRUNCATE TABLE {self.table_meander}'
        self.execute_query(query)
        return

    def drop_table_meander(self):
        query = f'DROP TABLE {self.table_meander}'
        self.execute_query(query)
        return
