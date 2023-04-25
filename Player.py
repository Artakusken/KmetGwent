from socket import gethostname, gethostbyname
from Data import global_init, create_session, Decks, create_deck, create_card
from requests import get, post, delete


class Player:
    def __init__(self, server):
        self.deck = None
        self.fraction = None
        self.ip = gethostbyname(gethostname())
        self.decks = None
        self.server = server
        self.playing = False
        self.ready_to_play = False

    def decks_base_session(self):
        global_init("decks")
        return create_session()

    def authorize(self, email, password, cid=""):
        if len(cid) > 0:
            email = password = -1
            data = get(f"http://{self.server}/api/v2/player/{email}&{password}&{cid}&in_cid").json()
        elif cid == "":
            data = get(f"http://{self.server}/api/v2/player/{email}&{password}&-1&in_email").json()
        if isinstance(data, list):
            self.id, self.nickname = data[0], data[1]
            self.email, self.password = email, password
            with open("player_data.txt", "w") as player_data_file:
                # print(data[0], end=";", file=player_data_file)
                # print(data[1], end=";", file=player_data_file)
                print(data[2], end="", file=player_data_file)
            return 1
        else:
            return data

    def import_decks(self):
        decks = dict()
        session = self.decks_base_session()
        for deck in session.query(Decks).all():
            real_cards = get(f'http://{self.server}/api/v2/my_deck/{deck.cards}').json()
            real_deck = create_deck(real_cards, deck)
            decks[deck.name] = real_deck
            if deck.last_chosen:
                self.deck = real_deck
        self.decks = decks

    def import_cards(self):
        data = get(f'http://{self.server}/api/v2/my_deck/constructor').json()
        cards = {"Нет карты": None}
        for asd in data:
            cards[asd] = create_card(data[asd])
        return cards

    def new_last_chosen_deck(self):
        session = self.decks_base_session()
        chosen_deck = session.query(Decks).get(self.deck.id)
        for deck in session.query(Decks).all():
            deck.last_chosen = 0
        chosen_deck.last_chosen = 1
        session.commit()

    def exit(self):
        get(f"http://{self.server}/api/v2/player/{self.email}&{self.password}&out")
        self.new_last_chosen_deck()
