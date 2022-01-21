import pygame as pg
import sys
import random


class Page(pg.sprite.AbstractGroup):
    def __init__(self, *sprites):
        super().__init__()
        self.add(*sprites)
        self.background = None

    def event_handler(self, e):
        if e.type == pg.MOUSEBUTTONDOWN:
            for button in self.sprites():
                if button.rect.collidepoint(e.pos):
                    if hasattr(button, 'click'):
                        button.click()

    def set_background(self, sprite):
        self.background = sprite

    def draw(self, surface):
        if self.background is not None:
            self.background.update()
            surface.blit(self.background.image, self.background.rect)
        super().draw(surface)


class PageControl(object):
    def __init__(self):
        self.current_page = None
        self.queue = {}

    def add_page(self, name, value):
        self.queue[name] = value

    def remove_page(self, name):
        del self.queue[name]

    def get_page(self, name):
        return self.queue[name] if name in self.queue else None

    def get_current_page(self):
        if self.current_page is None:
            return list(self.queue.values())[0]
        return self.current_page

    def set_current_page(self, name):
        self.current_page = self.queue[name]
    
    def event_handler(self, e):
        if not self.current_page:
            list(self.queue.values())[0].event_handler(e)
        self.current_page.event_handler(e)

    def set_background(self, *args):
        for page in self.queue.values():
            page.set_background(*args)

    def get_pages(self):
        return self.queue


class PageObject(pg.sprite.Sprite):
    def __init__(self, page, image):
        super().__init__(page)
        self.image = image
        self.rect = self.image.get_rect()

    def move(self, x, y):
        self.rect.x, self.rect.y = x, y

    def resize(self, w, h):
        self.image = pg.transform.scale(self.image, (int(w), int(h)))
        self.rect = self.image.get_rect()

    def set_geometry(self, x, y, w, h):
        self.resize(w, h)
        self.move(x, y)

    def click(self, *args, **kwargs):
        pass


class Button(PageObject):
    def __init__(self, page, image, target=lambda: 0):
        super().__init__(page, image)
        self.target = target
        
    def click(self, *args, **kwargs):
        self.target(*args, **kwargs)

    def set_target(self, target):
        self.target = target


class Background(pg.sprite.Sprite):
    def __init__(self, image, size):
        super().__init__()
        self.image = image
        self.image = pg.transform.scale(self.image, size)
        self.rect = self.image.get_rect()

    def update(self):
        pass


class DynamicalBackground(pg.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pg.surface.Surface(size)
        self.rect = self.image.get_rect()
        self.count = 0
        self.FPS = 1000

    def update(self):
        if not self.count % self.FPS:
            self.image.fill('black')
            for _ in range(10):
                pg.draw.circle(self.image, 'red', (random.randint(30, 770), random.randint(30, 770)), 20)
        self.count += 1
   
    def change_FPS(self, value):
        self.FPS = max(1, value)


class GamePage(Page):
    def __init__(self, main_process):
        super().__init__()
        self.main_process = main_process

    def update(self):
        self.main_process(self.sprites()[0])



if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((800, 800))
    img = pg.image.load('img.jpeg')
    # img2 = pg.image.load('images.jpeg')
    # background = Background(img2)
    background2 = Background(img)
    bg3 = DynamicalBackground()

    pages = PageControl()

    menu = Page()
    pages.add_page('menu', menu)
    pages.set_current_page('menu')
   
    Button(pages.get_current_page(), img, target=lambda: bg3.change_FPS(40)).move(0, 0)
    Button(pages.get_current_page(), img, target=lambda: print('hello')).move(400, 400)
    Button(pages.get_current_page(), img, target=lambda: pages.set_current_page('game')).move(10, 400)
    
    game = Page()
    pages.add_page('game', game)
    pages.set_current_page('game')

    Button(pages.get_current_page(), img, target=lambda: pages.set_current_page('menu')).move(10, 400)
    Button(pages.get_current_page(), img, target=lambda: print('100')).set_geometry(600, 400, 32, 32)
    
    pages.set_current_page('menu')
    pages.set_background(background2)
    print(pages.get_pages())
    c = 0
    while True:
        screen.fill('black')
        for event in pg.event.get():
            pages.event_handler(event)
        pages.get_current_page().draw(screen)
        pages.get_current_page().update()
        pg.display.flip()

