from Cards import Card
from Storages import Deck
import sqlite3


def chk_conn(connection):
    try:
        connection.cursor()
        return True
    except Exception:
        return False

CARDS_LIST = {"Нет карты": None}
CARDS_LIST['Clan Tuirseach Veteran'] = Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support")

DECKS_LIST = dict()
con = sqlite3.connect("Decks.db")
if chk_conn(con):
    cur = con.cursor()
    decks = cur.execute("""SELECT * FROM Decks""").fetchall()
    for deck in decks:
        if deck[2]:
            cards = []
            for i in deck[2].split(";"):
                name = CARDS_LIST[i].name
                base_power = CARDS_LIST[i].bp
                armor = CARDS_LIST[i].armor
                provision = CARDS_LIST[i].provision
                image = CARDS_LIST[i].image_path
                tags = CARDS_LIST[i].tags
                card_type = CARDS_LIST[i].card_type
                fraction = CARDS_LIST[i].fraction
                cards.append(Card(name, base_power, image, armor, provision, card_type, fraction, tags))
            DECKS_LIST[deck[1]] = Deck(deck[1], cards)
        else:
            DECKS_LIST[deck[1]] = Deck(deck[1], deck[2].split(";"))


