import random
import pygame_gui
import types

from Cards import Card, Leader
from Field import Field, Row
from CONSTANTS import *
from Storages import Dump, Deck, Hand
from Data import DECKS_LIST, CARDS_LIST, METHOD_LIST
from Menues import Menu, Constructor, init_menu

pygame.init()

size = SWIDTH, SHEIGHT
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

start_menu = Menu(SWIDTH, SHEIGHT)
play_menu = Menu(SWIDTH, SHEIGHT)
constructor = Constructor(SWIDTH, SHEIGHT, screen)
end_menu = Menu(SWIDTH, SHEIGHT)
pause_menu = Menu(SWIDTH, SHEIGHT)
background = pygame.Surface((SWIDTH, SHEIGHT))

MENU_VAR = 0
GAME_FONT = pygame.font.SysFont(FONT, 30, bold=True)
PAUSE = False
CHOSEN_OBJECT = None
FIELD = Field(screen)
PLAYER_HAND = Hand()
OPPONENT_HAND = Hand()
PLAYER_DUMP = Dump("Сброс игрока")
OPPONENT_DUMP = Dump("Сброс ИИ")
to_render = ""

menu_dict = {0: start_menu, 1: play_menu, 2: constructor, 3: "Game", 4: pause_menu, 5: end_menu}
init_menu(background, start_menu, play_menu, constructor, end_menu, pause_menu)


def draw_text(surf, text, text_size, x, y):
    """ Draw line of text in given coordinates"""
    text_font = pygame.font.Font(pygame.font.match_font('arial'), text_size)
    text_area = text_font.render(text, True, (100, 100, 100))
    text_rect = text_area.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_area, text_rect)


def in_area(coord, mouse_type, display):
    """ Check if mouse cursor is inside object's collision"""
    global MENU_VAR, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    x, y = coord
    for game_object in CLICKABLE:
        if game_object and game_object.rect:
            if game_object.rect[0] < x < game_object.rect[0] + game_object.rect[2] and game_object.rect[1] < y < game_object.rect[1] + game_object.rect[3]:
                if mouse_type == 3:
                    action_on_hover(game_object, FIELD)
                else:
                    if FIELD.turn:
                        action_on_click(game_object, mouse_type, display, coord)
                return str(game_object.name)
        if mouse_type == 3:
            PLAYER_HAND.up_when_hovered(coord)
            for row in FIELD.rows_list:
                row.when_hovered(coord, CHOSEN_OBJECT, display)
    if mouse_type == 1:
        if 305 < x < 455 and 450 < y < 600:
            if (FIELD.can_play_card or len(PLAYER_HAND.cards) == 0) and FIELD.turn:
                FIELD.passes += 2
            FIELD.make_move()
            PLAYER_HAND.make_move(FIELD)
            if FIELD.pl_round_score == 2 or FIELD.op_round_score == 2:
                MENU_VAR = 5
                screen.blit(background, (0, 0))
                FIELD.draw_end()
            if FIELD.turn is False:
                CHOSEN_OBJECT = None
                return str("Красная монета")
            else:
                CHOSEN_OBJECT = None
                return str("Синяя монета")
        if 5 < x < 80 and 500 < y < 575:
            MENU_VAR = 5
            screen.blit(background, (0, 0))
            FIELD.draw_end()
    return "Nothing"


def action_on_hover(obj, game_field):
    """ Act according hovered object"""
    if type(obj) == Card:
        game_field.set_panel_card(obj)
        if obj.location.str_type == "Row":
            if type(CHOSEN_OBJECT) == Card and type(CHOSEN_OBJECT.location) == Hand:
                obj.location.lit(screen, True)
            else:
                obj.location.lit(screen, False)
    if type(obj) == Leader:
        game_field.set_panel_card(obj)
    if type(obj) == Row:
        if not PAUSE:
            if type(CHOSEN_OBJECT) == Card and type(CHOSEN_OBJECT.location) == Hand:
                obj.lit(screen, True)
            else:
                obj.lit(screen, False)


def action_on_click(obj, click_type, display, coordinates):
    """ Act according clicked object"""
    global CHOSEN_OBJECT, PAUSE, MENU_VAR, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    if type(obj) == Card:
        CHOSEN_OBJECT = obj.on_click(FIELD, click_type, coordinates, CHOSEN_OBJECT)
    elif type(obj) == Leader and obj.fraction == "Королевства Севера":
        CHOSEN_OBJECT = obj.on_click(FIELD, click_type, CHOSEN_OBJECT)
    elif type(obj) == Deck and click_type == 1:
        if not PAUSE:
            surface = pygame.transform.smoothscale(display, (500, 400))
            blur = pygame.transform.smoothscale(surface, (SWIDTH, SHEIGHT))
            PAUSE = True
            display.blit(blur, (0, 0))
            MENU_VAR = 4
        else:
            PAUSE = False
    elif type(obj) == Dump and click_type == 1:
        if not PAUSE:
            surface = pygame.transform.smoothscale(screen, (500, 400))
            blur = pygame.transform.smoothscale(surface, (SWIDTH, SHEIGHT))
            PAUSE = True
            display.blit(blur, (0, 0))
            MENU_VAR = 4
        else:
            PAUSE = False

    elif type(obj) == Row:
        if type(CHOSEN_OBJECT) == Card and obj.player == "Human" and len(obj.cards) < 9 and type(CHOSEN_OBJECT.location) == Hand \
                and click_type == 1:
            PLAYER_HAND.play_card(CHOSEN_OBJECT)
            obj.add_card(CHOSEN_OBJECT, click_type, coordinates)
            CHOSEN_OBJECT.deploy(card=CHOSEN_OBJECT, field=FIELD, row=obj)
            FIELD.can_play_card = False
            CHOSEN_OBJECT = None


def set_deck(deck_name):
    """ Return copy of a deck with 'deck name' from DECK_LIST"""
    cards = []
    for i in DECKS_LIST[deck_name].cards:
        card = i.copy()
        card.deployment = types.MethodType(METHOD_LIST[i.name + ' deploy'], card)
        cards.append(card)
        CLICKABLE.append(card)
    return Deck(deck_name, cards)


def set_game(enemy_frac, pl_deck_name='Мужик * на 30', op_deck_name='Мужик * на 30, x2'):
    """ Called when game is chosen. Forms players' decks and hands. Choose who has first game turn and set field"""
    global FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    player_deck = set_deck(pl_deck_name)
    for i in player_deck.cards:
        i.location = player_deck
    PLAYER_HAND.start_hand(player_deck)
    opponent_deck = set_deck(op_deck_name)
    for i in opponent_deck.cards:
        i.location = opponent_deck
    OPPONENT_HAND.start_hand(opponent_deck)
    FIELD.turn = random.choice([True, False])
    FIELD.set_field(enemy_frac, player_deck, opponent_deck, CLICKABLE)
    CLICKABLE.reverse()  # reverse for the right order of objects (kinda importance sort)


def end_game():
    """ Nulling CLICKABLE and refreshes game, hands and dumps"""
    global CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP, CLICKABLE
    CHOSEN_OBJECT = None
    CLICKABLE = []
    FIELD.refresh(CLICKABLE)
    PLAYER_HAND.refresh()
    OPPONENT_HAND.refresh()
    PLAYER_DUMP.refresh(CLICKABLE)
    OPPONENT_DUMP.refresh(CLICKABLE)


while running:
    if MENU_VAR < 3:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти":
                    running = False
                if event.ui_element.text == "Выйти в меню":
                    MENU_VAR = 0
                if event.ui_element.text == "Играть":
                    MENU_VAR = 1
                if event.ui_element.text == "Конструктор колоды":
                    MENU_VAR = 2
                if event.ui_element.text == "Переименовать колоду":
                    constructor.rename_deck(constructor.entry_name.text)
                    constructor.update_decks_box()
                if event.ui_element.text == "Битва с Северянами":
                    end_game()
                    MENU_VAR = 3
                    set_game("NR")
                if event.ui_element.text == "Битва с длинноухими":
                    end_game()
                    MENU_VAR = 3
                    set_game("Scoia")
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.cards.keys():
                constructor.chosen_card = event.text
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.decks.keys():
                constructor.current_deck = constructor.decks[event.text]
            if MENU_VAR < 3:
                menu_dict[MENU_VAR].manager.process_events(event)
                menu_dict[MENU_VAR].manager.update(time_delta)
        if MENU_VAR < 3:
            screen.blit(background, (0, 0))
            menu_dict[MENU_VAR].manager.draw_ui(screen)
        if MENU_VAR == 2:
            screen.blit(constructor.deck_background, (50, 178))
            screen.blit(constructor.card_background, (1550, 140))
            constructor.display_deck()
            constructor.display_info()
            constructor.display_card()
        pygame.display.update()
    elif MENU_VAR == 3 or MENU_VAR == 4:
        if not PAUSE:
            FIELD.render_game_field(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)
            a = in_area(pygame.mouse.get_pos(), 3, screen)
            to_render = f"{a, clock.get_fps()}"
            # to_render = f"{a, pygame.mouse.get_pos()}"
            FIELD.draw_rows()
            text_surface = GAME_FONT.render(to_render, True, (200, 200, 200))
            screen.blit(text_surface, (250, 900))
        else:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    PAUSE = False
                    MENU_VAR = 3
                    break
                menu_dict[MENU_VAR].manager.process_events(event)
                menu_dict[MENU_VAR].manager.update(30 / 1000)
            if MENU_VAR == 4:
                menu_dict[MENU_VAR].manager.draw_ui(screen)
            pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                MENU_VAR = 0
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    a = in_area(event.pos, 1, screen)
                    to_render = f"{event.pos}, {a}"
                elif event.button == 3:
                    a = in_area(event.pos, 2, screen)
                    to_render = f"{event.pos}, 2"
                    if type(CHOSEN_OBJECT) == Card:
                        CHOSEN_OBJECT.status = "passive"
                        CHOSEN_OBJECT = None
        pygame.display.flip()
        clock.tick(FPS)
    elif MENU_VAR == 5:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти в меню":
                    MENU_VAR = 0
            menu_dict[MENU_VAR].manager.process_events(event)
            menu_dict[MENU_VAR].manager.update(30 / 1000)
        menu_dict[MENU_VAR].manager.draw_ui(screen)
        pygame.display.update()
pygame.quit()
