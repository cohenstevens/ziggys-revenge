import math
import pygame
import random
from scripts.particle import Particle
from scripts.spark import Spark

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size): #take game as parameter so anything in the game is accessible with entity
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0,0]
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}

        self.action = ''
        self.anim_offset = (-3, -3) # adds padding so animation can go outside hitbox
        self.flip = False
        self.set_action('idle')
        self.last_movement = [0,0]

# to create collision you need a rect to collide with and a rect that is colliding
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action # updates actions
            self.animation = self.game.assets[self.type + '/' + self.action].copy() # updates animation
    
    def update(self, tilemap, movement=(0,0)):
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}

        frame_movement = (movement[0] +  self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0] # x position movement
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):     # if youve made a collision
                if frame_movement[0] > 0:         # youre moving right
                    entity_rect.right = rect.left # right edge of entity snaps to left edge of tile
                    self.collisions['right'] = True
                if frame_movement[0] < 0:         # youre moving left
                    entity_rect.left = rect.right # left edge of entity snaps to right edge of tile
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
                

        self.pos[1] += frame_movement[1] # y position movement
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):     # 
                if frame_movement[1] > 0:         # 
                    entity_rect.bottom = rect.top # 
                    self.collisions['down'] = True
                if frame_movement[1] < 0:         # 
                    entity_rect.top = rect.bottom # 
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1) # (5, ?) represnets a maximum velo downwards of 5
                                                          # allows for gravity speed to not grow / terminal velocity
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size) # calls default constructor

        self.walking = 0

    def update(self, tilemap, movement=(0,0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip # if you run into something on your right or left flip/turn around
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1]) # if looking left you subtract that movement so move to the left, otherwise you add 0.5 bc youre facing right
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1]) # difference between player and enemy pos
                if (abs(dis[1] < 16)): # if they are less than 16 pixels away on the y-axis
                    if (self.flip and dis[0] < 0): # if looking left and player is left
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random())) # self.projectiles[-1][0] -1 is last projectile shot # + math.pi makes it face left
                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random())) 

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120) # random number to decide how many frames the enemy will continue to walk for 30-120

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

    def render(self, surf, offset=(0,0)):
        super().render(surf, offset=offset)

        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size) # calls default constructor
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

# deals with animation
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump') # dont want running animation to be playing while jumping so you put first in if statement
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        # creates a burst of particles in first 10 frames
        if abs(self.dashing) in {60, 50}:
                for i in range(20):
                    angle = random.random() * math.pi * 2 # deals with radians # spawns random direction in circle 
                    speed = random.random() * 0.5 + 0.5 # 0.5 - 1
                    pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed] # cos is x, sin is y # problems with scaling if you use random number
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0,7)))

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        else:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50: # during the first 10 frames of the dash
            self.velocity[0] = abs(self.dashing) / self.dashing * 8 # divides abs by itself you will get direction of scalar so -1 or 1
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1 # works as a cooldown so you cant keep dashing
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0] # makes particles move on x-axis with dash
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0,7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0) # makes sure you arent constantly getting moved to the left
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0,0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1) # making sure you dont get -1 jumps
                return True # return true so you can do something else based off jump
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps: # if jumps is 0 this is false
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5 # bc self.air_time > 4 so you want animation to start
            return True
        
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60 # 60 is for how long you are dashing, the negative is for the direction
            else:
                self.dashing = 60