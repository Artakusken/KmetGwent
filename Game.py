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
to_render = ""

menu_dict = {0: start_menu, 1: play_menu, 2: constructor, 3: "Game", 4: pause_menu, 5: end_menu}
init_menu(background, start_menu, play_menu, constructor, end_menu, pause_menu)


def draw_text(surf, text, text_size, x, y):
    text_font = pygame.font.Font(pygame.font.match_font('arial'), text_size)
    text_area = text_font.render(text, True, (100, 100, 100))
    text_rect = text_area.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_area, text_rect)


def in_area(coord, mouse_type, game_field, display):
    global MENU_VAR
    x, y = coord
    for i in CLICKABLE:
        if i and i.rect:
            if i.rect[0] < x < i.rect[0] + i.rect[2] and i.rect[1] < y < i.rect[1] + i.rect[3]:
                if mouse_type == 3:
                    action_on_hover(i, game_field)
                else:
                    action_on_click(i, mouse_type, game_field, display)
                return str(i.name)
        if mouse_type == 3:
            pl_hand.up_when_hovered(coord)
            for i in game_field.rows_list:
                i.up_when_hovered(coord)
    if mouse_type == 1:
        if 155 < x < 305 and 450 < y < 600:
            if game_field.turn is False:
                game_field.turn = True
                return str("Красная монета")
            else:
                game_field.turn = False
                return str("Синяя монета")
        if 5 < x < 80 and 500 < y < 575:
            MENU_VAR = 5
            game_field.player_score = sum(game_field.count_score("Human"))
            game_field.opponent_score = sum(game_field.count_score("AI"))
            screen.blit(background, (0, 0))
            game_field.draw_end()
    return "Nothing"


def action_on_hover(obj, game_field):
    if type(obj) == Card:
        game_field.set_panel_card(obj)
    if type(obj) == Leader:
        game_field.set_panel_card(obj)
    if type(obj) == Row:
        if not PAUSE:
            if type(CHOSEN_OBJECT) == Card:
                obj.lit(screen, True)
            else:
                obj.lit(screen, False)


def action_on_click(obj, click_type, game_field, display):
    global CHOSEN_OBJECT, PAUSE, MENU_VAR
    if type(obj) == Card:
        if obj.status != "chosen" and obj.status != "played" and click_type == 1:
            obj.status = "chosen"
            if CHOSEN_OBJECT:
                CHOSEN_OBJECT.status = 'passive'
            CHOSEN_OBJECT = obj
        elif obj.status == "chosen" and click_type != 3:
            obj.status = "passive"
            CHOSEN_OBJECT = None
    elif type(obj) == Leader:
        if CHOSEN_OBJECT:
            CHOSEN_OBJECT.status = 'passive'
            CHOSEN_OBJECT = obj
        if type(game_field.panel) != Leader and click_type == 1:
            print("Leader extra ability")
        if type(game_field.panel) == Leader and click_type == 2:
            print("Leader main ability")
        CHOSEN_OBJECT = obj
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
        if type(CHOSEN_OBJECT) == Card and obj.player == "Human" and len(obj.cards) < 9 and type(CHOSEN_OBJECT.location) == Hand:
            hand = CHOSEN_OBJECT.location.cards
            obj.cards.append(CHOSEN_OBJECT)
            hand.pop(CHOSEN_OBJECT.hand_position)
            if len(hand) > 1:
                for i in hand[CHOSEN_OBJECT.hand_position::]:
                    i.hand_position -= 1
            CHOSEN_OBJECT.location = obj
            CHOSEN_OBJECT.status = "played"
            CHOSEN_OBJECT = None


def set_game(display, enemy_frac, pl_deck_name='Мужик * на 30', op_deck_name='Мужик * на 30, x2'):
    player_leader = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 685)
    if enemy_frac == "Scoia":
        opponent_leader = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 70)
        game_field = Field(opponent_leader, player_leader, display, "Scoia")
    else:
        opponent_leader = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 70)
        game_field = Field(opponent_leader, player_leader, display, "NR")
    player_dump = Dump("Сброс игрока")
    player_hand = Hand()
    opponent_dump = Dump("Сброс противника")
    opponent_hand = Hand()
    player_deck = DECKS_LIST[pl_deck_name]
    player_hand.start_hand(player_deck)
    opponent_deck = DECKS_LIST[op_deck_name]
    opponent_hand.start_hand(opponent_deck)
    game_field.turn = random.choice([True, False])
    return player_leader, opponent_leader, game_field, player_deck, opponent_deck, player_hand, opponent_hand, player_dump, opponent_dump


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
                    MENU_VAR = 3
                    pl_leader, op_leader, field, pl_deck, op_deck, pl_hand, op_hand, pl_dump, op_dump = set_game(screen, "NR")
                if event.ui_element.text == "Битва с длинноухими":
                    MENU_VAR = 3
                    pl_leader, op_leader, field, pl_deck, op_deck, pl_hand, op_hand, pl_dump, op_dump = set_game(screen, "Scoia")
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
            field.render_ui_images()
            field.render_ui_leader()
            field.render_text(op_leader, pl_leader, pl_hand, pl_deck, pl_dump, op_hand, op_deck, op_dump)
            field.draw_hand(pl_hand)
            a = in_area(pygame.mouse.get_pos(), 3, field, screen)
            to_render = f"{a, clock.get_fps()}"
            field.draw_rows()
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    MENU_VAR = 0
                if event.key == pygame.K_a:
                    field.set_crowns(True)
                if event.key == pygame.K_s:
                    field.set_crowns(False)
                if event.key == pygame.K_d:
                    field.round += 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    a = in_area(event.pos, 1, field, screen)
                    to_render = f"{event.pos}, {a}"
                elif event.button == 3:
                    a = in_area(event.pos, 2, field, screen)
                    to_render = f"{event.pos}, 2"
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

# for i in CLICKABLE:
#     if type(i) != Card:
#         print(type(i), i.name, i.rect)
