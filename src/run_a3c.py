#codu3gng=UTF-8
from websocket import create_connection, WebSocketConnectionClosedException
import json
import sys

from bot import MLBot
from bots.pg.policy_gradient import Foo
from bots.luffy.ac import Luffy
from system_log import system_log

from sample_bot import PokerSocket
import multiprocessing
import threading

import tensorflow as tf

CONNECT_URL="ws://localhost:8080/"
IS_RESTORE=True

def worker(player_name, player_number, token, sess):
    a_bot = MLBot(player_name, Luffy(sess, is_restore=False))
    my_poker_socket = PokerSocket(player_name, player_number, token, CONNECT_URL, a_bot)
    my_poker_socket.doListen()


def main():
    num_workers = multiprocessing.cpu_count() # Set workers ot number of available CPU threads
    print("Total CPUs are %r" % num_workers)
    with tf.device("/cpu:0"): 
        master_network = AC_Network(s_size,a_size,'global',None) # Generate global network

    with tf.Session() as sess:
        coordinator = tf.train.Coordinator()
        master_brain = Luffy(sess, 'master', is_restore=IS_RESTORE)

        worker_threads = []
        for i in range(1, 5):
            player_name = "bot number: %r" % i
            player_number = i
            token="12345678"

            t = threading.Thread(target=worker(player_name, player_number, token, sess))
            t.start()
            sleep(0.5)
            worker_threads.append(t)

        coordinator.join(worker_threads)


if __name__ == "__main__":
    main()
