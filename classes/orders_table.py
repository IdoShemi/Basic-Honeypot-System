import psycopg2
from DatabaseConfig import DatabaseConfig
import datetime
import uuid

class Order_Data:
    def __init__(self, order_id=None, username=None, total_price=0.0, product_ids=None, address=None, order_date=None, order_status="Processed"):
        self.order_id = order_id if order_id is not None else str(uuid.uuid4())  # Generate a unique ID if not provided
        self.username = username
        self.total_price = total_price
        self.product_ids = product_ids if product_ids is not None else []
        self.address = address
        self.order_date = order_date if order_date is not None else datetime.datetime.now()
        self.order_status = order_status

class Order_Handler:
    def __init__(self):
        self.db_config = DatabaseConfig()
        
    def insert_order(self, order: Order_Data):
        error = "Order Inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            
            # Use placeholders for other values, including %s for integers and %s for timestamps
            sql_statement = f'''
                INSERT INTO {self.db_config.scheme}.orders 
                (order_id, username, total_price, products_ids, address, order_date, order_status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''

            # Ensure the data types of the values match the column types
            data = (
                order.order_id,         # UUID
                order.username,         # VARCHAR
                order.total_price,      # NUMERIC
                order.product_ids,      # ARRAY of VARCHAR
                order.address,          # VARCHAR
                order.order_date,       # TIMESTAMP
                order.order_status      # VARCHAR
            )

            cursor.execute(sql_statement, data)
            conn.commit()
            res = f"Order {order.order_id} Inserted"
        except psycopg2.Error as e:
            error = f"Error inserting order: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def select_order(self, order_id):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.orders WHERE order_id = %s'
            cursor.execute(sql_statement, (order_id,))
            result = cursor.fetchone()
            if result:
                res = Order_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
        except psycopg2.Error as e:
            print(f"Error selecting order by order_id: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def select_orders_by_date_range(self, start_date, end_date):
        orders = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'''
                SELECT * FROM {self.db_config.scheme}.orders 
                WHERE order_date BETWEEN %s AND %s
            '''
            cursor.execute(sql_statement, (start_date, end_date))
            results = cursor.fetchall()
            for result in results:
                order = Order_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
                orders.append(order)
        except psycopg2.Error as e:
            print(f"Error selecting orders by date range: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return orders

    def select_orders_by_username(self, username):
        orders = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.orders WHERE username = %s'
            cursor.execute(sql_statement, (username,))
            results = cursor.fetchall()
            for result in results:
                order = Order_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
                orders.append(order)
        except psycopg2.Error as e:
            print(f"Error selecting orders by username: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return orders

    def select_all_orders(self):
        orders = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.orders'
            cursor.execute(sql_statement)
            results = cursor.fetchall()
            for result in results:
                order = Order_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
                orders.append(order)
        except psycopg2.Error as e:
            print(f"Error selecting all orders: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return orders

    def cancel_order(self, order_id):
        error = "Order Canceled"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            # Check if the order exists
            sql_check = f'SELECT COUNT(*) FROM {self.db_config.scheme}.orders WHERE order_id = %s'
            cursor.execute(sql_check, (order_id,))
            count = cursor.fetchone()[0]
            if count == 0:
                error = f"Order with ID {order_id} not found"
            else:
                # Update the order status to 'Canceled'
                sql_update = f'''
                    UPDATE {self.db_config.scheme}.orders 
                    SET order_status = 'Canceled' 
                    WHERE order_id = %s
                '''
                cursor.execute(sql_update, (order_id,))
                conn.commit()
                res = f"Order {order_id} Canceled"
        except psycopg2.Error as e:
            error = f"Error canceling order: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error
