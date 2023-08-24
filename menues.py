import pygame.image
import pygame_gui
from constants import *
from storages import Deck
from cards_descriptions import descriptions


class Menu:
    """ A class to represent a base menu with buttons and manager."""

    def __init__(self, x, y):
        self.buttons = []
        self.manager = pygame_gui.UIManager((x, y), 'theme.json')
        self.font20 = pygame.font.SysFont(FONT, 20, bold=True)
        self.font25 = pygame.font.SysFont(FONT, 25, bold=True)

    def set_button(self, x, y, width, height, text):
        """ Create a button with assigned args"""
        self.buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x, y), (width, height)), text=text,
                                                         manager=self.manager))

    def delete_all_buttons(self):
        for button in self.buttons:
            button.kill()

    def draw_text(self, surf, text, size, x, y, color=(200, 200, 200)):
        """ Draw line of text in given coordinates"""
        if size == 20:
            font = self.font20
        else:
            font = self.font25
        text_surface = font.render(text, True, color)
        surf.blit(text_surface, (x, y))


class GameUI:
    """ Menus that are shown during game """

    def __init__(self):
        self.buttons_group = {}
        self.state = "pause"
        self.font20 = pygame.font.SysFont(FONT, 20, bold=True)
        self.font25 = pygame.font.SysFont(FONT, 25, bold=True)

    def add_button(self, x, y, width, height, text, group):
        """ Add a button to buttons_group """
        if group in self.buttons_group.keys():
            button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x, y), (width, height)), text=text,
                                                  manager=self.buttons_group[group][0])
            self.buttons_group[group][1].append(button)
        else:
            self.create_group(group)
            button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x, y), (width, height)), text=text,
                                                  manager=self.buttons_group[group][0])
            self.buttons_group[group][1].append(button)

    def create_group(self, name):
        """ New group with its own manager"""
        if name not in self.buttons_group.keys():
            self.buttons_group[name] = (pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), 'theme.json'), [])


class Matchmaking(Menu):
    """A menu to display available opponents and the ability to choose who to play with """

    def __init__(self, x, y, screen):
        super().__init__(x, y)
        self.players_list = [1, 2, 4, 5, 6, 7, 8, 0]
        self.connect()
        self.init_enemies()
        self.screen = screen

    def connect(self):
        """ Connection to server """
        pass

    def init_enemies(self):
        """ Get info about players and create button for each of them"""
        for player in range(len(self.players_list)):
            self.set_button(300, 80 + 70 * player, 150, 60, str(self.players_list[player]))

    def show_enemies(self):
        """ Display available players """
        for player in range(len(self.players_list)):
            self.draw_text(self.screen, f"Сыграть с {self.players_list[player]}", 20, 100, 100 + 70 * player, color=(20, 20, 220))


class Constructor(Menu):
    """ A class to represent deck constructor, which give player an ability to create decks and change existing ones"""

    def __init__(self, x, y, screen, player):
        super().__init__(x, y)
        self.entry_name = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220, 20), (250, 75)),
                                                              manager=self.manager, initial_text="")
        self.entry_index = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1610, 1030), (300, 50)),
                                                               manager=self.manager,
                                                               initial_text="Введите индекс карты для удаления")
        self.decks = player.decks
        self.cards = {"Нет карты": None}
        self.chosen_card = None
        self.decks_drop_box = pygame_gui.elements.UIDropDownMenu(self.decks.keys(), manager=self.manager,
                                                                 relative_rect=pygame.Rect((480, 20), (250, 75)),
                                                                 starting_option=player.deck.name)
        self.max_provision = 150
        self.provision = 0

        self.deck_background = pygame.Surface((350, 900))
        self.card_background = pygame.Surface((350, 500))
        self.deck_background.fill((15, 15, 15))
        self.card_background.fill((15, 15, 15))

        self.current_deck = player.deck
        self.screen = screen
        self.player = player

    def full_box(self):
        self.cards_drop_box = pygame_gui.elements.UIDropDownMenu(self.cards.keys(), manager=self.manager,
                                                                 relative_rect=pygame.Rect((740, 20), (250, 75)),
                                                                 starting_option=list(self.cards.keys())[0])

    def display_deck(self):
        """ Render a column of chosen deck's cards (name, power and provision)"""
        if type(self.current_deck) == Deck:
            if len(self.current_deck.cards) > 1:
                for i in range(len(self.current_deck.cards)):
                    card = self.current_deck.cards[i]
                    self.draw_text(self.screen, f"{card.name} {card.power} {card.provision}", 20, 60, 225 + 28 * i)

    def display_info(self):
        """ Render text to inform player what is what"""
        if type(self.current_deck) == Deck:
            if len(self.current_deck.cards) > 1:
                self.provision = sum([self.cards[i.name].provision for i in self.current_deck.cards])
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
            image_name = f"CardsPictures\\{self.cards[self.chosen_card].fraction}\\L" + self.chosen_card + ".png"
            image = pygame.transform.scale(pygame.image.load(os.path.join(image_name)), (572, 820))
            lines = self.cards[self.chosen_card].description
            self.screen.blit(image, (980, 120, 572, 820))
            self.draw_text(self.screen, self.cards[self.chosen_card].name, 25, 1560, 160)
            self.draw_text(self.screen, ", ".join(self.cards[self.chosen_card].tags), 25, 1560, 200)
            for i in range(len(lines)):
                a = i * 25
                self.draw_text(self.screen, lines[i], 20, 1560, 250 + a)

    def rename_deck(self, new_name):
        """ Update DECK list with new name and rename deck itself"""
        from data import update_deck_name
        if type(self.current_deck) == Deck:
            self.player.decks[new_name] = self.player.decks.pop(self.current_deck.name)
            update_deck_name(self.player, new_name)
            self.current_deck.name = new_name

    def update_decks_box(self):
        """ Reset decks' drop box"""
        self.decks_drop_box.kill()
        self.decks_drop_box = pygame_gui.elements.UIDropDownMenu(self.decks.keys(), manager=self.manager,
                                                                 relative_rect=pygame.Rect((490, 20), (250, 75)),
                                                                 starting_option=self.player.deck.name)

    def new_deck(self):
        pass

    def save_deck(self):
        pass


def auth_buttons(menu, login):
    from requests import get
    menu.set_button(860, 800, 200, 75, "Выйти")
    try:
        client_id = open("player_data.txt").readline()
    except FileNotFoundError:
        with open("player_data.txt", "w") as new_data_file:
            print("", end='', file=new_data_file)
        client_id = open("player_data.txt").readline()
    if len(client_id) < 1 or login:
        menu.set_button(860, 700, 200, 75, "Войти")
        menu.message_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((800, 680), (320, 25)),
                                                         manager=menu.manager, text="")
        menu.entry_email = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((835, 500), (250, 75)),
                                                               manager=menu.manager, initial_text="Почта")
        menu.entry_password = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((835, 600), (250, 75)),
                                                                  manager=menu.manager,
                                                                  initial_text="Пароль")
    else:
        menu.message_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((800, 680), (320, 25)),
                                                         manager=menu.manager, text=f"Войти как {get(f'http://127.0.0.1:8080/api/v2/player/-1&-1&{client_id}&in_cid&0').json()[1]}")
        menu.set_button(860, 700, 200, 75, "Войти в аккаунт")
        menu.set_button(860, 600, 200, 75, "Войти в другой аккаунт")


def init_menu(start, play, cons, end, dd, mulligan):
    """ Create all buttons for the menus and load background image"""
    start.set_button(300, 750, 200, 75, "Играть")
    start.set_button(300, 850, 200, 75, "Конструктор колоды")
    start.set_button(300, 950, 200, 75, "Выйти")

    play.set_button(50, 700, 200, 75, "Битва с Северянами")
    play.set_button(550, 700, 200, 75, "Битва с длинноухими")
    play.set_button(300, 900, 200, 75, "Выйти в меню")

    cons.set_button(20, 100, 200, 75, "Сохранить колоду")
    cons.set_button(230, 100, 200, 75, "Очистить колоду")
    cons.set_button(1450, 950, 200, 75, "Добавить карту")
    cons.set_button(1680, 950, 200, 75, "Удалить карту")
    cons.set_button(20, 20, 200, 75, "Переименовать колоду")

    cons.set_button(1700, 20, 200, 75, "Выйти в меню")
    cons.set_button(1000, 20, 200, 75, "Создать новую колоду")

    end.set_button(700, 450, 200, 100, "Выйти в меню")

    dd.set_button(20, 1020, 120, 50, "Скрыть")

    mulligan.add_button(20, 1020, 120, 50, "Скрыть", "pause")
    mulligan.add_button(160, 1020, 220, 50, "Закончить смену карт", "pause")
    mulligan.add_button(90, 965, 220, 50, "Посмотреть колоду", "pause")
    mulligan.add_button(90, 910, 220, 50, "Посмотреть сброс", "pause")
    mulligan.add_button(90, 855, 220, 50, "Вернуться к смене", "pause")
    mulligan.add_button(20, 1020, 100, 50, "Вернуть", "game")
