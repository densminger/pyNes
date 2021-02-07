import pygame
import time
import sys

class GameEngine():
    # color constants
    COLOR_BLACK = (0,0,0)
    COLOR_WHITE = (255,255,255)
    COLOR_RED = (255,0,0)
    COLOR_LIME = (0,255,0)
    COLOR_BLUE = (0,0,255)
    COLOR_YELLOW = (255,255,0)
    COLOR_CYAN = (0,255,255)
    COLOR_MAGENTA = (255,0,255)
    COLOR_SILVER = (192,192,192)
    COLOR_GRAY = (128,128,128)
    COLOR_MAROON = (128,0,0)
    COLOR_OLIVE = (128,128,0)
    COLOR_GREEN = (0,128,0)
    COLOR_PURPLE = (128,0,128)
    COLOR_TEAL = (0,128,128)
    COLOR_NAVY = (0,0,128)
    #COLOR_LIGHTBLUE = (0, 79, 132)

    # user_init and user_update both take 1 parameter - this GameEngine object
    def __init__(self):
        pygame.init()
        self.font = None
        self.updates_per_second = 30
        self.user_init()

    def construct(self, width, height, updates_per_second=60):
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(self.COLOR_BLACK)
        self.updates_per_second = updates_per_second
        self.last_update_time = None
        self.keypressed = None

    def run(self):
        while True:
            #clock.tick(1843266)
            self.keypressed = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.keypressed = pygame.key.name(event.key)
            curtime = time.clock_gettime(time.CLOCK_REALTIME)
            self.engine_update((curtime - self.last_update_time)) if self.last_update_time is not None else self.engine_update(0.0)
            self.last_update_time = curtime

    def set_font(self, filename, size):
        self.font = pygame.font.Font(filename, size)

    def user_init(self):
        pass

    def engine_update(self, elapsed_time):
        self.user_update(elapsed_time)

    def draw_string(self, x,  y, text, color=COLOR_WHITE):
        if self.font is None:
            return
        img = self.font.render(text, False, color)
        self.screen.blit(img, (x, y))
