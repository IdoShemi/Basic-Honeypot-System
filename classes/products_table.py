import random
import psycopg2
from DatabaseConfig import DatabaseConfig

class Product_Data:
    def __init__(self, product_id=None, product_name=None, price=0.0):
        self.product_id = product_id if product_id is not None else str(random.randint(100000000, 999999999))  # Serial code will be generated automatically
        self.product_name = product_name
        self.price = price

class Product_Handler:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def insert_product(self, product: Product_Data):
        error = "Product Inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            # Generate a unique 9-digit numeric product ID
            product.product_id = self.generate_numeric_product_id()

            # Insert a new product with the generated product_id
            sql_statement = f'''
                INSERT INTO {self.db_config.scheme}.products 
                (product_id, product_name, price) 
                VALUES (%s, %s, %s)
            '''

            data = (
                product.product_id,
                product.product_name,
                product.price
            )

            cursor.execute(sql_statement, data)
            conn.commit()
            res = f"Product inserted with ID {product.product_id}"
        except psycopg2.Error as e:
            error = f"Error inserting product: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def generate_numeric_product_id(self):
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            while True:
                # Generate a random 9-digit numeric product ID
                product_id = str(random.randint(100000000, 999999999))

                # Check if the generated product_id already exists in the database
                sql_check = f'SELECT COUNT(*) FROM {self.db_config.scheme}.products WHERE product_id = %s'
                cursor.execute(sql_check, (product_id,))
                count = cursor.fetchone()[0]

                if count == 0:
                    return product_id  # Return the unique product_id
        except psycopg2.Error as e:
            print(f"Error generating numeric product ID: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def select_product_by_id(self, product_id):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.products WHERE product_id = %s'
            cursor.execute(sql_statement, (product_id,))
            result = cursor.fetchone()
            if result:
                res = Product_Data(result[0], result[1], result[2])
        except psycopg2.Error as e:
            print(f"Error selecting product by product_id: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def select_products_by_name(self, product_name):
        products = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.products WHERE product_name = %s'
            cursor.execute(sql_statement, (product_name,))
            results = cursor.fetchall()
            for result in results:
                product = Product_Data(result[0], result[1], result[2])
                products.append(product)
        except psycopg2.Error as e:
            print(f"Error selecting products by product_name: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return products

    def select_all_products(self):
        products = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.products'
            cursor.execute(sql_statement)
            results = cursor.fetchall()
            for result in results:
                product = Product_Data(result[0], result[1], result[2])
                products.append(product)
        except psycopg2.Error as e:
            print(f"Error selecting all products: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return products

    def update_product(self, product_id, new_name, new_price):
        error = "Product Updated"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            # Check if the product exists
            sql_check = f'SELECT COUNT(*) FROM {self.db_config.scheme}.products WHERE product_id = %s'
            cursor.execute(sql_check, (product_id,))
            count = cursor.fetchone()[0]
            if count == 0:
                error = f"Product with ID {product_id} not found"
            else:
                # Update the product name and price
                sql_update = f'''
                    UPDATE {self.db_config.scheme}.products 
                    SET product_name = %s, price = %s
                    WHERE product_id = %s
                '''
                cursor.execute(sql_update, (new_name, new_price, product_id))
                conn.commit()
                res = f"Product {product_id} updated"
        except psycopg2.Error as e:
            error = f"Error updating product: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def remove_product(self, product_id):
        error = "Product Removed"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            # Check if the product exists
            sql_check = f'SELECT COUNT(*) FROM {self.db_config.scheme}.products WHERE product_id = %s'
            cursor.execute(sql_check, (product_id,))
            count = cursor.fetchone()[0]
            if count == 0:
                error = f"Product with ID {product_id} not found"
            else:
                # Delete the product
                sql_delete = f'DELETE FROM {self.db_config.scheme}.products WHERE product_id = %s'
                cursor.execute(sql_delete, (product_id,))
                conn.commit()
                res = f"Product {product_id} removed"
        except psycopg2.Error as e:
            error = f"Error removing product: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error
