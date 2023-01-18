import pygame
import os
import sys

from Cards import Card, Leader
from CONSTANTS import *
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


all_sprites = pygame.sprite.Group()
enemy_leader = pygame.sprite.Group()
ally_leader = pygame.sprite.Group()
ERoche = Leader("Roche180png", "Vernon Roche", "NR", enemy_leader, 181, 75, 70)
Roche = Leader("Roche180png", "Vernon Roche", "NR", ally_leader, 181, 75, 685)

size = SWIDTH, SHEIGHT
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()
c = 0
test = load_image('CardsPictures\LClan Tuirseach Veteran.png', 'M')
s_test = load_image('CardsPictures\SClan Tuirseach Veteran.png', 'S')
koloda = load_image('Field\\North.png', 'S')
sbros = load_image('Field\Dump.png', 'S')
moneta = load_image('Field\RCoin.png', 'K')
test_rect = test.get_rect()
test_srect = s_test.get_rect()
field = load_image('Field\\Field.jpg', "L")
Warrior = Card('Clan Tuirseach Veteran', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Skellige", "Warrior", "Support")


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, (100, 100, 100))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            surface = pygame.transform.smoothscale(screen, (500, 400))
            blur = pygame.transform.smoothscale(surface, (SWIDTH, SHEIGHT))
            screen.blit(blur, (0, 0))
            draw_text(screen, str('lorem ipsum'), 30, 1655, 688 + 10)
            for j in range(4):
                v = 9
                if j == 3:
                    v = 10
                for i in range(v):
                    a = i * 115
                    b = j * 155
                    if v == 10:
                        a = i * 110
                        Warrior.render(475 + a, 475 + b, "S", screen)
                    else:
                        Warrior.render(545 + a, 485 + b, "S", screen)
            c += 1
    if c % 2 == 0:
        screen.blit(field, (0, 0, SWIDTH, SHEIGHT))
        enemy_leader.update()
        ally_leader.update()
        enemy_leader.draw(screen)
        ally_leader.draw(screen)
        screen.blit(test, (1575, 230, 320, 458))
        Warrior.render(1575, 230, "M", screen)
        screen.blit(koloda, (1630, 0, 105, 150))
        screen.blit(koloda, (1630, 935, 105, 150))
        screen.blit(sbros, (1765, 0, 105, 150))
        screen.blit(sbros, (1765, 935, 105, 150))
        screen.blit(moneta, (155, 450, 150, 150))
        surf1 = pygame.Surface((75, 75))
        surf1.fill((150, 150, 150))
        screen.blit(surf1, (5, 440, 75, 75))
        surf2 = pygame.Surface((75, 75))
        surf2.fill((150, 250, 150))
        screen.blit(surf2, (5, 520, 75, 75))
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

