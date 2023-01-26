import os
import pygame

from CONSTANTS import *
from Cards_Descriptions import descriptions

pygame.init()


class Card:
    def __init__(self, name, base_power, image_name, armor, provision, card_type, fraction, *tags):
        if fraction == "NR":
            self.fraction = "Королевства Севера"
        elif fraction == "NG":
            self.fraction = "Нильфгаард"
        else:
            self.fraction = fraction
        self.name = name
        self.bp = base_power
        self.power = self.bp
        self.armor = armor
        self.image_path = image_name
        self.provision = provision
        if type(tags) is tuple:
            self.tags = ' '.join(tags)
        elif type(tags) is str:
            self.tags = tags
        else:
            self.tags = None
        self.card_type = card_type
        self.row = None
        self.column = None
        self.field_position = [self.row, self.column]
        if self.name in descriptions.keys():
            self.description = descriptions[self.name]
        else:
            self.description = "EMPTY DESCRIPTION"
        self.location = 0  # 0 - deck, 1 - hand, 2 - field, 3 - dump. Second arg is for place in 0, 1 and 3
        self.status = "passive"
        self.hand_position = None
        self.rect = None
        self.hover = False
        self.frame = self.load_card_image("Field\\cardFrame.png", "O")
        self.Mimage = self.load_card_image('CardsPictures\\' + 'L' + image_name, 'M')  # TODO: change namings, and L to M in image name
        self.Simage = self.load_card_image('CardsPictures\\' + 'S' + image_name, 'S')
        CLICKABLE.append(self)

    def set_tags(self, tagi):
        if self.tags is None:
            self.tags = tagi

    def load_card_image(self, name, size):
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'M':
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
            elif size == 'S':
                image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
            else:
                image = pygame.image.load(directory)
            return image

    def display_cards_points(self, x, y, size, ptype, screen):
        if size == "M":
            font_size = 40
            dx = 267
            text_coord_delta = 15
        else:
            font_size = 24
            dx = 77
            text_coord_delta = 10
        y += 2

        font = pygame.font.Font(None, font_size)
        if self.power == self.bp:
            font_color = (200, 200, 200)
        elif self.power > self.bp:
            font_color = (50, 200, 50)
        else:
            font_color = (200, 50, 50)
        if ptype == "p":
            points = font.render(str(self.power), True, font_color)
            if self.power > 9:
                screen.blit(points, (x + text_coord_delta, y + text_coord_delta))
            else:
                screen.blit(points, (x + text_coord_delta + 6, y + text_coord_delta))
        else:
            armor = font.render(str(self.armor), True, (0, 0, 0))
            if self.power > 9:
                screen.blit(armor, (x + dx + text_coord_delta, y + text_coord_delta))
            else:
                screen.blit(armor, (x + dx + text_coord_delta, y + text_coord_delta))

    def render(self, x, y, size, screen):
        if self.location == 1 or self.location == 2:
            if size == 'M':
                screen.blit(self.Mimage, (x, y, MCARD_W, MCARD_H))
                screen.blit(IMAGES["LLCorner"], (x, y))
                self.display_cards_points(x, y, "M", "p", screen)
                if self.armor > 0:
                    screen.blit(IMAGES["LRCorner"], (x + 263, y + 2))
                    self.display_cards_points(x, y, "M", "a", screen)
            else:
                screen.blit(self.Simage, (x, y, SCARD_W, SCARD_H))
                screen.blit(IMAGES["SLCorner"], (x, y))
                self.display_cards_points(x, y, "S", "p", screen)
                if self.armor > 0:
                    screen.blit(IMAGES["SRCorner"], (x + 77, y + 3))
                    self.display_cards_points(x, y, "S", "a", screen)
                if self.status == "chosen":
                    screen.blit(self.frame, (x - 3, y - 3))

    def kill(self, op_dump, pl_dump, pl_hand, op_hand):
        self.location = 3
        if self.fraction == "Skellige":
            pl_dump.cards.append(self)
            pl_hand.pop_card(-1)
        else:
            op_dump.cards.append(self)
            op_hand.pop_card(-1)
        self.rect = None


class Leader(pygame.sprite.Sprite):
    def __init__(self, animation, name, fraction, frame_n, x, y):
        super().__init__()
        self.frames = []
        if fraction == "NR":
            self.fraction = "Королевства Севера"
        elif fraction == "NG":
            self.fraction = "Нильфгаард"
        else:
            self.fraction = fraction
        self.name = name
        self.cur_frame = 0
        self.image_path = name + '.png'
        self.frames_number = frame_n
        self.rect = pygame.Rect(x, y, LEADER_W, LEADER_H)
        self.load_image(animation)
        if name in descriptions.keys():
            self.description = descriptions[name]
        else:
            self.description = "EMPTY DESCRIPTION"
        self.rability = 3
        self.mability = 1
        self.status = None
        CLICKABLE.append(self)

    def load_image(self, name):
        directory = os.path.join('Animations', name + '\\')
        for i in os.listdir(directory):
            if os.path.isfile(directory + i):
                image = pygame.image.load(directory + i)
                self.frames.append(pygame.transform.scale(image, (LEADER_W, LEADER_H)))
            else:
                print(f"Файл с изображением '{i}' не найден")

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % self.frames_number

    def draw(self, screen):
        screen.blit(self.frames[self.cur_frame], (self.rect[0], self.rect[1]))
