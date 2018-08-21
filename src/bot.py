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

