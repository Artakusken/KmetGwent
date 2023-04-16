import sqlite3
from socket import gethostname, gethostbyname
from Data import CARDS_LIST


class Player:
    def __init__(self):
        self.deck = None
        self.fraction = None
        self.local_base = self.connect_local_base("Decks.db")
        self.ip = gethostbyname(gethostname())
        if self.local_base:
            self.decks = self.import_decks()
        else:
            pass

    def connect_local_base(self, base):
        con = sqlite3.connect(base)
        if con:
            return con
        else:
            return False

    def import_decks(self):
        from Storages import Deck
        from Data import game_deck
        cursor = self.local_base.cursor()
        decks_data = cursor.execute("""SELECT * FROM Decks""").fetchall()
        decks = dict()
        for deck in decks_data:
            if deck[2]:
                cards = []
                for i in deck[2].split(";"):
                    card = CARDS_LIST[i].copy()
                    cards.append(card)
                decks[deck[1]] = Deck(deck[1], "Me", cards)
                if deck[3] == 1:
                    self.deck = decks[deck[1]]
            else:
                decks[deck[1]] = Deck(deck[1], "Me", deck[2].split(";"))
        decks["new"] = game_deck
        return decks

    def new_last_chosen_deck(self):
        cursor = self.local_base.cursor()

        cursor.execute("""  UPDATE Decks
                            SET chosen = 0
                            WHERE chosen = 1 """)

        cursor.execute("""  UPDATE Decks
                            SET chosen = 1 
                            WHERE name = ? """, (self.deck.name,))
        self.local_base.commit()

    def exit(self):
        self.new_last_chosen_deck()
        self.local_base.close()
