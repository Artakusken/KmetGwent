import pygame
import os
import sys

from Cards import Card

pygame.init()


def load_image(name, size='M'):
    directory = os.path.join(name)
    if os.path.isfile(directory):
        if size == 'M':
            image = pygame.image.load(directory)
        elif size == 'L':
            image = pygame.transform.scale(pygame.image.load(directory), (320, 458))
        elif size == 'K':
            image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
        else:
            image = pygame.transform.scale(pygame.image.load(directory), (105, 140))
        return image


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, name, group, x, y, frame_n=-1):
        super().__init__(group)
        self.frames = []
        self.cur_frame = 0
        self.frames_number = frame_n
        self.rect = pygame.Rect(x, y, 212, 309)
        self.load_image(name)

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


all_sprites = pygame.sprite.Group()
enemy_leader = pygame.sprite.Group()
ally_leader = pygame.sprite.Group()
ERoche = AnimatedSprite('Roche180png', ally_leader, 75, 70, 181)
Roche = AnimatedSprite('Roche180png', enemy_leader, 75, 685, 181)

size = 1920, 1080
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()
c = 0
test = load_image('CardsPictures\LClan Tuirseach Veteran.png', 'L')
s_test = load_image('CardsPictures\SClan Tuirseach Veteran.png', 'S')
koloda = load_image('Field\\North.png', 'S')
sbros = load_image('Field\Dump.png', 'S')
moneta = load_image('Field\RCoin.png', 'K')
test_rect = test.get_rect()
test_srect = s_test.get_rect()
Warrior = Card('dfgd', 10, "Clan Tuirseach Veteran.png", 2, 5, "U", "Warrior", "Support")


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
            blur = pygame.transform.smoothscale(surface, (1920, 1080))
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
        screen.blit(load_image('Field\\Field.jpg'), (0, 0, 1920, 1080))
        enemy_leader.update()
        ally_leader.update()
        enemy_leader.draw(screen)
        ally_leader.draw(screen)
        screen.blit(test, (1575, 230, 320, 458))
        Warrior.render(1575, 230, "L", screen)
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
    clock.tick(30)

pygame.quit()

