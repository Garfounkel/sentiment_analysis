import random
from functools import reduce
import datetime
from sklearn.utils import deprecated
from twitterscraper import query_tweets
from nltk import Counter
from sklearn.datasets import fetch_20newsgroups
from text_preprocessing import KerasTokenizer, FlatMap
from twitterscraper.ts_logger import logger
from mysql_utils import mysql_sink


logger.setLevel(0)


def or_binop(lhw, rhw):
    return lhw + ' OR ' + rhw


def fetch_tweets(vocab):
    query_string = reduce(or_binop, random.sample(vocab, 10))

    year = random.randint(2007, 2018)
    smonth = random.randint(1, 11)
    tweets = query_tweets(query_string + " lang:en",
                          limit=5000,
                          poolsize=50,
                          begindate=datetime.date(year, smonth, 1),
                          enddate=datetime.date(year, smonth + 1, 1))
    return tweets


if __name__ == '__main__':
    limit = 10000
    count = 0

    newsgroup = fetch_20newsgroups()
    counts = Counter(FlatMap(KerasTokenizer(newsgroup.data))).most_common(1500)
    search_vocab = list(map(lambda x: x[0], counts))

    startdate = datetime.datetime.now()
    print('Start fetching')
    try:

        while count < limit:
            tweets = fetch_tweets(search_vocab)
            errors, added, size = mysql_sink(iter(tweets))
            count += added

            print('\nBatch info:')
            print('tweets fetched: {}'.format(len(tweets)))
            print('insertion errors: {}'.format(errors))
            print('total inserted: {}'.format(added))
            print('still to fetch: {}'.format(limit - count))
    except KeyboardInterrupt:
        print('interrupted')

    enddate = datetime.datetime.now()
    tweets_per_seconds = count / (enddate - startdate).seconds
    hours_for_7M = 7000000 / tweets_per_seconds / 60 / 60

    print('\nstart time: {}'.format(startdate))
    print('end time: {}'.format(enddate))
    print('tweets per seconds: {}'.format(tweets_per_seconds))
    print('time for 7M: {}h'.format(hours_for_7M))  # Last benchmark : 476h

