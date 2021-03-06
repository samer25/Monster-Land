import pygame
import sys
from level import Level

from settings import *


class Game:
    def __init__(self):
        """Initiating pygame, creating display surface, creating a clock"""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Monster Land')
        self.clock = pygame.time.Clock()

        self.level = Level()

        # sound
        main_sound = pygame.mixer.Sound('./media/audio/main.ogg')
        main_sound.play(loops=-1)

    def run(self):
        """Game loop"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # checking if we quit the game
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()

            """Filling the display black, updating the screen, adding the fps"""
            self.screen.fill(WATER_COLOR)
            self.level.run()  # drawing and updating
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()  # instance of the Game class
    game.run()  # calling the run method
