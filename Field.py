from CONSTANTS import *
from Cards import Card, Leader
from Storages import Hand
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

        if player == "Human":
            if self.row == "melee":
                self.rect = (536, 480, 1034, 140)
            elif self.row == "ranged":
                self.rect = (536, 640, 1034, 140)
            else:
                self.rect = (536, 800, 1034, 140)
        else:
            if self.row == "melee":
                self.rect = (536, 320, 1034, 140)
            elif self.row == "ranged":
                self.rect = (536, 160, 1034, 140)
            else:
                self.rect = (536, 5, 1034, 140)

        self.active_frame = self.load_image("Field\\rowe5.png", "O")
        self.frame = self.load_image("Field\\enemy_rowe.png", "O")
        self.position_line = IMAGES["Position_line"]

    def load_image(self, name, size='M'):
        """ Load images from files into game. Size O - original, M - medium, K - square(150x150), S - small"""
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'O':
                image = pygame.image.load(directory)
            elif size == 'M':
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
            elif size == 'K':
                image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
            else:
                image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
            return image

    def lit(self, screen, active):
        """ When row is hovered it's also lit with frame. This func decide what frame to use."""
        if active:
            if self.player == "Human" and len(self.cards) < 9:
                screen.blit(self.active_frame, (self.rect[0] - 10, self.rect[1] - 40, self.rect[2], self.rect[3]))
            else:
                screen.blit(self.frame, (self.rect[0] - 10, self.rect[1] - 40, self.rect[2], self.rect[3]))
        else:
            screen.blit(self.frame, (self.rect[0] - 10, self.rect[1] - 40, self.rect[2], self.rect[3]))

    def when_hovered(self, coord, chosen_obj, display):
        """ Up a hovered card, render position line and remembering last hovered card"""
        for index, card in enumerate(self.cards):
            if card.rect[0] < coord[0] < card.rect[0] + card.rect[2] and card.rect[1] < coord[1] < card.rect[1] + card.rect[3]:
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
                                     (self.cards[self.last_hovered_card[0]].rect[0] + SCARD_W, self.rect[1]))
                if card.hover and (card.rect[1] + 10 < coord[1] < card.rect[1] + SCARD_H + 10) and (
                        card.rect[0] < coord[0] < card.rect[0] + SCARD_W):
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
            elif coord[0] > self.cards[-1].rect[0] + SCARD_W:
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

    def clear(self):
        """ When game ends, this func clear row's cards list and delete all cards collisions"""
        for i in self.cards:
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
        pl_mr, pl_rr, pl_sr, op_mr, op_rr, op_sr : class Row
            the rows where cards are located when played
        rows_list : list
            a list that contain all row classes of game field
        op_fraction : str
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
        pl_deck_image : pygame.image
            the picture of player's deck
        op_deck_image : pygame.image
            the picture of opponent's deck
        rcoin : pygame.image
            the picture of red coin (enemy turn)
        bcoin : pygame.image
            the picture of blue coin (player turn)
        pl_leader : class Leader
            player leader variable
        op_leader : class Leader
            opponent leader variable
        pl_deck : class Deck
            player deck variable
        op_deck : class Deck
            opponent deck variable
        op_round_score : int
            number of opponent's won rounds
        pl_round_score : int
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

    def __init__(self, screen):
        self.field_image = self.load_image('Field\\Field.jpg', "O")
        self.rcoin = self.load_image('Field\\RCoin.png', 'K')
        self.bcoin = self.load_image('Field\\BCoin.png', 'K')
        self.dump_image = self.load_image('Field\\Dump.png', 'S')
        self.pl_deck_image = self.load_image('Field\\Nilfgaard.png', 'S')
        self.exit = self.load_image('Field\\exit.png', 'O')

        self.round = 0
        self.player_score = 0
        self.opponent_score = 0
        self.op_round_score = 0
        self.pl_round_score = 0
        self.passes = 0
        self.op_crowns = {0: "Red0Crown", 1: "Red1Crown", 2: "Red2Crown"}
        self.pl_crowns = {0: "Blue0Crown", 1: "Blue1Crown", 2: "Blue2Crown"}

        self.pl_mr = Row("melee", "Human", self)  # player melee row
        self.pl_rr = Row("ranged", "Human", self)  # player range row
        self.pl_sr = Row("siege", "Human", self)  # player siege row
        self.op_mr = Row("melee", "AI", self)  # opponent melee row
        self.op_rr = Row("ranged", "AI", self)  # opponent range row
        self.op_sr = Row("siege", "AI", self)  # opponent siege row
        self.rows_list = [self.pl_mr, self.pl_rr, self.pl_sr, self.op_mr, self.op_rr, self.op_sr]

        self.turn = None
        self.can_play_card = True

        self.panel = None
        self.panel_name = ""
        self.panel_tags = ""
        self.panel_text = ""

        self.controls = ["?????? - ???????????????? ?????????? ??????????", "?????? - ?????????????? ??????????"]

        self.op_fraction = None
        self.op_deck_image = None
        self.pl_leader = None
        self.op_leader = None
        self.pl_deck = None
        self.op_deck = None

        self.screen = screen
        self.history = []

    def set_field(self, op_fraction, pl_deck, op_deck, storage):
        """
        When game is chosen in menu, this func makes field ready for a game.
        Based on op_fraction choose op_deck and op_leader. pl_leader, pl_deck and op_deck are stored inside class.
        """
        self.op_fraction = op_fraction
        if op_fraction == "NR":
            self.op_deck_image = self.load_image('Field\\North.png', 'S')
            self.op_leader = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 70)
        elif op_fraction == "Scoia":
            self.op_deck_image = self.load_image('Field\\Scotoeli.png', 'S')
            self.op_leader = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 70)
        self.pl_leader = Leader("Roche180png", "Vernon Roche", "NR", 181, 20, 685)
        storage.append(self.pl_leader)
        storage.append(self.op_leader)
        self.pl_deck = pl_deck
        self.op_deck = op_deck
        storage.append(self.pl_deck)
        storage.append(self.op_deck)

    def refresh(self, storage):
        """ When game ends, this func clear all storages and turn variables value to initial one """
        self.player_score, self.opponent_score = 0, 0
        self.round = 0
        self.pl_mr.refresh(storage)
        self.pl_rr.refresh(storage)
        self.pl_sr.refresh(storage)
        self.op_mr.refresh(storage)
        self.op_rr.refresh(storage)
        self.op_sr.refresh(storage)
        self.rows_list = [self.pl_mr, self.pl_rr, self.pl_sr, self.op_mr, self.op_rr, self.op_sr]
        self.op_fraction = None
        self.turn = None
        self.panel = None
        self.panel_name = ""
        self.panel_tags = ""
        self.panel_text = ""
        self.controls = ["?????? - ???????????????? ?????????? ??????????", "?????? - ?????????????? ??????????"]
        self.op_deck_image = None
        self.pl_leader = None
        self.op_leader = None
        self.pl_deck = None
        self.op_deck = None
        self.passes = 0
        self.op_round_score = 0
        self.pl_round_score = 0
        self.history = []

    def make_move(self):
        """ When coin is pressed this func transfer a possibility to play to another player"""
        if self.passes == 2:
            self.end_round()
        if not self.turn:
            for i in self.rows_list[3::]:
                i.make_turn()
            self.turn = True
            self.can_play_card = True
        else:
            self.turn = False
            for i in self.rows_list[:3]:
                i.make_turn()

    def end_round(self):
        """ When both players passed, func increment round's number and scores win of a round for a player, who has more points"""
        self.round += 1
        self.history.append((self.player_score, self.opponent_score))
        if self.player_score > self.opponent_score:
            self.pl_round_score += 1
        elif self.player_score < self.opponent_score:
            self.op_round_score += 1
        else:
            self.pl_round_score += 1
            self.op_round_score += 1
        if self.round == 3:
            return None
        for i in self.rows_list:
            i.clear()
        self.opponent_score = self.player_score = 0
        self.passes = 0

    def load_image(self, name, size='M'):
        """ Load images from files into game. Size O - original, M - medium, K - square(150x150), S - small"""
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'O':
                image = pygame.image.load(directory)
            elif size == 'M':
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
            elif size == 'K':
                image = pygame.transform.scale(pygame.image.load(directory), (150, 150))
            else:
                image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
            return image

    def set_panel_card(self, card):
        """ Set self.panel with a card class object"""
        self.panel = card

    def count_score(self, player):
        """ Return sum or rows scores"""
        if player == "Human":
            points_sum = 0
            for i in self.rows_list[:3]:
                points_sum += i.count_score()
            self.player_score = points_sum
            return points_sum
        else:
            points_sum = 0
            for i in self.rows_list[3::]:
                points_sum += i.count_score()
            self.opponent_score = points_sum
            return points_sum

    def draw_text(self, surf, text, size, x, y, color=(200, 200, 200)):
        """ Draw line of text in given coordinates"""
        font = pygame.font.SysFont(FONT, size, bold=True)
        text_surface = font.render(text, True, color)
        surf.blit(text_surface, (x, y))

    def render_text(self, pl_hand, op_hand, pl_dump, op_dump):
        """ Draw all text info on screen"""
        self.draw_text(self.screen, self.op_leader.fraction, 20, 20, 20)
        self.draw_text(self.screen, self.pl_leader.fraction, 20, 20, 620)

        self.draw_text(self.screen, self.op_leader.name, 20, 20, 40)
        self.draw_text(self.screen, self.pl_leader.name, 20, 20, 650)

        self.draw_text(self.screen, self.controls[0], 20, 1580, 160)
        self.draw_text(self.screen, self.controls[1], 20, 1580, 190)

        self.draw_text(self.screen, "?????? - ???????????????? ?????????????????????? ????????????", 20, 20, 1010)
        self.draw_text(self.screen, "?????? - ??????. ?????????????????????? ????????????", 20, 20, 1040)

        self.draw_text(self.screen, str(self.op_leader.rability), 20, 250, 325)
        self.draw_text(self.screen, str(self.op_leader.mability), 20, 250, 355)
        self.draw_text(self.screen, str(self.pl_leader.rability), 20, 250, 945)
        self.draw_text(self.screen, str(self.pl_leader.mability), 20, 250, 975)

        self.draw_text(self.screen, str(len(pl_hand.cards)), 30, 1580, 1045)
        self.draw_text(self.screen, str(len(self.pl_deck.cards)), 30, 1675, 1045)
        self.draw_text(self.screen, str(len(pl_dump.cards)), 30, 1810, 1045)

        self.draw_text(self.screen, str(len(op_hand.cards)), 30, 1580, 15)
        self.draw_text(self.screen, str(len(self.op_deck.cards)), 30, 1675, 15)
        self.draw_text(self.screen, str(len(op_dump.cards)), 30, 1810, 15)

        self.draw_text(self.screen, str(self.count_score("AI")), 30, 400, 305, (0, 0, 0))
        self.draw_text(self.screen, str(self.count_score("Human")), 30, 400, 715, (0, 0, 0))

        if self.turn:
            self.draw_text(self.screen, "?????? ??????", 20, 250, 845)
        else:
            self.draw_text(self.screen, "?????? ????????????????????", 20, 250, 845)

        if self.can_play_card:
            self.draw_text(self.screen, "??????????????????", 20, 305, 600)
        else:
            self.draw_text(self.screen, "???????????????? ??????", 20, 305, 600)

    def render_panel(self):
        """ Draw all info (name, tags, description, image) of hovered card"""
        if type(self.panel) == Card:
            card = self.panel
            self.panel_name = card.name
            self.panel_tags = card.tags
            self.panel_text = card.description
            card.render(1575, 230, "M", self.screen)
            self.draw_text(self.screen, str(card.column), 30, 1575, 830, (0, 0, 0))
            self.draw_text(self.screen, str(card.row), 30, 1655, 830, (0, 0, 0))
            self.draw_text(self.screen, card.status, 30, 1700, 830, (0, 0, 0))
        elif type(self.panel) == Leader:
            card = self.panel
            self.screen.blit(self.load_image('CardsPictures\\' + 'L' + card.image_path, 'M'),
                             (1575, 230, 320, 458))
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
        self.screen.blit(self.field_image, (0, 0, SWIDTH, SHEIGHT))
        self.screen.blit(self.op_deck_image, (1630, 0, 105, 150))
        self.screen.blit(self.pl_deck_image, (1630, 935, 105, 150))
        self.screen.blit(self.dump_image, (1765, 0, 105, 150))
        self.screen.blit(self.dump_image, (1765, 935, 105, 150))
        if self.turn:
            self.screen.blit(self.bcoin, (305, 450, 150, 150))
        else:
            self.screen.blit(self.rcoin, (305, 450, 150, 150))
        self.screen.blit(self.exit, (5, 500, 75, 75))
        self.screen.blit(IMAGES[self.op_crowns[self.op_round_score]], (280, 305, 71, 71))
        self.screen.blit(IMAGES[self.pl_crowns[self.pl_round_score]], (280, 925, 71, 71))

    def render_leader(self):
        """ Draw leaders' animated sprites"""
        self.op_leader.update()
        self.pl_leader.update()
        self.op_leader.draw(self.screen)
        self.pl_leader.draw(self.screen)

    def render_hand(self, hand):
        """ Draw all cards which are located in hand during the game"""
        for i in range(len(hand.cards)):
            start_x = 475 + 53 * (10 - len(hand.cards))
            a = i * 110
            if hand.cards[i].hover or hand.cards[i].status == "chosen":
                hand.cards[i].render(start_x + a, 935, "S", self.screen)
                hand.cards[i].rect = (start_x + a, 935, SCARD_W, SCARD_H)
                hand.cards[i].hand_position = i
            else:
                hand.cards[i].render(start_x + a, 945, "S", self.screen)
                hand.cards[i].rect = (start_x + a, 945, SCARD_W, SCARD_H)

    def draw_rows(self):
        """ Draw all cards of all rows which are located in row during the round"""
        for i in self.rows_list:
            length = len(i.cards)
            if length % 2 == 0:
                start_x = (536 + 1030 / 2) - (length // 2) * SCARD_W - length * 10 + 50
            else:
                start_x = (536 + 1030 / 2) - (length // 2) * SCARD_W - length * 10
            x, y = start_x, i.rect[1]
            for j in range(length):
                a = j * SCARD_W
                if i.cards[j].hover or i.cards[j].status == "chosen":
                    i.cards[j].render(x + a, y - 10, "S", self.screen)
                    i.cards[j].rect = (x + a, y - 10, SCARD_W, SCARD_H)
                else:
                    i.cards[j].render(x + a, y, "S", self.screen)
                    i.cards[j].rect = (x + a, y, SCARD_W, SCARD_H)
                x += 10

    def render_game_field(self, pl_hand, op_hand, pl_dump, op_dump):
        """ All render functions are used here"""
        self.render_ui_images()
        self.render_leader()
        self.render_hand(pl_hand)
        self.render_panel()
        self.render_text(pl_hand, op_hand, pl_dump, op_dump)

    def draw_end(self):
        """ Result is displayed, when game ends"""
        if self.pl_round_score > self.op_round_score:
            self.draw_text(self.screen, "???? ????????????????", 30, 700, 400)
        elif self.pl_round_score < self.op_round_score:
            self.draw_text(self.screen, "???? ??????????????????", 30, 750, 400)
        else:
            self.draw_text(self.screen, "??????????", 30, 750, 400)
        self.screen.blit(IMAGES[self.op_crowns[self.op_round_score]], (910, 370, 71, 71))
        self.screen.blit(IMAGES[self.pl_crowns[self.pl_round_score]], (620, 370, 71, 71))

        self.draw_text(self.screen, "????", 30, 650, 500)
        self.draw_text(self.screen, "??????????????????", 30, 910, 500)
        for i in range(len(self.history)):
            a = i * 30
            self.draw_text(self.screen, str(self.history[i][0]), 30, 650, 540 + a)
            self.draw_text(self.screen, str(self.history[i][1]), 30, 910, 540 + a)
