import psycopg2
from DatabaseConfig import DatabaseConfig
import uuid
from datetime import datetime, timedelta

class Event_Data:
    def __init__(self, timestamp=None, ip=None, location=None, service=None, tag=None, attempts=1, additional_data=None, event_id=None, trap_name=None):
        self.event_id = event_id if event_id is not None else str(uuid.uuid4())
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.ip = ip
        self.location = location
        self.service = service
        self.tag = tag
        self.attempts = attempts
        self.additional_data = additional_data
        self.trap_name = trap_name

class Event_Handler:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def insert_event(self, event: Event_Data):
        error = "Event Inserted"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            while True:
                event.event_id = str(uuid.uuid4())
                sql_check = f'SELECT COUNT(*) FROM {self.db_config.scheme}.events WHERE event_id = %s'
                cursor.execute(sql_check, (event.event_id,))
                count = cursor.fetchone()[0]

                if count == 0:
                    sql_statement = f'''
                        INSERT INTO {self.db_config.scheme}.events 
                        (event_id, timestamp, ip, location, service, tag, attempts, additional_data, trap_name) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''

                    data = (
                        event.event_id,
                        event.timestamp,
                        event.ip,
                        event.location,
                        event.service,
                        event.tag,
                        event.attempts,
                        event.additional_data,
                        event.trap_name
                    )

                    cursor.execute(sql_statement, data)
                    conn.commit()
                    res = f"Event {event.event_id} Inserted"
                    break
        except psycopg2.Error as e:
            error = f"Error inserting event: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return error

    def select_event(self, event_id):
        res = None
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.events WHERE event_id = %s'
            cursor.execute(sql_statement, (event_id,))
            result = cursor.fetchone()
            if result:
                res = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
        except psycopg2.Error as e:
            print(f"Error selecting event by event_id: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return res

    def select_events_by_date_range(self, start_date, end_date):
        events = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'''
                SELECT * FROM {self.db_config.scheme}.events 
                WHERE timestamp >= %s AND timestamp <= %s
            '''
            cursor.execute(sql_statement, (start_date, end_date))
            results = cursor.fetchall()
            for result in results:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                events.append(event)
        except psycopg2.Error as e:
            print(f"Error selecting events by date range: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return events

    def select_events_by_service(self, service):
        events = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.events WHERE service = %s'
            cursor.execute(sql_statement, (service,))
            results = cursor.fetchall()
            for result in results:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                events.append(event)
        except psycopg2.Error as e:
            print(f"Error selecting events by service: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return events

    def select_events_by_location(self, location):
        events = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.events WHERE location = %s'
            cursor.execute(sql_statement, (location,))
            results = cursor.fetchall()
            for result in results:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                events.append(event)
        except psycopg2.Error as e:
            print(f"Error selecting events by location: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return events

    def select_all_events(self):
        events = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.events'
            cursor.execute(sql_statement)
            results = cursor.fetchall()
            for result in results:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                events.append(event)
        except psycopg2.Error as e:
            print(f"Error selecting all events: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return events

    def select_events_by_trap_name(self, trap_name):
        events = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.events WHERE trap_name = %s'
            cursor.execute(sql_statement, (trap_name,))
            results = cursor.fetchall()
            for result in results:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                events.append(event)
        except psycopg2.Error as e:
            print(f"Error selecting events by trap_name: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return events

    def select_events_by_trap_name_and_ip(self, trap_name, ip):
        events = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            sql_statement = f'SELECT * FROM {self.db_config.scheme}.events WHERE trap_name = %s AND ip = %s'
            cursor.execute(sql_statement, (trap_name, ip))
            results = cursor.fetchall()
            for result in results:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                events.append(event)
        except psycopg2.Error as e:
            print(f"Error selecting events by trap_name and ip: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return events


    def filter_events(self, start_date=None, end_date=None, ip=None, location=None, trap_name=None, service=None):
        events = []
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

        # Build the SQL statement based on the provided parameters
            sql_statement = f'''
            SELECT * FROM {self.db_config.scheme}.events 
            WHERE timestamp >= %s AND timestamp <= %s
            AND (%s IS NULL OR ip = %s)
            AND (%s IS NULL OR location = %s)
            AND (%s IS NULL OR trap_name = %s)
            AND (%s IS NULL OR service = %s)
        '''

        # Create a tuple for the parameters
            data = (
              start_date, end_date + timedelta(days=1) if end_date else None,
              ip, ip,
              location, location,
              trap_name, trap_name,
              service, service
         )

            cursor.execute(sql_statement, data)
            results = cursor.fetchall()

            for result in results:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                events.append(event)

        except psycopg2.Error as e:
            print(f"Error filtering events: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return events 

    


    def select_recent_touch_event(self, ip, minutes=5):
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()
            current_time = datetime.now()
            start_time = current_time - timedelta(minutes=minutes)

            sql_statement = f'''
                SELECT * FROM {self.db_config.scheme}.events
                WHERE ip = %s AND tag = 'touch' AND timestamp BETWEEN %s AND %s
            '''
            cursor.execute(sql_statement, (ip, start_time, current_time))
            result = cursor.fetchone()

            if result:
                event = Event_Data(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
                return event
            else:
                return None
        except psycopg2.Error as e:
            print(f"Error selecting recent touch event: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    
    def update_event_attempts(self, event_data):
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_config.connection_string)
            cursor = conn.cursor()

            sql_statement = f'''
                UPDATE {self.db_config.scheme}.events
                SET attempts = %s
                WHERE event_id = %s
            '''

            data = (event_data.attempts, event_data.event_id)

            cursor.execute(sql_statement, data)
            conn.commit()

            return f"Attempts for Event {event_data.event_id} updated to {event_data.attempts}"
        except psycopg2.Error as e:
            error = f"Error updating event attempts: {e}"
            return error
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()