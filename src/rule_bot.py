# encoding: utf-8
import random
import pandas as pd
import numpy as np

from bot import *
from system_log import system_log


class ChunTingsBot(BaseBot):
    def declare_action(self, info):
        my_hand = info.players[info.me].hand.df
        columns = info.players[info.me].hand.columns

        if not info.table.exchanged and info.table.n_game % 4 != 0:
            pass_card = set()

            topS = filter(lambda x: x >= 12, list(my_hand[my_hand['S'] > 0].index))
            for s in topS:
                pass_card.add('%sS' % INT_TO_RANK[s])
                system_log.show_message(u'換掉黑桃大牌 %r' % pass_card)

            if len(pass_card) != 3:
                totals = list(my_hand.sum())
                for i, count in enumerate(totals):
                    if i == columns.index('S'):
                        continue
                    if count <= 3 - len(pass_card):
                        for rank in list(my_hand[my_hand[columns[i]] > 0].index):
                            pass_card.add('%s%s' % (INT_TO_RANK[rank], columns[i]))
                            system_log.show_message(u'除了黑桃，如果剛好可以缺門就拼缺門 %r' % pass_card)

            if len(pass_card) != 3:
                for suit in ['C', 'H', 'D']:
                    tops = filter(lambda x: x >= 12, sorted(list(my_hand[my_hand[suit] > 0].index), reverse=True))
                    for s in tops:
                        if len(pass_card) < 3:
                            pass_card.add('%sS' % INT_TO_RANK[s])
                            system_log.show_message(u'如果還沒滿，換掉Ｑ以上的大牌 %r' % pass_card)

            if len(pass_card) != 3:
                system_log.show_message(u'隨便啦')
                for _ in range(3 - len(pass_card)):
                    pass_card.add(random.choice(info.candidate))

            system_log.show_message('pass_card %r' % pass_card)
            return list(pass_card)

        elif not info.table.finish_expose:
            # TODO
            expose_card = ['AH']
            return expose_card
        else:
            # TODO
            FIRST = 0
            LAST = 3

            pos = info.get_pos()

            pick_card = None

            # 能安全丟黑桃Ｑ就丟
            if 'QS' in info.candidate:
                if info.table.first_draw and info.table.first_draw[1] != 'S':
                    return 'QS'
                if 'KS' in info.table.board or 'AS' in info.table.board:
                    return 'QS'

            if info.table.first_draw:
                if info.candidate[0][1] != info.table.first_draw[1]:
                    tops = ['AS', 'KS']

                    for card in tops:
                        if card in info.candidate:
                            system_log.show_message(u'缺門：先丟黑桃ＡＫ')
                            return card

                    totals = list(my_hand.sum())
                    try:
                        idx = totals.index(1)
                        suit = columns[idx]
                        rank = list(my_hand.loc[my_hand[suit] == 1].index)[0]
                        system_log.show_message(u'缺門：丟差一張缺門的')
                        return '%s%s' % (INT_TO_RANK[rank], suit)
                    except ValueError:
                        pass

                    hearts = sorted(list(my_hand.loc[my_hand['H'] == 1].index), reverse=True)
                    if hearts:
                        system_log.show_message(u'缺門：紅心從大開始丟')
                        return '%sH' % INT_TO_RANK[hearts[0]]

            if pos == LAST:
                max_rank = info.get_board_max()
                max_safe = 0
                target = None
                for r,s in info.candidate:
                    r = RANK_TO_INT[r]
                    if s == info.table.first_draw[1] and r < max_rank and r >= max_safe:
                        max_safe = r
                        target = '%s%s' % (INT_TO_RANK[r], s)
                if target:
                    system_log.show_message(u'最後手：挑安全牌中最大的出')
                else:
                    max_rank = 0
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if s == info.table.first_draw[1] and r > max_rank:
                            max_safe = r
                            target = '%s%s' % (INT_TO_RANK[r], s)
                    system_log.show_message(u'最後手：沒安全牌，挑最大的出')

                return target

            pick_card = info.get_possiable_min(3 - pos)

            return pick_card
<<<<<<< HEAD
=======

class RuleBot(TrendConnector):
    def __init__(self, name: str, a_bot: BaseBot):
        self.bot = a_bot
        super(RuleBot, self).__init__(name)
        self.reset()

    def reset(self):
        self.info = GameInfo()
        self.info.table.exchanged = False

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
        self.info.candidate = data['self']['cards']
        return self.bot.declare_action(self.info)

    def receive_opponent_cards(self, data):
        selfdata = data['self']

        system_log.show_message('receive_opponent_cards')
        self.info.table.exchanged = True

        self.get_hand(data)

        self.info.receive_from = selfdata['receivedFrom']
        self.info.picked = selfdata['pickedCards']
        self.info.received = selfdata['receivedCards']

    def expose_my_cards(self, data):
        self.info.candidate = data['self']['candidateCards']
        return self.bot.declare_action(self.info)

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
        system_log.show_message('board %r candidate %r' % (self.info.table.board, self.info.candidate))

        pick_card = self.bot.declare_action(self.info)
        system_log.show_message('pick_card %r' % pick_card)
        return pick_card

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
            self.info.players[player_id].no_suit.add(turnCard[1])

    def round_end(self, data):
        roundPlayer = data['roundPlayer']
        player_id = self.get_player_id(roundPlayer)

        system_log.show_message('%s receives %r' % (roundPlayer, self.info.table.board))
        for card in self.info.table.board:
            self.info.players[player_id].income.add_card(card)

    def deal_end(self, data):
        pass

    def game_over(self, data):
        pass
>>>>>>> 8ab24330d7feb0f0f16ff5d35aee6a49da471eb8
