from system_log import system_log
from card import Card
import numpy as np
from card import Card, Cards, RANK_TO_INT, INT_TO_RANK

INT_TO_SUIT = ['S', 'H', 'D', 'C']


class BaseBot:

    STORE_MODEL_FREQUENCY=100
    UPDATE_FREQUENCY = 10

    def declare_action(self, info):
        raise NotImplementedError()


class TrendConnector(object):

    def __init__(self,player_name):
        self.round_cards_history=[]
        self.pick_his={}
        self.round_cards = {}
        self.score_cards={}
        self.player_name=player_name
        self.players_current_picked_cards=[]
        self.game_score_cards = {Card("QS"), Card("TC"), Card("2H"), Card("3H"), Card("4H"), Card("5H"), Card("6H"),
                           Card("7H"), Card("8H"), Card("9H"), Card("TH"), Card("JH"), Card("QH"), Card("KH"),
                           Card("AH")}
    #@abstractmethod
    def receive_cards(self,data):
        err_msg = self.__build_err_msg("receive_cards")
        raise NotImplementedError(err_msg)
    def pass_cards(self,data):
        err_msg = self.__build_err_msg("pass_cards")
        raise NotImplementedError(err_msg)
    def pick_card(self,data):
        err_msg = self.__build_err_msg("pick_card")
        raise NotImplementedError(err_msg)
    def expose_my_cards(self,yourcards):
        err_msg = self.__build_err_msg("expose_my_cards")
        raise NotImplementedError(err_msg)
    def expose_cards_end(self,data):
        err_msg = self.__build_err_msg("expose_cards_announcement")
        raise NotImplementedError(err_msg)
    def new_round(self, data):
        pass
    def receive_opponent_cards(self,data):
        err_msg = self.__build_err_msg("receive_opponent_cards")
        raise NotImplementedError(err_msg)
    def round_end(self,data):
        err_msg = self.__build_err_msg("round_end")
        raise NotImplementedError(err_msg)
    def deal_end(self,data):
        err_msg = self.__build_err_msg("deal_end")
        raise NotImplementedError(err_msg)
    def game_over(self,data):
        err_msg = self.__build_err_msg("game_over")
        raise NotImplementedError(err_msg)
    def pick_history(self,data,is_timeout,pick_his):
        err_msg = self.__build_err_msg("pick_history")
        raise NotImplementedError(err_msg)

    def reset_card_his(self):
        self.round_cards_history = []
        self.pick_his={}

    def get_card_history(self):
        return self.round_cards_history

    def turn_end(self,data):
        turnCard=data['turnCard']
        turnPlayer=data['turnPlayer']
        players=data['players']
        is_timeout=data['serverRandom']
        for player in players:
            player_name=player['playerName']
            if player_name==self.player_name:
                current_cards=player['cards']
                for card in current_cards:
                    self.players_current_picked_cards.append(Card(card))
        self.round_cards[turnPlayer]=Card(turnCard)
        opp_pick={}
        opp_pick[turnPlayer]=Card(turnCard)
        if (self.pick_his.get(turnPlayer))!=None:
            pick_card_list=self.pick_his.get(turnPlayer)
            pick_card_list.append(Card(turnCard))
            self.pick_his[turnPlayer]=pick_card_list
        else:
            pick_card_list = []
            pick_card_list.append(Card(turnCard))
            self.pick_his[turnPlayer] = pick_card_list
        self.round_cards_history.append(Card(turnCard))
        self.pick_history(data,is_timeout,opp_pick)

    def get_cards(self,data):
        try:
            receive_cards=[]
            players=data['players']
            for player in players:
                if player['playerName']==self.player_name:
                    cards=player['cards']
                    for card in cards:
                        receive_cards.append(Card(card))
                    break
            return receive_cards
        except Exception as e:
            system_log.show_message(e.message)
            raise e
            return None

    def get_round_scores(self,is_expose_card=False,data=None):
        if data!=None:
            players=data['roundPlayers']
            picked_user = players[0]
            round_card = self.round_cards.get(picked_user)
            score_cards=[]
            for i in range(len(players)):
                card=self.round_cards.get(players[i])
                if card in self.game_score_cards:
                    score_cards.append(card)
                if round_card.suit_index==card.suit_index:
                    if round_card.value<card.value:
                        picked_user = players[i]
                        round_card=card
            if (self.score_cards.get(picked_user)!=None):
                current_score_cards=self.score_cards.get(picked_user)
                score_cards+=current_score_cards
            self.score_cards[picked_user]=score_cards
            self.round_cards = {}

        receive_cards={}
        for key in self.pick_his.keys():
            picked_score_cards=self.score_cards.get(key)
            round_score = 0
            round_heart_score=0
            is_double = False
            if picked_score_cards!=None:
                for card in picked_score_cards:
                    if card in self.game_score_cards:
                        if card == Card("QS"):
                            round_score += -13
                        elif card == Card("TC"):
                            is_double = True
                        else:
                            round_heart_score += -1
                if is_expose_card:
                    round_heart_score*=2
                round_score+=round_heart_score
                if is_double:
                    round_score*=2
            receive_cards[key] = round_score
        return receive_cards

    def get_deal_scores(self, data):
        try:
            self.score_cards = {}
            final_scores  = {}
            initial_cards = {}
            receive_cards = {}
            picked_cards  = {}
            players = data['players']
            for player in players:
                player_name     = player['playerName']
                palyer_score    = player['dealScore']
                player_initial  = player['initialCards']
                player_receive  = player['receivedCards']
                player_picked   = player['pickedCards']

                final_scores[player_name] = palyer_score
                initial_cards[player_name] = player_initial
                receive_cards[player_name]=player_receive
                picked_cards[player_name]=player_picked
            return final_scores, initial_cards,receive_cards,picked_cards
        except Exception as e:
            system_log.show_message(e.message)
            raise e
            return None

    def get_game_scores(self,data):
        try:
            receive_cards={}
            players=data['players']
            for player in players:
                player_name=player['playerName']
                palyer_score=player['gameScore']
                receive_cards[player_name]=palyer_score
            return receive_cards
        except Exception as e:
            system_log.show_message(e.message)
            raise e
            return None


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
        for c in data['self']['candidateCards']:
            self.info.candidate.add_card(c)
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
        for c in data['self']['candidateCards']:
            self.info.candidate.add_card(c)
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
        for c in data['self']['candidateCards']:
            self.info.candidate.add_card(c)

        self.get_hand(data)
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

        for card in self.info.table.board:
            self.info.players[player_id].income.add_card(card)

        for player in self.info.players:
            now_score = player.get_current_deal_score(self.info.table.heart_exposed)
            player.round_score = now_score - player.round_score

    def deal_end(self, data):
        pass

    def game_over(self, data):
        pass


class MLBot(RuleBot):

    def __init__(self, name: str, a_bot: BaseBot):
        super(MLBot, self).__init__(name, a_bot)

    def pass_cards(self, data):
        actions = super(MLBot, self).pass_cards(data)
        return self._52_to_trend_card(actions)

    def pick_card(self, data):
        action = super(MLBot, self).pick_card(data)
        return self._52_to_trend_card(action)

    def expose_my_cards(self, data):
        try:
            card = super(MLBot, self).expose_my_cards(data)
            action = self._52_to_trend_card(card)
        except:
            action = ['AH']

        return action

    def _52_to_trend_card(self, card: int):
        suit = INT_TO_SUIT[int(card/13)]
        rank = INT_TO_RANK[card%13 + 2]
        return rank+suit


class PlayerInfo:

    def __init__(self):
        self.no_suit = set()
        self.income = Cards()
        self.draw = Cards()
        self.hand = Cards()
        self.name = ''
        self.round_score = 0

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
        t = [self.round_score] + suit
        return np.array(t + self.income.df.values.reshape(1, 52)[0].tolist() + self.draw.df.values.reshape(1, 52)[0].tolist())

    def get_current_deal_score(self, heart_exposed):
        """
        Compute score from deal start to now.
        """
        qs_score = 0
        h_score = 0
        mul = 1
        if self.income.df['C'][10] == 1: #梅花10
            mul = 2

        if self.income.df['S'][12] == 1:
            qs_score = 13
        for c in self.income.df['H'].tolist():
            if c == 1:
                h_score +=1
        if heart_exposed:
            h_score = h_score * 2
        return (h_score + qs_score) * mul


class TableInfo:

    def __init__(self):
        self.heart_exposed = False
        self.exchanged = False
        self.n_round = 0
        self.n_game = 0
        self.board = [None, None, None, None]
        self.first_draw = None
        self.opening_card = Cards()
        self.finish_expose = False

    def to_array(self):
        return np.array([self.n_game, self.n_round])


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
        self.candidate = Cards()

    def get_pos(self):
        # (0, 1, 2, 3)
        return 4 - self.table.board.count(None)

    def get_board_score(self):
        score = 0
        for card in self.table.board:
            if card == 'QS':
                score += 13
            elif card and card[1] == 'H':
                score += 1
        return score

    def get_board_max(self):
        max_rank = RANK_TO_INT[self.table.first_draw[0]]
        for card in self.table.board:
            if card:
                r, s = card
                r = RANK_TO_INT[r]
                if s == self.table.first_draw[1]:
                    if r > max_rank:
                        max_rank = r
        return max_rank
    
    def get_no_suit(self, suit):
        count = 0
        for idx, player in enumerate(self.players):
            if idx == self.me:
                continue
            if suit in player.no_suit:
                count += 1
        return count

    def get_possiable_min(self, n):
        # 非最後一手
        card = None

        if self.table.first_draw:
            target = None

            max_rank = 0
            max_board = self.get_board_max()
            for r, s in self.candidate:
                r = RANK_TO_INT[r]
                if s == self.table.first_draw[1] and r <= max_board and r >= max_rank:
                    max_rank = r
                    target = '%s%s' % (INT_TO_RANK[r], s)
            if target:
                system_log.show_message(u'後手：挑最大的安全牌出')
            else:
                for r, s in self.candidate:
                    r = RANK_TO_INT[r]
                    if r >= 12 and s == 'S':
                        continue
                    if s == self.table.first_draw[1] and r >= max_rank:
                        max_rank = r
                        target = '%s%s' % (INT_TO_RANK[r], s)
                system_log.show_message(u'後手：沒有安全牌，挑最大的出')

            return target
        else:
            world_cards = self.players[self.me].hand.df + self.table.opening_card.df
            max_less = 0
            max_target = None
            for r, s in sorted(self.candidate, key=lambda x: x[1] == 'H'):
                r = RANK_TO_INT[r]
                wc = list(world_cards.loc[world_cards[s] == 0].index)
                lc = list(filter(lambda x: x < r, wc))

                less_count = len(lc)
                if less_count <= n - self.get_no_suit(s) and less_count >= max_less:
                    max_less = less_count
                    max_target = '%s%s' % (INT_TO_RANK[r], s)
                    system_log.show_message('r %d%s n %r' % (r, s, n))
                    system_log.show_message('wc %r' % wc)
                    system_log.show_message('lc %r' % lc)

            system_log.show_message(u'先手：挑小的出')
            return max_target

        return card

    def to_array(self):
        t = np.array([])
        for p in self.players:
            t = np.append(t, p.to_array())
        return np.append(t, self.table.to_array())


class GymConnector(object):

    INT_TO_SUIT = INT_TO_SUIT

    def __init__(self, position, a_bot: BaseBot):
        self.pos = position
        self.ML = a_bot
        self.bot = a_bot
        self.last_first_draw = None

    def declare_action(self, observation, valid_actions):
        info = self._gym2game_info(observation, valid_actions)
        action = self.bot.declare_action(info)
        return action

    def get_train_observation(self, observation, valid_actions):
        info = self._gym2game_info(observation, valid_actions)
        return info.to_array().reshape(1, self.ML.n_features)

    def _gym2game_info(self, observation, valid_actions):
        info = GameInfo()
        info.me = self.pos

        opponent = observation[0][0]
        my_score = observation[0][1]
        my_hand = observation[0][2]
        my_income = observation[0][3]

        table = observation[1]
        info.table.n_round, _, _, info.table.exchanged, _, info.table.n_game, \
        info.table.finish_expose, info.table.heart_exposed, board, (first_draw,), backup = table

        if not any([backup[i][0] == -1 for i in range(4)]):
            for idx, card in enumerate(backup):
                info.table.opening_card.add_card(self._convert_array_to_card(card))
                if self.last_first_draw is not None and card[1] != self.last_first_draw[1]:
                    info.players[idx].no_suit.add(GymConnector.INT_TO_SUIT[card[1]])

        for idx, player in enumerate(info.players):
            if idx != 3:
                player.round_score = opponent[idx * 2]
                
                for i, card in enumerate(opponent[idx * 2 + 1]):
                    if -1 not in card:
                        player.income.add_card(self._convert_array_to_card(card))

            else:
                player.round_score = my_score
            

        self.last_first_draw = first_draw

        first_draw = self._convert_array_to_card(first_draw)
        info.table.first_draw = first_draw

        for idx, card in enumerate(board):
            card = self._convert_array_to_card(card)
            if card is None:
                continue

            info.table.board[idx] = card
            if first_draw and first_draw[1] != card[1]:
                info.players[idx].no_suit.add(card[1])

        for card in my_hand:
            c = self._convert_array_to_card(card)
            if c is not None:
                info.players[info.me].hand.add_card(c)

        for action in np.array(valid_actions):
            c = self._convert_array_to_card(action)
            if c is not None:
                info.players[info.me].valid_action.add_card(c)
        return info

    def _convert_array_to_card(self, array_card):
        if all(array_card == (-1, -1)):
            return None
        r, s = array_card[0], array_card[1]
        rank = INT_TO_RANK[r+2]
        suit = GymConnector.INT_TO_SUIT[s]
        return rank+suit
