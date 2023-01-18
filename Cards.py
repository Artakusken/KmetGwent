import os
import sys
import pygame
from Cards_Descriptions import descriptions
pygame.init()


class Card:
    def __init__(self, name, base_power, image, armor, provision, card_type, fraction, *tags):
        self.name = name
        self.fraction = fraction
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

    def load_image(self, name, size):
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'L':
                image = pygame.transform.scale(pygame.image.load(directory), (320, 458))
            elif size == 'S':
                image = pygame.transform.scale(pygame.image.load(directory), (105, 140))
            else:
                image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
            return image

    def display_cards_points(self, x, y, size, ptype, screen):
        if size == "L":
            font_size = 40
            dx = 270
            text_coord_delta = 15
        else:
            font_size = 24
            dx = 84
            text_coord_delta = 0
            x += 4
            y += 5

        font = pygame.font.Font(None, font_size)
        if self.power == self.bp:
            font_color = (200, 200, 200)
        elif self.power > self.bp:
            font_color = (50, 200, 50)
        else:
            font_color = (200, 50, 50)
        if ptype == "p":
            points = font.render(str(self.power), True, font_color)
            screen.blit(points, (x + text_coord_delta, y + text_coord_delta))
        else:
            points = font.render(str(self.armor), True, (0, 0, 0))
            screen.blit(points, (x + dx + text_coord_delta, y + text_coord_delta))

    def render(self, x, y, size, screen):
        if size == 'L':
            self.image = self.load_image('CardsPictures\\' + 'L' + self.image_path, 'L')
            screen.blit(self.image, (x, y, 320, 458))
            screen.blit(pygame.image.load(os.path.join('CardsPictures\\LLCorner.png')), (x + 10, y + 10))
            self.display_cards_points(x, y, "L", "p", screen)
            if self.armor > 0:
                screen.blit(pygame.image.load(os.path.join('CardsPictures\\LRCorner.png')), (x + 275, y + 10))
                self.display_cards_points(x, y, "L", "a", screen)
        else:
            self.image = self.load_image('CardsPictures\\' + 'S' + self.image_path, 'S')
            screen.blit(self.image, (x, y, 105, 140))
            screen.blit(pygame.image.load(os.path.join('CardsPictures\\SLCorner.png')), (x + 3, y + 3))
            self.display_cards_points(x, y, "S", "p", screen)
            if self.armor > 0:
                screen.blit(pygame.image.load(os.path.join('CardsPictures\\SRCorner.png')), (x + 84, y + 3))
                self.display_cards_points(x, y, "S", "a", screen)


class Leader(pygame.sprite.Sprite):
    def __init__(self, animation, name, fraction, group, frame_n, x, y):
        super().__init__(group)
        self.frames = []
        self.name = name
        self.fraction = fraction
        self.cur_frame = 0
        self.frames_number = frame_n
        self.rect = pygame.Rect(x, y, 212, 309)
        self.load_image(animation)

    def load_image(self, name):
        directory = os.path.join('Animations', name + '\\')
        for i in os.listdir(directory):
            if os.path.isfile(directory + i):
                image = pygame.image.load(directory + i)
                self.frames.append(pygame.transform.scale(image, (212, 309)))
            else:
                print(f"Файл с изображением '{i}' не найден")

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % self.frames_number
        self.image = self.frames[self.cur_frame]

# Warrior = Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support")
# screen = pygame.display.set_mode((600, 600))
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             Warrior.power += 1
#         if event.type == pygame.KEYDOWN:
#             Warrior.power -= 1
#
#     screen.fill((150, 150, 150))
#     Warrior.render(20, 20, "S", screen)
#     pygame.display.flip()
#
# pygame.quit()
