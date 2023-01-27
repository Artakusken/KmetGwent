class Opponent:
    def __init__(self):
        pass


import types


class Test:
    def __init__(self, point, armor, deployment=None):
        self.points = point
        self.armor = armor
        self.row = 2
        self.deployment = deployment

    def deploy(self):
        self.deployment()


def deal_armor(clas):
    if clas.armor > 2:
        clas.points += 3
        clas.armor -= 3


def row_change(clas, drow):
    if 0 <= clas.row + drow < 3:
        clas.row += drow


xdd = Test(1, 4)
ddx = Test(1, 4)
xdd.deployment = types.MethodType(deal_armor, xdd)
ddx.deployment = types.MethodType(row_change, ddx)
print(xdd.armor, xdd.points)
xdd.deploy()
print(xdd.armor, xdd.points)
print(ddx.row)
ddx.deployment(1)
print(ddx.row)
print(", ".join(['Warrior', 'Support']))