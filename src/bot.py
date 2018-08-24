# utf-8

import gym
import sys


class Card:

    TREND2GYMSUIT = {'S':0, 'H':1, 'D':2, 'C':3}

    # Takes in strings of the format: "As", "Tc", "6d"
    def __init__(self, card_string):
        self.suit_value_dict = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9}
        self.suit_index_dict = {"S": 0, "C": 1, "H": 2, "D": 3}
        self.val_string = "AKQJT98765432"
        value, self.suit = card_string[0], card_string[1]
        self.value = self.suit_value_dict[value]
        self.suit_index = self.suit_index_dict[self.suit]

    def __str__(self):
        return self.val_string[14 - self.value] + self.suit

    def toString(self):
        return self.val_string[14 - self.value] + self.suit

    def __repr__(self):
        return self.val_string[14 - self.value] + self.suit

    def __eq__(self, other):
        if self is None:
            return other is None
        elif other is None:
            return False
        return self.value == other.value and self.suit == other.suit

    def __hash__(self):
        return hash(self.value.__hash__()+self.suit.__hash__())

    def gym_suit_index(self):
        return Card.TREND2GYMSUIT[self.suit]

    def gym_value_index(self):
        return self.value - 2


class BotBase:

    def __init__(self):
        self._reset_card_history()

    def choose_action(self):
        raise NotImplementedError()

    def _reset_card_history(self):
        self.player_info = {}


class TrendBotBase(BotBase):

    def __init__(self, player_name):
        self.round_cards_history=[]
        self.pick_his={}
        self.round_cards = {}
        self.score_cards={}
        self.player_name=player_name
        self.players_current_picked_cards=[]
        self.game_score_cards = {Card("QS"), Card("TC"), Card("2H"), Card("3H"), Card("4H"), Card("5H"), Card("6H"),
                           Card("7H"), Card("8H"), Card("9H"), Card("TH"), Card("JH"), Card("QH"), Card("KH"),
                           Card("AH")}

        self.reset_card_his()

    def receive_cards(self,data):
        err_msg = self.__build_err_msg("receive_cards")
        raise NotImplementedError(err_msg)
    def pass_cards(self,data):
        err_msg = self.__build_err_msg("pass_cards")
        raise NotImplementedError(err_msg)
    def pick_card(self,data):
        self.choose_action()

    def expose_my_cards(self,yourcards):
        err_msg = self.__build_err_msg("expose_my_cards")
        raise NotImplementedError(err_msg)
    def expose_cards_end(self,data):
        err_msg = self.__build_err_msg("expose_cards_announcement")
        raise NotImplementedError(err_msg)
    def receive_opponent_cards(self,data):
        err_msg = self.__build_err_msg("receive_opponent_cards")
        raise NotImplementedError(err_msg)

    def round_end(self,data):
        self._set_player_info_in_round_end(data)

    def _set_player_info_in_round_end(self, data):
        players=data['players']
        (round_first_player, first_player_index) = self._get_round_first_player(data)
        round_first_card = Card(players[first_player_index]['roundCard'])
        round_cards = [(round_first_player, round_first_card)]
        for player in players:
            player_name=player['playerName']
            round_cards.append((player_name, Card(player['roundCard'])))

        who_get_card = round_first_player
        for player_name, card in round_cards[1:]:
            if card.suit != round_first_card.suit:
                pass
            else:
                if card.gym_value_index() > round_first_card.gym_value_index():
                    who_get_card = player_name

        for _, card in round_cards:
            self.player_info[who_get_card].shou_de[card.gym_suit_index()][card.gym_value_index()] = 1


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
        self.enable_heart = 0
        self._reset_card_history()

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


        if (self.player_info.get(turnPlayer)) is None:
            self.player_info[turnPlayer] = PlayerInfo(name=turnPlayer, hash_id=turnPlayer)

        the_card = Card(turnCard)
        self.player_info[turnPlayer].guo_qu_chu_guo[the_card.gym_suit_index()][the_card.gym_value_index()] = 1

        (round_first_player, first_player_index) = self._get_round_first_player(data)
        if turnPlayer == round_first_player and turnCard[1] == 'H' and self.enable_heart == 0:
            self.player_info[turnPlayer].que_men = [1, 0, 1, 1]
        else:
            round_first_card = players[first_player_index]['roundCard']
            if round_first_card[1] != turnCard[1]:
                self.player_info[turnPlayer].que_men[Card(round_first_card).gym_suit_index()] = 1 
        if turnCard[1] == "H":
            self.enable_heart = 1

    def _get_round_first_player(self, data):
        players = data['players']
        round_first_player = data['roundPlayers'][0]
        for player in players:
            if player['playerName'] == round_first_player:
                first_player_index = player['playerNumber'] - 1 # origin value is 1, 2, 3, 4
        return round_first_player, first_player_index

    def get_cards(self, data):
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
            system_log.show_message(e)
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
            system_log.show_message(e)
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
            system_log.show_message(e)
            return None


class GymBotBase(BotBase):

    def __init__(self, player_position):
        self.my_position = player_position
        self._reset_card_history()

    def reset(self):
        self._reset_card_history()

    def declare_action(self, player_obs, table_obs):
        self.player_obs2features(player_obs, table_obs)
        return self.choose_action()

    def choose_action(self):
        return 1

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

        if exchanged or n_game % 4 == 0: # 過了換牌步驟
            if n_round == 0: # bank store last round information even game number is changed.
                bank = []

            for pos, (number, rank) in enumerate(board):
                if -1 not in (number, rank):
                    self.player_info[pos].guo_qu_chu_guo[rank][number] = 1
            for pos, (number, rank) in enumerate(bank):
                self.player_info[pos].guo_qu_chu_guo[rank][number] = 1


            for (number, rank) in bank:
                self.player_info[start_pos].shou_de[rank][number] = 1

            if len(bank) > 0:
                color = bank[self.last_round_start_pos][1]
                for pos, (number, rank) in enumerate(bank):
                    if rank != color: #缺門
                        self.player_info[pos].que_men[color] = 1
            color = board[start_pos][1]
            for pos, (number, rank) in enumerate(board):
                if -1 not in (number, rank) and rank != color:
                    self.player_info[pos].que_men[color] = 1


        self.last_round_start_pos = start_pos # 更新上round的起始位置


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

    def get_shape(self):
        return
