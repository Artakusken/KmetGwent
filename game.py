import random

import pygame.image
import pygame_gui
import sys
import time

from cards import Card, Leader
from field import Field, Row
from constants import *
from storages import Dump, Deck, Hand
from player import Player
from menues import Menu, Constructor, Matchmaking, GameUI, init_menu, auth_buttons
from PIL import Image, ImageEnhance, ImageFilter


log_file = open("info files\\log.txt", mode="w")
print("LOG: ", time.ctime(), file=log_file)
load_start_time = time.time()


pygame.init()
size = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode(size)
running = True  # game loop bool variable
clock = pygame.time.Clock()

georgia_font_26 = pygame.font.SysFont(FONT, 26, bold=True)
loadscreen = pygame.transform.scale(pygame.image.load(os.path.join('Field\\loadscreen.png')), (1920, 1080))
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.blit(loadscreen, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

auth_menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)  # authorization menu
auth_buttons(auth_menu, False)  # add specialized button for auth menu
player = Player("127.0.0.1:8080")
auth = True  # authorization loop bool variable

print("LOAD LOG: auth time loading ", time.time() - load_start_time, file=log_file)

while auth:  # authorization loop
    time_delta = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Выйти":
                auth = False
                sys.exit()
            if event.ui_element.text == "Войти":  # login with input data
                data = player.authorize(auth_menu.entry_email.text, auth_menu.entry_password.text)  # GET request with email and password
                if data == 1:  # authorization completed successfully
                    player.import_decks()  # player get info about all his decks, and creates all this decks (see change n. 5)
                    auth = False
                else:
                    auth_menu.message_label.set_text(data)  # server connection error notification
            if event.ui_element.text == "Войти в аккаунт":  # login with user cid (client ID)
                try:
                    client_id = open("player_data.txt").readline()  # get client id from local file
                except FileNotFoundError:  # create such file
                    with open("player_data.txt", "w") as new_data_file:
                        print("", end='', file=new_data_file)
                    client_id = open("player_data.txt").readline()
                data = player.authorize("", "", client_id)  # GET request with client id
                if data == 1:  # authorization completed successfully
                    player.import_decks()  # player get info about all his decks, and creates all this decks (see change n. 5)
                    auth = False
                else:
                    auth_menu.message_label.set_text(data)  # server connection error notification
            if event.ui_element.text == "Войти в другой аккаунт":  # authorization input fields, button to input data about account that differs from proposed one (by cid)
                auth_menu.delete_all_buttons()
                auth_menu.message_label.set_text("")
                auth_buttons(auth_menu, True)
        auth_menu.manager.process_events(event)  # gui check for events
        auth_menu.manager.update(time_delta)  # gui hover check
    screen.blit(background, (0, 0))  # render background image
    auth_menu.manager.draw_ui(screen)  # gui render
    pygame.display.update()  # update screen
load_start_time = time.time()

start_menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
play_menu = Matchmaking(SCREEN_WIDTH, SCREEN_HEIGHT, screen)
constructor = Constructor(SCREEN_WIDTH, SCREEN_HEIGHT, screen, player)
end_menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
deck_dump_menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
mulligan_menu = GameUI()

MENU_INDEX = 0
PAUSE = False
CHOSEN_OBJECT = None  # card that is chosen using leader, or by clicking on it
PLAYER_HAND = Hand()  # INSTANT game object (means that it once created and always used throughout all game)
OPPONENT_HAND = Hand()  # ↑ Hand contains cards, every game end it's nulled and then replenished when new session start
PLAYER_DUMP = Dump("Сброс игрока")  # INSTANT game object
OPPONENT_DUMP = Dump("Сброс ИИ")
FIELD = Field(screen, PLAYER_DUMP, PLAYER_HAND)  # INSTANT game object
text_to_render = ""  # in-game log

# ↓ all menus classes in the dictionary
MENU_DICT = {0: start_menu, 1: play_menu, 2: constructor, 3: "Game", 4: deck_dump_menu, 5: mulligan_menu, 6: end_menu}
init_menu(start_menu, play_menu, constructor, end_menu, deck_dump_menu, mulligan_menu)


def draw_text(surf: pygame.Surface, text: str, text_size: int, x: int, y: int):
    """ Draw the line of text in given coordinates"""
    text_font = pygame.font.Font(pygame.font.match_font('arial'), text_size)
    text_area = text_font.render(text, True, (100, 100, 100))
    text_rect = text_area.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_area, text_rect)


def pause_game():
    """ Clears panel, renders field once again, sets darken and blurred background, pauses game"""
    global MENU_INDEX, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP, PAUSE

    FIELD.set_panel_card(None)  # remove panel card
    FIELD.render_game_field(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)  # render field without panel card
    FIELD.draw_rows()  # field was re-rendered so row cards should do the same (otherwise they'll disappear)
    im = Image.frombuffer("RGB", (1920, 1080), pygame.image.tostring(screen, "RGB"), "raw")  # get screen image
    im = im.filter(ImageFilter.GaussianBlur(radius=2))  # filter image with gaussian blur
    im = ImageEnhance.Brightness(im).enhance(0.7)  # darken image
    FIELD.set_background(pygame.image.frombuffer(im.tobytes(), im.size, "RGB"))  # now this image used as background for pause menu
    MENU_INDEX = 4  # pause menu
    PAUSE = True


def end_move():
    """ When coin is clicked, this func checks field stats and
        change field if game is going to have a new round """
    global MENU_INDEX, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP

    if (FIELD.can_play_card or len(PLAYER_HAND.cards) == 0) and FIELD.turn:  # pass the round (player haven't played the card)
        FIELD.passes += 2  # for now players pass means that both players has passed the round
    MENU_INDEX = FIELD.end_move()
    PLAYER_HAND.end_move(FIELD)  # When both players passed, func increments round number and scores win of a round for a player, who has more points
    if FIELD.player_round_score == 2 or FIELD.opponent_round_score == 2:  # end game condition (any player got two crowns)
        MENU_INDEX = 6  # end menu
        screen.blit(background, (0, 0))  # render end menu background
        FIELD.draw_end()  # draw all session info on the screen
    if MENU_INDEX == 5:  # new round start
        pause_game()
        FIELD.chosen_storage = PLAYER_HAND
    CHOSEN_OBJECT = None  # no more chosen_objects


def in_area(coord: list | tuple, mouse_type: int, display: pygame.Surface) -> str:
    """ Check if mouse cursor is inside object's collision """
    global MENU_INDEX, CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP

    x, y = coord  # cursor screen location
    for game_object in CLICKABLE:
        if game_object and game_object.rect:  # if object exists and have collision
            start_x = game_object.rect[0]
            end_x = game_object.rect[0] + game_object.rect[2]
            start_y = game_object.rect[1]
            end_y = game_object.rect[1] + game_object.rect[3]
            if start_x < x < end_x and start_y < y < end_y:  # cursor is inside rectangle collision
                if mouse_type == 3:  # mouse just hovers over the object
                    action_on_hover(game_object, FIELD)
                else:  # mouse click on object
                    action_on_click(game_object, mouse_type, coord)
                return str(game_object.name)  # returns which object was clicked or hovered over
        if mouse_type == 3:
            PLAYER_HAND.up_when_hovered(coord)
            for row in FIELD.rows:
                row.when_hovered(coord, CHOSEN_OBJECT, display)
    if mouse_type == 1:
        if 305 < x < 455 and 450 < y < 600:  # coin collision
            end_move()
        if 5 < x < 80 and 500 < y < 575:  # exit collision
            MENU_INDEX = 6
            screen.blit(background, (0, 0))
            FIELD.draw_end()
        return "Nothing"   # returns that none of objects were clicked or hovered over


def deck_dump_hover(cards: list, mouse_pos: tuple | list, click_type: int):
    """ Checks if mouse cursor is inside collision of a card from deck, dump or hand during the pause """
    global MENU_INDEX, FIELD, PAUSE, PLAYER_HAND

    x, y = mouse_pos
    for card in cards:
        if card.rect[0] < x < card.rect[0] + card.rect[2] and card.rect[1] < y < card.rect[1] + card.rect[3]:  # cursor is inside rectangle collision
            if click_type == 3:  # mouse is just over the card
                FIELD.set_panel_card(card)
            elif click_type == 1 and isinstance(FIELD.chosen_storage, Hand):  # click on card during mulligan
                PLAYER_HAND.mulligan(FIELD.player_deck, card)
                if PLAYER_HAND.mulligans == 0:   # when mulligan's score reaches 0, mulligan's menu closes
                    PAUSE = False
                    MENU_INDEX = 3
                    FIELD.back_to_game(PLAYER_HAND)
                    PLAYER_HAND.end_mulligan(FIELD.player_deck)
                    FIELD.set_panel_card(None)
                    break


def action_on_hover(hovered_object: Card | Row | Leader, game_field: Field):
    """ Executes the functions of the hovered objects (Card or Leader or Row) during game """
    if type(hovered_object) == Card:  # card was hovered over
        game_field.set_panel_card(hovered_object)  # panel displays this card

        # if card is located in the row, this row should still be able to be highlighted (card collision overwrites row collision)
        if hovered_object.location.str_type == "Row":
            if type(CHOSEN_OBJECT) == Card and type(CHOSEN_OBJECT.location) == Hand:  # card was chosen previously (e.g: to play from the hand)
                hovered_object.location.lit(screen, True)  # activate bright highlight
            else:
                hovered_object.location.lit(screen, False)  # activate dim highlight

    if type(hovered_object) == Leader:  # leader card was hovered over
        game_field.set_panel_card(hovered_object)  # panel displays leader

    if type(hovered_object) == Row:  # highlight the row when mouse hovers over it
        if not PAUSE:  # during the pause rows aren't hoverable (otherwise row is highlighted over cards and doesn't fade)
            if type(CHOSEN_OBJECT) == Card and type(CHOSEN_OBJECT.location) == Hand:
                hovered_object.lit(screen, True)
            else:
                hovered_object.lit(screen, False)


def action_on_click(clicked_object: Card | Leader | Deck | Dump | Row, click_type: int, coordinates: tuple | list):
    """ Executes the functions of the clicked objects (Card or Leader or Deck or Dump or Row) during game"""
    global CHOSEN_OBJECT, PAUSE, MENU_INDEX, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP

    if type(clicked_object) == Card and FIELD.turn:  # card was clicked during the player's turn
        CHOSEN_OBJECT = clicked_object.on_click(FIELD, click_type, coordinates, CHOSEN_OBJECT)
    elif type(clicked_object) == Leader and FIELD.turn:  # leader was clicked during the player's turn
        CHOSEN_OBJECT = clicked_object.on_click(FIELD, click_type, CHOSEN_OBJECT)
    elif type(clicked_object) == Deck and click_type == 1 and clicked_object.player == "Me":  # deck was clicked
        if not PAUSE:
            pause_game()
            FIELD.chosen_storage = clicked_object  # deck is now game's chosen storage
            clicked_object.random_order()  # shuffle the deck (actual card order doesn't change)
    elif type(clicked_object) == Dump and click_type == 1:  # dump was clicked
        if not PAUSE:
            pause_game()
            FIELD.chosen_storage = clicked_object  # dump is now game's chosen storage
    elif type(clicked_object) == Row and FIELD.turn:
        if type(CHOSEN_OBJECT) == Card and clicked_object.player == "Me" and len(clicked_object.cards) < 9 and type(CHOSEN_OBJECT.location) == Hand \
                and click_type == 1:  # play the card from the hand condition
            PLAYER_HAND.play_card(CHOSEN_OBJECT)
            clicked_object.add_card(CHOSEN_OBJECT, click_type, coordinates)  # row gets new card
            CHOSEN_OBJECT.deploy(card=CHOSEN_OBJECT, field=FIELD, row=clicked_object)  # card deploy ability activated
            FIELD.can_play_card = False  # player can play only 1 card from the hand per turn
            CHOSEN_OBJECT = None  # no more chosen object


def get_player_deck(player_class: Player) -> Deck | None:
    """ Creates a deck object from the player deck data """
    cards = []
    if player_class.deck:
        for i in player_class.deck.cards:
            card = i.copy()
            cards.append(card)
            CLICKABLE.append(card)
        return Deck(player_class.deck.name, "Me", cards, 1)
    return None


def set_game(enemy_fraction: str, player_class: Player, pl_deck_name='Мужик * на 30', op_deck_name='Мужик * на 30, x2'):
    """ Called when game is chosen. Forms players' decks and hands. Chooses who starts and prepares field for the game """
    global FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP

    set_game_start_time = time.time()  # for log

    player_deck = get_player_deck(player_class)
    for i in player_deck.cards:  # all the cards at the beginning of the game are in the deck object
        i.location = player_deck
    PLAYER_HAND.start_hand(player_deck)  # hand is prepared for the game (draws first 10 cards from the deck top)

    opponent_deck = get_player_deck(player_class)  # same ↑ but for the opponent (this code section will be changed)
    for i in opponent_deck.cards:
        i.location = opponent_deck
    OPPONENT_HAND.start_hand(opponent_deck)

    FIELD.turn = random.choice([True, False])  # will be changed
    FIELD.set_field(enemy_fraction, player_deck, opponent_deck, CLICKABLE)  # prepare field for the game
    CLICKABLE.reverse()  # reverse for the right order of objects (kinda importance sort)
    pause_game()  # game starts with mulligan menu
    FIELD.chosen_storage = PLAYER_HAND  # ↑ so at that moment hand is a CHOSEN_STORAGE
    player_class.start_the_game()
    print("LOAD LOG: game loading time", time.time() - set_game_start_time, file=log_file)


def end_game():
    """ Nulls CLICKABLE and refreshes game, hands and dumps"""
    global CHOSEN_OBJECT, FIELD, PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP, CLICKABLE

    CHOSEN_OBJECT = None
    CLICKABLE = []
    FIELD.refresh(CLICKABLE)  # somewhere here ~20 mbytes of memory left (not all variables are nulled ?)
    PLAYER_HAND.refresh()
    OPPONENT_HAND.refresh()
    PLAYER_DUMP.refresh(CLICKABLE)
    OPPONENT_DUMP.refresh(CLICKABLE)


print("LOAD LOG: post auth time loading ", time.time() - load_start_time, file=log_file)
connection_check_timer = 0.0
time_delta = clock.tick(FPS) / 1000.0

while running:
    connection_check_timer += time_delta
    if connection_check_timer > 1000:  # TODO: time in seconds, approximately
        player.ensure_connection()
        connection_check_timer = 0

    if MENU_INDEX < 3:  # game haven't started, player is in the menus
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # cross at the right upper corner, should be safe exit
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти":  # TODO change from button text check to ui_element id or smth similar
                    running = False
                    player.exit()
                if event.ui_element.text == "Выйти в меню":  # exit from deck constructor or matchmaking
                    constructor.cards = {}
                    MENU_INDEX = 0
                    player.find_opponents(stop=True)
                if event.ui_element.text == "Играть":  # matchmaking menu
                    if player.deck:  # if player deck is valid TODO full deck check
                        MENU_INDEX = 1
                        play_menu.init_enemies()  # find all opponents
                        player.find_opponents(stop=False)  # user's status server update
                if event.ui_element.text == "Конструктор колоды":  # deck constructor menu
                    constructor.cards = player.import_cards()  # all available player's cards
                    constructor.update_cards_box()  # cards_drop_box is re-created with all cards
                    MENU_INDEX = 2
                if event.ui_element.text == "Переименовать колоду":  # rename deck TODO decks should be server-based as cards
                    constructor.rename_deck(constructor.entry_name.text)
                    constructor.update_decks_box()  # show changes
                if event.ui_element.text == "Битва с Северянами":  # just test against 0 AI
                    end_game()
                    MENU_INDEX = 3
                    set_game("NR", player)
                if event.ui_element.text == "Битва с длинноухими":  # just test against 0 AI
                    end_game()
                    MENU_INDEX = 3
                    set_game("Scoia", player)
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.cards.keys():  # constructor drop down menu (choose card)
                constructor.chosen_card = event.text
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.decks.keys():  # constructor drop down menu (choose deck)
                constructor.current_deck = constructor.decks[event.text]
                player.deck = constructor.current_deck
            if MENU_INDEX < 3:  # all buttons event and hover check
                MENU_DICT[MENU_INDEX].manager.process_events(event)
                MENU_DICT[MENU_INDEX].manager.update(time_delta)
        if MENU_INDEX < 3:  # update screen
            screen.blit(background, (0, 0))  # render background image
            MENU_DICT[MENU_INDEX].manager.draw_ui(screen)  # render all ui buttons
            screen.blit(georgia_font_26.render(player.nickname, True, (200, 200, 200)), (20, 20))  # render player's nickname
        if MENU_INDEX == 2:  # deck constructor render
            screen.blit(constructor.deck_background, (50, 178))  # render background image
            screen.blit(constructor.card_background, (1550, 140))  # render black background for card's description
            constructor.display_deck()  # render text, where all cards are listed with its name, power and deck capacity value
            constructor.display_info()  # render card's description
            constructor.display_card()  # render card image
        if MENU_INDEX == 1:
            play_menu.show_enemies()  # render text of all online players
        if MENU_INDEX < 2:  # render name of the current deck
            if player.deck:
                screen.blit(georgia_font_26.render(f"Выбранная колода: {player.deck.name}", True, (200, 200, 200)), (520, 870))
            else:
                screen.blit(georgia_font_26.render(f"Выбранная колода: нет", True, (200, 200, 200)), (520, 870))
        pygame.display.update()  # update screen
    elif MENU_INDEX == 3 or MENU_INDEX == 4 or MENU_INDEX == 5:  # game session (3 is game, 4 pause (deck, dum), 5 mulligan menu)
        if not PAUSE:
            FIELD.render_game_field(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)  # render field, all images except cards
            a = in_area(pygame.mouse.get_pos(), 3, screen)  # check objects which collide with mouse position
            # text_to_render = f"{a, clock.get_fps()}"
            text_to_render = f"{a, pygame.mouse.get_pos()}"  # ↑ and render this info for log
            FIELD.draw_rows()  # render row highlighting and all cards in the rows
            # text_surface = georgia_font_26.render(text_to_render, True, (200, 200, 200))
            # screen.blit(text_surface, (250, 900))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # should be safe exit
                    running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # check every LMB click
                        a = in_area(event.pos, 1, screen)
                        text_to_render = f"{event.pos}, {a}"
                    elif event.button == 3:  # check every RMB click
                        a = in_area(event.pos, 2, screen)
                        text_to_render = f"{event.pos}, 2"
                        if type(CHOSEN_OBJECT) == Card:  # unfocus card
                            CHOSEN_OBJECT.status = "passive"
                            CHOSEN_OBJECT = None
            pygame.display.flip()  # update game screen
        else:
            # ↓ check what type of pause (deck, dump or mulligan)
            if isinstance(FIELD.chosen_storage, Deck):  # deck menu
                FIELD.check_deck(FIELD.chosen_storage)
            elif isinstance(FIELD.chosen_storage, Hand):  # mulligan menu
                FIELD.mulligan_hand(mulligan_menu.state)
                MENU_INDEX = 5
            elif isinstance(FIELD.chosen_storage, Dump):  # dump menu
                FIELD.check_dump(FIELD.chosen_storage)
            else:  # pause is active but no menu (when mulligan menu is hidden)
                FIELD.mulligan_hand(mulligan_menu.state)
                FIELD.render_game_field(PLAYER_HAND, OPPONENT_HAND, PLAYER_DUMP, OPPONENT_DUMP)
                in_area(pygame.mouse.get_pos(), 3, screen)  # check is mouse hover over the cards
                FIELD.draw_rows()

            if FIELD.chosen_storage:  # the pause menu is active so the hover check should also be active
                deck_dump_hover(FIELD.chosen_storage.cards, pygame.mouse.get_pos(), 3)
            FIELD.render_panel()  # render panel card/leader
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:  # check mouse click
                    pos = event.pos  # coords of the click
                    if MENU_INDEX == 4:  # deck or dump are open during game, not during mulligan stage
                        if deck_dump_menu.buttons[0].hover_point(pos[0], pos[1]):  # first button from buttons list is same for deck and dump, and if clicked stops pause
                            PAUSE = False
                            MENU_INDEX = 3
                            FIELD.back_to_game(FIELD.chosen_storage)
                            FIELD.set_panel_card(None)
                            break
                    elif MENU_INDEX == 5:  # IT JUST WORKS
                        if mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][1].hover_point(pos[0], pos[1]):  # end mulligan button
                            PAUSE = False
                            MENU_INDEX = 3
                            FIELD.back_to_game(FIELD.chosen_storage)
                            PLAYER_HAND.end_mulligan(FIELD.player_deck)
                            FIELD.set_panel_card(None)
                            break
                        elif mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][0].hover_point(pos[0], pos[1]):  # hide mulligan button
                            FIELD.back_to_game(FIELD.chosen_storage)
                            FIELD.set_panel_card(None)
                            mulligan_menu.state = "game"
                        elif mulligan_menu.state == "game" and mulligan_menu.buttons_group["game"][1][0].hover_point(pos[0], pos[1]):  # back to mulligan button
                            mulligan_menu.state = "pause"
                            FIELD.chosen_storage = PLAYER_HAND
                            pause_game()
                        elif mulligan_menu.state == "pause" and mulligan_menu.buttons_group["pause"][1][2].hover_point(pos[0], pos[1]):  # go to deck button
                            FIELD.chosen_storage = FIELD.player_deck
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
                    if FIELD.chosen_storage:  # mulligan card
                        deck_dump_hover(FIELD.chosen_storage.cards, pos, 1)
                if MENU_INDEX == 4:  # hover check for deck/dump menu buttons
                    deck_dump_menu.manager.update(clock.tick(FPS) / 1000.0)
                elif MENU_INDEX == 5:  # hover check for mulligan menu buttons
                    mulligan_menu.buttons_group[mulligan_menu.state][0].update(clock.tick(FPS) / 1000.0)

            if MENU_INDEX == 4:  # render deck/dump menu buttons
                deck_dump_menu.manager.draw_ui(screen)
            elif MENU_INDEX == 5:  # render mulligan menu buttons
                mulligan_menu.buttons_group[mulligan_menu.state][0].draw_ui(screen)
                FIELD.draw_text(screen, "Осталось замен " + str(PLAYER_HAND.mulligans), 20, 165, 35)  # alert player about number of available mulligans
            pygame.display.update()  # update screen
    elif MENU_INDEX == 6:  # game's end menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # should be safe exit
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти в меню":
                    MENU_INDEX = 0
                    player.end_the_game(FIELD.player_round_score, FIELD.opponent_round_score, 0)  # update server data
            MENU_DICT[MENU_INDEX].manager.process_events(event)  # check for hover and click events
            MENU_DICT[MENU_INDEX].manager.update(30 / 1000)
        MENU_DICT[MENU_INDEX].manager.draw_ui(screen)  # draw ui
        pygame.display.update()  # update screen
    clock.tick(FPS)  # lock fps to 30
pygame.quit()  # close game
log_file.close()  # close log file
