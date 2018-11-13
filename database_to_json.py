from mysql_utils import mysql_reader
import json


def read_tweet_json(filename='tweet_database.json', max=None):
    f = open(filename, 'r')
    max = max or -1
    for line in f:
        yield json.loads(line)['text']
        max -= 1
        if max == 0:
            break
    f.close()


if __name__ == '__main__':
    f = open('tweet_database.json', 'w')
    for tweet in mysql_reader():
        f.write(json.dumps({'text': tweet[1]}) + '\n')
    f.close()
