# -*- coding: utf-8 -*-
# kenmin_lin@trendmicro.com

import random

# print rule validation messages
B_MESSAGE = False
# print pretty suit
B_PRETTY = True
# how many games to play
GAMES_TO_PLAY = 1

class Suit:
    def __init__(self, suit):
        # suit input can be str (c, d, s, h)
        self.s_table = ["c", "d", "s", "h"]
        if suit not in self.s_table:
            self.string = "?"
            self.value = -1
        else:
            self.string = suit
            self.value = self.s_table.index(suit)

    def __str__(self):
        return self.string

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return not (self < other)

    def __le__(self, other):
        return not (self > other)


class Rank:
    def __init__(self, rank):
        # rank input can be int (2~14) or str (TJQKA)
        if rank == "T":
            self.value = 10
        elif rank == "J":
            self.value = 11
        elif rank == "Q":
            self.value = 12
        elif rank == "K":
            self.value = 13
        elif rank == "A":
            self.value = 14
        else:
            self.value = int(rank)

        if self.value < 10:
            self.string = str(self.value)
        elif self.value >= 10:
            self.string = ["T", "J", "Q", "K", "A"][self.value - 10]

    def __str__(self):
        return self.string

    def __lt__(self, other):
        return self.value < other.value

    def __ge__(self, other):
        return not (self < other)

    def __gt__(self, other):
        return self.value > other.value

    def __le__(self, other):
        return not (self > other)

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not (self == other)


class Card:
    def __init__(self, rank, suit):
        self.rank = Rank(rank)
        self.suit = Suit(suit)

    def rank(self):
        return self.rank

    def suit(self):
        return self.suit

    def __str__(self):
        return self.rank.__str__() + self.suit.__str__()

    def __lt__(self, other):
        return (self.rank < other.rank or (self.rank == other.rank and self.suit < other.suit))

    def __ge__(self, other):
        return not (self < other)

    def __gt__(self, other):
        return (self.rank > other.rank or (self.rank == other.rank and self.suit > other.suit))

    def __le__(self, other):
        return not (self > other)

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __ne__(self, other):
        return not (self == other)


class Deck:
    def __init__(self):
        self.reset()

    def reset(self):
        self.deck = []
        for suit in ["c", "d", "s", "h"]:
            for rank in range(2, 15):
                self.deck.append(Card(rank, suit))
        random.shuffle(self.deck)

    def deal(self):
        return self.deck.pop(0)


class Hand:
    def __init__(self):
        self.reset()

    def reset(self):
        self.played = []
        self.clubs = []
        self.diamonds = []
        self.spades = []
        self.hearts = []
        # create hand of cards split up by suit
        self.hand = [self.clubs, self.diamonds, self.spades, self.hearts]

    def size(self):
        return len(self.clubs + self.diamonds + self.spades + self.hearts)

    def hasCard(self, card):
        b_ret = False
        for c in self.clubs + self.diamonds + self.spades + self.hearts:
            if c == card:
                b_ret = True
        return b_ret

    def addCard(self, card):
        if card.suit == Suit("c"):
            self.clubs.append(card)
        elif card.suit == Suit("d"):
            self.diamonds.append(card)
        elif card.suit == Suit("s"):
            self.spades.append(card)
        elif card.suit == Suit("h"):
            self.hearts.append(card)
        else:
            print 'Invalid card'

        if self.size() == 13:
            for suit in self.hand:
                suit.sort()

    def getRandomCard(self):
        cards = self.clubs + self.diamonds + self.spades + self.hearts
        index = random.randint(0, len(cards)-1)
        return cards[index]

    def removeCard(self, card, b_pass=False):
        s = card.suit.value
        for c in self.hand[s]:
            if c == card:
                self.hand[card.suit.value].remove(c)
                if not b_pass:
                    # add cards into played
                    self.played.append(c)

    def hasOnlyHearts(self):
        return len(self.hearts) == self.size()

    def __str__(self):
        handStr = ''
        if len(self.played) > 0:
            for card in self.played:
                handStr += card.__str__() + ' '
            handStr += '| '
        for suit in self.hand:
            for card in suit:
                handStr += card.__str__() + ' '
        return handStr


class Trick:
    def __init__(self):
        self.reset()

    def reset(self):
        self.trick = [0, 0, 0, 0]
        self.suit = Suit("?")
        self.cardsInTrick = 0
        # rank of the high trump suit card in the trick
        self.highest = 0
        self.winner = -1

    def addCard(self, card, index):
        # if this is the first card added, set the trick suit
        if self.cardsInTrick == 0:
            self.suit = card.suit

        self.trick[index] = card
        self.cardsInTrick += 1

        if card.suit == self.suit:
            if card.rank.value > self.highest:
                self.highest = card.rank.value
                self.winner = index


class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.hand = Hand()
        self.cardsWon = Hand()

    def addCard(self, card):
        self.hand.addCard(card)

    def play(self, c=None):
        if c is not None:
            # play a specific card
            card = Card(c[0], c[1])
        else:
            # implement AI here
            card = self.hand.getRandomCard()
        return card

    def addTrick(self, trick):
        for card in trick.trick:
            if card.suit == Suit("h") or card == Card("Q", "s"):
                self.cardsWon.addCard(card)

    def countPoints(self):
        points = 0
        for card in self.cardsWon.spades+self.cardsWon.hearts:
            if card.suit == Suit("h"):
                points += 1
            else:
                points += 13
        return points

    def hasSuit(self, suit):
        return len(self.hand.hand[suit.value]) > 0

    def removeCard(self, card, b_pass=False):
        self.hand.removeCard(card, b_pass)

    def hasOnlyHearts(self):
        return self.hand.hasOnlyHearts()

    def resetCards(self):
        self.hand.reset()
        self.cardsWon.reset()

    def resetScore(self):
        self.score = 0


class Hearts:
    def __init__(self):
        self.totalTricks = 13
        self.maxScore = 100
        self.cardsToPass = 3
        self.passes = [1, -1, 2, 0]  # left, right, across, no pass
        self.trick = Trick()
        # make four players
        self.players = [Player("A"), Player("B"), Player("C"), Player("D")]
        self.p_len = len(self.players)

    def game(self):
        self.b_end = False
        self.roundNum = -1
        for p in self.players:
            p.resetScore()
        while not self.b_end:
            for p in self.players:
                p.resetCards()
            self.trick.reset()
            self.roundNum += 1
            self.heartsBroken = False
            self.passingCards = [[], [], [], []]

            # deal
            self.deck = Deck()
            for i in range(self.p_len):
                for j in range(self.totalTricks):
                    self.players[i].addCard(self.deck.deal())

            print "======================"
            print "=== Round {} Start ===".format(self.roundNum+1)
            print "======================"

            for i in range(self.totalTricks):
                if i == 0:
                    self.passCards()
                print "[Trick #{}]".format(i+1)
                self.playTrick(i, self.trickWinner)
            self.scoring()
        print "Winner: {}".format(self.winner())

    def passCards(self):
        # don't pass every fourth round
        if not self.roundNum % 4 == 3:
            # print before pass cards
            print "[BeforePass]"
            self.printPlayers()

            # select pass cards
            for i in range(self.p_len):
                # the index to which cards are passed
                passTo = (i + self.passes[self.roundNum % self.p_len]) % self.p_len
                # pick 3 cards to pass
                for j in range(self.cardsToPass):
                    passCard = self.players[i].play()
                    self.passingCards[passTo].append(passCard)
                    self.players[i].removeCard(passCard, b_pass=True)

            # print passed cards
            print "[GetPass]"
            for i, passed in enumerate(self.passingCards):
                o = []
                for card in passed:
                    o.append(card.__str__())
                print self.players[i].name + ": " + self.pretty_suit(" ".join(o))

            # do pass cards
            for i, passed in enumerate(self.passingCards):
                for card in passed:
                    self.players[i].addCard(card)

            # print after pass cards
            print "[AfterPass]"
            self.printPlayers()

        # find the player who owns 2c
        for i, p in enumerate(self.players):
            if p.hand.hasCard(Card(2, "c")):
                self.trickWinner = i

    def playTrick(self, trickNum, start):
        # force to play 2c at the beginning
        shift = 0
        if trickNum == 0:
            startPlayer = self.players[start]
            addCard = startPlayer.play('2c')
            startPlayer.removeCard(addCard)
            self.trick.addCard(addCard, start)
            self.printPlayer(start)
            shift = 1

        # have each player take their turn
        for i in range(start + shift, start + self.p_len):
            curPlayerIndex = i % self.p_len
            curPlayer = self.players[curPlayerIndex]
            addCard = None
            while addCard is None:
                addCard = curPlayer.play()
                # rule validation
                msg = ""
                if trickNum == 0:
                    # the first trick, not the first card in the trick
                    if addCard.suit != self.trick.suit:
                        # not follow the suit
                        if curPlayer.hasSuit(self.trick.suit):
                            # still have the suit
                            msg = self.pretty_suit(str(addCard)) + ", Must follow the suit."
                            addCard = None
                        elif addCard.suit == Suit("h"):
                            # have no the suit and play hearts
                            msg = self.pretty_suit(str(addCard)) + ", cannot play penalty cards in the first trick."
                            addCard = None
                        elif addCard == Card("Q", "s"):
                            # have no the suit and play spade-queen
                            msg = self.pretty_suit(str(addCard)) + ", cannot play penalty cards in the first trick."
                            addCard = None
                elif self.trick.cardsInTrick == 0:
                    # not the first trick, the first card in the trick
                    if addCard.suit == Suit("h") and not self.heartsBroken:
                        # play heart but not heart-broken yet
                        if curPlayer.hasOnlyHearts():
                            # only have hearts, hearts-broken
                            self.heartsBroken = True
                            print self.pretty_suit(str(addCard)) + ", Hearts-broken."
                        else:
                            # not only have hearts
                            msg = self.pretty_suit(str(addCard)) + ", Hearts have not been broken."
                            addCard = None
                else:
                    # not the first trick, not the first card in the trick
                    if addCard.suit != self.trick.suit:
                        # not follow the suit
                        if curPlayer.hasSuit(self.trick.suit):
                            # still have the suit
                            msg = self.pretty_suit(str(addCard)) + ", Must follow the suit."
                            addCard = None
                        elif addCard.suit == Suit("h") and not self.heartsBroken:
                            # have no the suit and play hearts, hearts-broken
                            print self.pretty_suit(str(addCard)) + ", Hearts-broken."
                            self.heartsBroken = True

                if B_MESSAGE and msg != "":
                    print msg

            curPlayer.removeCard(addCard)
            self.trick.addCard(addCard, curPlayerIndex)
            self.printPlayer(curPlayerIndex)

        # evaluate this trick
        self.trickWinner = self.trick.winner
        p = self.players[self.trickWinner]
        p.addTrick(self.trick)
        # next trick
        self.trick.reset()

    def scoring(self):
        self.printPlayersCardsWon()
        b_moon = False
        for player in self.players:
            pts = player.countPoints()
            if pts < 26:
                player.score += pts
            else:
                player.score -= pts
                b_moon = True
        if b_moon:
            print "[ShootingTheMoon]"
            for player in self.players:
                player.score += 26
        msg = []
        for player in self.players:
            msg.append("{}: {}".format(player.name, str(player.score)))
            if player.score >= self.maxScore:
                self.b_end = True
        print "[Scores]"
        print ", ".join(msg)

    def winner(self):
        s = []
        for p in self.players:
            s.append(p.score)
        m = min(s)
        winner = []
        for p in self.players:
            if p.score == m:
                winner.append(p.name)
        return winner

    def printPlayer(self, index):
        p = self.players[index]
        print p.name + ": " + self.pretty_suit(str(p.hand))

    def printPlayers(self):
        for p in self.players:
            print p.name + ": " + self.pretty_suit(str(p.hand))

    def printPlayersCardsWon(self):
        print "[CardsWon]"
        for p in self.players:
            p.cardsWon.spades.sort()
            p.cardsWon.hearts.sort()
            print p.name + ": " + self.pretty_suit(str(p.cardsWon))

    def pretty_suit(self, s):
        if B_PRETTY:
            try:
                from termcolor import colored
                poker_character = {'c': u'♣', 'd': colored(u'♦', "red"), 'h': colored(u'♥', "red"), 's': u'♠'}
            except ImportError:
                poker_character = {'c': u'♣', 'd': u'♦', 'h': u'♥', 's': u'♠'}
            for i in poker_character:
                s = s.replace(i, poker_character[i])
        return s

if __name__ == '__main__':
    h = Hearts()
    for i in range(GAMES_TO_PLAY):
        h.game()
