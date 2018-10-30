import threading
import datetime
import sys
from mpi4py import MPI
from fetch_tweets import config, TweepyProducer
import mysql.connector

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


if rank == 0:  # Master
    mySQLdb = mysql.connector.connect(
        host="localhost",
        user="nicolas",
        passwd="jVHuEE??",
        database="tweets",
    )
    cursor = mySQLdb.cursor()
    count = comm.size - 1
    while count != 0:
        status, id, text = comm.recv(source=MPI.ANY_SOURCE)
        text = text.translate(str.maketrans({"\\": r"\\", "\"": r"\\\""}))
        try:
            sql = 'INSERT INTO tweets (id, text) VALUES ({}, "{}")'.format(id, text)
            cursor.execute(sql, ())
            mySQLdb.commit()
        except Exception as e:
            print(e)
        sys.stdout.flush()
        if status:
            count -= 1
else:  # Slave
    producer = TweepyProducer(config, rank, comm.size)
    thr = threading.Thread(target=producer.stream_handler, args=(), kwargs={})
    thr.start()

    for index, tweet in enumerate(producer.tweet_generator(limit=config['tweet_per_process'])):
        sys.stdout.flush()
        comm.send((None, tweet[0], tweet[1]), dest=0)

    comm.send((rank, None), dest=0)
    thr.join()

print(datetime.datetime.now())
