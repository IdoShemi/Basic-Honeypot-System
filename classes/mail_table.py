import psycopg2
from DatabaseConfig import DatabaseConfig  # Assuming your DatabaseConfig class is in a separate file

class Mail_Data:
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def __str__(self):
        return f"User: {self.user}, Password: {self.password}"

class Mail_Handler:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def insert_mail(self, mail):
        res = "mail inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f"INSERT INTO {self.db_config.scheme}.mail (\"user\", password) VALUES (%s, %s)"
            data = (mail.user, mail.password)
            cursor.execute(sql_statement, data)
            conn.commit()
        except psycopg2.Error as e:
            res = (f"Error inserting mail: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def get_mail_by_user(self, user):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT "user", password FROM {self.db_config.scheme}.mail WHERE "user" = %s'
            cursor.execute(sql_statement, (user,))
            result = cursor.fetchone()
            if result:
                res =  Mail_Data(result[0], result[1])
            else:
                return None
        except psycopg2.Error as e:
            (f"Error getting mail by user: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res
    
    def get_all_mail(self):
        res = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT "user", password FROM {self.db_config.scheme}.mail'
            cursor.execute(sql_statement)
            results = cursor.fetchall()
            for result in results:
                mail_data = Mail_Data(result[0], result[1])
                res.append(mail_data)
        except psycopg2.Error as e:
            print(f"Error getting all mail: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res