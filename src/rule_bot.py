import pandas as pd

from bot import PokerBot
from card import Cards, RANK_TO_INT, INT_TO_RANK
from system_log import system_log

class PlayerInfo:
    no_suit = []
    income = Cards()
    draw = Cards()
    hand = Cards()
    name = ''

class TableInfo:
    heart_exposed = False
    exchanged = False
    n_round = 0
    n_game = 0
    board = []
    first_draw = None
    opening_card = Cards()
    finish_expose = False

class GameInfo:
    # Major
    players = [PlayerInfo() for _ in range(5)] # 0 is unused
    table = TableInfo()
    me = -1
    # Minor
    pass_to = ''
    receive_from = ''
    picked = []
    received = []
    who_exposed = -1
    candidate = []
    


def declare_action(info):
    my_hand = info.players[info.me].hand.df
    columns = info.players[info.me].hand.columns

    if not info.table.exchanged and info.table.n_game % 4 != 0:
        pass_card = []

        topS = filter(lambda x: x >= 12, list(my_hand[my_hand['S'] > 0].index))
        for s in topS:
            pass_card.append('%sS' % INT_TO_RANK[s])

        if len(pass_card) != 3:
            totals = list(my_hand.sum())
            for i, count in enumerate(totals):
                if i == columns.index('S'):
                    continue
                if count <= 3 - len(pass_card):
                    for rank in list(df[df[columns[i]] > 0].index):
                        pass_card.append('%s%s' % (INT_TO_RANK[rank], columns[i]))

        if len(pass_card) != 3:
            for suit in ['C', 'H', 'D']:
                tops = filter(lambda x: x >= 12, list(my_hand[my_hand[suit] > 0].index))
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
        pick_card = random.choice(candidate)
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

        self.info.me = selfdata['playerNumber']
        cards = selfdata['cards']
        self.info.players[self.info.me].hand = Cards(cards)

    def get_player_id(self, name):
        for i in range(4):
            system_log.show_message(self.info.players[i].name)
            if self.info.players[i].name == name:
                return i
        system_log.show_message(self.info.players)
        raise Exception('Player %r not found' % name)
        

    # new_deal
    def receive_cards(self, data): 
        self.reset() # XXX

        dealNumber = data['dealNumber']
        players = data['players']
        selfdata = data['self']

        system_log.show_message('new_deal')
        system_log.show_message(data)
        for player in players:
            playerNumber = player['playerNumber']
            playerName = player['playerName']
            
            self.info.players[playerNumber].name = playerName

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
                self.info.who_exposed = player['playerNumber']
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

