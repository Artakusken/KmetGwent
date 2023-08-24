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
        card.conditional = None


def brothers_at_arms(card, field, row):
    my_position = card.column
    if my_position != 0 and my_position != len(row.cards) - 1:
        if "Солдаты" in row.cards[my_position - 1].tags and "Солдаты" in row.cards[my_position + 1].tags:
            card.power += 1


METHODS = {
    "cant_stand_brothers": cant_stand_brothers,
    "healing_armor": healing_armor,
    "recruit": recruit
}

if __name__ == '__main__':
    import marshal
    import ujson as json
    import json
    import types

    def multiplier(a, b):
        return a * b

    print(multiplier)
    a = marshal.dumps(multiplier.__code__)
    print(a)

    def f(jfile):
        x = marshal.loads(jfile)
        print(x)
        # print(compile("""
        # def multiplier(a, b):
        #     return a * b""", "sdg.py", mode='exec'))
        # maybe save the function name in dict
        func = types.FunctionType(x, globals(), "some_func_name")
        return func

    fu = f(a)
    print(fu)
    print(fu(2, 4))