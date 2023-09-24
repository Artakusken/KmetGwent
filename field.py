from constants import *
from cards import Card, Leader
from storages import Hand
from math import atan2, cos, sin, radians
import pygame
import os


class Row:
    """
    A class to represent a row - main part of game field

    Attributes
        ----------
        row : str
            type of row (melee, ranged or siege)
        places : int
            number of slots in row
        player : str
            player or AI
        cards : list
            a list of cards in a row
        name : str
            row and player together
        active_frame : pygame.image
            image of active frame
        frame : pygame.image
            image of usual frame
    """

    def __init__(self, row_type, player, field):
        self.row = row_type
        self.player = player
        self.field = field

        self.places = ROW_SIZE
        self.cards = []
        self.name = self.row + self.player
        self.str_type = "Row"
        self.last_hovered_card = None

        if player == "Me":
            if self.row == "melee":
                self.rect = (536, 475, 1034, 140)
            elif self.row == "ranged":
                self.rect = (536, 635, 1034, 140)
            else:
                self.rect = (536, 795, 1034, 140)
        else:
            if self.row == "melee":
                self.rect = (536, 310, 1034, 140)
            elif self.row == "ranged":
                self.rect = (536, 155, 1034, 140)
            else:
                self.rect = (536, 0, 1034, 140)

        self.active_frame = load_image("Field\\row.png", "O")
        self.frame = load_image("Field\\enemy_row.png", "O")
        self.position_line = IMAGES["Position_line"]

    def lit(self, screen, active):
        """ When row is hovered it's also lit with frame. This func decide what frame to use."""
        if active:
            if self.player == "Me" and len(self.cards) < 9:
                screen.blit(self.active_frame, (self.rect[0] - 5, self.rect[1] - 1, self.rect[2], self.rect[3]))
            else:
                screen.blit(self.frame, (self.rect[0], self.rect[1], self.rect[2], self.rect[3]))
        else:
            screen.blit(self.frame, (self.rect[0], self.rect[1], self.rect[2], self.rect[3]))

    def when_hovered(self, coord, chosen_obj, display):
        """ Up a hovered card, render position line and remembering last hovered card"""
        for index, card in enumerate(self.cards):
            if card.rect[0] < coord[0] < card.rect[0] + card.rect[2] and card.rect[1] < coord[1] < card.rect[1] + card.rect[3] - 5:  # possible (rare) mistake when last hovered card is none because card hasn't been hovered (-5 of y axis)
                if isinstance(chosen_obj, Card) and isinstance(chosen_obj.location, Hand):
                    if coord[0] < card.rect[0] + (card.rect[2] / 2):
                        display.blit(self.position_line, (card.rect[0] - 10, self.rect[1]))
                        self.last_hovered_card = (index, "l")
                    elif coord[0] > card.rect[0] + (card.rect[2] / 2):
                        display.blit(self.position_line, (card.rect[0] + card.rect[2], self.rect[1]))
                        self.last_hovered_card = (index, "r")
                    card.hover = False
                else:
                    card.hover = True
            else:
                if type(chosen_obj) == Card and type(chosen_obj.location) == Hand and self.rect[0] < coord[0] < self.rect[0] + \
                        self.rect[2] and self.rect[1] < coord[1] < self.rect[1] + self.rect[3]:
                    if coord[0] < self.cards[0].rect[0]:
                        display.blit(self.position_line, (self.cards[0].rect[0] - 10, self.rect[1]))
                        self.last_hovered_card = (0, "l")
                    elif coord[0] > self.cards[-1].rect[0] + self.cards[-1].rect[2]:
                        display.blit(self.position_line, (self.cards[-1].rect[0] + self.cards[-1].rect[2], self.rect[1]))
                        self.last_hovered_card = (len(self.cards) - 1, "r")
                    elif self.last_hovered_card[1] == "l":
                        display.blit(self.position_line, (self.cards[self.last_hovered_card[0]].rect[0] - 10, self.rect[1]))
                    elif self.last_hovered_card[1] == "r":
                        display.blit(self.position_line,
                                     (self.cards[self.last_hovered_card[0]].rect[0] + SMALL_CARD_WIDTH, self.rect[1]))
                if card.hover and (card.rect[1] + 5 < coord[1] < card.rect[1] + SMALL_CARD_HEIGHT + 5) and (
                        card.rect[0] < coord[0] < card.rect[0] + SMALL_CARD_WIDTH):
                    card.hover = True
                else:
                    card.hover = False

    def add_card(self, game_object, click_type, coord):
        """
        Used as a part of action_on_click func in game.py if row is clicked.
        Add a chosen card from hand to a row. Also, this func decide a position of a new card in a row
        """
        #  TODO: i have two ways. First is to continue what I've done.
        #   In case player want to put card between others it's need to parse through cards and check which card would left for a new card.
        #   Second is to get rid of spaces between cards. Position line(position_line) will move cards and put self between them.
        #   Also this way will solve problem in func draw_lines.
        if self.cards:
            if coord[0] < self.cards[0].rect[0]:
                self.cards = [game_object] + self.cards
            elif coord[0] > self.cards[-1].rect[0] + SMALL_CARD_WIDTH:
                self.cards.append(game_object)
            else:
                card = self.cards[self.last_hovered_card[0]]
                index = self.last_hovered_card[0]
                if self.last_hovered_card[1] == "r":
                    self.cards = self.cards[:index + 1] + [game_object] + self.cards[index + 1:]
                elif self.last_hovered_card[1] == "l":
                    self.cards = self.cards[:index] + [game_object] + self.cards[index:]
        else:
            self.cards.append(game_object)
        game_object.status = "passive"
        game_object.location = self
        game_object.row = self.row
        game_object.column = len(self.cards) - 1
        self.field.can_play_card = False

    def refresh(self, storage):
        """ When game ends, this func clear row's cards list"""
        self.cards = []
        storage.append(self)

    def clear(self, dump):
        """ When game ends, this func clear row's cards list and delete all cards collisions"""
        for i in self.cards:
            i.location = dump
            i.row = None
            i.column = None
            i.status = "passive"
            dump.cards.append(i)
            i.rect = None
        self.cards = []

    def make_turn(self):
        """ Set status of all cards in hand to passive"""
        for i in self.cards:
            i.status = "passive"

    def count_score(self):
        """ Return score of a row"""
        return sum([i.power for i in self.cards])


class Field:
    """
    A class to represent a game field, where all game components are shown and acted.

    Attributes
        ----------
        player_score : int
            the score of player
        opponent_score : int
            the score of opponent or AI
        field_image : pygame.image
            background, image of game field
        round : int
            the number of a game round, game has 2 or 3 rounds
        player_melee_row, player_range_row, player_siege_row, opponent_melee_row, opponent_range_row, opponent_siege_row : class Row
            the rows where cards are located when played
        rows : list
            a list that contain all row classes of game field
        opponent_fraction : str
            name of opponent's fraction
        turn : bool
            express which turn is now. True if it's player turn, False if it's AI turn
        can_play_card : bool
            express if player can play a card.
            True if player haven't played card during the turn, False if played, so he can't more
        panel : pygame.image
            the picture of hoovered card. Displayed on right-mid of board
        panel_name : str
            the name of hoovered card. Displayed on right-mid of board, under the picture
        panel_tags : str
            the tags of hoovered card. Displayed on right-mid of board, under the name
        panel_text : list
            the list of lines (28 symbols length) of hoovered card's description. Text is displayed on right-mid of board, under the tags
        controls : list
            the list of instructions displayed to player, so he can know what and how to do
        dump_image : pygame.image
            the picture of cards' dump
        player_deck_image : pygame.image
            the picture of player's deck
        opponent_deck_image : pygame.image
            the picture of opponent's deck
        red_coin_image : pygame.image
            the picture of red coin (enemy turn)
        blue_coin_image : pygame.image
            the picture of blue coin (player turn)
        player_leader : class Leader
            player leader variable
        opponent_leader : class Leader
            opponent leader variable
        player_deck : class Deck
            player deck variable
        opponent_deck : class Deck
            opponent deck variable
        opponent_round_score : int
            number of opponent's won rounds
        player_round_score : int
            number of player's won rounds
        op_crowns : dict
            op_round_score is key of opponent's crown image
        pl_crowns : dict
            pl_round_score is key of player's crown image
        exit : pygame.image
            the picture of exit. When clicked game ends
        screen : pygame.display
            screen where all is displayed
        passes : int
            number of passes in round, if it's equal 2 - round ends
        history : list
            the list which stores values of player's and opponent's points when round ends
    """

    def __init__(self, screen, player_dump, player_hand):
        # get images
        self.field_image = load_image('Field\\Field.jpg', "O")
        self.background = None
        self.red_coin_image = load_image('Field\\RCoin.png', 'K')
        self.blue_coin_image = load_image('Field\\BCoin.png', 'K')
        self.dump_image = load_image('Field\\Dump.png', 'S')
        self.player_deck_image = load_image('Field\\Nilfgaard.png', 'S')
        self.exit = load_image('Field\\exit.png', 'O')
        # set initial values
        self.round = 0
        self.player_score = 0
        self.opponent_score = 0
        self.opponent_round_score = 0
        self.player_round_score = 0
        self.passes = 0
        self.op_crowns = {0: "Red0Crown", 1: "Red1Crown", 2: "Red2Crown"}
        self.pl_crowns = {0: "Blue0Crown", 1: "Blue1Crown", 2: "Blue2Crown"}
        # set field objects
        self.player_melee_row = Row("melee", "Me", self)
        self.player_range_row = Row("ranged", "Me", self)
        self.player_siege_row = Row("siege", "Me", self)
        self.opponent_melee_row = Row("melee", "Op", self)
        self.opponent_range_row = Row("ranged", "Op", self)
        self.opponent_siege_row = Row("siege", "Op", self)
        self.my_dump = player_dump
        self.my_hand = player_hand
        self.rows = (self.player_melee_row, self.player_range_row, self.player_siege_row,
                     self.opponent_melee_row, self.opponent_range_row, self.opponent_siege_row)

        self.turn = None
        self.can_play_card = True

        self.panel = None
        self.panel_name = ""
        self.panel_tags = ""
        self.panel_text = ""

        self.controls = ("ПКМ - отменить выбор карты", "ЛКМ - сыграть карту")

        self.opponent_fraction = None
        self.opponent_deck_image = None
        self.player_leader = None
        self.opponent_leader = None
        self.player_deck = None
        self.opponent_deck = None
        self.chosen_storage = None

        self.text_font26 = pygame.font.SysFont(FONT, 26, bold=True)
        self.text_font20 = pygame.font.SysFont(FONT, 20, bold=True)
        self.font24 = pygame.font.Font(None, 24)
        self.font40 = pygame.font.Font(None, 40)
        self.font60 = pygame.font.Font(None, 60)
        self.screen = screen
        self.history = []

    def set_field(self, op_fraction, pl_deck, op_deck, storage):
        """
        When game is chosen in menu, this func makes field ready for a game.
        Based on op_fraction choose op_deck and op_leader. pl_leader, pl_deck and op_deck are stored inside class.
        """
        self.opponent_fraction = op_fraction
        if op_fraction == "NR":
            self.opponent_deck_image = load_image('Field\\North.png', 'S')
            self.opponent_leader = Leader("Roche180png", "Вернон Роше", "NR", 181, 20, 70)
        elif op_fraction == "Scoia":
            self.opponent_deck_image = load_image('Field\\Scotoeli.png', 'S')
            self.opponent_leader = Leader("Roche180png", "Вернон Роше", "NR", 181, 20, 70)
        self.player_leader = Leader("Joachim De Wett180png", "Йоахим де Ветт", "NG", 181, 20, 695)
        storage.append(self.player_leader)
        storage.append(self.opponent_leader)
        self.player_deck = pl_deck
        self.opponent_deck = op_deck
        storage.append(self.player_deck)
        storage.append(self.opponent_deck)

    def refresh(self, storage):
        """ When game ends, this func clear all storages and turn variables value to initial one """
        self.player_score, self.opponent_score = 0, 0
        self.round = 0
        self.player_melee_row.refresh(storage)
        self.player_range_row.refresh(storage)
        self.player_siege_row.refresh(storage)
        self.opponent_melee_row.refresh(storage)
        self.opponent_range_row.refresh(storage)
        self.opponent_siege_row.refresh(storage)
        self.opponent_fraction = None
        self.turn = None
        self.panel = None
        self.panel_name = ""
        self.panel_tags = ""
        self.panel_text = ""
        self.opponent_deck_image = None
        self.player_leader = None
        self.opponent_leader = None
        self.player_deck = None
        self.opponent_deck = None
        self.passes = 0
        self.opponent_round_score = 0
        self.player_round_score = 0
        self.history = []

    def new_turn(self):
        for i in self.rows:
            for j in i.cards:
                j.new_turn()

    def end_move(self):
        """ When coin is pressed this func transfer a possibility to play to another player"""
        if self.passes == 2:
            self.end_round()
            if self.turn:
                self.new_turn()
            return 5
        if not self.turn:
            for i in self.rows[3::]:
                i.make_turn()
            self.turn = True
            self.new_turn()
            self.can_play_card = True
        else:
            self.turn = False
            for i in self.rows[:3]:
                i.make_turn()
        return 3

    def end_round(self):
        """ When both players passed, func increments round number and scores win of a round for a player, who has more points"""
        self.round += 1
        self.history.append((self.player_score, self.opponent_score))
        if self.player_score > self.opponent_score:
            self.player_round_score += 1
        elif self.player_score < self.opponent_score:
            self.opponent_round_score += 1
        else:
            self.player_round_score += 1
            self.opponent_round_score += 1
        if self.round == 3:
            return None
        for i in self.rows:
            i.clear(self.my_dump)
        self.opponent_score = self.player_score = 0
        self.passes = 0

    def set_panel_card(self, card):
        """ Set self.panel with a card class object"""
        if card is None:
            self.panel_name = ""
            self.panel_tags = ""
            self.panel_text = ""
        self.panel = card

    def set_background(self, image):
        """ Darken and blurred display screen used as background for a deck and dump view mode"""
        self.background = image

    def count_score(self, player):
        """ Return sum or rows scores"""
        if player == "Me":
            points_sum = 0
            for i in self.rows[:3]:
                points_sum += i.count_score()
            self.player_score = points_sum
            return points_sum
        else:
            points_sum = 0
            for i in self.rows[3::]:
                points_sum += i.count_score()
            self.opponent_score = points_sum
            return points_sum

    def draw_text(self, surf, text, size, x, y, color=(200, 200, 200)):
        """ Draw line of text in given coordinates"""
        if size > 20:
            surf.blit(self.text_font26.render(text, True, color), (x, y))
        else:
            surf.blit(self.text_font20.render(text, True, color), (x, y))

    def render_text(self, pl_hand, op_hand, pl_dump, op_dump):
        """ Draw all text info on screen"""
        self.draw_text(self.screen, self.opponent_leader.fraction, 20, 20, 15)
        self.draw_text(self.screen, self.player_leader.fraction, 20, 20, 635)

        self.draw_text(self.screen, self.opponent_leader.name, 20, 20, 40)
        self.draw_text(self.screen, self.player_leader.name, 20, 20, 660)

        self.draw_text(self.screen, self.controls[0], 20, 1580, 160)
        self.draw_text(self.screen, self.controls[1], 20, 1580, 190)

        self.draw_text(self.screen, "ПКМ - основная способность лидера", 20, 20, 1020)
        self.draw_text(self.screen, "ЛКМ - доп. способность лидера", 20, 20, 1050)

        self.draw_text(self.screen, str(self.opponent_leader.move_ability), 30, 250, 110)
        self.draw_text(self.screen, str(self.opponent_leader.leader_ability), 30, 250, 70)
        self.draw_text(self.screen, str(self.player_leader.move_ability), 30, 250, 935)
        self.draw_text(self.screen, str(self.player_leader.leader_ability), 30, 250, 975)

        self.draw_text(self.screen, str(len(pl_hand.cards)), 30, 1580, 1045)
        self.draw_text(self.screen, str(len(self.player_deck.cards)), 30, 1665, 1045)
        self.draw_text(self.screen, str(len(pl_dump.cards)), 30, 1810, 1045)

        self.draw_text(self.screen, str(len(op_hand.cards)), 30, 1580, 5)
        self.draw_text(self.screen, str(len(self.opponent_deck.cards)), 30, 1665, 5)
        self.draw_text(self.screen, str(len(op_dump.cards)), 30, 1810, 5)

        self.draw_text(self.screen, str(self.count_score("Op")), 30, 400, 305, (0, 0, 0))
        self.draw_text(self.screen, str(self.count_score("Me")), 30, 400, 715, (0, 0, 0))

        if self.turn:
            self.draw_text(self.screen, "Ваш ход", 30, 295, 395)
        else:
            self.draw_text(self.screen, "Ход противника", 30, 185, 395)

        if self.can_play_card:
            self.draw_text(self.screen, "Спасовать", 30, 260, 610)
        else:
            self.draw_text(self.screen, "Передать ход", 30, 215, 610)

    def render_panel(self):
        """ Draw all info (name, tags, description, image) of hovered card"""
        if type(self.panel) == Card:
            card = self.panel
            self.panel_name = card.name
            if card.tags:
                self.panel_tags = ", ".join(card.tags)
            self.panel_text = card.description
            card.render(1580, 230, "M", self.screen, self.font60)
            self.draw_text(self.screen, str(card.column), 30, 1580, 850, (0, 0, 0))
            self.draw_text(self.screen, str(card.row), 30, 1610, 850, (0, 0, 0))
            self.draw_text(self.screen, card.status, 30, 1750, 850, (0, 0, 0))
        elif type(self.panel) == Leader:
            card = self.panel
            self.screen.blit(card.image, (1580, 230, 320, 459))
            self.screen.blit(IMAGES["border_golden_medium"], (1580, 230))
            self.panel_name = card.name
            self.panel_text = card.description
            self.panel_tags = ""
        self.draw_text(self.screen, self.panel_name, 30, 1580, 690)
        self.draw_text(self.screen, self.panel_tags, 25, 1580, 730)
        for i in range(len(self.panel_text)):
            a = i * 25
            self.draw_text(self.screen, self.panel_text[i], 20, 1580, 770 + a)

    def render_ui_images(self):
        """ Draw all UI images"""
        self.screen.blit(self.field_image, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(self.opponent_deck_image, (1630, 0, 105, 150))
        self.screen.blit(self.player_deck_image, (1630, 935, 105, 150))
        self.screen.blit(self.dump_image, (1765, 0, 105, 150))
        self.screen.blit(self.dump_image, (1765, 935, 105, 150))
        if self.turn:
            self.screen.blit(self.blue_coin_image, (320, 443, 150, 150))
        else:
            self.screen.blit(self.red_coin_image, (320, 443, 150, 150))
        self.screen.blit(self.exit, (5, 485, 75, 75))
        self.screen.blit(IMAGES[self.op_crowns[self.opponent_round_score]], (280, 70, 71, 71))
        self.screen.blit(IMAGES[self.pl_crowns[self.player_round_score]], (280, 935, 71, 71))

    def render_leader(self):
        """ Draw leaders' animated sprites"""
        self.opponent_leader.update()
        self.player_leader.update()
        self.opponent_leader.draw(self.screen)
        self.player_leader.draw(self.screen)

    def render_hand(self, hand):
        """ Draw all cards which are located in hand during the game"""
        for i in range(len(hand.cards)):
            start_x = 475 + 53 * (10 - len(hand.cards))
            a = i * 110
            if hand.cards[i].hover or hand.cards[i].status == "chosen":
                hand.cards[i].render(start_x + a, 949, "S", self.screen, self.font24)
                hand.cards[i].rect = (start_x + a, 949, SMALL_CARD_WIDTH, SMALL_CARD_HEIGHT)
                hand.cards[i].hand_position = i
            else:
                hand.cards[i].render(start_x + a, 954, "S", self.screen, self.font24)
                hand.cards[i].rect = (start_x + a, 954, SMALL_CARD_WIDTH, SMALL_CARD_HEIGHT)

    def draw_rows(self):
        """ Draw all cards of all rows which are located in row during the round"""
        arrow = None
        hovered = None
        for i in self.rows:
            length = len(i.cards)
            if length % 2 == 0:
                start_x = (536 + 1030 / 2) - (length // 2) * SMALL_CARD_WIDTH - length * 8 + 50
            else:
                start_x = (536 + 1030 / 2) - (length // 2) * SMALL_CARD_WIDTH - length * 8
            x, y = start_x, i.rect[1]
            for j in range(length):
                a = j * SMALL_CARD_WIDTH
                i.cards[j].column = j
                if i.cards[j].status == "chosen":
                    if i.cards[j].order:
                        arrow = i.cards[j].rect[0:2]
                    i.cards[j].render(x + a, y - 8, "S", self.screen, self.font24)
                    i.cards[j].rect = (x + a, y - 8, SMALL_CARD_WIDTH, SMALL_CARD_HEIGHT)
                elif i.cards[j].hover:
                    hovered = i.cards[j]
                    i.cards[j].render(x + a, y - 8, "S", self.screen, self.font24)
                    i.cards[j].rect = (x + a, y - 8, SMALL_CARD_WIDTH, SMALL_CARD_HEIGHT)
                else:
                    i.cards[j].render(x + a, y, "S", self.screen, self.font24)
                    i.cards[j].rect = (x + a, y, SMALL_CARD_WIDTH, SMALL_CARD_HEIGHT)
                if self.player_leader.status == "chosen extra ability":
                    arrow = self.player_leader.rect[0:2]
                x += 6

        if arrow:
            if hovered:
                self.render_arrow(arrow, hovered, True)
            else:
                self.render_arrow(arrow, pygame.mouse.get_pos())

    def render_arrow(self, start, end, card=False):
        card_center = start[0] + 53, start[1] + 70
        if card:
            if end.location.player == "Me":
                color = (20, 20, 220, 127)
            else:
                color = (220, 20, 20, 127)
            end = end.rect[0] + 53, end.rect[1] + 70
            dx, dy = end[0] - card_center[0], end[1] - card_center[1]
        else:
            color = (20, 20, 220, 127)
            dx, dy = end[0] - card_center[0], end[1] - card_center[1]
        angle = atan2(dy, dx)
        diag = (dy ** 2 + dx ** 2) ** 0.5 - 30
        if diag > 200:
            width = 10 / (diag // 100)
        elif diag > 75:
            width = 10 / (diag // 75)
        else:
            width = 10

        if diag > 0:
            pygame.draw.polygon(self.screen, color, (card_center,
                                                     (card_center[0] + diag * cos(angle - radians(width)),
                                                      card_center[1] + diag * sin(angle - radians(width))),
                                                     (card_center[0] + diag * cos(angle + radians(width)),
                                                      card_center[1] + diag * sin(angle + radians(width)))))
            pygame.draw.polygon(self.screen, color, (end,
                                                     (card_center[0] + diag * cos(angle - radians(width)),
                                                      card_center[1] + diag * sin(angle - radians(width))),
                                                     (card_center[0] + diag * cos(angle + radians(width)),
                                                      card_center[1] + diag * sin(angle + radians(width)))))

    def render_game_field(self, pl_hand, op_hand, pl_dump, op_dump):
        """ All render functions are used here"""
        self.render_ui_images()
        self.render_leader()
        self.render_hand(pl_hand)
        self.render_panel()
        self.render_text(pl_hand, op_hand, pl_dump, op_dump)

    def check_deck(self, deck):
        """ Render list of cards which are in deck"""
        c = 0
        x, y = 350, 50
        self.screen.blit(self.background, (0, 0))
        for i in deck.fake_order:
            deck.cards[i].render(x + (c % 5 * 250), y + (350 * (c // 5)), "D", self.screen, self.font40)
            deck.cards[i].rect = (x + (c % 5 * 250), y + (350 * (c // 5)), LEADER_WIDTH, LEADER_HEIGHT)
            c += 1

    def check_dump(self, dump):
        """ Render list of cards which are in dump """
        c = 0
        x, y = 350, 50
        self.screen.blit(self.background, (0, 0))
        for i in dump.cards:
            i.render(x + (c % 5 * 250), y + (350 * (c // 5)), "D", self.screen, self.font40)
            i.rect = (x + (c % 5 * 250), y + (350 * (c // 5)), LEADER_WIDTH, LEADER_HEIGHT)
            c += 1

    def mulligan_hand(self, menu_state):
        """ Render list of cards which are in hand """
        if menu_state == "pause":
            c = 0
            x, y = 250, 150
            self.screen.blit(self.background, (0, 0))
            for i in self.chosen_storage.cards:
                i.render(x + (c % 5 * 250), y + (350 * (c // 5)), "D", self.screen, self.font40)
                i.rect = (x + (c % 5 * 250), y + (350 * (c // 5)), LEADER_WIDTH, LEADER_HEIGHT)
                c += 1

    def back_to_game(self, storage):
        """ Null cards' collisions and field chosen storage"""
        for i in storage.cards:
           i.rect = None
        self.chosen_storage = None

    def draw_end(self):
        """ Result is displayed, when game ends"""
        if self.player_round_score > self.opponent_round_score:
            self.draw_text(self.screen, "Вы выиграли", 30, 700, 400)
        elif self.player_round_score < self.opponent_round_score:
            self.draw_text(self.screen, "Вы проиграли", 30, 750, 400)
        else:
            self.draw_text(self.screen, "Ничья", 30, 750, 400)
        self.screen.blit(IMAGES[self.op_crowns[self.opponent_round_score]], (910, 370, 71, 71))
        self.screen.blit(IMAGES[self.pl_crowns[self.player_round_score]], (620, 370, 71, 71))

        self.draw_text(self.screen, "Вы", 30, 650, 500)
        self.draw_text(self.screen, "Противник", 30, 910, 500)
        for i in range(len(self.history)):
            a = i * 30
            self.draw_text(self.screen, str(self.history[i][0]), 30, 650, 540 + a)
            self.draw_text(self.screen, str(self.history[i][1]), 30, 910, 540 + a)
