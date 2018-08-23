# utf-8

import gym
import sys

_ignore__1 = lambda card: -1 not in card

class TrendBotBase:

    def __init__(self):
        pass

    def player_obs2features(self, *args, **wargs):
        raise NotImplemented()


class GymBotBase:

    def __init__(self, player_position):
        self.my_position = player_position
        self._init()

    def reset(self):
        self._init()

    def _init(self):
        self.player_info = {
            0: PlayerInfo(),
            1: PlayerInfo(),
            2: PlayerInfo(),
            3: PlayerInfo(),
        }
        self.last_round_start_pos = None
        self.myself = PlayerInfo()

    def declare_action(self, player_obs, table_obs, env):
        self.player_obs2features(player_obs, table_obs)
        return self._random_action(env)

    def player_obs2features(self, player_obs, table_obs):
        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game,\
            finish_expose, heart_exposed,\
                board, first_draw, bank = table_obs 

        players, my_score, \
            hand, income = player_obs

        """
        board: 這一round的牌
        bank : 上一round的結果
        """

        if exchanged: # 過了換牌步驟
            for pos, (number, rank) in enumerate(filter(_ignore__1, board)):
                self.player_info[pos].guo_qu_chu_guo[rank][number] = 1
            for pos, (number, rank) in enumerate(bank):
                self.player_info[pos].guo_qu_chu_guo[rank][number] = 1


            for (number, rank) in bank:
                self.player_info[start_pos].shou_de[rank][number] = 1


            color = bank[self.last_round_start_pos][1]
            for pos, (number, rank) in enumerate(bank):
                if rank != color: #缺門
                    self.player_info[pos].que_men[color] = 1
            color = board[start_pos][1]
            for pos, (number, rank) in enumerate(filter(_ignore__1, board)):
                if rank != color:
                    self.player_info[pos].que_men[color] = 1


        self.last_round_start_pos = start_pos # 更新上round的起始位置


    def _random_action(self, env):
        return env.action_space.sample()


class PlayerInfo:

    def __init__(self, name=None, hash_id=None):
        self.name = name
        self.hash_id = hash_id
        self.accumulate_score = 0
        self.que_men = [None, None, None, None] # 缺門
        # [S, H, D, C]
        self.guo_qu_chu_guo = self._init_card() #過去出過的牌
        self.shou_de = self._init_card() # 每個人收的
        self.yi_zhi_de = self._init_card() # 已知的牌，換的

    def _init_card(self):
        return [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]
