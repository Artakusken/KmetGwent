from Cards import Card, Warrior
from Storages import Deck
import sqlite3


def chk_conn(con):  # проверка на соединение для этого класса
    try:
        con.cursor()
        return True
    except Exception:
        return False

cards_list = {"Нет карты": None}
cards_list[Warrior.name] = Warrior

decks_list = dict()
con = sqlite3.connect("Decks.db")
if chk_conn(con):
    cur = con.cursor()
    decks = cur.execute("""SELECT * FROM Decks""").fetchall()
    for deck in decks:
        if deck[2]:
            decks_list[deck[1]] = Deck(deck[1], [cards_list[i] for i in deck[2].split(";")])
        else:
            decks_list[deck[1]] = Deck(deck[1], deck[2].split(";"))


