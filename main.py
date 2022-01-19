import pygame
import random
import json
from Race.client import Client
from menu import *

# TODO:
#  menu
#  class button
#  group of sprites
#  music
#  voice phrases


class Car:
    def __init__(self, x, y, sprite, speed=2, max_speed=100):
        self.x, self.y = x, y
        self.sprite, self.speed, self.max_speed = sprite, speed, max_speed

class Animation(pygame.sprite.Sprite):
    def __init__(self, images, time_interval, index=0):
        super(Animation, self).__init__()
        self.images = images
        self.image = self.images[0]
        self.time_interval = time_interval
        self.index = index
        self.timer = 0

    def update(self, seconds, reverse=False):
        self.timer += seconds
        if self.timer >= self.time_interval:
            self.image = self.images[self.index]
            if reverse:
                self.image = pygame.transform.flip(self.image, True, False)
            self.index = (self.index + 1) % len(self.images)
            self.timer = 0


def game():
    global running_game, w_cars
    global b_UP, b_DOWN, b_LEFT, b_RIGHT

    mw.blit(sprite_background, (0, 0))
    flag = False

    distance_render = 300

    while running_game:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause()
                    mw.blit(w_background, (0, 0))
                    mw.blit(w_hills, (0, Y * 0.5))
                    mw.blit(w_cars, (0, Y * 0.6))
                    pygame.display.flip()

            if event.type == pygame.QUIT:
                running_game = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            b_UP = True

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            b_DOWN = True

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            b_LEFT = True

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            b_RIGHT = True

        flag = False

        mw.blit(w_background, (0, 0))
        # mw.blit(w_hills, (0, Y * 0.5))
        mw.blit(road.image, (0, Y * 0.6))

        s.fill((255, 255, 255))
        speedometer = pygame.font.SysFont('Arial', 40).render(
            f'{int(player.speed)} км/ч    {int(clock.get_fps())}/{FPS}fps', True, (139, 16, 200))
        s.blit(speedometer, (0, 0))
        mw.blit(s, (0, Y * 0.9))

        if online:
            data = client_.get_data()
            player_auto = data[0]
            for obj in data:
                if 100 > obj['length'] - player_auto['length'] >= 0:
                    sprite = None
                    if obj['is_go_right']: sprite = sprite_car13
                    elif obj['is_go_left']: sprite = sprite_car11
                    else: sprite = sprite_car12

                    # Тут должна быть формула вычисления размера машинки, пока я не могу её вывести
                    K = distance_render - (obj['length'] - player_auto['length'])
                    aspect = (distance_render / K)
                    sprite = pygame.transform.scale(sprite, (aspect * sprite.get_width(), aspect * sprite.get_height()))

                    # sprite = pygame.transform.scale(sprite, (sprite.get_width() * K, sprite.get_height() * K))

                    mw.blit(sprite, (obj['pos_on_road'] * 300 + X * 0.5 - 0.5 * sprite_car12.get_rect()[2],
                                     max((Y * 0.8 * aspect), Y * 0.55)))
            w_cars.blit(sprite_car12, (X * 0.5 + (100 * data[0]['pos_on_road']), Y * 0.75))

            client_.send_data({'up': b_UP,
                               'down': b_DOWN,
                               'left': b_LEFT,
                               'right': b_RIGHT})

            b_UP = b_DOWN = b_LEFT = b_RIGHT = False
        '''mw.blit(w_background, (0, 0))
        mw.blit(w_hills, (0, Y * 0.5))
        mw.blit(w_cars, (0, Y * 0.6))'''

        pygame.display.flip()
        mw.fill((0, 0, 0))
        w_cars.fill((0, 0, 0))
        clock.tick(FPS)


def menu():
    global running_menu
    b = pygame.Rect(100, 100, 100, 100)
    c = pygame.Rect(300, 300, 100, 100)
    d = Button(500, 500, 100, 100, a4)
    mw.blit(a1, (0, 0))
    mw.blit(d.sprite, (d.x, d.y))
    pygame.draw.rect(mw, (0, 0, 255), b), pygame.draw.rect(mw, (0, 255, 0), c)

    while running_menu:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
                if b.collidepoint(event.pos):
                    game()
                if c.collidepoint(event.pos):
                    if server_connect():
                        game()
                    else:
                        print('no connection')
                if d.collidepoint(event.pos):
                    d.my()

        pygame.display.flip()
        clock.tick(FPS)


def pause():
    global running_game, running_game

    running_pause = True

    pause_menu = pygame.Rect((X * 0.3, Y * 0.2), (X * 0.4, Y * 0.6))
    pause_resume = pygame.Rect((X * 0.35, Y * 0.25), (X * 0.3, Y * 0.1))
    pause_settings = pygame.Rect((X * 0.35, Y * 0.4), (X * 0.3, Y * 0.1))
    pause_exit = pygame.Rect((X * 0.35, Y * 0.55), (X * 0.3, Y * 0.1))

    pause_resume_txt = pygame.font.SysFont('Arial', 40).render('Продолжить', True, (0, 0, 0))
    pause_settings_txt = pygame.font.SysFont('Arial', 40).render('Настройки', True, (0, 0, 0))
    pause_exit_txt = pygame.font.SysFont('Arial', 40).render('Выйти', True, (0, 0, 0))

    while running_pause:
        pygame.draw.rect(mw, (100, 100, 100), pause_menu)
        pygame.draw.rect(mw, (200, 200, 200), pause_resume)
        pygame.draw.rect(mw, (200, 200, 200), pause_settings)
        pygame.draw.rect(mw, (200, 200, 200), pause_exit)

        mw.blit(pause_resume_txt, (X * 0.45, Y * 0.3))
        mw.blit(pause_settings_txt, (X * 0.45, Y * 0.45))
        mw.blit(pause_exit_txt, (X * 0.45, Y * 0.6))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                xx, yy = event.pos

                if pause_resume.collidepoint(xx, yy):
                    running_pause = False

                elif pause_settings.collidepoint(xx, yy):
                    pass

                elif pause_exit.collidepoint(xx, yy):
                    running_pause = running_game = False

            if event.type == pygame.QUIT:
                running_pause = running_game = False

        pygame.display.flip()
        clock.tick(FPS)

    mw.blit(w_background, (x_background, y_background))
    mw.blit(w_hills, (0, Y * 0.5))
    mw.blit(w_cars, (0, Y * 0.6))
    pygame.display.flip()


client = None
online = False

CarGoRight0 = pygame.image.load('car13.png')
CarGoFront0 = pygame.image.load('car12.png')
CarGoLeft0 = pygame.image.load('car11.png')


def server_connect():
    try:
        global client, online
        client = Client('192.168.0.173', 5555)
        client.join_room()
        online = True
        return True
    except ConnectionRefusedError:
        print('aboba')
        return False
    except TimeoutError:
        print('amoma')
        return False


def main():
    global client, online
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    FPS = 100
    X, Y = pygame.display.get_window_size()
    is_running = True
    
    # Loading images
    StartButton = pygame.image.load('StartButton.png')
    ExitButton = pygame.image.load('ExitButton.jpg')
    ExitButton = ExitButton.convert_alpha()
    ExitButton.set_colorkey('white')

    # game process
    def process(screen):
        global CarGoLeft0, CarGoRight0, CarGoFront0
        distance_render = 300
        screen.image.fill((0, 0, 0))
        K_UP, K_DOWN, K_LEFT, K_RIGHT = False, False, False, False

        keys = pygame.key.get_pressed()
        K_UP = keys[pygame.K_UP] or keys[pygame.K_w]
        K_DOWN = keys[pygame.K_DOWN] or keys[pygame.K_s]
        K_LEFT = keys[pygame.K_LEFT] or keys[pygame.K_a]
        K_RIGHT = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        if online:
            data = client.get_data()
            me = data[0]
            print(me)
            for obj in data:
                if distance_render > obj['length'] - me['length'] >= 0 or True:
                    if obj['is_go_right']: sprite = CarGoRight0
                    elif obj['is_go_left']: sprite = CarGoLeft0
                    else: sprite = CarGoFront0

                    k = distance_render - (obj['length'] - me['length'])
                    aspect = distance_render / k
                    if aspect <= 0: continue
                    sprite = pygame.transform.scale(sprite, (sprite.get_width() * aspect, sprite.get_height() * aspect))
                    
                    screen.image.blit(sprite,
                            (obj['pos_on_road'] * 300 * aspect + X * 0.5 - sprite.get_width() / 2, Y * 0.7 * aspect))
                    screen.image.blit(pygame.font.SysFont('Calibri', 12).render(obj['name'], 1, 'white'),
                            (obj['pos_on_road'] * 300 + X * 0.5 - 30, Y * 0.7 * aspect + 60))
            screen.image.blit(pygame.font.SysFont('Calibri', 20).render(str(obj['speed']), 1, 'black', 'white'), (0, Y * 0.8))
            client.send_data({'up': K_UP, 'down': K_DOWN, 'left': K_LEFT, 'right': K_RIGHT})


    
    pages = PageControl()

    menu = Page()
    pages.add_page('menu', menu)
    pages.set_current_page('menu')

    Button(pages.get_current_page(), StartButton, target=lambda: pages.set_current_page('game')).set_geometry(X * 0.45, Y * 0.55, X * 0.1, Y * 0.1)
    Button(pages.get_current_page(), ExitButton, target=lambda: sys.exit()).set_geometry(X * 0.97, Y * 0.01, X * 0.02, Y * 0.02)

    game = GamePage(process)

    game_window = pygame.sprite.Sprite(game)
    game_window.image = pygame.surface.Surface((X, Y))
    game_window.rect = game_window.image.get_rect()
    print(game_window.rect)

    pages.add_page('game', game)

    print(pages.get_pages())
    
    while is_running:
        screen.fill('black')
        for e in pygame.event.get():
            pages.event_handler(e)
        pages.get_current_page().update()
        pages.get_current_page().draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


if __name__ == '__main__':
    server_connect()
    main()
