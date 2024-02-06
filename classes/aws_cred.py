import psycopg2
from DatabaseConfig import DatabaseConfig  

class AWSCredentialsHandler:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.aws_access_key = None
        self.aws_secret_key = None
        self.load_aws_credentials()

    def load_aws_credentials(self):
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT aws_access_key, aws_secret_key FROM {self.db_config.scheme}.aws_cred LIMIT 1'
            cursor.execute(sql_statement)
            result = cursor.fetchone()
            if result:
                self.aws_access_key, self.aws_secret_key = result
        except psycopg2.Error as e:
            print(f"Error loading AWS credentials: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()