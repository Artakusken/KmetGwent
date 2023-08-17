from CONSTANTS import *
from Cards_Descriptions import descriptions
pygame.init()


class Card:
    """
    A class which represent game card. The main and the only unit on the field.
    It can have many various positions. Card's points value is thing that defines player score in a round.
    """

    def __init__(self, name, base_power, image_name, armor, provision, card_type, fraction, tags, d=None, o=None, e=None, c=None):
        # fraction set
        if fraction == "NR":
            self.fraction = "Королевства Севера"
        elif fraction == "NG":
            self.fraction = "Нильфгаард"
        else:
            self.fraction = fraction
        # get cards parameters and set fonts
        self.name = name
        self.bp = base_power
        self.power = self.bp
        self.armor = armor
        self.image_path = image_name
        self.provision = provision
        self.card_type = card_type
        self.tags = tags
        # initial game parameters
        self.row = None
        self.column = None
        self.field_position = [self.row, self.column]
        self.turns_in_hand = 0
        self.turns_in_deck = 0
        self.turns_on_field = 0
        self.turns_in_dump = 0
        self.location = None
        self.status = "passive"
        self.hand_position = None
        self.rect = None
        self.hover = False
        # get description text (from py-file) and images (from pictures folder)
        self.description = self.form_text()
        self.frame = self.load_card_image("Field\\cframe.png", "O")
        self.Mimage = self.load_card_image(f'CardsPictures\\{self.fraction}\\' + 'M' + image_name, 'O')
        self.MSimage = self.load_card_image(f'CardsPictures\\{self.fraction}\\' + 'MS' + image_name, 'O')
        self.Simage = self.load_card_image(f'CardsPictures\\{self.fraction}\\' + 'S' + image_name, 'O')
        # cards abilities
        self.deployment = d
        self.order = o
        self.turn_end = e
        self.conditional = c

    def load_card_image(self, name, size):
        """ Load images from files into game. Size O - original, M - medium, K - square(150x150), S - small"""
        directory = os.path.join(name)
        if os.path.isfile(directory):
            if size == 'M':
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
            elif size == 'S':
                image = pygame.transform.scale(pygame.image.load(directory), (SCARD_W, SCARD_H))
            else:
                image = pygame.image.load(directory)
            return image

    def form_text(self):
        """ Form a text which consists of lines with length of TEXT_LENGTH symbols"""
        if self.name in descriptions.keys():
            length = 0
            lines = []
            line = ''
            for i in descriptions[self.name].split():
                if length + len(i) < TEXT_LENGTH:
                    line = f"{line} {i}"
                    length += len(i)
                else:
                    lines.append(line)
                    line = '' + i
                    length = 0 + len(i)
            lines.append(line)
            return lines
        else:
            return ["EMPTY DESCRIPTION"]

    def display_cards_points(self, x, y, size, ptype, screen, font):
        """ Render card's (placed in the row or hand) points over slot on the left upper corner and armor on the right upper corner"""
        if size == "M":
            dx = 267
            text_coord_delta = 15
        elif size == "D":
            dx = 160
            text_coord_delta = 15
        else:
            dx = 77
            text_coord_delta = 10
        y += 2

        if self.power == self.bp:
            font_color = (200, 200, 200)
        elif self.power > self.bp:
            font_color = (50, 200, 50)
        else:
            font_color = (200, 50, 50)
        if ptype == "p":
            points = font.render(str(self.power), True, font_color)
            # screen.blit(font.render(str(self.turns_on_field), True, font_color), (x + dx // 2, y + 90))
            if self.power > 9:
                screen.blit(points, (x + text_coord_delta, y + text_coord_delta))
            else:
                screen.blit(points, (x + text_coord_delta + 6, y + text_coord_delta))
        else:
            armor = font.render(str(self.armor), True, (0, 0, 0))
            if self.armor > 9:
                screen.blit(armor, (x + dx + text_coord_delta - 6, y + text_coord_delta))
            else:
                screen.blit(armor, (x + dx + text_coord_delta, y + text_coord_delta))

    def render(self, x, y, size, screen, font):
        """ Render card's image and set its collision"""
        if self.rect:
            if size == 'M':
                screen.blit(self.Mimage, (x, y, MCARD_W, MCARD_H))
                screen.blit(IMAGES["LLCorner"], (x, y))
                self.display_cards_points(x, y, "M", "p", screen, font)
                if self.armor > 0:
                    screen.blit(IMAGES["LRCorner"], (x + 263, y + 2))
                    self.display_cards_points(x, y, "M", "a", screen, font)
            elif size == 'D':
                screen.blit(self.MSimage, (x, y, LEADER_W, LEADER_H))
                screen.blit(IMAGES["LLCorner"], (x, y))
                self.display_cards_points(x, y, "D", "p", screen, font)
                if self.armor > 0:
                    screen.blit(IMAGES["LRCorner"], (x + 156, y + 4))
                    self.display_cards_points(x, y, "D", "a", screen, font)
            else:
                screen.blit(self.Simage, (x, y, SCARD_W, SCARD_H))
                screen.blit(IMAGES["SLCorner"], (x, y))
                self.display_cards_points(x, y, "S", "p", screen, font)
                if self.armor > 0:
                    screen.blit(IMAGES["SRCorner"], (x + 77, y + 3))
                    self.display_cards_points(x, y, "S", "a", screen, font)
                if self.status == "chosen":
                    screen.blit(self.frame, (x - 3, y - 3))

    def on_click(self, game_field, click_type, coord, game_object):
        """ Manage arguments and choose what actions to do"""
        if click_type == 1:
            if self.location.str_type == "Hand" and game_field.can_play_card:
                if game_object is None:
                    if self.status == "passive":
                        self.status = "chosen"
                        return self
                elif game_object is self:
                    if self.status == "chosen":
                        self.status = "passive"
                        return None
                else:
                    game_object.status = "passive"
                    self.status = "chosen"
                    return self
            if self.location.str_type == "Row":
                if game_object is None:
                    if self.status == "passive":
                        return self.activate_order(card=self, field=game_field, row=self.location)
                    else:
                        self.status = "passive"
                        return None
                elif game_object is self:
                    if self.status == "chosen":
                        self.status = "passive"
                        return None
                elif isinstance(game_object, Card) and game_object.location.str_type == "Hand" and len(self.location.cards) < 9:
                    game_object.location.cards.pop(game_object.hand_position)
                    if len(game_object.location.cards) > 1:
                        for i in game_object.location.cards[game_object.hand_position::]:
                            i.hand_position -= 1
                    self.location.add_card(game_object, 1, coord)
                    game_object.deploy(card=game_object, field=game_field, row=self.location)
                    return None
                elif isinstance(game_object, Leader) and game_object.status == "chosen extra ability" and game_object.rability > 0:
                    if game_object.card_to_move1 is self:
                        self.status = "passive"
                        game_object.card_to_move1 = None
                    else:
                        if game_object.card_to_move1 is None:
                            game_object.card_to_move1 = self
                            self.status = "chosen"
                        elif game_object.card_to_move2 is None:
                            game_object.card_to_move2 = self
                            game_object.extra_ability()
                return game_object
        else:
            if game_object is self:
                if self.status == "chosen":
                    self.status = "passive"
                    return None
            elif game_object:
                game_object.status = "passive"
                return None

    def deploy(self, card=None, field=None, row=None):
        """ Action that card does, when deployed on the field (row)"""
        if self.deployment:
            self.deployment(self, field, row)

    def activate_order(self, card=None, field=None, row=None):
        if self.turns_on_field > 0 and self.order:
            self.order(self, field, row)
            self.order = None
            return None
        self.status = "chosen"
        return self

    def new_turn(self):
        loc = self.location
        if loc.str_type == "Hand":
            self.turns_in_hand += 1
        elif loc.str_type == "Deck":
            self.turns_in_deck += 1
        elif loc.str_type == "Row":
            self.turns_on_field += 1
        elif loc.str_type == "Dump":
            self.turns_in_dump += 1

        if self.conditional:
            self.conditional(self, self.location.field, self.location)

        if self.turn_end:
            self.turn_end(self, self.location.field, self.location)

    def kill(self, op_dump, pl_dump, pl_hand, op_hand):
        """ Move card with 0 points to dump"""
        if self.fraction == "Skellige":
            self.location = pl_dump
            pl_dump.cards.append(self)
            pl_hand.pop_card(-1)
        else:
            self.location = op_dump
            op_dump.cards.append(self)
            op_hand.pop_card(-1)
        self.rect = None

    def copy(self):
        """ Return Card class with same args"""
        return Card(self.name, self.bp, self.image_path, self.armor, self.provision, self.card_type, self.fraction, self.tags, self.deployment, self.order, self.turn_end, self.conditional)


class Leader(pygame.sprite.Sprite):
    """
    A class which represent player unique card - leader.
    It's static. Doesn't have any points but has two abilities to manipulate cards.
    """

    def __init__(self, animation, name, fraction, frame_n, x, y):
        super().__init__()
        self.frames = []
        self.name = name
        self.cur_frame = 0
        self.frames_number = frame_n

        if fraction == "NR":
            self.fraction = "Королевства Севера"
        elif fraction == "NG":
            self.fraction = "Нильфгаард"
        elif fraction == "SC":
            self.fraction = "Скоятаэли"

        self.rect = pygame.Rect(x, y, LEADER_W, LEADER_H)
        # self.image_path = name + '.png'
        self.image = self.load_image("CardsPictures\\Лидеры\\" + self.name + ".png")
        self.load_image(animation, True)
        self.description = self.form_text()
        self.rability = 3
        self.card_to_move1 = None
        self.card_to_move2 = None
        self.mability = 1
        self.status = "passive"
        self.frame = self.load_image('Field\\BigCardFrame.png')

    def load_image(self, name, animation=False):
        """ Load animation frames and image for a panel"""
        if animation:
            directory = os.path.join('Animations', name + '\\')
            for i in os.listdir(directory):
                if os.path.isfile(directory + i):
                    image = pygame.image.load(directory + i)
                    self.frames.append(pygame.transform.scale(image, (LEADER_W, LEADER_H)))
                else:
                    print(f"Файл с изображением '{i}' не найден")
        else:
            directory = os.path.join(name)
            if os.path.isfile(directory):
                image = pygame.transform.scale(pygame.image.load(directory), (MCARD_W, MCARD_H))
                return image

    def form_text(self):
        """ Form a text which consists of lines with length of TEXT_LENGTH symbols"""
        if self.name in descriptions.keys():
            length = 0
            lines = []
            line = ''
            for i in descriptions[self.name].split():
                if length + len(i) < TEXT_LENGTH:
                    line = f"{line} {i}"
                    length += len(i)
                else:
                    lines.append(line)
                    line = '' + i
                    length = 0 + len(i)
            lines.append(line)
            return lines
        else:
            return ["EMPTY DESCRIPTION"]

    def extra_ability(self):
        card1_row = self.card_to_move1.location
        if card1_row == self.card_to_move2.location:
            card1_row.cards.insert(self.card_to_move2.column, card1_row.cards.pop(self.card_to_move1.column))

        self.card_to_move1.status = "passive"
        self.card_to_move1 = None
        self.card_to_move2 = None
        self.rability -= 1

    def update(self):
        """ Pick next frame from frames and set is as current frame"""
        self.cur_frame = (self.cur_frame + 1) % self.frames_number

    def on_click(self, game_field, click_type, game_object):
        """ Manage arguments and choose what actions to do"""
        if self.status == "passive" and click_type == 1 and self.rability > 0:
            self.status = "chosen extra ability"
            if type(game_object) == Card or type(game_object) == Leader:
                game_object.status = 'passive'
            return self
        elif self.status == "chosen extra ability" and click_type == 1:
            if any([self.card_to_move1, self.card_to_move2]):
                self.card_to_move1.status = "passive"
                self.card_to_move1 = None
                self.card_to_move2 = None
            self.status = "passive"
            return None
        if self.status == "passive" and click_type == 2:
            self.status = "chosen main ability"
            if type(game_object) == Card or type(game_object) == Leader:
                game_object.status = 'passive'
            return self
        elif self.status == "chosen main ability" and click_type == 2:
            self.status = "passive"
            return None

    def draw(self, screen):
        """ Render images"""
        if self.status != 'passive':
            screen.blit(self.frame, (self.rect[0] - 10, self.rect[1] - 10))
        screen.blit(self.frames[self.cur_frame], (self.rect[0], self.rect[1]))
