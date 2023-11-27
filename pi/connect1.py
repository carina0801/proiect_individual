import psycopg2 

__conn = None

def get_sql_conn():
    global __conn
    if __conn is None:
        conn = psycopg2.connect( host="localhost",
            database="postgres",
            user="postgres",
            password="aloe")
        return conn