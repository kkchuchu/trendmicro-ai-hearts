# encoding: utf-8
import random
import pandas as pd
import numpy as np

from bot import PokerBot
from card import Cards, RANK_TO_INT, INT_TO_RANK
from system_log import system_log


class PlayerInfo:

    def __init__(self):
        self.no_suit = []
        self.income = Cards()
        self.draw = Cards()
        self.hand = Cards()
        self.name = ''

    def to_array(self):
        # S, H, D, C
        suit = [-1, -1, -1, -1]
        if 'S' in self.no_suit:
            suit[0] = 1
        elif 'H' in self.no_suit:
            suit[1] = 1
        elif 'D' in self.no_suit:
            suit[2] = 1
        elif 'C' in self.no_suit:
            suit[3] = 1
        suit = np.array(suit)
        return np.concatenate(suit, self.income.values.reshape(1, 52), self.draw.values.reshape(1, 52))


class TableInfo:

    def __init__(self):
        self.heart_exposed = False
        self.exchanged = False
        self.n_round = 0
        self.n_game = 0
        self.board = []
        self.first_draw = None
        self.opening_card = Cards()
        self.finish_expose = False


class GameInfo:

    def __init__(self):
        # Major
        self.players = [PlayerInfo() for _ in range(4)]
        self.table = TableInfo()
        self.me = -1
        # Minor
        self.pass_to = ''
        self.receive_from = ''
        self.picked = []
        self.received = []
        self.who_exposed = -1
        self.candidate = []

    def get_pos(self):
        # (0, 1, 2, 3)
        return 4 - self.table.board.count(None)

    def get_board_score(self):
        score = 0
        for card in self.table.board:
            if card == 'QS':
                score += 13
            elif suit == 'H':
                score += 1
        return score

    def get_board_max(self):
        max_rank = RANK_TO_INT[self.table.first_draw[0]]
        for r,s in self.table.board:
            r = RANK_TO_INT[r]
            if s == self.table.first_draw[1]:
                if r > max_rank:
                    max_rank = r
        return max_rank

    def get_possiable_min(self, n):
        max_level = 0
        card = None

        my_hand = self.players[self.me].hand.df
        world_cards = self.table.opening_card.df + my_hand

        for r,s in self.candidate:
            r = RANK_TO_INT[r]
            wc = list(world_cards.loc[world_cards[s] == 0].index)

            level = len(list(filter(lambda x: x < r, wc)))
            if level <= n and level >= max_level:
                card = '%d%s' % (r, s)
                max_level = level

        return card


def declare_action(info: GameInfo):
    my_hand = info.players[info.me].hand.df
    columns = info.players[info.me].hand.columns

    if not info.table.exchanged and info.table.n_game % 4 != 0:
        pass_card = []

        # 換掉黑桃大牌
        topS = filter(lambda x: x >= 12, list(my_hand[my_hand['S'] > 0].index))
        for s in topS:
            pass_card.append('%sS' % INT_TO_RANK[s])

        # 除了黑桃，如果剛好可以缺門就拼缺門
        if len(pass_card) != 3:
            totals = list(my_hand.sum())
            for i, count in enumerate(totals):
                if i == columns.index('S'):
                    continue
                if count <= 3 - len(pass_card):
                    for rank in list(my_hand[my_hand[columns[i]] > 0].index):
                        pass_card.append('%s%s' % (INT_TO_RANK[rank], columns[i]))

        # 如果還沒滿，換掉Ｑ以上的大牌
        if len(pass_card) != 3:
            for suit in ['C', 'H', 'D']:
                tops = filter(lambda x: x >= 12, sorted(list(my_hand[my_hand[suit] > 0].index), reverse=True))
                for s in tops:
                    if len(pass_card) < 3:
                        pass_card.append('%sS' % INT_TO_RANK[s])

        system_log.show_message('pass_card %r' % pass_card)
        return pass_card

    elif not info.table.finish_expose:
        # TODO
        expose_card = ['AH']
        return expose_card
    else:
        # TODO
        FIRST = 0
        LAST = 3

        pos = info.get_pos()

        def pick_one():
            pick_card = None

            # 能安全丟黑桃Ｑ就丟
            if 'QS' in info.candidate:
                if info.table.first_draw and info.table.first_draw[1] != 'S':
                    return 'QS'
                if 'KS' in info.table.board or 'AS' in info.table.board:
                    return 'QS'

            # 缺門：先丟黑桃ＡＫ，再丟差一張缺門的，然後是紅心從大開始丟
            if info.table.first_draw:
                if info.candidate[0][1] != info.table.first_draw[1]:
                    tops = ['AS', 'KS']

                    for card in tops:
                        if card in info.candidate:
                            return card

                    totals = list(my_hand.sum())
                    try:
                        idx = totals.index(1)
                        suit = columns[idx]
                        rank = list(my_hand.loc[my_hand[suit] == 1].index)[0]
                        return '%s%s' % (INT_TO_RANK[rank], suit)
                    except ValueError:
                        pass

                    hearts = sorted(list(my_hand.loc[my_hand['H'] == 1].index), reverse=True)
                    if hearts:
                        return '%sH' % INT_TO_RANK[hearts[0]]

            if pos == LAST:
                max_rank = info.get_board_max()
                if info.get_board_score() != 0:
                    max_safe = 0
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if s == info.table.first_draw[1] and r < max_rank and r > max_safe:
                            max_safe = r
                    return '%d%s' % (max_safe, info.table.first_draw[1])
                else:
                    max_rank = 0
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if s == info.table.first_draw[1] and r > max_rank:
                            max_rank = r
                    return '%d%s' % (max_rank, info.table.first_draw[1])

            # 丟安全中的最大牌
            pick_card = info.get_possiable_min(3 - pos)

            return pick_card

        pick_card = pick_one()

        system_log.show_message('pick_card %r' % pick_card)
        return pick_card


class RuleBot(PokerBot):
    def __init__(self, name):
        super(RuleBot, self).__init__(name)
        self.reset()

    def reset(self):
        self.info = GameInfo()

    def get_hand(self, data):
        selfdata = data['self']

        self.info.me = selfdata['playerNumber'] - 1
        cards = selfdata['cards']
        self.info.players[self.info.me].hand = Cards(cards)

    def get_player_id(self, name):
        for i in range(4):
            if self.info.players[i].name == name:
                return i
        raise Exception('Player %r not found' % name)

    # new_deal
    def receive_cards(self, data):
        self.reset() # XXX

        dealNumber = data['dealNumber']
        players = data['players']
        selfdata = data['self']

        for player in players:
            playerNumber = player['playerNumber'] -1
            playerName = player['playerName']

            self.info.players[playerNumber].name = playerName
            system_log.show_message('new_deal %s' % self.info.players[playerNumber].name)

        self.info.table.n_game = dealNumber

        self.get_hand(data)

    def pass_cards(self, data):
        self.info.pass_to = data['receiver']
        return declare_action(self.info)

    def receive_opponent_cards(self, data):
        selfdata = data['self']

        self.info.table.exchanged = True

        self.get_hand(data)

        self.info.receive_from = selfdata['receivedFrom']
        self.info.picked = selfdata['pickedCards']
        self.info.received = selfdata['receivedCards']

    def expose_my_cards(self, data):
        return declare_action(self.info)

    def expose_cards_end(self, data):
        players = data['players']

        for player in players:
            if 'AH' in player['exposedCards']:
                self.info.table.heart_exposed = True
                self.info.who_exposed = player['playerNumber'] - 1
                break

    def new_round(self, data):
        self.info.table.finish_expose = True
        self.info.table.first_draw = None
        self.info.table.board = [None for _ in range(4)]
        self.info.table.n_round = data['roundNumber']

    def pick_card(self, data):
        self.info.candidate = data['self']['candidateCards']
        self.get_hand(data)
        return declare_action(self.info)

    def turn_end(self, data):
        turnPlayer = data['turnPlayer']
        turnCard = data['turnCard']

        player_id = self.get_player_id(turnPlayer)

        self.info.table.opening_card.add_card(turnCard)

        self.info.players[player_id].draw.add_card(turnCard)
        self.info.table.board[player_id] = turnCard
        if not self.info.table.first_draw:
            self.info.table.first_draw = turnCard

        if self.info.table.first_draw[1] != turnCard[1]:
            self.info.players[player_id].no_suit.append(turnCard[1])

    def round_end(self, data):
        roundPlayer = data['roundPlayer']
        player_id = self.get_player_id(roundPlayer)

        for card in self.info.table.board:
            self.info.players[player_id].income.add_card(card)

    def deal_end(self, data):
        pass

    def game_over(self, data):
        pass
