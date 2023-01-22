from CONSTANTS import *
import random
import sqlite3


def chk_conn(con):  # проверка на соединение для этого класса
    try:
        con.cursor()
        return True
    except Exception:
        return False


class Hand:
    def __init__(self):
        self.cards = []

    def draw_cards(self, deck):
        while self.cards != 10:
            card = deck.cards.pop()
            self.cards.append(card)

    def play_card(self, chosen_card, dump):
        index = chosen_card
        dump.cards.append(self.cards.pop(index))

    def start_hand(self, deck):
        for i in range(10):
            card = deck.cards.pop()
            card.status = "in hand"
            self.cards.append(card)


class Deck:
    def __init__(self, name, cards):
        self.cards = self.set_cards(cards)
        CLICKABLE.append(self)
        self.rect = (1630, 935, 105, 150)
        self.name = name

    def set_cards(self, cards):
        random.shuffle(cards)
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
    def __init__(self):
        self.cards = []
        self.rect = (1765, 935, 105, 150)
        CLICKABLE.append(self)

    def get_card(self, name):
        for i in range(len(self.cards)):
            if self.cards[i].name == name:
                self.cards.pop(i)
                return i
