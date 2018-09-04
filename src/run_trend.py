#codu3gng=UTF-8
from websocket import create_connection, WebSocketConnectionClosedException
import json
import sys

from bot import LowPlayBot
from bot import MLBot
from bots.pg.policy_gradient import Foo
from system_log import system_log

from sample_bot import PokerSocket


def main():
    player_name="Eric"
    player_number=4
    token="12345678"
    connect_url="ws://localhost:8080/"
    #sample_bot=LowPlayBot(player_name)
    sample_bot=MLBot(player_name, Foo(is_restore=True))
    myPokerSocket=PokerSocket(player_name,player_number,token,connect_url,sample_bot)
    myPokerSocket.doListen()

if __name__ == "__main__":
    main()
