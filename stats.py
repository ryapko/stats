#!/usr/bin/env python

import docker, time
import psycopg2 as db_connect
import sqlite3
from sqlite3 import Error
from optparse import OptionParser


host_name = "192.168.99.100"
db_user = "postgres"
db_password = "postgres"
db_name = "postgres"

database = r"C:\sqlite\db\pythonsqlite.db"


def parse_args():
    parser = OptionParser(add_help_option=False)
    parser.add_option(
        "-f",
        "--frequency",
        help="frequency of metcrics gathering(in seconds)",
        action="store",
        dest="ftime",
        type="int",
        default=15,
    )
    options, args = parser.parse_args()
    return options, args


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_metric(conn, metric):
    sql = """ INSERT INTO metric(cpu_usage_total, system_cpu_usage,memory_usage, memory_usage_limit, usage_percent, exec_time)
              VALUES(?,?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, metric)
    conn.commit()
    return cur.lastrowid


def create_proceses(conn, proceses):
    sql = """ INSERT INTO proceses(pid,state,age,usename,query)
              VALUES(?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, proceses)
    conn.commit()
    return cur.lastrowid


def main():
    global options
    docker_client = docker.from_env()
    sp = docker_client.containers.get("some-postgres")

    conn_postgres = db_connect.connect(
        host=host_name, user=db_user, password=db_password, database=db_name
    )
    conn_sqlite = create_connection(database)

    while True:
        dockerstats = sp.stats(stream=False)
        cpu_usage_total = dockerstats["cpu_stats"]["cpu_usage"]["total_usage"]
        system_cpu_usage = dockerstats["cpu_stats"]["system_cpu_usage"]
        memory_usage = dockerstats["memory_stats"]["usage"]
        memory_usage_limit = dockerstats["memory_stats"]["limit"]
        usage_percent = round(memory_usage / memory_usage_limit * 100, 2)
        exec_time = time.asctime(time.localtime(time.time()))
        print("\n Common performance metrics \n ",
            "\n cpu_usage_total:",
            cpu_usage_total,
            "\n system_cpu_usage:",
            system_cpu_usage,
            "\n memory_usage:",
            memory_usage,
            "\n usage_percent:",
            usage_percent,
            "\n time:",
            exec_time,
        )

        cursor = conn_postgres.cursor()
        query = "SELECT pid, state, query_start, usename, query FROM pg_stat_activity;"
        cursor.execute(query)
        results = cursor.fetchall()
        print("\nNumber of proceses:  ", len(results), "\n ")
        for row in results:
            print("pid: ", row[0])
            print("state: ", row[1])
            print("age: ", row[2])
            print("usename: ", row[3])
            print("query: ", row[4])
            print("\n")

        with conn_sqlite:
            metric = (
                cpu_usage_total,
                system_cpu_usage,
                memory_usage,
                memory_usage_limit,
                usage_percent,
                exec_time,
            )
            metric_id = create_metric(conn_sqlite, metric)
            i = 0

            for i in range(len(results)):
                proceses = results[i]
                proceses_id = create_proceses(conn_sqlite, proceses)
                i = +i

        options, args = parse_args()
        time.sleep(options.ftime)

    conn_postgres.close()
    conn_sqlite.close()


if __name__ == "__main__":
    main()
