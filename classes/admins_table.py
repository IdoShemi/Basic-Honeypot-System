import psycopg2
from DatabaseConfig import DatabaseConfig  # Assuming your DatabaseConfig class is in a separate file
from datetime import datetime

class Admin_Data:
    def __init__(self, user, password, mail, lastLogin=None, login_attempts=0):
        self.admin_name = user
        self.password = password
        self.admin_mail = mail
        self.LastLogin = lastLogin if lastLogin is not None else datetime.now()
        self.Login_attempts = login_attempts


class Admin_Handler:
    def __init__(self):
        self.db_config = DatabaseConfig()
        
     
    # Check about inserting admin how to implement email veryfing.
    def insert_admin(self, admin: Admin_Data):
        error = "Admin Inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            
            # Use placeholders for all values, including %s for integers and %s for timestamps
            sql_statement = f'''
                INSERT INTO {self.db_config.scheme}.admins 
                (admin_name, admin_password, admin_mail, last_login, login_attempts) 
                VALUES (%s, %s, %s, %s, %s)
            '''
            
            # Ensure the data types of the values match the column types
            data = (
                admin.admin_name,       # VARCHAR
                admin.password,   # VARCHAR
                admin.admin_mail,       # VARCHAR
                admin.LastLogin,       # TIMESTAMP
                admin.Login_attempts   # INTEGER
            )
            
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            error = f"Error inserting admin: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def get_admin_by_mail(self, admin_mail):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.admins WHERE admin_mail = %s'
            cursor.execute(sql_statement, (admin_mail,))
            result = cursor.fetchone()
            if result:
                res = Admin_Data(result[0], result[1], result[2], result[3], result[4])
        except psycopg2.Error as e:
            print(f"Error getting admin by admin_mail: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res


    def delete_admin(self, admin_name):
        res = "admin deleted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'DELETE FROM {self.db_config.scheme}.admins WHERE admin_name = %s'
            data = (admin_name,)
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            res = (f"Error deleting admin: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res



    def update_admin(self, admin_name, new_admin_data: Admin_Data):
        res = "admin updated"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'''
                UPDATE {self.db_config.scheme}.admins 
                SET admin_password = %s, admin_mail = %s, last_login = %s, login_attempts = %s 
                WHERE admin_name = %s
            '''
            data = (
                new_admin_data.password,
                new_admin_data.admin_mail,
                new_admin_data.LastLogin,
                new_admin_data.Login_attempts,
                admin_name
            )
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            res = (f"Error updating admin: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res
    
    
    def get_admin_by_user(self, admin_name):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.admins WHERE admin_name = %s'
            cursor.execute(sql_statement, (admin_name,))
            result = cursor.fetchone()
            if result:
                res = Admin_Data(result[0], result[1], result[2], result[3], result[4])
        except psycopg2.Error as e:
            print(f"Error getting admin by admin_name: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res