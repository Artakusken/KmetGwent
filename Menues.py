import pygame
import pygame_gui
import os
from CONSTANTS import *
from Cards import Warrior
from Cards_Descriptions import descriptions
pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((SWIDTH, SHEIGHT))


def load_image(name, size='M'):
    directory = os.path.join(name)
    if os.path.isfile(directory):
        if size == 'L':
            image = pygame.image.load(directory)
        elif size == 'M':
            image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
        elif size == 'K':
            image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
        elif size == 'HD':
            image = pygame.transform.scale(pygame.image.load(directory), (SWIDTH, SHEIGHT))
        elif size == 'C':
            image = pygame.transform.scale(pygame.image.load(directory), (496, 707))
        else:
            image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
        return image


background = pygame.Surface((SWIDTH, SHEIGHT))
background.blit(load_image('Field\\NG_loadscreen.png', "HD"), (0, 0, SWIDTH, SHEIGHT))

clock = pygame.time.Clock()
is_running = True


class Menu:
    def __init__(self, x, y):
        self.buttons = []
        self.manager = pygame_gui.UIManager((x, y), 'theme.json')

    def set_button(self, x, y, width, height, text):
        self.buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x, y), (width, height)),
                                            text=text,
                                            manager=self.manager))


class Constructor(Menu):
    def __init__(self, x, y, screen):
        super().__init__(x, y)
        self.entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 20), (250, 75)),
                                                         manager=self.manager, initial_text="Колода#1")
        self.entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1610, 1030), (300, 50)),
                                                         manager=self.manager, initial_text="Введите индекс карты для удаления")
        self.decks = ["Нет колоды"]
        self.cards = ["Нет карты", Warrior.name]
        self.chosen_card = None
        self.decks_drop_box = pygame_gui.elements.UIDropDownMenu(self.decks, relative_rect=pygame.Rect((520, 20), (250, 75)),
                                                                 manager=self.manager, starting_option='Нет колоды')
        self.cards_drop_box = pygame_gui.elements.UIDropDownMenu(self.cards, relative_rect=pygame.Rect((780, 20), (250, 75)),
                                                                 manager=self.manager, starting_option='Нет карты')
        self.max_provision = 150
        self.provision = 0

        self.deck_background = pygame.Surface((350, 900))
        self.card_background = pygame.Surface((350, 500))
        self.deck_background.fill((15, 15, 15))
        self.card_background.fill((15, 15, 15))

        self.current_deck = [Warrior for _ in range(30)]
        self.screen = screen

    def draw_text(self, surf, text, size, x, y, color=(200, 200, 200)):
        font = pygame.font.SysFont(FONT, size, bold=True)
        text_surface = font.render(text, True, color)
        surf.blit(text_surface, (x, y))

    def display_deck(self):
        for i in range(len(self.current_deck)):
            card = self.current_deck[i]
            self.draw_text(self.screen, f"{card.name} {card.power} {card.provision}", 20, 60, 225 + 28 * i)

    def diplay_info(self):
        if self.provision <= self.max_provision:
            self.draw_text(self.screen, f"{self.provision} {self.max_provision} (Имя, сила, провизия)", 20, 60, 185)
        else:
            self.draw_text(self.screen, f"{self.provision} {self.max_provision} (Имя, сила, провизия)", 20, 60, 185, (200, 40, 40))

    def display_card(self):
        if self.chosen_card in descriptions.keys():
            text = descriptions[self.chosen_card]
            print(text, "L" + self.chosen_card + ".png")
            image = load_image("CardsPictures\\L" + self.chosen_card + ".png", "C")
            self.screen.blit(image, (1050, 20, 496, 707))
            self.draw_text(self.screen, f"{self.chosen_card}", 30, 1560, 150)
            self.draw_text(self.screen, ", ".join(Warrior.tags), 25, 1560, 200)
            self.draw_text(self.screen, f"{text}", 20, 1560, 250)

Start_menu = Menu(SWIDTH, SHEIGHT)
Start_menu.set_button(300, 750, 200, 75, "Играть")
Start_menu.set_button(300, 850, 200, 75, "Конструктор колоды")
Start_menu.set_button(300, 950, 200, 75, "Выйти")

Play_menu = Menu(SWIDTH, SHEIGHT)
Play_menu.set_button(150, 700, 200, 75, "Битва с Северянами")
Play_menu.set_button(450, 700, 200, 75, "Битва с длинноухими")
Play_menu.set_button(300, 900, 200, 75, "Выйти в меню")

constructor = Constructor(SWIDTH, SHEIGHT, window_surface)
constructor.set_button(50, 100, 200, 75, "Сохранить колоду")
constructor.set_button(250, 100, 200, 75, "Очистить колоду")
constructor.set_button(1480, 950, 200, 75, "Добавить карту")
constructor.set_button(1710, 950, 200, 75, "Удалить карту")
constructor.set_button(50, 20, 200, 75, "Переименовать колоду")

constructor.set_button(1700, 20, 200, 75, "Выйти в меню")

menu_dict = {0: Start_menu, 1: Play_menu, 2: constructor}
menu_var = 0
while is_running:
    time_delta = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Выйти":
                is_running = False
            if event.ui_element.text == "Выйти в меню":
                menu_var = 0
            if event.ui_element.text == "Играть":
                menu_var = 1
            if event.ui_element.text == "Конструктор колоды":
                menu_var = 2
            if event.ui_element.text == "Сохранить колоду":
                print(constructor.entry.text)
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            # if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            constructor.chosen_card = event.text
        menu_dict[menu_var].manager.process_events(event)
        menu_dict[menu_var].manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    menu_dict[menu_var].manager.draw_ui(window_surface)
    if menu_var == 2:
        window_surface.blit(constructor.deck_background, (50, 178))
        window_surface.blit(constructor.card_background, (1550, 140))
        constructor.display_deck()
        constructor.diplay_info()
        constructor.display_card()
    pygame.display.update()
