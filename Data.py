from Cards import Card
from Storages import Deck

import sqlalchemy
import sqlalchemy_serializer
import sqlalchemy.orm as orm
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


def healing_armor(card, field, row):
    healing_points = card.armor
    card.power += healing_points
    card.armor = 0


SqlAlchemyBase = orm.declarative_base()
__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    # print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> orm.Session:
    global __factory
    return __factory()


class CardsBase(SqlAlchemyBase, sqlalchemy_serializer.SerializerMixin):
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


class Methods(SqlAlchemyBase, sqlalchemy_serializer.SerializerMixin):
    __tablename__ = "Methods"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)


class MethodsType(SqlAlchemyBase, sqlalchemy_serializer.SerializerMixin):
    __tablename__ = "Methods_types"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String)


# class DecksBase(SqlAlchemyBase, sqlalchemy_serializer.SerializerMixin):
#     __tablename__ = "Decks"
#
#     id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
#     name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
#     cards = sqlalchemy.Column(sqlalchemy.String)
#     last_chosen = sqlalchemy.Column(sqlalchemy.Integer)


CARDS_LIST = {"Нет карты": None}
CARDS_LIST["Воин клана Турсеах"] = Card("Воин клана Турсеах", 10, "Воин клана Турсеах.png", 2, 5, "U", "NR", None, None, None, None, "Воин", "Поддержка")
CARDS_LIST["Пикинёры Ард Феаин"] = Card("Пикинёры Ард Феаин", 10, "Пикинёры Ард Феаин.png", 10, 6, "U", "NG", "Солдаты", "Поддержка")
CARDS_LIST["Аpбалетчики 'Импера'"] = Card("Аpбалетчики 'Импера'", 6, "Аpбалетчики 'Импера'.png", 2, 6, "U", "NG", "Солдаты", "Поддержка")
CARDS_LIST["Бригада 'Импера'"] = Card("Бригада 'Импера'", 4, "Бригада 'Импера'.png", 6, 5, "U", "NG", "Солдаты", "Поддержка")
CARDS_LIST["Новобранец"] = Card("Новобранец", 4, "Новобранец.png", 1, 4, "U", "NG", "Солдаты", "Поддержка")
CARDS_LIST["Пикинёры 'Альба'"] = Card("Пикинёры 'Альба'", 6, "Пикинёры 'Альба'.png", 2, 4, "U", "NG", "Солдаты", "Поддержка")
CARDS_LIST["Рыцарь Нильфгаарда"] = Card("Рыцарь Нильфгаарда", 8, "Рыцарь Нильфгаарда.png", 12, 6, "U", "NG", "Рыцарь", "Поддержка")
CARDS_LIST["Бригада Даэрляндцев"] = Card("Бригада Даэрляндцев", 8, "Бригада Даэрляндцев.png", 12, 6, "U", "NG", "Рыцарь", "Поддержка")
CARDS_LIST["Дивизия Магна"] = Card("Дивизия Магна", 8, "Дивизия Магна.png", 12, 6, "U", "NG", "Рыцарь", "Поддержка")
CARDS_LIST["Кавалерия Наузикка"] = Card("Кавалерия Наузикка", 8, "Кавалерия Наузикка.png", 12, 6, "U", "NG", "Рыцарь", "Поддержка")
CARDS_LIST["Кирасиры 'Ард Феаин'"] = Card("Кирасиры 'Ард Феаин'", 8, "Кирасиры 'Ард Феаин'.png", 12, 6, "U", "NG", "Рыцарь", "Поддержка")
CARDS_LIST["Тяжёлая Хельга"] = Card("Тяжёлая Хельга", 8, "Тяжёлая Хельга.png", 12, 6, "U", "NG", "Рыцарь", "Поддержка")

METHOD_LIST = {"Воин клана Турсеах deploy": cant_stand_brothers}
METHOD_LIST["Воин клана Турсеах order"] = healing_armor

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
            DECKS_LIST[deck[1]] = Deck(deck[1], "Me", cards)
        else:
            DECKS_LIST[deck[1]] = Deck(deck[1], "Me", deck[2].split(";"))

methods = {"cant_stand_brothers": cant_stand_brothers}
methods["healing_armor"] = healing_armor

# if __name__ == "__main__":
global_init("NCards.db")
deck = "1;2;1;2;1;2;1;2;2;2;2;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1;1"
session = create_session()
for i in session.query(CardsBase):
    if session.query(Methods).filter(Methods.id == i.deployment).first():
        print(session.query(Methods).filter(Methods.id == i.deployment).first().name)
    else:
        print(None)

dec = []
for card_id in deck.split(";"):
    params = session.query(CardsBase).filter(CardsBase.id == card_id).first()
    name = params.name
    bp = params.bp
    armor = params.armor
    provision = params.provision
    card_type = params.card_type
    fraction = params.fraction
    tags = params.tags
    deploy = session.query(Methods).filter(Methods.id == params.deployment).first()
    if deploy:
        deployment = methods[deploy.name]
    else:
        deployment = None
    ord = session.query(Methods).filter(Methods.id == params.order).first()
    if ord:
        order = methods[session.query(Methods).filter(Methods.id == params.order).first().name]
    else:
        order = None
    turn_end = params.turn_end
    conditional = params.conditional
    dec.append(
        Card(name, bp, name + ".png", armor, provision, card_type, fraction, deployment, order, turn_end, conditional, tags))
game_deck = Deck("new", "Me", dec)
session.commit()
