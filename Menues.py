import pygame_gui
from CONSTANTS import *
from Data import DECKS_LIST, CARDS_LIST
from Storages import Deck
from Cards_Descriptions import descriptions


class Menu:
    """ A class to represent a base menu with buttons and manager."""

    def __init__(self, x, y):
        self.buttons = []
        self.manager = pygame_gui.UIManager((x, y), 'theme.json')

    def set_button(self, x, y, width, height, text):
        """ Create a button with assigned args"""
        self.buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x, y), (width, height)), text=text,
                                                         manager=self.manager))


class Constructor(Menu):
    """ A class to represent deck constructor, which give player an ability to create decks and change existing ones"""

    def __init__(self, x, y, screen):
        super().__init__(x, y)
        self.entry_name = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 20), (250, 75)),
                                                              manager=self.manager, initial_text="")
        self.entry_index = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1610, 1030), (300, 50)),
                                                               manager=self.manager,
                                                               initial_text="Введите индекс карты для удаления")
        self.decks = DECKS_LIST
        self.cards = CARDS_LIST
        self.chosen_card = None
        self.decks_drop_box = pygame_gui.elements.UIDropDownMenu(self.decks.keys(), manager=self.manager,
                                                                 relative_rect=pygame.Rect((520, 20), (250, 75)),
                                                                 starting_option=list(self.decks.keys())[0])
        self.cards_drop_box = pygame_gui.elements.UIDropDownMenu(self.cards.keys(), manager=self.manager,
                                                                 relative_rect=pygame.Rect((780, 20), (250, 75)),
                                                                 starting_option=list(self.cards.keys())[0])
        self.max_provision = 150
        self.provision = 0

        self.deck_background = pygame.Surface((350, 900))
        self.card_background = pygame.Surface((350, 500))
        self.deck_background.fill((15, 15, 15))
        self.card_background.fill((15, 15, 15))

        self.current_deck = None
        self.screen = screen

    def draw_text(self, surf, text, size, x, y, color=(200, 200, 200)):
        """ Draw line of text in given coordinates"""
        font = pygame.font.SysFont(FONT, size, bold=True)
        text_surface = font.render(text, True, color)
        surf.blit(text_surface, (x, y))

    def display_deck(self):
        """ Render a column of chosen deck's cards (name, power and provision)"""
        if type(self.current_deck) == Deck:
            if len(self.current_deck.cards) > 1:
                for i in range(len(self.current_deck.cards)):
                    card = self.current_deck.cards[i]
                    self.draw_text(self.screen, f"{card.name} {card.power} {card.provision}", 20, 60, 225 + 28 * i)

    def display_info(self):
        """ Render text to inform player what is what"""
        if self.current_deck:
            if len(self.current_deck.cards) > 1:
                self.provision = sum([CARDS_LIST[i.name].provision for i in self.current_deck.cards])
            else:
                self.provision = 0
        if self.provision <= self.max_provision:
            self.draw_text(self.screen, f"{self.provision} {self.max_provision} (Имя, сила, провизия)", 20, 60, 185)
        else:
            self.draw_text(self.screen, f"{self.provision} {self.max_provision} (Имя, сила, провизия)", 20, 60, 185,
                           (200, 40, 40))

    def display_card(self):
        """ Display info about card on the right of menu"""
        if self.chosen_card in descriptions.keys():
            image_name = "CardsPictures\\L" + self.chosen_card + ".png"
            image = pygame.transform.scale(pygame.image.load(os.path.join(image_name)), (496, 707))
            lines = self.cards[self.chosen_card].description
            self.screen.blit(image, (1050, 140, 496, 707))
            self.draw_text(self.screen, self.cards[self.chosen_card].name, 25, 1560, 160)
            self.draw_text(self.screen, self.cards[self.chosen_card].tags, 25, 1560, 200)
            for i in range(len(lines)):
                a = i * 25
                self.draw_text(self.screen, lines[i], 20, 1560, 250 + a)

    def rename_deck(self, new_name):
        """ Update DECK list with new name and rename deck itself"""
        if type(self.current_deck) == Deck:
            DECKS_LIST[new_name] = DECKS_LIST.pop(self.current_deck.name)
            self.current_deck.update_name(new_name)

    def update_decks_box(self):
        """ Reset decks' drop box"""
        self.decks_drop_box.kill()
        self.decks_drop_box = pygame_gui.elements.UIDropDownMenu(self.decks.keys(), manager=self.manager,
                                                                 relative_rect=pygame.Rect((520, 20), (250, 75)),
                                                                 starting_option=list(self.decks.keys())[0])

    def new_deck(self):
        pass

    def save_deck(self):
        pass


def init_menu(back, start, play, cons, end, pause):
    """ Create all buttons for the menus and load background image"""
    image = pygame.transform.scale(pygame.image.load(os.path.join('Field\\NG_loadscreen.png')), (1920, 1080))
    back.blit(image, (0, 0, SWIDTH, SHEIGHT))

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

    end.set_button(700, 450, 200, 100, "Выйти в меню")

    pause.set_button(800, 900, 200, 100, "Скрыть")
    pause.set_button(1100, 900, 200, 100, "Закончить смену карт")
