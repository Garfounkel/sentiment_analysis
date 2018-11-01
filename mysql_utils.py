import mysql.connector

mySQLdb = mysql.connector.connect(
        host="localhost",
        user="nicolas",
        passwd="nicolas",
        database="tweets",
    )


def mysql_sink(tweets, db=mySQLdb):
    errors = 0
    cursor = db.cursor()
    sql = 'SELECT COUNT(ID) FROM tweets'
    cursor.execute(sql, ())
    before = cursor.fetchall()[0][0]
    stream_size = 0

    cont = True
    while cont:
        val = []
        for _ in range(100):
            try:
                v = next(tweets)
                v = (str(v.id), v.text)
                val.append(v)
            except StopIteration:
                cont = False
                break
        stream_size += len(val)
        try:
            sql = 'INSERT INTO tweets (id, text) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id = id'
            cursor.executemany(sql, val)
            db.commit()
        except Exception as e:
            print(e)
            errors += 1
    sql = 'SELECT COUNT(ID) FROM tweets'
    cursor.execute(sql, ())
    after = cursor.fetchall()[0][0]
    inserted = after - before
    return errors, inserted, stream_size


def mysql_reader(db=mySQLdb, max=None):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tweets")

    count = max
    if max is None:
        count = -1
    while count:
        count -= 1
        yield cursor.fetchone()


if __name__ == "__main__":
    print(list(mysql_reader(max=10)))
