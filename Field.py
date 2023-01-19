from CONSTANTS import *
from Cards import Card, Leader
import pygame
import os


class Field:
    def __init__(self, op_leader, pl_leader):
        self.field_image = self.load_image('Field\\Field.jpg', "L")
        self.round = 1
        self.pl_mr = []  # player melee row
        self.pl_rr = []  # player range row
        self.pl_sr = []  # player siege row
        self.op_mr = []  # opponent melee row
        self.op_rr = []  # opponent range row
        self.op_sr = []  # opponent siege row
        self.turn = None  # true if it's player turn, false if it's ai turn
        self.panel = None
        self.panel_name = ""
        self.panel_tags = ""
        self.panel_text = ""
        self.controls = "Правая кнопка мыши - отменить выбор карты \n Правая кнопка мыши - сыграть карту"
        self.dump_image = self.load_image('Field\Dump.png', 'S')
        self.pl_deck_image = self.load_image('Field\\North.png', 'S')
        self.op_deck_image = self.load_image('Field\\Nilfgaard.png', 'S')
        self.rcoin = self.load_image('Field\RCoin.png', 'K')
        self.bcoin = self.load_image('Field\BCoin.png', 'K')
        self.pl_leader = pl_leader
        self.op_leader = op_leader
        self.history = pygame.Surface((75, 75))
        self.history.fill((150, 150, 150))
        self.exit = pygame.Surface((75, 75))
        self.exit.fill((150, 250, 150))

    def test(self, card):
        self.panel = self.load_image('CardsPictures\\' + 'L' + card.image_path, 'M')
        self.panel_name = card.name
        self.panel_tags = card.tags
        self.panel_text = card.description

    def load_image(self, name, size='M'):
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'L':
                image = pygame.image.load(directory)
            elif size == 'M':
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
            elif size == 'K':
                image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
            else:
                image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
            return image

    def render_ui_images(self, screen):
        screen.blit(self.field_image, (0, 0, SWIDTH, SHEIGHT))
        if type(self.panel) == Card:
            card = self.panel
            self.panel_name = card.name
            self.panel_tags = card.tags
            self.panel_text = card.description
            card.render(1575, 230, "M", screen)
        elif type(self.panel) == Leader:
            card = self.panel
            screen.blit(self.load_image('CardsPictures\\' + 'L' + card.image_path, 'M'),
                        (1575, 230, 320, 458))
            self.panel_name = card.name
            self.panel_text = card.description
        screen.blit(self.op_deck_image, (1630, 0, 105, 150))
        screen.blit(self.pl_deck_image, (1630, 935, 105, 150))
        screen.blit(self.dump_image, (1765, 0, 105, 150))
        screen.blit(self.dump_image, (1765, 935, 105, 150))
        if self.turn:
            screen.blit(self.bcoin, (155, 450, 150, 150))
        else:
            screen.blit(self.rcoin, (155, 450, 150, 150))
        screen.blit(self.history, (5, 440, 75, 75))
        screen.blit(self.exit, (5, 520, 75, 75))

    def render_ui_leader(self, screen):
        self.op_leader.update()
        self.pl_leader.update()
        self.op_leader.draw(screen)
        self.pl_leader.draw(screen)

    def set_panel_card(self, card):
        self.panel = card
