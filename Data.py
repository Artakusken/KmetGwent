from Cards import Card
from Storages import Deck
from Cards_Abilities import METHODS

import sqlalchemy
import sqlalchemy_serializer
import sqlalchemy.orm as orm


def cant_stand_brothers(card, field, row):
    """Clan Tuirseach Veteran: "Размещение. Нанесите себе 1 ед. урона за каждую такую же карту в ряду"""
    c = -1
    for i in row.cards:
        if i.name == card.name:
            c += 1
    card.power -= c


def healing_armor(card, field, row):
    healing_points = card.armor
    card.power += healing_points
    card.armor = 0


def recruit(card, field, row):
    if card.turns_on_field >= 4:
        card.power += 4


base_engines = {"cards": sqlalchemy.create_engine('sqlite:///NC.db?check_same_thread=False'),
                "decks": sqlalchemy.create_engine('sqlite:///ND.db?check_same_thread=False')}


CardsBase = orm.declarative_base()
DecksBase = orm.declarative_base()
__factory = None


class CardsParams(CardsBase, sqlalchemy_serializer.SerializerMixin):
    __tablename__ = "Cards"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    bp = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    armor = sqlalchemy.Column(sqlalchemy.Integer)
    provision = sqlalchemy.Column(sqlalchemy.Integer)
    card_type = sqlalchemy.Column(sqlalchemy.Integer)
    fraction = sqlalchemy.Column(sqlalchemy.String)
    tags = sqlalchemy.Column(sqlalchemy.String)
    deployment = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))
    order = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))
    turn_end = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))
    conditional = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))

    def __init__(self, name, bp, armor, provision, card_type, fraction, deployment, order, turn_end, conditional, *tags):
        self.name = name
        self.bp = bp
        self.armor = armor
        self.provision = provision
        self.card_type = card_type
        self.fraction = fraction
        self.tags = ";".join([i for i in tags])
        self.deployment = deployment
        self.order = order
        self.turn_end = turn_end
        self.conditional = conditional


class Methods(CardsBase, sqlalchemy_serializer.SerializerMixin):
    __tablename__ = "Methods"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    def __init__(self, def_name, type):
        self.name = def_name
        self.type = type


class MethodsType(CardsBase, sqlalchemy_serializer.SerializerMixin):
    __tablename__ = "Methods_types"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String)


class Decks(DecksBase, sqlalchemy_serializer.SerializerMixin):
    __tablename__ = "Decks"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    cards = sqlalchemy.Column(sqlalchemy.String)
    last_chosen = sqlalchemy.Column(sqlalchemy.Integer)

    def __init__(self, name, cards):
        self.name = name
        self.cards = cards
        self.last_chosen = 0


def create_bases():
    CardsBase.metadata.create_all(base_engines["cards"])
    DecksBase.metadata.create_all(base_engines["decks"])


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    engine = base_engines[db_file]
    # __factory = orm.sessionmaker(bind=engine)
    __factory = orm.sessionmaker(binds={CardsBase: base_engines["cards"], DecksBase: base_engines["decks"]})

    create_bases()


def create_session() -> orm.Session:
    global __factory
    return __factory()


def choose_deck(name):
    global_init("decks")
    session = create_session()
    if session.query(Decks).filter(name == Decks.name).first():
        deck = session.query(Decks).filter(name == Decks.name).first().cards
        session.commit()
        return [int(card_id) for card_id in deck.split(";")]

def get_decks(player):
    global_init("cards")
    global_init("decks")
    session = create_session()
    all_deca = []
    for decks_name in session.query(Decks).all():
        deca = []
        for card_id in choose_deck(decks_name.name):
            params = session.query(CardsParams).filter(CardsParams.id == card_id).first()
            name = params.name
            bp = params.bp
            armor = params.armor
            provision = params.provision
            card_type = params.card_type
            fraction = params.fraction
            tags = params.tags.split(";")
            if session.query(Methods).filter(Methods.id == params.deployment).first():
                deployment = METHODS[session.query(Methods).filter(Methods.id == params.deployment).first().name]
            else:
                deployment = None
            if session.query(Methods).filter(Methods.id == params.order).first():
                order = METHODS[session.query(Methods).filter(Methods.id == params.order).first().name]
            else:
                order = None
            if session.query(Methods).filter(Methods.id == params.turn_end).first():
                turn_end = METHODS[session.query(Methods).filter(Methods.id == params.turn_end).first().name]
            else:
                turn_end = None
            if session.query(Methods).filter(Methods.id == params.conditional).first():
                conditional = METHODS[session.query(Methods).filter(Methods.id == params.conditional).first().name]
            else:
                conditional = None

            deca.append(
                Card(name, bp, name + ".png", armor, provision, card_type, fraction, tags, deployment, order, turn_end, conditional))
        all_deca.append(Deck(decks_name.name, "Me", deca, decks_name.last_chosen, decks_name.id))
    session.commit()
    return all_deca


def create_deck(deck_cards, deck):
    deca = []
    for params in deck_cards:
        name = params[0]
        bp = params[1]
        armor = params[2]
        provision = params[3]
        card_type = params[4]
        fraction = params[5]
        if params[6]:
            deployment = METHODS[params[6]]
        else:
            deployment = None
        if params[7]:
            order = METHODS[params[7]]
        else:
            order = None
        if params[8]:
            turn_end = METHODS[params[8]]
        else:
            turn_end = None
        if params[9]:
            conditional = METHODS[params[9]]
        else:
            conditional = None
        tags = params[10].split(";")
        deca.append(Card(name, bp, name + ".png", armor, provision, card_type, fraction, tags, deployment, order, turn_end, conditional))
    return Deck(deck.name, "Me", deca, deck.last_chosen, deck.id)


def create_card(params):
    name = params[0]
    bp = params[1]
    armor = params[2]
    provision = params[3]
    card_type = params[4]
    fraction = params[5]
    if params[6]:
        deployment = METHODS[params[6]]
    else:
        deployment = None
    if params[7]:
        order = METHODS[params[7]]
    else:
        order = None
    if params[8]:
        turn_end = METHODS[params[8]]
    else:
        turn_end = None
    if params[9]:
        conditional = METHODS[params[9]]
    else:
        conditional = None
    tags = params[10].split(";")
    return Card(name, bp, name + ".png", armor, provision, card_type, fraction, tags, deployment, order, turn_end, conditional)

def update_deck_name(player, new_name):
    global_init("decks")
    session = create_session()
    session.query(Decks).get(player.deck.id).name = new_name
    session.commit()
