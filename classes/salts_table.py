import random
import string
import psycopg2
import uuid
from DatabaseConfig import DatabaseConfig

class Salt_Data:
    def __init__(self, salt=None, username_reporting=None, username_admin=None):
        self.salt = salt if salt is not None else self.generate_salt()
        self.username_reporting = username_reporting
        self.username_admin = username_admin

    @staticmethod
    def generate_salt(length=32):
        return str(uuid.uuid4()).replace("-", "")

class Salt_Handler:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def insert_salt(self, salt_data: Salt_Data):
        error = "Salt Inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            # Insert the salt with given values or NULL
            sql_statement = f'''
                INSERT INTO {self.db_config.scheme}.salts 
                (salt, username_reporting, username_admin) 
                VALUES (%s, %s, %s)
            '''

            data = (
                salt_data.salt,
                salt_data.username_reporting,
                salt_data.username_admin
            )

            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            error = f"Error inserting salt: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def select_salt_by_username_and_service(self, username_reporting=None, username_admin=None):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            # Depending on the input, construct the appropriate WHERE clause
            if username_reporting is not None and username_admin is not None:
                sql_statement = f'''
                    SELECT salt
                    FROM {self.db_config.scheme}.salts
                    WHERE username_reporting = %s AND username_admin = %s
                '''
                cursor.execute(sql_statement, (username_reporting, username_admin))
            elif username_reporting is not None:
                sql_statement = f'''
                    SELECT salt
                    FROM {self.db_config.scheme}.salts
                    WHERE username_reporting = %s
                '''
                cursor.execute(sql_statement, (username_reporting,))
            elif username_admin is not None:
                sql_statement = f'''
                    SELECT salt
                    FROM {self.db_config.scheme}.salts
                    WHERE username_admin = %s
                '''
                cursor.execute(sql_statement, (username_admin,))
            else:
                print("Both username_reporting and username_admin are None. Provide at least one value.")

            result = cursor.fetchone()
            if result:
                res = result[0]
        except psycopg2.Error as e:
            print(f"Error selecting salt by username and service: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def update_salt(self, username_reporting=None, username_admin=None):
        error = "Salt Updated"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            while True:
                # Generate a new unique salt
                new_salt = Salt_Data.generate_salt()

                # Construct the appropriate WHERE clause based on input
                where_clause = ""
                if username_reporting is not None and username_admin is not None:
                    where_clause = f"WHERE username_reporting = %s AND username_admin = %s"
                    params = (username_reporting, username_admin)
                elif username_reporting is not None:
                    where_clause = f"WHERE username_reporting = %s"
                    params = (username_reporting,)
                elif username_admin is not None:
                    where_clause = f"WHERE username_admin = %s"
                    params = (username_admin,)
                else:
                    error = ("Both username_reporting and username_admin are None. Provide at least one value.")
                    return error

                # Check if the salt record exists
                sql_check = f'''
                    SELECT COUNT(*)
                    FROM {self.db_config.scheme}.salts
                    {where_clause}
                '''
                cursor.execute(sql_check, params)
                count = cursor.fetchone()[0]

                if count == 0:
                    error = f"Salt for username_reporting '{username_reporting}' and username_admin '{username_admin}' not found"
                    break
                else:
                    # Update the salt value
                    sql_update = f'''
                        UPDATE {self.db_config.scheme}.salts 
                        SET salt = %s
                        {where_clause}
                    '''
                    cursor.execute(sql_update, (new_salt,) + params)
                    conn.commit()
                    break
        except psycopg2.Error as e:
            error = f"Error updating salt: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error
