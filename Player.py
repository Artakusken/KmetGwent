from socket import gethostname, gethostbyname
from Data import global_init, create_session, Decks, create_deck, create_card
from requests import get, post, delete


class Player:
    def __init__(self):
        self.deck = None
        self.fraction = None
        self.ip = gethostbyname(gethostname())
        self.decks = None
        self.import_decks()
        self.import_cards()

    def decks_base_session(self):
        global_init("decks")
        return create_session()

    def authorize(self):
        post("http://kmetgwent.ddns.net/authorization")

    def import_decks(self):
        decks = dict()
        session = self.decks_base_session()
        for deck in session.query(Decks).all():
            real_cards = get(f'http://kmetgwent.ddns.net/api/v2/my_deck/{deck.cards}').json()
            real_deck = create_deck(real_cards, deck)
            decks[deck.name] = real_deck
            if deck.last_chosen:
                self.deck = real_deck
        self.decks = decks

    def import_cards(self):
        # global CARDS_LIST
        data = get('http://kmetgwent.ddns.net/api/v2/my_deck/constructor/').json()
        cards = {"Нет карты": None}
        for asd in data:
            cards[asd] = create_card(data[asd])
        print(cards)
        return cards

    # def import_decks(self):
    #     from Data import get_decks
    #     decks = dict()
    #     session = self.decks_base_session()
    #     for deck in get_decks(self):
    #         if deck.last_chosen:
    #             self.deck = deck
    #         decks[deck.name] = deck
    #     session.commit()
    #     self.decks = decks

    def new_last_chosen_deck(self):
        session = self.decks_base_session()
        chosen_deck = session.query(Decks).get(self.deck.id)
        for deck in session.query(Decks).all():
            deck.last_chosen = 0
        chosen_deck.last_chosen = 1
        session.commit()

    def exit(self):
        self.new_last_chosen_deck()
