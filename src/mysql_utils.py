import mysql.connector

from processing_pipeline import Preprocessor

mySQLdb = mysql.connector.connect(
        host="localhost",
        user="nicolas",
        passwd="nicolas",
        database="tweets",
    )


class Tweet:
    def __init__(self, id, text):
        self.id = id
        self.text = text


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


def mysql_reader(db=mySQLdb, max=None, chunk_size=10000):
    cursor = db.cursor()
    sql = 'SELECT COUNT(ID) FROM tweets'
    cursor.execute(sql)
    db_size = cursor.fetchall()[0][0]
    if max is None or max > db_size:
        max = db_size
    count = max
    offset = 0
    limit = chunk_size
    while count:
        if limit > count:
            limit = count
        sql = "SELECT * FROM tweets LIMIT {}, {}".format(offset, limit)
        cursor.execute(sql)
        for _ in range(limit):
            yield cursor.fetchone()
        count -= limit
        offset += limit


class MysqlTweetTextGetter(Preprocessor):
    def __call__(self, *args, **kwargs):
        return args[0][1]


if __name__ == "__main__":
    print(list(mysql_reader(max=10)))
