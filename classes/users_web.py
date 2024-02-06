import psycopg2
from DatabaseConfig import DatabaseConfig

class UsersWebData:
    def __init__(self, username, password=None, mail=None):
        self.username = username
        self.password = password
        self.mail = mail
        
class UsersWebHandler:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def insert_user_web(self, user_web_data: UsersWebData):
        error = "User Web Inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                INSERT INTO {self.db_config.scheme}.users_web 
                (username, password, mail) 
                VALUES (%s, %s, %s)
            '''

            data = (
                user_web_data.username,
                user_web_data.password,
                user_web_data.mail
            )

            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            error = f"Error inserting user web: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def get_user_web_by_username(self, username):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.users_web WHERE username = %s'
            cursor.execute(sql_statement, (username,))
            result = cursor.fetchone()
            if result:
                res = UsersWebData(result[0], result[1], result[2])
        except psycopg2.Error as e:
            print(f"Error getting user web by username: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def delete_user_web(self, username):
        res = "user web deleted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'DELETE FROM {self.db_config.scheme}.users_web WHERE username = %s'
            data = (username,)
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            res = f"Error deleting user web: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def update_user_web(self, username, new_user_web_data: UsersWebData):
        res = "user web updated"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'''
                UPDATE {self.db_config.scheme}.users_web 
                SET password = %s, mail = %s 
                WHERE username = %s
            '''
            data = (
                new_user_web_data.password,
                new_user_web_data.mail,
                username
            )
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            res = f"Error updating user web: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res