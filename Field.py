from CONSTANTS import *
from Cards import Card, Leader
import pygame
import os


class Row:
    def __init__(self, row_type, player):
        self.row = row_type
        self.places = ROW_SIZE
        self.player = player
        if player == "Human":
            if self.row == "melee":
                self.rect = (540, 480, 1030, 140)
            elif self.row == "ranged":
                self.rect = (540, 640, 1030, 140)
            else:
                self.rect = (540, 800, 1030, 140)
        else:
            if self.row == "melee":
                self.rect = (540, 320, 1030, 140)
            elif self.row == "ranged":
                self.rect = (540, 160, 1030, 140)
            else:
                self.rect = (540, 5, 1030, 140)
        self.cards = []
        CLICKABLE.append(self)
        self.name = self.row + self.player
        self.active_frame = self.load_image("Field\\rowe5.png", "O")
        self.frame = self.load_image("Field\\enemy_rowe.png", "O")

    def load_image(self, name, size='M'):
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'O':
                image = pygame.image.load(directory)
            elif size == 'M':
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
            elif size == 'K':
                image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
            else:
                image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
            return image

    def lit(self, screen, active):
        if active:
            if self.player == "Human":
                screen.blit(self.active_frame, (self.rect[0] - 10, self.rect[1] - 40, self.rect[2], self.rect[3]))
            else:
                screen.blit(self.frame, (self.rect[0] - 10, self.rect[1] - 40, self.rect[2], self.rect[3]))
        else:
            screen.blit(self.frame, (self.rect[0] - 10, self.rect[1] - 40, self.rect[2], self.rect[3]))

    def up_when_hovered(self, coord):
        for i in self.cards:
            if i.rect[0] < coord[0] < i.rect[0] + i.rect[2] and i.rect[1] < coord[1] < i.rect[1] + i.rect[3]:
                i.hover = True
            else:
                i.hover = False


class Field:
    def __init__(self, op_leader, pl_leader, screen, op_fraction):
        self.player_score, self.opponent_score = 0, 0
        self.field_image = self.load_image('Field\\Field.jpg', "O")
        self.round = 1
        self.pl_mr = Row("melee", "Human")  # player melee row
        self.pl_rr = Row("ranged", "Human")  # player range row
        self.pl_sr = Row("siege", "Human")  # player siege row
        self.op_mr = Row("melee", "AI")  # opponent melee row
        self.op_rr = Row("ranged", "AI")  # opponent range row
        self.op_sr = Row("siege", "AI")  # opponent siege row
        self.rows_list = [self.pl_mr, self.pl_rr, self.pl_sr, self.op_mr, self.op_rr, self.op_sr]
        self.op_fraction = op_fraction
        self.turn = None  # true if it's player turn, false if it's ai turn
        self.panel = None
        self.panel_name = ""
        self.panel_tags = ""
        self.panel_text = ""
        self.controls = ["ПКМ - отменить выбор карты", "ЛКМ - сыграть карту"]
        self.dump_image = self.load_image('Field\\Dump.png', 'S')
        self.pl_deck_image = self.load_image('Field\\Nilfgaard.png', 'S')
        if op_fraction == "NR":
            self.op_deck_image = self.load_image('Field\\North.png', 'S')
        else:
            self.op_deck_image = self.load_image('Field\\Scotoeli.png', 'S')
        self.rcoin = self.load_image('Field\\RCoin.png', 'K')
        self.bcoin = self.load_image('Field\\BCoin.png', 'K')
        self.op_crown = self.load_image('Field\\R0Crown.png', 'O')
        self.pl_crown = self.load_image('Field\\B0Crown.png', 'O')
        self.pl_leader = pl_leader
        self.op_leader = op_leader
        self.exit = self.load_image('Field\\exit.png', 'O')
        self.screen = screen

    def load_image(self, name, size='M'):
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'O':
                image = pygame.image.load(directory)
            elif size == 'M':
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
            elif size == 'K':
                image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
            else:
                image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
            return image

    def render_ui_images(self):
        self.screen.blit(self.field_image, (0, 0, SWIDTH, SHEIGHT))
        if type(self.panel) == Card:
            card = self.panel
            self.panel_name = card.name
            self.panel_tags = card.tags
            self.panel_text = card.description
            card.render(1575, 230, "M", self.screen)
        elif type(self.panel) == Leader:
            card = self.panel
            self.screen.blit(self.load_image('CardsPictures\\' + 'L' + card.image_path, 'M'),
                             (1575, 230, 320, 458))
            self.panel_name = card.name
            self.panel_text = card.description
            self.panel_tags = ""
        self.screen.blit(self.op_deck_image, (1630, 0, 105, 150))
        self.screen.blit(self.pl_deck_image, (1630, 935, 105, 150))
        self.screen.blit(self.dump_image, (1765, 0, 105, 150))
        self.screen.blit(self.dump_image, (1765, 935, 105, 150))
        if self.turn:
            self.screen.blit(self.bcoin, (155, 450, 150, 150))
        else:
            self.screen.blit(self.rcoin, (155, 450, 150, 150))
        self.screen.blit(self.exit, (5, 500, 75, 75))
        self.screen.blit(self.op_crown, (280, 305, 71, 71))
        self.screen.blit(self.pl_crown, (280, 925, 71, 71))

    def render_ui_leader(self):
        self.op_leader.update()
        self.pl_leader.update()
        self.op_leader.draw(self.screen)
        self.pl_leader.draw(self.screen)

    def set_panel_card(self, card):
        self.panel = card

    def set_crowns(self, win):
        if win:
            if self.round == 1:
                self.pl_crown = IMAGES["Blue1Crown"]
            elif self.round == 2:
                self.pl_crown = IMAGES["Blue2Crown"]
        else:
            if self.round == 1:
                self.op_crown = IMAGES["Red1Crown"]
            elif self.round == 2:
                self.op_crown = IMAGES["Red2Crown"]

    def draw_text(self, surf, text, size, x, y, color=(200, 200, 200)):
        font = pygame.font.SysFont(FONT, size, bold=True)
        text_surface = font.render(text, True, color)
        surf.blit(text_surface, (x, y))

    def render_text(self, op_leader, pl_leader, pl_hand, pl_deck, pl_dump, op_hand, op_deck, op_dump):
        self.draw_text(self.screen, self.panel_name, 30, 1580, 690)
        self.draw_text(self.screen, self.panel_tags, 25, 1580, 730)
        self.draw_text(self.screen, self.panel_text, 20, 1580, 770)

        self.draw_text(self.screen, op_leader.fraction, 20, 20, 20)
        self.draw_text(self.screen, pl_leader.fraction, 20, 20, 620)

        self.draw_text(self.screen, op_leader.name, 20, 20, 40)
        self.draw_text(self.screen, pl_leader.name, 20, 20, 650)

        self.draw_text(self.screen, self.controls[0], 20, 1580, 160)
        self.draw_text(self.screen, self.controls[1], 20, 1580, 190)

        self.draw_text(self.screen, "ПКМ - основная способность лидера", 20, 20, 1010)
        self.draw_text(self.screen, "ЛКМ - доп. способность лидера", 20, 20, 1040)

        self.draw_text(self.screen, str(op_leader.rability), 20, 250, 325)
        self.draw_text(self.screen, str(op_leader.mability), 20, 250, 355)
        self.draw_text(self.screen, str(pl_leader.rability), 20, 250, 945)
        self.draw_text(self.screen, str(pl_leader.mability), 20, 250, 975)

        self.draw_text(self.screen, str(len(pl_hand.cards)), 30, 1580, 1045)
        self.draw_text(self.screen, str(len(pl_deck.cards)), 30, 1675, 1045)
        self.draw_text(self.screen, str(len(pl_dump.cards)), 30, 1810, 1045)

        self.draw_text(self.screen, str(len(op_hand.cards)), 30, 1580, 15)
        self.draw_text(self.screen, str(len(op_deck.cards)), 30, 1675, 15)
        self.draw_text(self.screen, str(len(op_dump.cards)), 30, 1810, 15)

        points_sum = 0
        self.draw_text(self.screen, str(l := sum([i.power for i in self.op_sr.cards])), 30, 485, 60, (0, 0, 0))
        points_sum += l
        self.draw_text(self.screen, str(l := sum([i.power for i in self.op_rr.cards])), 30, 485, 210, (0, 0, 0))
        points_sum += l
        self.draw_text(self.screen, str(l := sum([i.power for i in self.op_mr.cards])), 30, 485, 370, (0, 0, 0))
        points_sum += l
        self.draw_text(self.screen, str(points_sum), 30, 400, 305, (0, 0, 0))

        points_sum = 0
        self.draw_text(self.screen, str(l := sum([i.power for i in self.pl_mr.cards])), 30, 485, 540, (0, 0, 0))
        points_sum += l
        self.draw_text(self.screen, str(l := sum([i.power for i in self.pl_rr.cards])), 30, 485, 690, (0, 0, 0))
        points_sum += l
        self.draw_text(self.screen, str(l := sum([i.power for i in self.pl_sr.cards])), 30, 485, 850, (0, 0, 0))
        points_sum += l
        self.draw_text(self.screen, str(points_sum), 30, 400, 715, (0, 0, 0))

        if self.turn:
            self.draw_text(self.screen, "Ваш ход", 20, 250, 845)
        else:
            self.draw_text(self.screen, "Ход противника", 20, 250, 845)

    def count_score(self, player):
        if player == "Human":
            points_sum, l = [], 0
            l = sum([i.power for i in self.pl_sr.cards])
            points_sum += [l]
            l = sum([i.power for i in self.pl_rr.cards])
            points_sum += [l]
            l = sum([i.power for i in self.pl_mr.cards])
            points_sum += [l]
            return points_sum
        else:
            points_sum, l = [], 0
            l = sum([i.power for i in self.op_sr.cards])
            points_sum += [l]
            l = sum([i.power for i in self.op_rr.cards])
            points_sum += [l]
            l = sum([i.power for i in self.op_mr.cards])
            points_sum += [l]
            return points_sum

    def draw_hand(self, hand):
        for i in range(len(hand.cards)):
            a = i * 110
            if hand.cards[i].hover or hand.cards[i].status == "chosen":
                hand.cards[i].render(475 + a, 935, "S", self.screen)
                hand.cards[i].rect = (475 + a, 935, SCARD_W, SCARD_H)
                hand.cards[i].hand_position = i
            else:
                hand.cards[i].render(475 + a, 945, "S", self.screen)
                hand.cards[i].rect = (475 + a, 945, SCARD_W, SCARD_H)

    def draw_rows(self):
        for i in self.rows_list:
            x, y = i.rect[0], i.rect[1]
            for j in range(len(i.cards)):
                a = j * 115
                if i.cards[j].hover or i.cards[j].status == "chosen":
                    i.cards[j].render(x + a, y - 10, "S", self.screen)
                    i.cards[j].rect = (x + a, y - 10, SCARD_W, SCARD_H)
                else:
                    i.cards[j].render(x + a, y, "S", self.screen)
                    i.cards[j].rect = (x + a, y, SCARD_W, SCARD_H)

    def draw_end(self):
        if self.player_score > self.opponent_score:
            self.draw_text(self.screen, "Вы выиграли", 30, 700, 400)
            if self.round == 2:
                self.screen.blit(IMAGES["Red0Crown"], (910, 370, 71, 71))
            else:
                self.screen.blit(IMAGES["Red1Crown"], (910, 370, 71, 71))
            self.screen.blit(IMAGES["Blue2Crown"], (620, 370, 71, 71))
        elif self.player_score < self.opponent_score:
            self.draw_text(self.screen, "Вы проиграли", 30, 750, 400)
            if self.round == 2:
                self.screen.blit(IMAGES["Blue0Crown"], (670, 370, 71, 71))
            else:
                self.screen.blit(IMAGES["Blue1Crown"], (670, 370, 71, 71))
            self.screen.blit(IMAGES["Red2Crown"], (860, 370, 71, 71))
        else:
            self.draw_text(self.screen, "Ничья", 30, 750, 400)
            self.screen.blit(IMAGES["Red2Crown"], (860, 370, 71, 71))
            self.screen.blit(IMAGES["Blue2Crown"], (670, 370, 71, 71))

        self.draw_text(self.screen, "Вы", 30, 650, 500)
        self.draw_text(self.screen, "Противник", 30, 910, 500)
        self.draw_text(self.screen, str(self.player_score), 30, 650, 550)
        self.draw_text(self.screen, str(self.opponent_score), 30, 910, 550)
