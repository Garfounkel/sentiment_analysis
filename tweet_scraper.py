import random
from functools import reduce
import datetime
from twitterscraper import query_tweets
import mysql.connector
from nltk import Counter
from sklearn.datasets import fetch_20newsgroups
from text_preprocessing import KerasTokenizer
from twitterscraper.ts_logger import logger


logger.setLevel(0)


def or_binop(lhw, rhw):
    return lhw + ' OR ' + rhw


def fetch_tweets(vocab):
    query_string = reduce(or_binop, random.sample(vocab, 10))

    year = random.randint(2007, 2018)
    smonth = random.randint(1, 11)
    tweets = query_tweets(query_string + " lang:en",
                          limit=2000,
                          poolsize=20,
                          begindate=datetime.date(year, smonth, 1),
                          enddate=datetime.date(year, smonth + 1, 1))
    return tweets


def insert_db(db, tweets):
    errors = 0
    cursor = db.cursor()
    sql = 'SELECT COUNT(ID) FROM tweets'
    cursor.execute(sql, ())
    before = cursor.fetchall()[0][0]
    for tweet in tweets:
        id = tweet.id
        text = tweet.text.translate(str.maketrans({"\\": r"\\", "\"": r"\\\""}))
        try:
            sql = 'INSERT INTO tweets (id, text) VALUES ({}, "{}") ON DUPLICATE KEY UPDATE id = id'.format(id, text)
            cursor.execute(sql, ())
            mySQLdb.commit()
        except Exception as e:
            print(e)
            errors += 1
    sql = 'SELECT COUNT(ID) FROM tweets'
    cursor.execute(sql, ())
    after = cursor.fetchall()[0][0]
    return errors, after, before


if __name__ == '__main__':

    startdate = datetime.datetime.now()

    mySQLdb = mysql.connector.connect(
        host="localhost",
        user="nicolas",
        passwd="nicolas",
        database="tweets",
    )

    limit = 10000
    count = 0

    try:

        while count < limit:

            newsgroup = fetch_20newsgroups()
            counts = Counter(KerasTokenizer(newsgroup.data, corpus=True)).most_common(1500)
            search_vocab = list(map(lambda x: x[0], counts))
            total_tweets = len(search_vocab)

            tweets = fetch_tweets(search_vocab)
            errors, after, before = insert_db(mySQLdb, tweets)

            added = after - before
            count += added

            print('\nBatch info:')
            print('tweets fetched: {}'.format(total_tweets))
            print('insertion errors: {}'.format(errors))
            print('total inserted: {}'.format(added))
            print('still to fetch: {}'.format(limit - count))

    except KeyboardInterrupt:
        print('interrupted')

    enddate = datetime.datetime.now()
    tweets_per_seconds = count / (enddate - startdate).seconds
    hours_for_30B = 30000000 / tweets_per_seconds / 60 / 60

    print('\nstart time: {}'.format(startdate))
    print('end time: {}'.format(enddate))
    print('tweets per seconds: {}'.format(tweets_per_seconds))
    print('time for 30B: {}h'.format(hours_for_30B))  # Last benchmark : 476h

