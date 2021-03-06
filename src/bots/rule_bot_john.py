# encoding: utf-8
import random
import pandas as pd
import numpy as np

from bot import *
from system_log import system_log

class JohnsBot(BaseBot):
    def declare_action(self, info):
        my_hand = info.players[info.me].hand.df
        columns = info.players[info.me].hand.columns
        print('displaying dataframe')
        print(my_hand)
        if not info.table.exchanged and info.table.n_game % 4 != 0:
            pass_card = set()

            topS = filter(lambda x: x >= 12, list(my_hand[my_hand['S'] > 0].index))
            for s in topS:
                pass_card.add('%sS' % INT_TO_RANK[s])
                system_log.show_message(u'get rid of large spades %r' % pass_card)

            if len(pass_card) < 3:
                totals = list(my_hand.sum())
                for count in sorted(totals):
                    if count > 0 and count <= 3 - len(pass_card):
                        for rank in list(my_hand[my_hand[columns[totals.index(count)]] > 0].index):
                            if columns[totals.index(count)] not in ['S','C']:
                                pass_card.add('%s%s' % (INT_TO_RANK[rank], columns[totals.index(count)]))
                                system_log.show_message(u'attempt to eliminate a suit that is neither Spay nor Clover %r' % pass_card)

            if len(pass_card) != 3:
                for ind in sorted(list(my_hand.index), reverse=True):
                    if len(pass_card) < 3:
                        for suit in ['C', 'D', 'H', 'S']:
                            if len(pass_card) < 3:
                                pass_card.add('%s%s' % (INT_TO_RANK[ind], suit))
                                system_log.show_message(u'unable to elminiate a suit, fill with largest rank %r' % pass_card)
                            else:
                                break
                    else:
                        break

            system_log.show_message('ready to exchange pass_card %r' % pass_card)
            return list(pass_card)

        elif not info.table.finish_expose:
            expose_card = ['AH']
            totals = list(my_hand.sum())
            for i, count in enumerate(totals):
                if count > 4:
                    ranks = list(my_hand[columns[i]].index)
                    tops = list(filter(lambda x: x >= 12, ranks))
                    if len(tops) > 1:
                        expose_card = []
            return expose_card
        else:
            FIRST = 0
            LAST = 3

            pos = info.get_pos()

            pick_card = None

            
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

                    if info.table.n_round != 1:
                        hearts = sorted(list(my_hand.loc[my_hand['H'] == 1].index), reverse=True)
                        if hearts:
                            system_log.show_message(u'缺門：紅心從大開始丟')
                            return '%sH' % INT_TO_RANK[hearts[0]]
                    else:
                        max_rank = 0
                        target = None
                        for cand in info.candidate:
                            if card[1] != 'H' and card != 'QS' and RANK_TO_INT[card[0]] > max_rank:
                                max_rank = RANK_TO_INT[card[0]]
                                target = card
                        system_log.show_message(u'缺門：第一回合只能丟大牌')
                        return target

                    max_rank = 0
                    target = None
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if r > max_rank:
                            max_safe = r
                            target = '%s%s' % (INT_TO_RANK[r], s)
                    system_log.show_message(u'缺門：從最大開始丟')
                    return target


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
