import psycopg2


def main():
    conn = psycopg2.connect('postgresql://avnadmin:AVNS_6kmcp-nNyDI2rk7mUHg@topicos-xd.i.aivencloud.com:18069/defaultdb?sslmode=require')

    query_sql = 'SELECT VERSION()'

    cur = conn.cursor()
    cur.execute(query_sql)

    version = cur.fetchone()[0]
    print(version)

    conn.close()


if __name__ == "__main__":
    main()