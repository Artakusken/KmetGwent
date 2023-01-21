from CONSTANTS import *
import random


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
    def __init__(self):
        self.cards = []
        CLICKABLE.append(self)
        self.rect = (1630, 935, 105, 150)
        self.name = ""

    # def set_hand(self, hand):
    #     self.hand = hand

    def set_cards(self, cards):
        random.shuffle(cards)
        self.cards = cards

    def draw_card(self, hand):
        if len(hand) < 10:
            card = self.cards.pop()
            hand.cards.append(card)

    def pop_card(self, chosen_card, dump):
        index = chosen_card
        dump.cards.append(self.cards.pop(index))


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
