import pygame
import pygame_gui
import os
# import sqlite3
from CONSTANTS import *
from Data import decks_list, cards_list
from Storages import Deck
from Cards_Descriptions import descriptions


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
        self.entry_name = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 20), (250, 75)),
                                                              manager=self.manager, initial_text="")
        self.entry_index = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1610, 1030), (300, 50)),
                                                               manager=self.manager,
                                                               initial_text="Введите индекс карты для удаления")
        self.decks = decks_list
        self.cards = cards_list
        self.chosen_card = None
        self.decks_drop_box = pygame_gui.elements.UIDropDownMenu(self.decks.keys(),
                                                                 relative_rect=pygame.Rect((520, 20), (250, 75)),
                                                                 manager=self.manager, starting_option=list(self.decks.keys())[0])
        self.cards_drop_box = pygame_gui.elements.UIDropDownMenu(self.cards.keys(),
                                                                 relative_rect=pygame.Rect((780, 20), (250, 75)),
                                                                 manager=self.manager, starting_option=list(self.cards.keys())[0])
        self.max_provision = 150
        self.provision = 0

        self.deck_background = pygame.Surface((350, 900))
        self.card_background = pygame.Surface((350, 500))
        self.deck_background.fill((15, 15, 15))
        self.card_background.fill((15, 15, 15))

        self.current_deck = None
        self.screen = screen

    def draw_text(self, surf, text, size, x, y, color=(200, 200, 200)):
        font = pygame.font.SysFont(FONT, size, bold=True)
        text_surface = font.render(text, True, color)
        surf.blit(text_surface, (x, y))

    def display_deck(self):
        if type(self.current_deck) == Deck:
            if len(self.current_deck.cards) > 1:
                for i in range(len(self.current_deck.cards)):
                    card = self.current_deck.cards[i]
                    self.draw_text(self.screen, f"{card.name} {card.power} {card.provision}", 20, 60, 225 + 28 * i)

    def display_info(self):
        if self.current_deck:
            if len(self.current_deck.cards) > 1:
                self.provision = sum([cards_list[i.name].provision for i in self.current_deck.cards])
            else:
                self.provision = 0
        if self.provision <= self.max_provision:
            self.draw_text(self.screen, f"{self.provision} {self.max_provision} (Имя, сила, провизия)", 20, 60, 185)
        else:
            self.draw_text(self.screen, f"{self.provision} {self.max_provision} (Имя, сила, провизия)", 20, 60, 185,
                           (200, 40, 40))

    def display_card(self):
        if self.chosen_card in descriptions.keys():
            text = descriptions[self.chosen_card]
            print(text, "L" + self.chosen_card + ".png")
            image = load_image("CardsPictures\\L" + self.chosen_card + ".png", "C")
            self.screen.blit(image, (1050, 140, 496, 707))
            self.draw_text(self.screen, f"{self.chosen_card}", 30, 1560, 150)
            self.draw_text(self.screen, ", ".join(self.cards[self.chosen_card].tags), 25, 1560, 200)
            self.draw_text(self.screen, f"{text}", 20, 1560, 250)

    def rename_deck(self, new_name):
        if type(self.current_deck) == Deck:
            decks_list[new_name] = decks_list.pop(self.current_deck.name)
            self.current_deck.update_name(new_name)

    def update_decks_box(self):
        self.decks_drop_box.kill()
        self.decks_drop_box = pygame_gui.elements.UIDropDownMenu(self.decks.keys(),
                                                                 relative_rect=pygame.Rect((520, 20), (250, 75)),
                                                                 manager=self.manager, starting_option=list(self.decks.keys())[0])

    def new_deck(self):
        pass

    def save_deck(self):
        pass


def init_menu(back, start, play, cons):
    back.blit(load_image('Field\\NG_loadscreen.png', "HD"), (0, 0, SWIDTH, SHEIGHT))

    start.set_button(300, 750, 200, 75, "Играть")
    start.set_button(300, 850, 200, 75, "Конструктор колоды")
    start.set_button(300, 950, 200, 75, "Выйти")

    play.set_button(150, 700, 200, 75, "Битва с Северянами")
    play.set_button(450, 700, 200, 75, "Битва с длинноухими")
    play.set_button(300, 900, 200, 75, "Выйти в меню")

    cons.set_button(50, 100, 200, 75, "Сохранить колоду")
    cons.set_button(250, 100, 200, 75, "Очистить колоду")
    cons.set_button(1480, 950, 200, 75, "Добавить карту")
    cons.set_button(1710, 950, 200, 75, "Удалить карту")
    cons.set_button(50, 20, 200, 75, "Переименовать колоду")

    cons.set_button(1700, 20, 200, 75, "Выйти в меню")
    cons.set_button(1050, 20, 200, 75, "Создать новую колоду")
