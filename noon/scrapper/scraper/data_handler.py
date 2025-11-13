import sqlite3
from datetime import datetime
import pandas as pd
from custom_logger import Logger

class DataHandler:
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.table_name = table_name
        self.logger = Logger()
        self.connection = None
        self.cursor = None
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            self.create_table_if_not_exists()
        except sqlite3.Error as e:
            self.logger.log_error(f"Error connecting to the database: {e}")
            raise

    def create_table_if_not_exists(self):
        try:
            check_table_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';"
            self.cursor.execute(check_table_query)
            table_exists = self.cursor.fetchone()

            if not table_exists:
                columns = [
                    'id INTEGER PRIMARY KEY',
                    'order_number TEXT',
                    'order_unique_id TEXT UNIQUE',
                    'order_datetime TEXT',
                    'order_outlet TEXT',
                    'outlet_location TEXT',
                    'customer_name TEXT',
                    'mobile_number TEXT',
                    'delivery_address TEXT',
                    'items TEXT',
                    'order_total REAL',
                    'order_sub_total REAL',
                    'order_discount_outlet REAL',
                    'internal_commission REAL',
                    'final_earning REAL',
                    'da_name TEXT',
                    'da_mobile TEXT',
                    'orderStatusCode TEXT',
                    'inserted_on TEXT',
                    'updated_on TEXT'
                ]

                create_table_query = f'''
                    CREATE TABLE {self.table_name} (
                        {', '.join(columns)}
                    );
                '''

                self.cursor.execute(create_table_query)
                self.connection.commit()
        except sqlite3.Error as e:
            self.logger.log_error(f"Error creating table: {e}")
            raise

    def insert_data(self, values):
        try:
            #print(values)
            insert_query = f'''
                INSERT INTO {self.table_name} (
                    order_number, order_unique_id, order_datetime, order_outlet, outlet_location,
                    customer_name, mobile_number, delivery_address, items,
                    order_total, order_sub_total, order_discount_outlet, internal_commission, final_earning, da_name, da_mobile, orderStatusCode,
                    inserted_on, updated_on
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?);
            '''

            self.cursor.execute(insert_query, values)
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.log_error(f"Error inserting data: {e}")
            raise

    def update_data(self, order_unique_id, column_name, new_value):
        try:
            update_query = f'''
                UPDATE {self.table_name}
                SET {column_name}=?, updated_on=?
                WHERE order_unique_id=?;
            '''

            self.cursor.execute(update_query, (new_value, datetime.now(), order_unique_id))
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.log_error(f"Error updating data: {e}")
            raise

    def retrieve_data(self, order_unique_id):
        try:
            retrieve_query = f'''
                SELECT * FROM {self.table_name}
                WHERE order_unique_id=?;
            '''

            self.cursor.execute(retrieve_query, (order_unique_id,))
            result = self.cursor.fetchone()

            return result
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving data: {e}")
            raise
    def retrieve_data_by_date(self, date):
        try:
            retrieve_query = f'''
                SELECT * FROM {self.table_name}
                WHERE order_datetime LIKE ? || '%'
            '''

            self.cursor.execute(retrieve_query, (date,))
            rows = self.cursor.fetchall()

            column_names = [description[0] for description in self.cursor.description][1:]

            result = [dict(zip(column_names, row[1:])) for row in rows]

            #print(type(result))
            return result
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving data: {e}")
            raise

    def retrieve_data_by_date_location_daily(self, date, location):
        try:
            print(location, date)
            retrieve_query = f'''
                SELECT * FROM {self.table_name}
                WHERE order_datetime LIKE ? || '%' AND outlet_location = ?
            '''

            self.cursor.execute(retrieve_query, (date, location))
            rows = self.cursor.fetchall()

            """column_names = [description[0] for description in self.cursor.description][1:]

            result = [dict(zip(column_names, row[1:])) for row in rows]"""

            column_names = [description[0] for description in self.cursor.description][1:]

            result = [dict(zip(column_names, row[1:])) for row in rows]

            for entry in result:
                if 'outlet_location' in entry:
                    del entry['outlet_location']


            return result
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving data: {e}")
            raise

    def retrieve_data_by_location(self, date,location):
        try:
            print(location)
            retrieve_query = f'''
                SELECT * FROM {self.table_name}
                WHERE outlet_location = ?
            '''

            self.cursor.execute(retrieve_query, (location,))
            rows = self.cursor.fetchall()

            column_names = [description[0] for description in self.cursor.description][1:]

            result = [dict(zip(column_names, row[1:])) for row in rows]

            for entry in result:
                if 'outlet_location' in entry:
                    del entry['outlet_location']

            return result
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving data: {e}")
            raise


    def export_to_excel(self, file_path):
        try:
            print("Exporting")
            select_all_query = f'''
                SELECT * FROM {self.table_name};
            '''

            self.cursor.execute(select_all_query)
            result = self.cursor.fetchall()

            df = pd.DataFrame(result, columns=[desc[0] for desc in self.cursor.description])

            df.to_excel(file_path, index=False)
        except (sqlite3.Error, pd.errors.EmptyDataError) as e:
            self.logger.log_error(f"Error exporting data to Excel: {e}")
            raise

    def close_connection(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except sqlite3.Error as e:
            self.logger.log_error(f"Error closing connection: {e}")
            raise

