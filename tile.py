import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILE_SIZE, TILE_SIZE))):
        super().__init__(groups)
        # self.image = pygame.image.load('./media/test/rock.png').convert_alpha()
        self.sprite_type = sprite_type  # it can be enemy, invisible ...
        y_offset = HIT_BOX_OFFSET[sprite_type]
        self.image = surface
        if sprite_type == 'object':
            # do an offset
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILE_SIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)  # full size of our image
        self.hit_box = self.rect.inflate(0, y_offset)  # changing the size of the image for overlapping

