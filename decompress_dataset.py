import json
import subprocess
import glob
import mysql.connector
from tweet_scraper import insert_db


def tweet_generator():
    tar_files = glob.glob('./*.tar')

    for tar_file in tar_files:
        subprocess.call(['tar', '-xf', tar_file])
        bz2_files = glob.glob('./*/*/*/*/*.json.bz2')
        for bz2_file in bz2_files:
            subprocess.call(['bzip2', '-d', bz2_file])
            file = bz2_file.split('.')
            file = '.'.join(file[:-1])
            with open(file, "r") as ins:
                for line in ins:
                    yield json.loads(line)
            subprocess.call(["rm", file])


def get_tweet_text(tweet):
    if "extended_tweet" in tweet:
        return tweet["extended_tweet"]["full_text"]
    return tweet["text"]


class Tweet:
    def __init__(self, id, text):
        self.id = id
        self.text = text


if __name__ == "__main__":

    mySQLdb = mysql.connector.connect(
        host="localhost",
        user="nicolas",
        passwd="nicolas",
        database="tweets",
    )

    tweets = filter(lambda x: "lang" in x, tweet_generator())
    tweets = filter(lambda x: x["lang"] == "en", tweets)
    tweets = filter(lambda x: "retweeted_status" not in x, tweets)
    tweets = map(lambda x: Tweet(x["id"], get_tweet_text(x)), tweets)
    tweets = filter(lambda x: '…' not in x.text, tweets)

    insert_db(mySQLdb, tweets)
