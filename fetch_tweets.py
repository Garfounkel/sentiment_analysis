import threading
from random import randint
import tweepy
from nltk import corpus
import queue
import sys


config = {
    'tweet_per_process': 100000,
    'tweet_per_batch': 1000,
    'queue_size': 50,
    'consumer_key': 'pY08ZEfFQm4YxSCCQJgSrnxoh',
    'consumer_secret': 'OhWMXJOpZeRYhBEAePn7NnEIKNY4umPxyUGndOYRZfmSQ5Tdzy',
    'access_token': '410735094-Eigosf9U14iufUT46u7aKFztaB7gGmTKPALIHoAE',
    'access_token_secret': 'zRQncPnmZcV9TV5BCKUPr0BUuIsSe0eY4CeBYICPLdWLp',
    'max_query_size': 400,
}


class SyncQueueListener(tweepy.StreamListener):
    def __init__(self, max_tweets, out_stream):
        super().__init__()
        self.count = 0
        self.max_tweets = max_tweets
        self.out_stream = out_stream

    def on_status(self, data):
        super().on_status(data)
        if hasattr(data, 'extended_tweet'):
            text = data.extended_tweet['full_text']
            self.count += 1
        elif hasattr(data, 'retweeted_status'):
            return
        else:
            text = data.text
            self.count += 1
        self.out_stream.put((data.id, text))
        return self.count < self.max_tweets

    def on_error(self, status):
        if status == 420:
            print('ERROR: Rate limit')
        else:
            print('ERROR: received error code: {}'.format(status))
        return True

    def reset_count(self):
        self.count = 0


class TweepyProducer:
    def __init__(self, config, mpi_index, mpi_world_size):
        if mpi_index == 0:
            raise Exception("The mpi_index 0 is for the master process and can't be used for the producers")
        self.config = config
        self.auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
        self.auth.set_access_token(config['access_token'], config['access_token_secret'])
        self.api = tweepy.API(self.auth)
        self.mpi_index = mpi_index
        self.start_vocabulary = corpus.words.words()
        l = int(len(self.start_vocabulary) / mpi_world_size)
        s = (mpi_index - 1) * l
        e = mpi_index * l
        self.start_vocabulary = self.start_vocabulary[s:e]
        self.partition_size = int(len(self.start_vocabulary) / mpi_world_size)
        self.partition_size = self.partition_size if self.partition_size <= config['max_query_size'] else self.config['max_query_size']
        self.out_stream = queue.Queue(config['queue_size'])
        self.listener = SyncQueueListener(config['tweet_per_batch'], self.out_stream)
        self.stream = tweepy.Stream(auth=self.auth, listener=self.listener, tweet_mode='extended')

    def stream_handler(self, nb_tweets=None):
        nb_tweets = nb_tweets or self.config['tweet_per_process']
        count = 0
        while count < nb_tweets:
            print('Stream handler got {} tweets'.format(count))
            sys.stdout.flush()
            s = randint(0, len(self.start_vocabulary) - self.config['max_query_size'])
            e = s + self.config['max_query_size']
            track_list = self.start_vocabulary[s:e]
            self.stream.filter(track=track_list, languages=['en'])
            count += self.stream.listener.count
            self.stream.listener.reset_count()
            print('Stream handler batch end')
            sys.stdout.flush()
        print('Stream handler reached the limit of {} tweets'.format(nb_tweets))
        sys.stdout.flush()

    def tweet_generator(self, limit=20):
        while limit > 0:
            limit -= 1
            try:
                val = self.out_stream.get()
                yield val
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    # Testing the TweepyProducer
    producer = TweepyProducer(config, 1, 1)
    thr = threading.Thread(target=producer.stream_handler, args=(), kwargs={})
    thr.start()
    for index, tweet in enumerate(producer.tweet_generator(limit=config['tweet_per_process'])):
        print('Got a tweet: {}'.format(index), end='\r')
    thr.join()
