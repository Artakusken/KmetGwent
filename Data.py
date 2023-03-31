from Cards import Card
from Storages import Deck
import sqlite3


def chk_conn(connection):
    try:
        connection.cursor()
        return True
    except Exception:
        return False


def cant_stand_brothers(card, field, row):
    """Clan Tuirseach Veteran: "Размещение. Нанесите себе 1 ед. урона за каждую такую же карту в ряду"""
    c = -1
    for i in row.cards:
        if i.name == card.name:
            c += 1
    card.power -= c


CARDS_LIST = {"Нет карты": None}
CARDS_LIST['Clan Tuirseach Veteran'] = Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support")
METHOD_LIST = {'Clan Tuirseach Veteran deploy': cant_stand_brothers}

DECKS_LIST = dict()

con = sqlite3.connect("Decks.db")
if chk_conn(con):
    cur = con.cursor()
    decks = cur.execute("""SELECT * FROM Decks""").fetchall()
    for deck in decks:
        if deck[2]:
            cards = []
            for i in deck[2].split(";"):
                card = CARDS_LIST[i].copy()
                cards.append(card)
            DECKS_LIST[deck[1]] = Deck(deck[1], "me", cards)
        else:
            DECKS_LIST[deck[1]] = Deck(deck[1], "me", deck[2].split(";"))
