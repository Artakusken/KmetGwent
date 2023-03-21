from CONSTANTS import *
import random
import sqlite3


def chk_conn(con):
    try:
        con.cursor()
        return True
    except Exception:
        return False


class Hand:
    """
    A class which represent container of cards usable for player. These cards are seen only for player and their points don't affect on score.
    Player picks card from hand and then play it.
    """

    def __init__(self):
        self.cards = []
        self.round = 0
        self.str_type = "Hand"

    def draw_cards(self, deck):
        """ Add up to 4 cards to hand"""
        a = len(self.cards)
        c = 4
        while len(self.cards) != 10 and c > 0:
            card = deck.cards.pop()
            card.hand_position = a
            card.location = self
            a += 1
            c -= 1
            self.cards.append(card)

    def play_card(self, chosen_card):
        """ Move card away from the hand and update cards positions"""
        self.cards.pop(chosen_card.hand_position)
        if len(self.cards) > 1:
            for i in self.cards[chosen_card.hand_position::]:
                i.hand_position -= 1

    def start_hand(self, deck):
        """take 10 cards from the deck to hand"""
        for i in range(10):
            card = deck.cards.pop()
            card.location = self
            card.hand_position = i
            self.cards.append(card)

    def pop_card(self, index):
        """ Delete card from hand by index"""
        if len(self.cards) > 0:
            self.cards.pop(index)

    def up_when_hovered(self, coord):
        """ Up hand cards when they are hovered"""
        for i in self.cards:
            if i.rect[0] < coord[0] < i.rect[0] + i.rect[2] and i.rect[1] < coord[1] < i.rect[1] + i.rect[3] + 5:
                i.hover = True
            else:
                i.hover = False

    def refresh(self):
        """ Assign initial values to variables"""
        self.cards = []
        self.round = 0

    def make_move(self, field):
        """ Make hand be ready for a new play"""
        for i in self.cards:
            i.status = 'passive'
        if self.round < field.round:
            self.draw_cards(field.pl_deck)
            self.round += 1


class Deck:
    """
    A class which represent container of cards unusable for player (but callable). It's main storage for all cards.
    These cards are seen only for a player, their points don't affect on score and player don't know their order.
    """

    def __init__(self, name, cards):
        self.cards = self.set_cards(cards)
        self.name = name
        if len(self.cards) > 1:
            if self.name == "Мужик * на 30":
                self.rect = (1630, 935, 105, 150)
            else:
                self.rect = (1630, 15, 105, 150)

    def set_cards(self, cards):
        """ Shuffle cards and set their deck as location"""
        random.shuffle(cards)
        if len(cards) > 1:
            for i in cards:
                i.location = self
        return cards

    def draw_card(self, hand):
        """ Take card from the deck"""
        if len(hand) < 10:
            card = self.cards.pop()
            hand.cards.append(card)

    def pop_card(self, chosen_card, dump):
        """ Move card from deck to dump (undone)"""
        index = chosen_card
        dump.cards.append(self.cards.pop(index))

    def update_name(self, new_name):
        """ Set a new name for the deck"""
        con = sqlite3.connect("Decks.db")
        if chk_conn(con):
            cur = con.cursor()
            cur.execute('''UPDATE Decks
                                   SET Name = ?
                                   WHERE Name = ? ''', (new_name, self.name))
            con.commit()
            self.name = new_name
            con.close()


class Dump:
    """
    A class which represent container of cards unusable for player (but callable). It's last storage for all cards.
    These cards are seen for both players, their points don't affect on score and players know their order.
    """

    def __init__(self, name):
        self.cards = []
        self.name = name
        if self.name == "Сброс игрока":
            self.rect = (1765, 935, 105, 150)
        else:
            self.rect = (1765, 15, 105, 150)

    def get_card(self, name):
        """Return card from dump, if card with such name exist (undone, maybe instead of name should be index or object itself)"""
        for i in range(len(self.cards)):
            if self.cards[i].name == name:
                self.cards.pop(i)
                return i

    def refresh(self, s):
        """ Clear self from all cards and add self to clickable objects"""
        self.cards = []
        s.append(self)
