import psycopg2
from DatabaseConfig import DatabaseConfig
from datetime import datetime

class UsersReportingData:
    def __init__(self, admin_name, slt_hashed_pass=None, mail=None, last_login=None, login_attempts=0):
        self.admin_name = admin_name
        self.slt_hashed_pass = slt_hashed_pass
        self.mail = mail
        self.last_login = last_login if last_login is not None else datetime.now()
        self.login_attempts = login_attempts

class UsersReportingHandler:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def insert_user_reporting(self, user_reporting_data: UsersReportingData):
        error = "User Reporting Inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                INSERT INTO {self.db_config.scheme}.users_reporting 
                (admin_name, slt_hashed_pass, mail, last_login, login_attempts) 
                VALUES (%s, %s, %s, %s, %s)
            '''

            data = (
                user_reporting_data.admin_name,
                user_reporting_data.slt_hashed_pass,
                user_reporting_data.mail,
                user_reporting_data.last_login,
                user_reporting_data.login_attempts
            )

            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            error = f"Error inserting user reporting: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def select_user_reporting_by_name(self, admin_name):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                SELECT * 
                FROM {self.db_config.scheme}.users_reporting 
                WHERE admin_name = %s
            '''
            cursor.execute(sql_statement, (admin_name,))


            result = cursor.fetchone()
            if(result):
                res = UsersReportingData(result[0], result[1], result[2], result[3], result[4])
        except psycopg2.Error as e:
            print(f"Error selecting user reporting by admin_name: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def delete_user_reporting(self, admin_name):
        res = "user reporting deleted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'DELETE FROM {self.db_config.scheme}.users_reporting WHERE admin_name = %s'
            data = (admin_name,)
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            res = f"Error deleting user reporting: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def update_user_reporting(self, admin_name, new_user_reporting_data: UsersReportingData):
        res = "user reporting updated"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'''
                UPDATE {self.db_config.scheme}.users_reporting 
                SET slt_hashed_pass = %s, mail = %s, last_login = %s, login_attempts = %s 
                WHERE admin_name = %s
            '''
            data = (
                new_user_reporting_data.slt_hashed_pass,
                new_user_reporting_data.mail,
                new_user_reporting_data.last_login,
                new_user_reporting_data.login_attempts,
                admin_name
            )
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            res = f"Error updating user reporting: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res
    
    
    def select_user_reporting_by_mail(self, mail, default_timestamp=True):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            if default_timestamp:
                sql_statement = f'''
                    SELECT * 
                    FROM {self.db_config.scheme}.users_reporting 
                    WHERE mail = %s
                '''
                cursor.execute(sql_statement, (mail,))
            else:
                sql_statement = f'''
                    SELECT *, COALESCE(last_login, CURRENT_TIMESTAMP) AS last_login 
                    FROM {self.db_config.scheme}.users_reporting 
                    WHERE mail = %s
                '''
                cursor.execute(sql_statement, (mail,))

            result = cursor.fetchone()
            if result:
                res = UsersReportingData(result[0], result[1], result[2], result[3], result[4])
        except psycopg2.Error as e:
            print(f"Error selecting user reporting by mail: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res
    

