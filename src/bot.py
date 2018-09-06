from system_log import system_log
from card import Card
import numpy as np
from card import Card, Cards, RANK_TO_INT, INT_TO_RANK, SUIT_TO_INDEX, INDEX_TO_SUIT



class BaseBot:

    STORE_MODEL_FREQUENCY=100
    UPDATE_FREQUENCY = 10
    N_FEATURES=438
    N_ACTIONS=52

    def declare_action(self, info):
        raise NotImplementedError()


class RuleBot:

    def __init__(self, name: str, a_bot: BaseBot):
        self.name = name
        self.bot = a_bot
        self.reset()
        self.episode = 0

    def _its_my_turn(self, info):
        return self.bot.declare_action(info)

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
        return self._its_my_turn(self.info)

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
        return self._its_my_turn(self.info)

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
        pick_card = self._its_my_turn(self.info)
        system_log.show_message('pick_card %r' % pick_card)
        return pick_card

    def turn_end(self, data):
        """
        有人做完一個action
        """
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
        """
        每人出完一次牌
        """
        roundPlayer = data['roundPlayer']
        player_id = self.get_player_id(roundPlayer) # who get earn this round

        for card in self.info.table.board:
            self.info.players[player_id].income.add_card(card)

        for player in self.info.players:
            now_score = player.get_current_deal_score(self.info.table.heart_exposed)
            player.round_score = now_score - player.round_score

    def deal_end(self, data):
        """
        13次出完牌
        """
        pass

    def game_over(self, data):
        pass


class MLBot(RuleBot):

    def __init__(self, name, a_bot):
        super(MLBot, self).__init__(name, a_bot)
        self.before_my_turn_game_info = None
        self.after_my_turn_game_info = None

    def _its_my_turn(self, info):
        self.before_my_turn_game_info = None
        self.my_turn_action = None
        self.before_my_turn_game_info = info
        action = self.bot.declare_action(info)
        self.my_turn_action = action
        return action

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
        suit = INDEX_TO_SUIT[int(card/13)]
        rank = INT_TO_RANK[card%13 + 2]
        return rank+suit

    def deal_end(self, data):
        super(MLBot, self).deal_end(data)
        # update reward if shooting moon
        self.bot.learn(self.episode)
        self.episode = self.episode + 1

    def turn_end(self, data):
        super(MLBot, self).turn_end(data)
        turnPlayer = data['turnPlayer']
        turnCard = data['turnCard']

        if turnPlayer == self.name: # it's me
            self.after_my_turn_game_info = self.info

        # Store train data
        """
        card = data['players'][self.info.me]['roundCard']
        action = RANK_TO_INT[card[0]] - 2 + SUIT_TO_INDEX[card[1]] * 13
        train_data = self.info.to_array().reshape(1, self.bot.N_FEATURES)
        """

    def round_end(self, data):
        super(MLBot, self).round_end(data)
        self.bot.store_transition((self.before_my_turn_game_info, self.my_turn_action, 1, self.after_my_turn_game_info))

class PlayerInfo:

    def __init__(self):
        self.no_suit = set()
        self.income = Cards()
        self.draw = Cards()
        self.hand = Cards()
        self.name = ''
        self.round_score = 0.0

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

    INDEX_TO_SUIT = INDEX_TO_SUIT

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
                    info.players[idx].no_suit.add(GymConnector.INDEX_TO_SUIT[card[1]])

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
        suit = GymConnector.INDEX_TO_SUIT[s]
        return rank+suit
