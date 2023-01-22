import random
import pygame
import os
import pygame_gui

from Cards import Card, Leader
from Field import Field
from CONSTANTS import *
from Storages import Dump, Deck, Hand
from Data import decks_list, cards_list
from Menues import Menu, Constructor, init_menu

pygame.init()


def load_image(name, size='M'):
    directory = os.path.join(name)
    if os.path.isfile(directory):
        if size == 'L':
            image = pygame.image.load(directory)
        elif size == 'M':
            image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
        elif size == 'K':
            image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
        else:
            image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
        return image


size = SWIDTH, SHEIGHT
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()
c = 0

Start_menu = Menu(SWIDTH, SHEIGHT)
Play_menu = Menu(SWIDTH, SHEIGHT)
constructor = Constructor(SWIDTH, SHEIGHT, screen)
end_menu = Menu(SWIDTH, SHEIGHT)
background = pygame.Surface((SWIDTH, SHEIGHT))

menu_dict = {0: Start_menu, 1: Play_menu, 2: constructor, 3: "Game", 4: end_menu}
menu_var = 0

init_menu(background, Start_menu, Play_menu, constructor, end_menu)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, (100, 100, 100))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def in_area(coord, mouse_type, field):
    global menu_var
    x, y = coord
    for i in CLICKABLE:
        if i != field.rcoin and i != field.bcoin and i.rect:
            if i.rect[0] < x < i.rect[0] + i.rect[2] and i.rect[1] < y < i.rect[1] + i.rect[3]:
                action_on_click(i, mouse_type, field)
                if mouse_type == 3:
                    action_on_hover(i, field)
                return str(i.name)
    if mouse_type == 1:
        if 155 < x < 305 and 450 < y < 600:
            if field.turn is False:
                field.turn = True
                return str("Красная монета")
            else:
                field.turn = False
                return str("Синяя монета")
        if 5 < x < 80 and 500 < y < 575:
            menu_var = 4
    return "Nothing"


def action_on_hover(obj, field):
    if type(obj) == Card:
        field.set_panel_card(obj)
    if type(obj) == Leader:
        field.set_panel_card(obj)


def action_on_click(obj, click_type, field):
    if type(obj) == Card:
        if obj.status != "chosen" and click_type == 1:
            obj.status = "chosen"
        if obj.status == "chosen" and click_type == 2:
            obj.status = "in hand"
    elif type(obj) == Leader:
        if type(field.panel) != Leader and click_type == 1:
            print("Leader extra ability")
        if type(field.panel) == Leader and click_type == 2:
            print("Leader main ability")
    elif type(obj) == Deck:
        pass
    elif type(obj) == Dump:
        pass


to_render = ""
while running:
    if menu_var < 3:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти":
                    running = False
                if event.ui_element.text == "Выйти в меню":
                    menu_var = 0
                if event.ui_element.text == "Играть":
                    menu_var = 1
                if event.ui_element.text == "Конструктор колоды":
                    menu_var = 2
                if event.ui_element.text == "Переименовать колоду":
                    constructor.rename_deck(constructor.entry_name.text)
                    constructor.update_decks_box()
                if event.ui_element.text == "Битва с Северянами":
                    menu_var = 3
                    ERoche = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 70)
                    Roche = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 685)
                    field = Field(ERoche, Roche, screen, "NR")
                    pl_dump = Dump("Сброс игрока")
                    pl_deck = decks_list['Мужик * на 30']
                    pl_hand = Hand()
                    pl_hand.start_hand(pl_deck)
                    op_dump = Dump("Сброс противника")
                    op_deck = decks_list['Мужик * на 30, x2']
                    op_hand = Hand()
                    op_hand.start_hand(op_deck)
                    field.turn = random.choice([True, False])
                if event.ui_element.text == "Битва с длинноухими":
                    ERoche = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 70)
                    Roche = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 685)
                    menu_var = 3
                    field = Field(ERoche, Roche, screen, "Scoia")
                    pl_dump = Dump("Сброс игрока")
                    pl_deck = decks_list['Мужик * на 30']
                    pl_hand = Hand()
                    pl_hand.start_hand(pl_deck)
                    op_dump = Dump("Сброс противника")
                    op_deck = decks_list['Мужик * на 30, x2']
                    op_hand = Hand()
                    op_hand.start_hand(pl_deck)
                    field.turn = random.choice([True, False])
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.cards.keys():
                constructor.chosen_card = event.text
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.text in constructor.decks.keys():
                constructor.current_deck = constructor.decks[event.text]
            if menu_var < 3:
                menu_dict[menu_var].manager.process_events(event)
                menu_dict[menu_var].manager.update(time_delta)
        if menu_var < 3:
            screen.blit(background, (0, 0))
            menu_dict[menu_var].manager.draw_ui(screen)
        if menu_var == 2:
            screen.blit(constructor.deck_background, (50, 178))
            screen.blit(constructor.card_background, (1550, 140))
            constructor.display_deck()
            constructor.display_info()
            constructor.display_card()
        pygame.display.update()
    elif menu_var == 3:
        if c % 2 == 0:
            field.render_ui_images()
            field.render_ui_leader()
            field.render_text(ERoche, Roche, pl_hand, pl_deck, pl_dump, op_hand, op_deck, op_dump)
            field.draw_hand(pl_hand)
            font = pygame.font.SysFont(FONT, 30, bold=True)
            text_surface = font.render(to_render, True, (200, 200, 200))
            screen.blit(text_surface, (250, 900))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_var = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_var = 0
                if event.key == pygame.K_a:
                    field.set_crowns(True)
                if event.key == pygame.K_s:
                    field.set_crowns(False)
                if event.key == pygame.K_d:
                    field.round += 1
                if event.key == pygame.K_z:
                    pl_hand.play_card(-1, pl_dump)
                if event.key == pygame.K_f:
                    surface = pygame.transform.smoothscale(screen, (500, 400))
                    blur = pygame.transform.smoothscale(surface, (SWIDTH, SHEIGHT))
                    screen.blit(blur, (0, 0))
                    c += 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    a = in_area(event.pos, 1, field)
                    to_render = f"{event.pos}, {a}"
                elif event.button == 3:
                    a = in_area(event.pos, 2, field)
                    to_render = f"{event.pos}, 2"
            if event.type == pygame.MOUSEMOTION:
                font = pygame.font.SysFont(FONT, 30, bold=True)
                a = in_area(event.pos, 3, field)
                to_render = f"{event.pos}"
        pygame.display.flip()
        clock.tick(FPS)
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Выйти в меню":
                    menu_var = 0
            menu_dict[menu_var].manager.process_events(event)
            menu_dict[menu_var].manager.update(30 / 1000)
        screen.blit(background, (0, 0))
        field.draw_end()
        menu_dict[menu_var].manager.draw_ui(screen)
        pygame.display.update()
pygame.quit()

# for i in CLICKABLE:
#     if type(i) != Card:
#         print(type(i), i.name, i.rect)
