import pygame
import os
# import sys

from Cards import Card, Leader
from Field import Field
from CONSTANTS import *
from Storages import Dump, Deck, Hand

pygame.init()


def load_image(name, size='M'):
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


ERoche = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 70)
Roche = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 685)

Warrior = Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support")

pl_dump = Dump()
pl_deck = Deck()
pl_hand = Hand()
pl_deck.set_cards(
    [Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support") for i in
     range(12)])
pl_hand.start_hand(pl_deck)

size = SWIDTH, SHEIGHT
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()
c = 0
s_test = load_image('CardsPictures\SClan Tuirseach Veteran.png', 'S')
field = Field(ERoche, Roche, screen)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, (100, 100, 100))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def in_area(coord):
    x, y = coord
    for i in CLICKABLE:
        if i.rect:
            if i.rect[0] < x < i.rect[0] + i.rect[2] and i.rect[1] < y < i.rect[1] + i.rect[3]:
                if type(i) == Card:
                    i.status = "chosen"
                print(str(type(i)))
                return str(type(i))
    return "Nothing"


# for i in CLICKABLE:
#     print(type(i), i)

while running:
    if c % 2 == 0:
        field.render_ui_images()
        field.render_ui_leader()
        field.render_text(ERoche, Roche, pl_hand, pl_deck, pl_dump)
        field.draw_hand(pl_hand)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_q:
                field.set_panel_card(Roche)
            if event.key == pygame.K_w:
                field.set_panel_card(Warrior)
            if event.key == pygame.K_a:
                field.set_crowns(True)
            if event.key == pygame.K_s:
                field.set_crowns(False)
            if event.key == pygame.K_d:
                field.round += 1
            if event.key == pygame.K_z:
                pl_hand.play_card(-1, pl_dump)
            if event.key == pygame.K_f:
                surface = pygame.transform.smoothscale(screen, (500, 400))
                blur = pygame.transform.smoothscale(surface, (SWIDTH, SHEIGHT))
                screen.blit(blur, (0, 0))
                for j in range(3):
                    v = 9
                    if j == 3:
                        v = 10
                    for i in range(v):
                        a = i * 115
                        b = j * 155
                        Warrior.render(545 + a, 485 + b, "S", screen)
                c += 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                font = pygame.font.SysFont(FONT, 30, bold=True)
                a = in_area(event.pos)
                text_surface = font.render(f"{event.pos}, {a}", True, (200, 200, 200))
                screen.blit(text_surface, (250, 900))
            elif event.button == 3:
                font = pygame.font.SysFont(FONT, 30, bold=True)
                text_surface = font.render(f"{event.pos}, 2", True, (200, 200, 200))
                screen.blit(text_surface, (250, 900))
        # if event.type == pygame.MOUSEMOTION:
        #     font = pygame.font.SysFont(FONT, 30, bold=True)
        #     text_surface = font.render(f"{event.pos}, 0", True, (200, 200, 200))
        #     screen.blit(text_surface, (250, 900))
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
