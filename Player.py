from socket import gethostname, gethostbyname
from Data import global_init, create_session, Decks, create_deck, create_card
from requests import get, post, delete, put


class Player:
    def __init__(self, server):
        self.deck = None
        self.fraction = None
        self.id = None
        self.nickname = None
        self.email = None
        self.password = None
        self.cid = None
        self.ip = gethostbyname(gethostname())
        self.decks = None
        self.server = server
        self.playing = False
        self.ready_to_play = False

    def decks_base_session(self):
        global_init("decks")
        return create_session()

    def authorize(self, email, password, cid=""):
        if cid:
            data = get(f"http://{self.server}/api/v2/player/-1&-1&{cid}&in_cid&1").json()
        else:
            data = get(f"http://{self.server}/api/v2/player/{email}&{password}&-1&in_email&1").json()
        if isinstance(data, list):
            self.id, self.nickname = data[0], data[1]
            self.email, self.password, self.cid = email, password, cid
            with open("player_data.txt", "w") as player_data_file:
                # print(data[0], end=";", file=player_data_file)
                # print(data[1], end=";", file=player_data_file)
                print(data[2], end="", file=player_data_file)
            return 1
        else:
            return data

    def import_decks(self):
        decks = {}
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

    def find_opponents(self, stop):
        self.ready_to_play = True
        if not stop:
            put(f"http://{self.server}/api/v2/player/-1&-1&{self.cid}&in_cid&find_opponents")
        else:
            put(f"http://{self.server}/api/v2/player/-1&-1&{self.cid}&in_cid&stop_find_opponents")

    def start_the_game(self):
        self.playing = True
        self.ready_to_play = False
        put(f"http://{self.server}/api/v2/player/-1&-1&{self.cid}&in_cid&start_the_game")

    def ensure_connection(self):
        get(f'http://{self.server}/session/{self.id}')

    def end_the_game(self):
        self.playing = False
        put(f"http://{self.server}/api/v2/player/-1&-1&{self.cid}&in_cid&end_the_game")

    def exit(self):
        get(f"http://{self.server}/api/v2/player/-1&-1&{self.cid}&out&1")
        self.new_last_chosen_deck()
