from Cards import Card
from Storages import Deck
import sqlite3


def chk_conn(con):  # проверка на соединение для этого класса
    try:
        con.cursor()
        return True
    except Exception:
        return False

cards_list = {"Нет карты": None}
cards_list['Clan Tuirseach Veteran'] = Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support")

decks_list = dict()
con = sqlite3.connect("Decks.db")
if chk_conn(con):
    cur = con.cursor()
    decks = cur.execute("""SELECT * FROM Decks""").fetchall()
    for deck in decks:
        if deck[2]:
            cards = []
            for i in deck[2].split(";"):
                name = cards_list[i].name
                base_power = cards_list[i].bp
                armor = cards_list[i].armor
                provision = cards_list[i].provision
                image = cards_list[i].image_path
                tags = cards_list[i].tags
                card_type = cards_list[i].card_type
                fraction = cards_list[i].fraction
                cards.append(Card(name, base_power, image, armor, provision, card_type, fraction, tags))
            decks_list[deck[1]] = Deck(deck[1], cards)
        else:
            decks_list[deck[1]] = Deck(deck[1], deck[2].split(";"))


