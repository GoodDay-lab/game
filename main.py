import math
import sys
import time
import pygame as pg
import os

import pygame.draw

pg.init()


def get_periodicity(value):
    return value / FPS


def load_image(fileName, colorkey=None):
    fileName = os.path.join('Images', fileName)
    if not os.path.exists(fileName):
        raise FileExistsError
    image = pg.image.load(fileName)
    if colorkey is not None:
        image = image.convert()
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class PageControl():
    def __init__(self):
        self.pages = {}
        self.current_page = None

    def get_current(self):
        if self.current_page:
            return self.current_page
        return list(self.pages.values())[0]

    def set_current(self, name):
        if name in self.pages:
            self.current_page = self.pages[name]

    def add_page(self, name, page):
        self.pages[name] = page

    def execute_current(self):
        process = self.get_current()
        if process:
            next(process)


class ObjectControl():
    def __init__(self):
        self.objects = {}

    def add_object(self, name, object):
        self.objects[name] = object

    def remove_object(self, name):
        del self.objects[name]

    def update(self, e):
        for obj in self.objects.values():
            if hasattr(obj, 'update'):
                obj.update(e)

    def draw(self, screen):
        for obj in self.objects.values():
            if hasattr(obj, 'draw'):
                obj.draw(screen)

    def play_animation(self):
        for obj in self.objects.values():
            if hasattr(obj, 'play_animation'):
                obj.play_animation()
                if obj.count > 1.5:
                    obj.add_animation(message(1 / FPS,
                                              pg.mouse.get_pos(),
                                              screen,
                                              obj.__doc__,
                                              pg.font.SysFont('Arial', 12)))


class Object():
    def init(self):
        self.count = 0
        self.animations = []
        self.add_animation(count_waiting(self))

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def resize(self, w, h):
        self.rect.w = w
        self.rect.h = h

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    @property
    def on_mouse(self):
        return self.rect.collidepoint(pg.mouse.get_pos())

    def play_animation(self):
        i = 0
        while i < len(self.animations):
            animation = self.animations[i]
            try:
                next(animation)
            except StopIteration:
                del self.animations[i]
            i += 1

    def add_animation(self, animation):
        self.animations.append(animation)


class Button(Object):
    def __init__(self, image, func, pos, size=None):
        self.image = image
        self.image = pg.transform.scale(self.image, size or self.image.get_size())
        self.rect = self.image.get_rect()
        self.move(*pos)
        self.statuses = [(self.rect.x, self.rect.y), (self.rect.x + 5, self.rect.y + 5)]
        self.func = func
        self.moveable = True
        self.init()

    def set_sprite(self, fileName):
        self.image = load_image(fileName)

    def set_moveable(self, value):
        self.moveable = value

    def update(self, e):
        self.rect.x, self.rect.y = self.statuses[self.rect.collidepoint(*pg.mouse.get_pos()) and self.moveable]
        if e.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            self.func()

    __doc__ = "Виджет кнопки"


class Input(Object):

    INPUT_FONT = pg.font.SysFont('Arial', 26)
    INPUT_FONT.set_bold(1)

    def __init__(self, image, pos, size):
        self.start_message = "Введите имя"
        self.message = ""
        self.image = pg.transform.scale(image, size)
        self.rect = self.image.get_rect()
        self.move(*pos)
        statements = ['', '|']
        self.animation = animation(1, statements)
        self.animations = []
        self.init()

    def get_centre_h(self):
        return (self.rect.h * 0.45)

    def draw(self, screen):
        message = (self.message or self.start_message)[:16]
        color = 'lightgray' if self.message == "" else "white"
        if self.on_mouse:
            statement = next(self.animation)
        else:
            statement = ''
        textSurface = self.INPUT_FONT.render(message + statement, 1, color)
        screen.blit(self.image, self.rect)
        screen.blit(textSurface, (self.rect.x + WIDTH * 0.010, self.get_centre_h()))

    def update(self, e):
        if not self.on_mouse:
            return
        if pg.key.get_pressed()[pg.K_BACKSPACE]:
            self.message = self.message[:-1]
        if e.type == pg.KEYDOWN and e.key != pg.K_BACKSPACE:
            if len(self.message) < 16:
                self.message += e.unicode

    __doc__ = "Виджет ввода"


class Image(Object):
    def __init__(self, image, pos, size):
        self.image = pg.transform.scale(image, size)
        self.rect = self.image.get_rect()
        self.move(*pos)
        self.animations = []
        self.init()

    __doc__ = "Виджет картинки"


class ValueBar(Object):
    def __init__(self, image, pos, size):
        self.image = pg.transform.scale(image, size)
        self.rect = self.image.get_rect()
        self.move(*pos)
        self.value = 0
        self.init()

    def draw(self, screen):
        visible_value = (pg.mouse.get_pos()[0] - self.rect.x) / self.rect.w if self.rect.collidepoint(pg.mouse.get_pos()) else self.value
        statusSurface = pg.surface.Surface(((self.rect.w - 1) * self.value, self.rect.h - 4))
        statusSurface.fill('green')
        screen.blit(statusSurface, (self.rect.x + 1, self.rect.y + 2))
        screen.blit(self.image, self.rect)

    def update(self, e):
        global VOLUME
        if e.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            self.value = (e.pos[0] - self.rect.x) / self.rect.w
            tuman.set_volume(self.value)
            self.animations.append(message(0.5, (self.rect.x + 10, self.rect.y + 15), screen, f'Volume {round(self.value * 100)}%',
                                           pg.font.SysFont('Arial', 12)))

    __doc__ = "Виджет горизонтальной шкалы"


class DynamicBackground(Object):
    def __init__(self, image):
        self.image = pg.transform.scale(image, (WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.objects = []
        self.init()

    def add_object(self, obj):
        self.objects.append(obj)

    def draw(self, screen):
        surface = pg.surface.Surface(self.rect.size)
        surface.blit(self.image, (0, 0))
        for obj in self.objects:
            obj.play_animation()
            obj.draw(surface)
        screen.blit(surface, (0, 0))

    def update(self, e):
        for obj in self.objects:
            if hasattr(obj, 'update'):
                obj.update(e)

    __doc__ = "Виджет фона"


def animation(perodicity, statements):
    period = 0
    while True:
        statement = statements[int(period // (1 / len(statements)))]
        period = (period + get_periodicity(perodicity)) % 1
        yield statement


def transport(time, self, target_pos):
    current_pos = self.rect.x, self.rect.y
    period = time * FPS
    speed = (target_pos[0] - current_pos[0]) / period, (target_pos[1] - current_pos[1] ) / period
    while not (abs(current_pos[0] - target_pos[0]) <= 0.1 and abs(current_pos[1] - target_pos[1]) <= 0.1):
        current_pos = current_pos[0] + speed[0],\
                        current_pos[1] + speed[1]
        self.rect.x, self.rect.y = current_pos
        yield


def message(time, pos, screen, message, font):
    i = 0
    bg = (245, 245, 220)
    side_c = 'black'
    text = 'black'

    textSurface = font.render(message, 1, text, bg)
    surface = pg.surface.Surface((textSurface.get_width() + 20, textSurface.get_height() + 20))
    surface.fill(bg)
    surface.blit(textSurface, (10, 10))
    pg.draw.rect(surface, side_c, surface.get_rect(), width=3)
    while i < time * FPS:
        screen.blit(surface, pos)
        i += 1
        yield


def count_waiting(self):
    while True:
        self.count += 1 / FPS
        self.count *= self.rect.collidepoint(pg.mouse.get_pos())
        yield


def menu(screen):
    objectControl = ObjectControl()
    button = Button(load_image('StartButton.png', 'white'),
                    lambda: PAGECONTROL.set_current('settings'),
                    (WIDTH * 0.40, HEIGHT * 0.5))
    objectControl.add_object('start_button', button)
    button = Button(load_image('ExitButton.png', 'white'),
                    lambda: sys.exit(),
                    (WIDTH * 0.40, HEIGHT * 0.66),)
    objectControl.add_object('exit', button)
    button = Button(load_image('SettingsButton.png', 'white'),
                    lambda: PAGECONTROL.set_current('settings'),
                    (WIDTH * 0.40, HEIGHT * 0.58), )
    objectControl.add_object('settings', button)
    inputbar = Input(load_image('input.png', 'white'), (WIDTH * 0.008 + 74, HEIGHT * 0.016),
                   (WIDTH * 0.3, 64))
    objectControl.add_object('input', inputbar)
    avatar = Image(load_image('ExitButton.png'), (WIDTH * 0.008 + 2, HEIGHT * 0.016 + 2), (60, 60))
    image = Image(load_image('icon.png', 'white'), (WIDTH * 0.008, HEIGHT * 0.016), (64, 64))
    objectControl.add_object('avatar', avatar)
    objectControl.add_object('icon', image)

    while True:
        for e in pg.event.get():
            objectControl.update(e)
        objectControl.draw(screen)
        objectControl.play_animation()
        yield


def settings(screen):
    objectControl = ObjectControl()

    button = Button(load_image('ExitButton.png'),
                    lambda: PAGECONTROL.set_current('menu'),
                    (WIDTH * 0.7, HEIGHT * 0.2),
                    (32, 32))
    objectControl.add_object('start_button', button)
    valueBar = ValueBar(load_image('VolumeBar.png', 'white'), (WIDTH * 0.1, HEIGHT * 0.5), (WIDTH * 0.3, 64))
    objectControl.add_object('volume', valueBar)

    while True:
        for e in pg.event.get():
            objectControl.update(e)
        objectControl.draw(screen)
        objectControl.play_animation()
        yield


WIDTH, HEIGHT = 0, 0
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
FPS = 100
PAGECONTROL = PageControl()
VOLUME = 0
tuman = pg.mixer.Sound('Music/Tuman.mp3')
tuman.play(loops=-1)
tuman.set_volume(VOLUME)


def main():
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    clock = pg.time.Clock()

    PAGECONTROL.add_page('menu', menu(screen))
    PAGECONTROL.add_page('settings', settings(screen))

    PAGECONTROL.set_current('menu')

    background = DynamicBackground(load_image('background.jpg'))
    image =Image(load_image('ExitButton.png'), (30, 150), (30, 30))
    image.add_animation(transport(6, image, (400, 30)))
    background.add_object(image)

    while True:
        background.draw(screen)
        PAGECONTROL.execute_current()
        clock.tick(FPS)
        pg.display.flip()


if __name__ == '__main__':
    main()