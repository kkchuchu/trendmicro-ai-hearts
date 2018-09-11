#codu3gng=UTF-8
from websocket import create_connection, WebSocketConnectionClosedException
import json
import sys

from bot import MLBot, BaseBot
from bots.pg.policy_gradient import Foo
from bots.luffy.ac import Luffy, GlobalAC
from system_log import system_log

from sample_bot import PokerSocket
import multiprocessing
from multiprocessing import Process, Value, Array
import threading

import tensorflow as tf

CONNECT_URL="ws://localhost:8080/"
IS_RESTORE=False

def worker(player_name, player_number, token):
    with tf.Session() as sess:
        a_bot = MLBot(player_name, Luffy(sess, player_name, is_restore=False))
        my_poker_socket = PokerSocket(player_name, player_number, token, CONNECT_URL, a_bot)
        print("Prepare listening")
        my_poker_socket.doListen()
        print("Start listening")


def main():
    num_workers = multiprocessing.cpu_count() # Set workers ot number of available CPU threads
    print("Total CPUs are %r" % num_workers)

    with tf.Session() as sess:
        master_network = GlobalAC(sess, BaseBot.N_FEATURES, BaseBot.N_ACTIONS) # Generate global network

    worker_processes = []
    for i in range(1, 5):
        player_name = "bot_number_%r" % i
        player_number = i
        token="12345678"
        # worker(player_name, player_number, token)
        t = Process(target=worker, args=(player_name, player_number, token))
        t.start()
        worker_processes.append(t)
        print("start player_name: %r with player_number: %r" % (player_name, player_number))

    for w in worker_processes:
        w.join()



if __name__ == "__main__":
    main()
