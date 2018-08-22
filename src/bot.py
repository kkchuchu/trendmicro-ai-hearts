# utf-8

import gym
import universe  # register the universe environments
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.hearts import HeartsEnv
from hearts.bot import BotBase


class TrendBotBase(BotBase):

    def __init__(self, idx):
        self.idx = idx
        pass

    def declare_action(self, player_obs, table_obs):
        raise NotImplemented()


class Player:
    """
    [S, H, D, C]
    """

    def __init__(self):
        self.a = [None, None, None, None]
        self.b = self._init_card() #過去出過的牌
        self.c = self._init_card() # 每個人收的
        self.d = self._init_card() # 已知的牌，換的
        self.f = self._init_card() # 缺門

    def _init_card(self):
        return [[-1 for i in range(13)] for i in range(3)]
