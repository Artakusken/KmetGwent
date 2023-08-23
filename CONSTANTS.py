import os
import pygame

SWIDTH, SHEIGHT = 1920, 1080
FPS = 30
LEADER_W, LEADER_H = 212, 309  # ideal aspect ratio is 212x304  (default card is 992x1424)
MCARD_W, MCARD_H = 320, 459  # ideal aspect ratio is 320x459  (default card is 992x1424)
SCARD_W, SCARD_H = 106, 148  # ideal aspect ratio is 106x152  (default card is 992x1424)
DECK_SIZE = 30
HAND_SIZE = 10
ROW_SIZE = 9
GET_CARDS = 4
TEXT_LENGTH = 26
FONT = 'Georgia'
CLICKABLE = []
IMAGES = {}


def load_image(name, card_size):
    directory = os.path.join(name)
    if os.path.isfile(directory):
        if isinstance(card_size, tuple):
            image = pygame.transform.smoothscale(pygame.image.load(directory), card_size)
        elif card_size == "O":
            image = pygame.image.load(directory)
        elif card_size == 'M':
            image = pygame.transform.smoothscale(pygame.image.load(directory), (MCARD_W, MCARD_H))
        elif card_size == 'K':
            image = pygame.transform.smoothscale(pygame.image.load(directory), (150, 150))
        elif card_size == 'HD':
            image = pygame.transform.smoothscale(pygame.image.load(directory), (SWIDTH, SHEIGHT))
        else:
            image = pygame.transform.smoothscale(pygame.image.load(directory), (SCARD_W, SCARD_H))
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

IMAGES["nilf_frame_large"] = load_image('CardsPictures\\nilfgaard_frame.png', "O")
IMAGES["nilf_frame_medium"] = load_image('CardsPictures\\nilfgaard_frame.png', (120, 121))
IMAGES["nilf_frame_deck"] = load_image('CardsPictures\\nilfgaard_frame.png', (80, 81))
IMAGES["nilf_frame_small"] = load_image('CardsPictures\\nilfgaard_frame.png', (40, 40))

IMAGES["armor_large"] = load_image('CardsPictures\\armor.png', "O")
IMAGES["armor_medium"] = load_image('CardsPictures\\armor.png', (90, 104))
IMAGES["armor_deck"] = load_image('CardsPictures\\armor.png', (60, 69))
IMAGES["armor_small"] = load_image('CardsPictures\\armor.png', (30, 35))

IMAGES["border_bronze_large"] = load_image('CardsPictures\\border_bronze.png', "O")
IMAGES["border_bronze_medium"] = load_image('CardsPictures\\border_bronze.png', "M")
IMAGES["border_bronze_deck"] = load_image('CardsPictures\\border_bronze.png', (LEADER_W, LEADER_H))
IMAGES["border_bronze_small"] = load_image('CardsPictures\\border_bronze.png', "S")

IMAGES["border_golden_leader"] = load_image('CardsPictures\\border_gold.png', (LEADER_W, LEADER_H))
IMAGES["border_golden_large"] = load_image('CardsPictures\\border_gold.png', "O")
IMAGES["border_golden_medium"] = load_image('CardsPictures\\border_gold.png', "M")
