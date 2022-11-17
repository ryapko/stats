import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    database = r"C:\sqlite\db\pythonsqlite.db"
    
    sql_create_metric_table = """ CREATE TABLE IF NOT EXISTS metric (
                                        id integer PRIMARY KEY,
                                        cpu_usage_total integer NOT NULL,
                                        system_cpu_usage integer,
                                        memory_usage integer integer,
                                        memory_usage_limit integer,
                                        usage_percent integer,
                                        exec_time integer
                                    ); """

    sql_create_proceses_table = """CREATE TABLE IF NOT EXISTS proceses (
                                    id integer PRIMARY KEY,
                                    pid integer,
                                    state text,
                                    age text,
                                    usename text,
                                    query text
                                    ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_metric_table)

        create_table(conn, sql_create_proceses_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()