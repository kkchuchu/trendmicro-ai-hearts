from bot import TrendBotBase, Card

class kittoBot(TrendBotBase):

    def __init__(self,name):
        super(kittoBot,self).__init__(name)
        self.my_hand_cards=[]
        self.expose_card=False
        self.my_pass_card=[]
    def receive_cards(self,data):
        self.my_hand_cards=self.get_cards(data)

    def pass_cards(self,data):
        cards = data['self']['cards']
        self.my_hand_cards = []
        for card_str in cards:
            card = Card(card_str)
            self.my_hand_cards.append(card)
        pass_cards=[]
        count=0
        for i in range(len(self.my_hand_cards)):
            card=self.my_hand_cards[len(self.my_hand_cards) - (i + 1)]
            if card==Card("QS"):
                pass_cards.append(card)
                count+=1
            elif card==Card("TC"):
                pass_cards.append(card)
                count += 1
        for i in range(len(self.my_hand_cards)):
            card = self.my_hand_cards[len(self.my_hand_cards) - (i + 1)]
            if card.suit_index==2:
                pass_cards.append(card)
                count += 1
                if count ==3:
                    break
        if count <3:
            for i in range(len(self.my_hand_cards)):
                card = self.my_hand_cards[len(self.my_hand_cards) - (i + 1)]
                if card not in self.game_score_cards:
                    pass_cards.append(card)
                    count += 1
                    if count ==3:
                        break
        return_values=[]
        for card in pass_cards:
            return_values.append(card.toString())
        message="Pass Cards:{}".format(return_values)
        self.my_pass_card=return_values
        return return_values

    def pick_card(self,data):
        cadidate_cards=data['self']['candidateCards']
        cards = data['self']['cards']
        self.my_hand_cards = []
        for card_str in cards:
            card = Card(card_str)
            self.my_hand_cards.append(card)
        message = "My Cards:{}".format(self.my_hand_cards)
        card_index=0
        message = "Pick Card Event Content:{}".format(data)
        message = "Candidate Cards:{}".format(cadidate_cards)
        message = "Pick Card:{}".format(cadidate_cards[card_index])

        players = data['players']
        #Get first card if it exist
        (round_first_player, first_player_index) = self._get_round_first_player(data)
        roundCardColor = "" #fitst card suit
        round_first_card_temp = players[first_player_index]['roundCard']
        if round_first_card_temp != "":
            round_first_card = Card(round_first_card_temp)
            roundCardColor = round_first_card.suit

        roundCardMaxNum = 0 #card max num (suit same with the first)
        for player in players:
            if player['roundCard'] != "":
                if Card(player['roundCard']).suit != roundCardColor:
                    pass
                else:
                    if Card(player['roundCard']).value > roundCardMaxNum:
                        roundCardMaxNum = Card(player['roundCard']).value
        
        #if no suit card
        NoSuit = True
        for it in cadidate_cards:
            if it[1] == roundCardColor:
                NoSuit = False

        returnCard = cadidate_cards[card_index]
        if roundCardMaxNum == 0: # I am the first hand
            returnCard = cadidate_cards[card_index]
        elif roundCardMaxNum != 0: # I am not the first hand
            #handle NoSuit
            if NoSuit == True:
                returnCard = cadidate_cards[len(cadidate_cards)-1]
            #handle heart
            if roundCardColor != "H" and NoSuit == True:
                for it in sorted(cadidate_cards, reverse=True):
                    if Card(it).suit == "H":
                        returnCard = it
                        break
            #handle QS
            if roundCardColor != "S" and NoSuit == True:
                for it in sorted(cadidate_cards, reverse=True):
                    if it == "QS":
                        returnCard = "QS"
                        break
            elif roundCardColor == "S" and (roundCardMaxNum == 14 or roundCardMaxNum == 13):
                for it in sorted(cadidate_cards, reverse=True):
                    if it == "QS":
                        returnCard = "QS"
                        break

            

        return returnCard

    def expose_my_cards(self,yourcards):
        expose_card=[]
        for card in self.my_hand_cards:
            if card==Card("AH"):
                expose_card.append(card.toString())
        message = "Expose Cards:{}".format(expose_card)
        return expose_card

    def expose_cards_end(self,data):
        players = data['players']
        expose_player=None
        expose_card=None
        for player in players:
            try:
                if player['exposedCards']!=[] and len(player['exposedCards'])>0 and player['exposedCards']!=None:
                    expose_player=player['playerName']
                    expose_card=player['exposedCards']
            except Exception as e:
                raise e
        if expose_player!=None and expose_card!=None:
            message="Player:{}, Expose card:{}".format(expose_player,expose_card)
            self.expose_card=True
        else:
            message="No player expose card!"
            self.expose_card=False

    def receive_opponent_cards(self,data):
        self.my_hand_cards = self.get_cards(data)
        players = data['players']
        for player in players:
            player_name = player['playerName']
            if player_name == self.player_name:
                picked_cards = player['pickedCards']
                receive_cards = player['receivedCards']
                message = "User Name:{}, Picked Cards:{}, Receive Cards:{}".format(player_name, picked_cards,receive_cards)

    def deal_end(self,data):
        pass

    def game_over(self,data):
        game_scores = self.get_game_scores(data)
        for key in game_scores.keys():
            message = "Player name:{}, Game score:{}".format(key, game_scores.get(key))

    def pick_history(self,data,is_timeout,pick_his):
        for key in pick_his.keys():
            message = "Player name:{}, Pick card:{}, Is timeout:{}".format(key,pick_his.get(key),is_timeout)


