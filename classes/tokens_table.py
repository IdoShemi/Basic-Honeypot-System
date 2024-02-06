import psycopg2
import uuid
from datetime import datetime, timedelta
from DatabaseConfig import DatabaseConfig

class TokenData:
    def __init__(self, token=None, username_reporting=None, username_admin=None):
        self.token = token if token is not None else str(uuid.uuid4())
        self.username_reporting = username_reporting
        self.username_admin = username_admin
        current_time = datetime.now()
        self.expiration_date = current_time + timedelta(minutes=30)

class TokenHandler:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def insert_token(self, token_data: TokenData):
        error = "Token Inserted"
        conn = None
        cursor = None
        try:
            self.delete_token_by_username(username_admin=token_data.username_admin, username_reporting=token_data.username_reporting)
            
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                INSERT INTO {self.db_config.scheme}.tokens_web 
                (token, username_reporting, username_admin, expiration_date) 
                VALUES (%s, %s, %s, %s)
            '''

            data = (
                token_data.token,
                token_data.username_reporting,
                token_data.username_admin,
                token_data.expiration_date
            )

            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            error = f"Error inserting token: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def select_token_by_username(self, username_reporting="", username_admin=""):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                SELECT token, expiration_date
                FROM {self.db_config.scheme}.tokens_web
                WHERE COALESCE(username_reporting, '') = %s AND COALESCE(username_admin, '') = %s
            '''

            cursor.execute(sql_statement, (username_reporting, username_admin))
            result = cursor.fetchone()
            if result:
                res = {
                    'token': result[0],
                    'expiration_date': result[1]
                }
        except psycopg2.Error as e:
            print(f"Error selecting token by username: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res.values()

    def update_token(self, username_reporting="", username_admin=""):
        error = "Token Updated"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            while True:
                new_token = str(uuid.uuid4())

                sql_check = f'''
                    SELECT COUNT(*)
                    FROM {self.db_config.scheme}.tokens_web
                    WHERE username_reporting = %s AND username_admin = %s
                '''
                cursor.execute(sql_check, (username_reporting, username_admin))
                count = cursor.fetchone()[0]

                if count == 0:
                    error = f"Token not found"
                    break
                else:
                    sql_update = f'''
                        UPDATE {self.db_config.scheme}.tokens_web 
                        SET token = %s
                        WHERE COALESCE(username_reporting, '') = %s AND COALESCE(username_admin, '') = %s
                    '''
                    cursor.execute(sql_update, (new_token, username_reporting, username_admin))
                    conn.commit()
                    break
        except psycopg2.Error as e:
            error = f"Error updating token: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error
    
    
    def delete_token_by_username(self, username_reporting="", username_admin=""):
        error = "Token Deleted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                DELETE FROM {self.db_config.scheme}.tokens_web
                WHERE COALESCE(username_reporting, '') = %s AND COALESCE(username_admin, '') = %s
            '''

            cursor.execute(sql_statement, (username_reporting, username_admin))
            conn.commit()
        except psycopg2.Error as e:
            error = f"Error deleting token: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error
    
    
    def select_username_from_token(self, token):
        username = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                SELECT username_reporting, username_admin
                FROM {self.db_config.scheme}.tokens_web
                WHERE token = %s
            '''

            cursor.execute(sql_statement, (token,))
            result = cursor.fetchone()

            if result:
                # Check which username field is not None and return it
                username_reporting, username_admin = result
                if username_reporting:
                    username = username_reporting
                elif username_admin:
                    username = username_admin
        except psycopg2.Error as e:
            print(f"Error getting username from token: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return username
