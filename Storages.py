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
    def __init__(self):
        self.cards = []

    def draw_cards(self, deck):
        a = len(self.cards)
        while len(self.cards) != 10:
            card = deck.cards.pop()
            card.hand_position = a
            a += 1
            self.cards.append(card)

    def play_card(self, chosen_card, dump):
        pass

    def start_hand(self, deck):
        for i in range(10):
            card = deck.cards.pop()
            card.location = self
            card.hand_position = i
            self.cards.append(card)

    def pop_card(self, index):
        if len(self.cards) > 0:
            self.cards.pop(index)

    def up_when_hovered(self, coord):
        for i in self.cards:
            if i.rect[0] < coord[0] < i.rect[0] + i.rect[2] and i.rect[1] < coord[1] < i.rect[1] + i.rect[3]:
                i.hover = True
            else:
                i.hover = False


class Deck:
    def __init__(self, name, cards):
        self.cards = self.set_cards(cards)
        self.name = name
        if len(self.cards) > 1:
            CLICKABLE.append(self)
            if self.name == "Мужик * на 30":
                self.rect = (1630, 935, 105, 150)
            else:
                self.rect = (1630, 15, 105, 150)

    def set_cards(self, cards):
        random.shuffle(cards)
        if len(cards) > 1:
            for i in cards:
                i.location = self
        return cards

    def draw_card(self, hand):
        if len(hand) < 10:
            card = self.cards.pop()
            hand.cards.append(card)

    def pop_card(self, chosen_card, dump):
        index = chosen_card
        dump.cards.append(self.cards.pop(index))

    def update_name(self, new_name):
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
    def __init__(self, name):
        self.cards = []
        self.name = name
        if self.name == "Сброс игрока":
            self.rect = (1765, 935, 105, 150)
        else:
            self.rect = (1765, 15, 105, 150)
        CLICKABLE.append(self)

    def get_card(self, name):
        for i in range(len(self.cards)):
            if self.cards[i].name == name:
                self.cards.pop(i)
                return i
