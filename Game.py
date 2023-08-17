import random
import pygame_gui
import sys
import time

from Cards import Card, Leader
from Field import Field, Row
from CONSTANTS import *
from Storages import Dump, Deck, Hand
from Player import Player
from Menues import Menu, Constructor, Matchmaking, GameUI, init_menu, auth_buttons
from PIL import Image, ImageEnhance, ImageFilter
log_file = open("log.txt", mode="w")
load_start_time = time.time()
pygame.init()

size = SWIDTH, SHEIGHT
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()
player = Player("127.0.0.1:8080")
GAME_FONT = pygame.font.SysFont(FONT, 26, bold=True)

auth_menu = Menu(SWIDTH, SHEIGHT)
auth_buttons(auth_menu, False)
image = pygame.transform.scale(pygame.image.load(os.path.join('Field\\loadscreen.png')), (1920, 1080))
background = pygame.Surface((SWIDTH, SHEIGHT))
background.blit(image, (0, 0, SWIDTH, SHEIGHT))
auth = True
print("LOAD LOG: auth time loading ", time.time() - load_start_time, file=log_file)
while auth:
    time_delta = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Выйти":
                auth = False
                sys.exit()
            if event.ui_element.text == "Войти":
                data = player.authorize(auth_menu.entry_email.text, auth_menu.entry_password.text)
                if data == 1:
                    player.import_decks()
                    auth = False
                else:
                    auth_menu.message_label.set_text(data)
            if event.ui_element.text == "Войти в аккаунт":
                try:
                    client_id = open("player_data.txt").readline()
                except FileNotFoundError:
                    with open("player_data.txt", "w") as new_data_file:
                        print("", end='', file=new_data_file)
                    client_id = open("player_data.txt").readline()
                data = player.authorize("", "", client_id)
                if data == 1:
                    player.import_decks()
                    auth = False
                else:
                    auth_menu.message_label.set_text(data)
            if event.ui_element.text == "Войти в другой аккаунт":
                auth_menu.delete_all_buttons()
                auth_menu.message_label.set_text("")
                auth_buttons(auth_menu, True)
        auth_menu.manager.process_events(event)
        auth_menu.manager.update(time_delta)
    screen.blit(background, (0, 0))
    auth_menu.manager.draw_ui(screen)
    pygame.display.update()
load_start_time = time.time()

start_menu = Menu(SWIDTH, SHEIGHT)
play_menu = Matchmaking(SWIDTH, SHEIGHT, screen)
constructor = Constructor(SWIDTH, SHEIGHT, screen, player)
end_menu = Menu(SWIDTH, SHEIGHT)
dd_menu = Menu(SWIDTH, SHEIGHT)
mulligan_menu = GameUI()

MENU_VAR = 0
PAUSE = False
CHOSEN_OBJECT = None
PLAYER_HAND = Hand()
OPPONENT_HAND = Hand()
PLAYER_DUMP = Dump("Сброс игрока")
OPPONENT_DUMP = Dump("Сброс ИИ")
FIELD = Field(screen, PLAYER_DUMP, PLAYER_HAND)
to_render = ""

menu_dict = {0: start_menu, 1: play_menu, 2: constructor, 3: "Game", 4: dd_menu, 5: mulligan_menu, 6: end_menu}
init_menu(start_menu, play_menu, constructor, end_menu, dd_menu, mulligan_menu)


def draw_text(surf, text, text_size, x, y):
    """ Draw line of text in given coordinates"""
    text_font = pygame.font.Font(pygame.font.match_font('arial'), text_size)
    text_area = text_font.render(text, True, (100, 100, 100))
    text_rect = text_area.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_area, text_rect)


def pause_game():
    """ Clear panel, set darken and blurred background, pause game"""
    global MENU_VAR, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP, PAUSE
    FIELD.set_panel_card(None)
    FIELD.render_game_field(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)
    FIELD.draw_rows()
    pygame.image.save(screen, "field_screen.jpg")
    im = Image.open("field_screen.jpg")
    im = im.filter(ImageFilter.GaussianBlur(radius=2))
    im = ImageEnhance.Brightness(im).enhance(0.7)
    im.save("background_field.jpg")
    FIELD.set_background(load_image("background_field.jpg", "O"))
    MENU_VAR = 4
    PAUSE = True


def end_move():
    """ When coin is clicked, this func checks field stats and
        change field if game is going to have a new round """
    global MENU_VAR, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    if (FIELD.can_play_card or len(PLAYER_HAND.cards) == 0) and FIELD.turn:
        FIELD.passes += 2
    MENU_VAR = FIELD.end_move()
    PLAYER_HAND.end_move(FIELD)
    if FIELD.pl_round_score == 2 or FIELD.op_round_score == 2:
        MENU_VAR = 6
        screen.blit(background, (0, 0))
        FIELD.draw_end()
        return
    if MENU_VAR == 5:
        pause_game()
        FIELD.chosen_storage = PLAYER_HAND
    if FIELD.turn is False:
        CHOSEN_OBJECT = None
        return str("Красная монета")
    else:
        CHOSEN_OBJECT = None
        return str("Синяя монета")


def in_area(coord, mouse_type, display):
    """ Check if mouse cursor is inside object's collision """
    global MENU_VAR, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    x, y = coord
    for game_object in CLICKABLE:
        if game_object and game_object.rect:
            if game_object.rect[0] < x < game_object.rect[0] + game_object.rect[2] and game_object.rect[1] < y < game_object.rect[1] + game_object.rect[3]:
                if mouse_type == 3:
                    action_on_hover(game_object, FIELD)
                else:
                    action_on_click(game_object, mouse_type, display, coord)
                return str(game_object.name)
        if mouse_type == 3:
            PLAYER_HAND.up_when_hovered(coord)
            for row in FIELD.rows:
                row.when_hovered(coord, CHOSEN_OBJECT, display)
    if mouse_type == 1:
        if 305 < x < 455 and 450 < y < 600:
            end_move()
        if 5 < x < 80 and 500 < y < 575:
            MENU_VAR = 6
            screen.blit(background, (0, 0))
            FIELD.draw_end()
    return "Nothing"


def deck_dump_hover(cards, mouse_pos, click_type):
    """ Check if mouse cursor is inside card's collision from deck, dump or hand"""
    global MENU_VAR
    x, y = mouse_pos
    for card in cards:
        if card.rect[0] < x < card.rect[0] + card.rect[2] and card.rect[1] < y < card.rect[1] + card.rect[3]:
            if click_type == 3:
                action_on_hover(card, FIELD)
            elif click_type == 1 and isinstance(FIELD.chosen_storage, Hand):
                card.location.mulligan(FIELD.pl_deck, card)


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
    if type(obj) == Card and FIELD.turn:
        CHOSEN_OBJECT = obj.on_click(FIELD, click_type, coordinates, CHOSEN_OBJECT)
    elif type(obj) == Leader and FIELD.turn:
        CHOSEN_OBJECT = obj.on_click(FIELD, click_type, CHOSEN_OBJECT)
    elif type(obj) == Deck and click_type == 1 and obj.player == "Me":
        if not PAUSE:
            pause_game()
            FIELD.chosen_storage = obj
            obj.random_order()
    elif type(obj) == Dump and click_type == 1:
        if not PAUSE:
            pause_game()
            FIELD.chosen_storage = obj
    elif type(obj) == Row and FIELD.turn:
        if type(CHOSEN_OBJECT) == Card and obj.player == "Me" and len(obj.cards) < 9 and type(CHOSEN_OBJECT.location) == Hand \
                and click_type == 1:
            PLAYER_HAND.play_card(CHOSEN_OBJECT)
            obj.add_card(CHOSEN_OBJECT, click_type, coordinates)
            CHOSEN_OBJECT.deploy(card=CHOSEN_OBJECT, field=FIELD, row=obj)
            FIELD.can_play_card = False
            CHOSEN_OBJECT = None


def get_player_deck(player):
    cards = []
    if player.deck:
        for i in player.deck.cards:
            card = i.copy()
            cards.append(card)
            CLICKABLE.append(card)
        return Deck(player.deck.name, "Me", cards, 1)
    return None


def set_game(enemy_frac, player, pl_deck_name='Мужик * на 30', op_deck_name='Мужик * на 30, x2'):
    """ Called when game is chosen. Forms players' decks and hands. Choose who has first game turn and set field"""
    global FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP
    set_game_start_time = time.time()
    player_deck = get_player_deck(player)
    for i in player_deck.cards:
        i.location = player_deck
    PLAYER_HAND.start_hand(player_deck)
    opponent_deck = get_player_deck(player)
    for i in opponent_deck.cards:
        i.location = opponent_deck
    OPPONENT_HAND.start_hand(opponent_deck)
    FIELD.turn = random.choice([True, False])
    FIELD.set_field(enemy_frac, player_deck, opponent_deck, CLICKABLE)
    CLICKABLE.reverse()  # reverse for the right order of objects (kinda importance sort)
    pause_game()
    FIELD.chosen_storage = PLAYER_HAND
    player.start_the_game()
    print("LOAD LOG: game loading time", time.time() - set_game_start_time, file=log_file)


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


print("LOAD LOG: post auth time loading ", time.time() - load_start_time, file=log_file)
connection_check_timer = 0.0
time_delta = clock.tick(FPS) / 1000.0
while running:
    connection_check_timer += time_delta
    if connection_check_timer > 1000:
        player.ensure_connection()
        connection_check_timer = 0

    if MENU_VAR < 3:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти":
                    running = False
                    player.exit()
                if event.ui_element.text == "Выйти в меню":
                    constructor.cards = {}
                    MENU_VAR = 0
                    player.find_opponents(stop=True)
                if event.ui_element.text == "Играть":
                    if player.deck:
                        MENU_VAR = 1
                        play_menu.init_enemies()
                        player.find_opponents(stop=False)
                if event.ui_element.text == "Конструктор колоды":
                    constructor.cards = player.import_cards()
                    constructor.full_box()
                    MENU_VAR = 2
                if event.ui_element.text == "Переименовать колоду":
                    constructor.rename_deck(constructor.entry_name.text)
                    constructor.update_decks_box()
                if event.ui_element.text == "Битва с Северянами":
                    end_game()
                    MENU_VAR = 3
                    set_game("NR", player)
                if event.ui_element.text == "Битва с длинноухими":
                    end_game()
                    MENU_VAR = 3
                    set_game("Scoia", player)
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.cards.keys():
                constructor.chosen_card = event.text
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.decks.keys():
                constructor.current_deck = constructor.decks[event.text]
                player.deck = constructor.current_deck
            if MENU_VAR < 3:
                menu_dict[MENU_VAR].manager.process_events(event)
                menu_dict[MENU_VAR].manager.update(time_delta)
        if MENU_VAR < 3:
            screen.blit(background, (0, 0))
            menu_dict[MENU_VAR].manager.draw_ui(screen)
            screen.blit(GAME_FONT.render(player.nickname, True, (200, 200, 200)), (20, 20))
        if MENU_VAR == 2:
            screen.blit(constructor.deck_background, (50, 178))
            screen.blit(constructor.card_background, (1550, 140))
            constructor.display_deck()
            constructor.display_info()
            constructor.display_card()
        if MENU_VAR == 1:
            play_menu.show_enemies()
        if MENU_VAR < 2:
            if player.deck:
                screen.blit(GAME_FONT.render(f"Выбранная колода: {player.deck.name}", True, (200, 200, 200)), (520, 870))
            else:
                screen.blit(GAME_FONT.render(f"Выбранная колода: нет", True, (200, 200, 200)), (520, 870))
        pygame.display.update()
    elif MENU_VAR == 3 or MENU_VAR == 4 or MENU_VAR == 5:
        if not PAUSE:
            FIELD.render_game_field(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)
            a = in_area(pygame.mouse.get_pos(), 3, screen)
            # to_render = f"{a, clock.get_fps()}"
            to_render = f"{a, pygame.mouse.get_pos()}"
            FIELD.draw_rows()
            # text_surface = GAME_FONT.render(to_render, True, (200, 200, 200))
            # screen.blit(text_surface, (250, 900))
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
        else:
            if isinstance(FIELD.chosen_storage, Deck):
                FIELD.check_deck(FIELD.chosen_storage)
            elif isinstance(FIELD.chosen_storage, Hand):
                FIELD.mulligan_hand(mulligan_menu.state)
                MENU_VAR = 5
            elif isinstance(FIELD.chosen_storage, Dump):
                FIELD.check_dump(FIELD.chosen_storage)
            else:
                FIELD.mulligan_hand(mulligan_menu.state)
                FIELD.render_game_field(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)
                a = in_area(pygame.mouse.get_pos(), 3, screen)
                FIELD.draw_rows()

            if FIELD.chosen_storage:
                deck_dump_hover(FIELD.chosen_storage.cards, pygame.mouse.get_pos(), 3)
            FIELD.render_panel()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if MENU_VAR == 4:
                        if any([i.hover_point(pos[0], pos[1]) for i in dd_menu.buttons]):
                            PAUSE = False
                            MENU_VAR = 3
                            FIELD.back_to_game(FIELD.chosen_storage)
                            FIELD.set_panel_card(None)
                            break
                    elif MENU_VAR == 5:
                        if mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][1].hover_point(pos[0], pos[1]):  # end mulligan button
                            PAUSE = False
                            MENU_VAR = 3
                            FIELD.back_to_game(FIELD.chosen_storage, True)
                            PLAYER_HAND.end_mulligan(FIELD.pl_deck)
                            FIELD.set_panel_card(None)
                            break
                        elif mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][0].hover_point(pos[0], pos[1]):  # hide mulligan button
                            FIELD.back_to_game(FIELD.chosen_storage, True)
                            FIELD.set_panel_card(None)
                            mulligan_menu.state = "game"
                        elif mulligan_menu.state == "game" and mulligan_menu.buttons_group["game"][1][0].hover_point(pos[0], pos[1]):  # back to mulligan button
                            mulligan_menu.state = "pause"
                            FIELD.chosen_storage = PLAYER_HAND
                            pause_game()
                        elif mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][2].hover_point(pos[0], pos[1]):  # go to deck button
                            FIELD.chosen_storage = FIELD.pl_deck
                            FIELD.set_panel_card(None)
                            FIELD.chosen_storage.random_order()
                            FIELD.check_deck(FIELD.chosen_storage)
                        elif mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][3].hover_point(pos[0], pos[1]):  # go to dump button
                            FIELD.chosen_storage = PLAYER_DUMP
                            FIELD.set_panel_card(None)
                            FIELD.check_dump(FIELD.chosen_storage)
                        elif mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][4].hover_point(pos[0], pos[1]):  # go to mulligan button
                            FIELD.chosen_storage = PLAYER_HAND
                            FIELD.set_panel_card(None)
                            FIELD.mulligan_hand(mulligan_menu.state)
                    if FIELD.chosen_storage:
                        deck_dump_hover(FIELD.chosen_storage.cards, pos, 1)
                if MENU_VAR == 4:
                    dd_menu.manager.update(clock.tick(FPS) / 1000.0)
                elif MENU_VAR == 5:
                    mulligan_menu.buttons_group[mulligan_menu.state][0].update(clock.tick(FPS) / 1000.0)

            if MENU_VAR == 4:
                dd_menu.manager.draw_ui(screen)
            elif MENU_VAR == 5:
                mulligan_menu.buttons_group[mulligan_menu.state][0].draw_ui(screen)
                FIELD.draw_text(screen, "Осталось замен " + str(PLAYER_HAND.mulligans), 20, 165, 35)
            pygame.display.update()
    elif MENU_VAR == 6:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти в меню":
                    MENU_VAR = 0
                    player.end_the_game()
            menu_dict[MENU_VAR].manager.process_events(event)
            menu_dict[MENU_VAR].manager.update(30 / 1000)
        menu_dict[MENU_VAR].manager.draw_ui(screen)
        pygame.display.update()
    clock.tick(FPS)
pygame.quit()
log_file.close()