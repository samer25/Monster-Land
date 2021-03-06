from random import choice, randint

import pygame

from enemy import Enemy
from magic import MagicPlayer
from particles import AnimationPLayer
from settings import *
from support import import_csv_layout, import_folder
from tile import Tile
from player import Player
from debug import debug
from ui import UI
from upgrade import Upgrade
from weapon import Weapon


class Level:
    """ contains all sprites (player, enemies, map, all the obstacles) also deal with their interactions"""

    def __init__(self):
        """visible sprites - group for sprites that will be drawn only group that draws sprites"""
        self.player = None
        """obstacle_sprites - group for sprites that the player can collide with"""
        # getting display surface anywhere from our code (like from main Game self.screen)
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False
        # sprite group setup
        self.visible_sprites = YSortCameraGroup()  # custom sprites Group
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprite = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        # particles
        self.animation_player = AnimationPLayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        else:
            self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprite, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def create_map(self):
        """ Creating a map using the WORLD_Map matrix if col is x will be a wall if it is p will be the player"""
        layouts = {
            'boundary': import_csv_layout('media/csv/map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('media/csv/map/map_Grass.csv'),
            'object': import_csv_layout('media/csv/map/map_Objects.csv'),
            'entities': import_csv_layout('./media/csv/map/map_Entities.csv')
        }

        graphics = {
            'grass': import_folder('./media/grass'),
            'objects': import_folder('./media/objects')
        }
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        if style == 'grass':
                            # create a grass tile
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprite], 'grass',
                                 random_grass_image)
                        if style == 'object':
                            # create an object tile
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)

                        if style == 'entities':
                            if col == '394':
                                self.player = Player((x, y),
                                                     [self.visible_sprites],
                                                     self.obstacle_sprites,
                                                     self.create_attack,
                                                     self.destroy_attack,
                                                     self.create_magic)
                            else:
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'
                                Enemy(monster_name,
                                      (x, y),
                                      [self.visible_sprites, self.attackable_sprite],
                                      self.obstacle_sprites, self.damage_player, self.trigger_death_particles, self.add_xp)
        # for row_index, row in enumerate(WORLD_MAP):
        #     for col_index, col in enumerate(row):
        #         x = col_index * TITLE_SIZE
        #         y = row_index * TITLE_SIZE
        #         if col == 'x':
        #             Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
        #         if col == 'p':
        #             self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()

            # spawn particles
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def add_xp(self, amount):
        self.player.exp += amount

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def run(self):
        # update and draw the game
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            # display upgrade menu
            self.upgrade.display()
        else:
            # run the game
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()

        # debug(self.player.direction)


class YSortCameraGroup(pygame.sprite.Group):
    """First part: Function as a camera """
    """Second part: Y sort is going to sort the sprite by the Y coordinate that way will give them some overlap"""

    def __init__(self):
        super().__init__()
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load('./media/tilemap/ground.png')
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        """Sorting the sprite to be created first and drawing the all elements"""
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_position)

    def enemy_update(self, player):
        enemy_sprite = [sprite for sprite in self.sprites() if
                        hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprite:
            enemy.enemy_update(player)
