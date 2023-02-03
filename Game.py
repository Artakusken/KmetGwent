import random
import pygame
import os
import pygame_gui

from Cards import Card, Leader
from Field import Field, Row
from CONSTANTS import *
from Storages import Dump, Deck, Hand
from Data import DECKS_LIST, CARDS_LIST
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
    text_font = pygame.font.Font(pygame.font.match_font('arial'), text_size)
    text_area = text_font.render(text, True, (100, 100, 100))
    text_rect = text_area.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_area, text_rect)


def in_area(coord, mouse_type, display):
    global MENU_VAR, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    x, y = coord
    for i in CLICKABLE:
        if i and i.rect:
            if i.rect[0] < x < i.rect[0] + i.rect[2] and i.rect[1] < y < i.rect[1] + i.rect[3]:
                if mouse_type == 3:
                    action_on_hover(i, FIELD)
                else:
                    if FIELD.turn:
                        action_on_click(i, mouse_type, display)
                return str(i.name)
        if mouse_type == 3:
            PLAYER_HAND.up_when_hovered(coord)
            for i in FIELD.rows_list:
                i.up_when_hovered(coord)
    if mouse_type == 1:
        if 305 < x < 455 and 450 < y < 600:
            if (FIELD.can_play_card or len(PLAYER_HAND.cards) == 0) and FIELD.turn:
                FIELD.passes += 2
            FIELD.make_move()
            PLAYER_HAND.make_move()
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
    if type(obj) == Card:
        game_field.set_panel_card(obj)
    if type(obj) == Leader:
        game_field.set_panel_card(obj)
    if type(obj) == Row:
        if not PAUSE:
            if type(CHOSEN_OBJECT) == Card and type(CHOSEN_OBJECT.location) == Hand:
                obj.lit(screen, True)
            else:
                obj.lit(screen, False)


def action_on_click(obj, click_type, display):
    global CHOSEN_OBJECT, PAUSE, MENU_VAR, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    if type(obj) == Card:
        if type(obj.location) == Hand and FIELD.can_play_card:
            if obj.status == "passive" and click_type == 1:
                obj.status = "chosen"
                if type(CHOSEN_OBJECT) == Card or type(CHOSEN_OBJECT) == Leader:
                    CHOSEN_OBJECT.status = 'passive'
                CHOSEN_OBJECT = obj
            elif obj.status == "chosen":
                obj.status = "passive"
                CHOSEN_OBJECT = None
        elif type(obj.location) == Row:
            if obj.status == "passive" and click_type == 1:
                obj.status = "chosen"
                if type(CHOSEN_OBJECT) == Card or type(CHOSEN_OBJECT) == Leader:
                    CHOSEN_OBJECT.status = 'passive'
                CHOSEN_OBJECT = obj
            elif obj.status == "chosen":
                obj.status = "passive"
                CHOSEN_OBJECT = None
    elif type(obj) == Leader and obj.fraction == "Королевства Севера":
        if obj.status == "passive" and click_type == 1:
            obj.status = "chosen extra ability"
            if type(CHOSEN_OBJECT) == Card or type(CHOSEN_OBJECT) == Leader:
                CHOSEN_OBJECT.status = 'passive'
            CHOSEN_OBJECT = obj
        elif obj.status == "chosen extra ability" and click_type == 1:
            obj.status = "passive"
            CHOSEN_OBJECT = None
        if obj.status == "passive" and click_type == 2:
            obj.status = "chosen main ability"
            if type(CHOSEN_OBJECT) == Card or type(CHOSEN_OBJECT) == Leader:
                CHOSEN_OBJECT.status = 'passive'
            CHOSEN_OBJECT = obj
        elif obj.status == "chosen main ability" and click_type == 2:
            obj.status = "passive"
            CHOSEN_OBJECT = None
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
            obj.cards.append(CHOSEN_OBJECT)
            PLAYER_HAND.cards.pop(CHOSEN_OBJECT.hand_position)
            if len(PLAYER_HAND.cards) > 1:
                for i in PLAYER_HAND.cards[CHOSEN_OBJECT.hand_position::]:
                    i.hand_position -= 1
            CHOSEN_OBJECT.location = obj
            CHOSEN_OBJECT.status = "passive"
            CHOSEN_OBJECT.row = obj.row
            CHOSEN_OBJECT.column = len(obj.cards) - 1
            FIELD.can_play_card = False
            CHOSEN_OBJECT = None


def set_game(enemy_frac, pl_deck_name='Мужик * на 30', op_deck_name='Мужик * на 30, x2'):
    global FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    cards = []
    for i in DECKS_LIST[pl_deck_name].cards:
        name = CARDS_LIST[i.name].name
        base_power = CARDS_LIST[i.name].bp
        armor = CARDS_LIST[i.name].armor
        provision = CARDS_LIST[i.name].provision
        image = CARDS_LIST[i.name].image_path
        tags = CARDS_LIST[i.name].tags
        card_type = CARDS_LIST[i.name].card_type
        fraction = CARDS_LIST[i.name].fraction
        card = Card(name, base_power, image, armor, provision, card_type, fraction, tags)
        cards.append(card)
        CLICKABLE.append(card)
    player_deck = Deck(pl_deck_name, cards)
    PLAYER_HAND.start_hand(player_deck)
    cards = []
    for i in DECKS_LIST[pl_deck_name].cards:
        name = CARDS_LIST[i.name].name
        base_power = CARDS_LIST[i.name].bp
        armor = CARDS_LIST[i.name].armor
        provision = CARDS_LIST[i.name].provision
        image = CARDS_LIST[i.name].image_path
        tags = CARDS_LIST[i.name].tags
        card_type = CARDS_LIST[i.name].card_type
        fraction = CARDS_LIST[i.name].fraction
        card = Card(name, base_power, image, armor, provision, card_type, fraction, tags)
        cards.append(card)
        CLICKABLE.append(card)
    opponent_deck = Deck(op_deck_name, cards)
    OPPONENT_HAND.start_hand(opponent_deck)
    FIELD.turn = random.choice([True, False])
    FIELD.set_field(enemy_frac, player_deck, opponent_deck, CLICKABLE)
    CLICKABLE.reverse()


def end_game():
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
            FIELD.render_ui_images()
            FIELD.render_ui_leader()
            FIELD.render_text(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)
            FIELD.draw_hand(PLAYER_HAND)
            a = in_area(pygame.mouse.get_pos(), 3, screen)
            to_render = f"{a, clock.get_fps()}"
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
