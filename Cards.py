import os
import sys
import pygame

from CONSTANTS import *
from Cards_Descriptions import descriptions

pygame.init()


class Card:
    def __init__(self, name, base_power, image, armor, provision, card_type, fraction, *tags):
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
        self.provision = provision
        self.image_path = image
        self.tags = tags
        self.card_type = card_type
        self.row = None
        self.column = None
        self.field_position = [self.row, self.column]
        if self.name in descriptions.keys():
            self.description = descriptions[self.name]
        else:
            self.description = "EMPTY DESCRIPTION"
        self.location = [0, None]  # 0 - deck, 1 - hand, 2 - field, 3 - dump. Second arg is for place in 0, 1 and 3
        self.status = "in_deck"  # test variable which tell us card condition. Ex. chosen or used and etc
        self.hand_position = None
        self.rect = None
        CLICKABLE.append(self)

    def load_image(self, name, size):
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
            y += 2
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
        if size == 'M':
            self.image = self.load_image('CardsPictures\\' + 'L' + self.image_path, 'M')
            screen.blit(self.image, (x, y, MCARD_W, MCARD_H))
            screen.blit(pygame.image.load(os.path.join('CardsPictures\\LLCorner.png')), (x, y))
            self.display_cards_points(x, y, "M", "p", screen)
            if self.armor > 0:
                screen.blit(pygame.image.load(os.path.join('CardsPictures\\LRCorner.png')), (x + 263, y + 2))
                self.display_cards_points(x, y, "M", "a", screen)
        else:
            self.image = self.load_image('CardsPictures\\' + 'S' + self.image_path, 'S')
            screen.blit(self.image, (x, y, SCARD_W, SCARD_H))
            screen.blit(pygame.image.load(os.path.join('CardsPictures\\LRight_Corner.png')), (x, y))
            self.display_cards_points(x, y, "S", "p", screen)
            if self.armor > 0:
                screen.blit(pygame.image.load(os.path.join('CardsPictures\\SRCorner.png')), (x + 77, y + 3))
                self.display_cards_points(x, y, "S", "a", screen)


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


Warrior = Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support")