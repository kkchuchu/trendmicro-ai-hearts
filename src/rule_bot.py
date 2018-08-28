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
            pass_card = []

            topS = filter(lambda x: x >= 12, list(my_hand[my_hand['S'] > 0].index))
            for s in topS:
                pass_card.append('%sS' % INT_TO_RANK[s])
                system_log.show_message(u'換掉黑桃大牌 %r' % pass_card)

            if len(pass_card) != 3:
                totals = list(my_hand.sum())
                for i, count in enumerate(totals):
                    if i == columns.index('S'):
                        continue
                    if count <= 3 - len(pass_card):
                        for rank in list(my_hand[my_hand[columns[i]] > 0].index):
                            pass_card.append('%s%s' % (INT_TO_RANK[rank], columns[i]))
                            system_log.show_message(u'除了黑桃，如果剛好可以缺門就拼缺門' % pass_card)

            if len(pass_card) != 3:
                for suit in ['C', 'H', 'D']:
                    tops = filter(lambda x: x >= 12, sorted(list(my_hand[my_hand[suit] > 0].index), reverse=True))
                    for s in tops:
                        if len(pass_card) < 3:
                            pass_card.append('%sS' % INT_TO_RANK[s])
                            system_log.show_message(u'如果還沒滿，換掉Ｑ以上的大牌' % pass_card)

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
                if info.get_board_score() != 0:
                    max_safe = 2
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if s == info.table.first_draw[1] and r < max_rank and r >= max_safe:
                            max_safe = r
                    system_log.show_message(u'最後手：場上有分，挑小的出')
                    return '%s%s' % (INT_TO_RANK[max_safe], info.table.first_draw[1])
                else:
                    max_rank = 2
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if s == info.table.first_draw[1] and r >= max_rank:
                            max_rank = r
                    system_log.show_message(u'最後手：場上無分，挑大的出')
                    return '%s%s' % (INT_TO_RANK[max_rank], info.table.first_draw[1])

            pick_card = info.get_possiable_min(3 - pos)

            return pick_card
