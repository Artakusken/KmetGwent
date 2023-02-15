import os
import pygame

SWIDTH, SHEIGHT = 1920, 1080
FPS = 30
LEADER_W, LEADER_H = 212, 309
MCARD_W, MCARD_H = 320, 458
SCARD_W, SCARD_H = 106, 140
DECK_SIZE = 30
HAND_SIZE = 10
ROW_SIZE = 9
GET_CARDS = 4
TEXT_LENGTH = 26
FONT = 'arial'
CLICKABLE = []
IMAGES = {}


def load_image(name, card_size='M'):
    directory = os.path.join(name)
    if os.path.isfile(directory):
        if card_size == 'O':
            image = pygame.image.load(directory)
        elif card_size == 'M':
            image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
        elif card_size == 'K':
            image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
        elif card_size == 'HD':
            image = pygame.transform.scale(pygame.image.load(directory), (SWIDTH, SHEIGHT))
        else:
            image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
        return image


IMAGES["RedCoin"] = load_image('Field\\RCoin.png', 'K')
IMAGES["BlueCoin"] = load_image('Field\\BCoin.png', 'K')
IMAGES["Blue0Crown"] = load_image('Field\\B0Crown.png', 'O')
IMAGES["Blue1Crown"] = load_image('Field\\B1Crown.png', 'O')
IMAGES["Blue2Crown"] = load_image('Field\\B2Crown.png', 'O')
IMAGES["Red0Crown"] = load_image('Field\\R0Crown.png', 'O')
IMAGES["Red1Crown"] = load_image('Field\\R1Crown.png', 'O')
IMAGES["Red2Crown"] = load_image('Field\\R2Crown.png', 'O')
IMAGES["Position_line"] = load_image('Field\\Position_line.png', 'O')

IMAGES["LLCorner"] = load_image('CardsPictures\\LLCorner.png', 'O')
IMAGES["LRCorner"] = load_image('CardsPictures\\LRCorner.png', 'O')
IMAGES["SLCorner"] = load_image('CardsPictures\\SLCorner.png', 'O')
IMAGES["SRCorner"] = load_image('CardsPictures\\SRCorner.png', 'O')
