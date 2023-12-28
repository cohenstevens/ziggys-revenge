import sys
import pygame
import random
import math
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("ninja go")
        self.screen = pygame.display.set_mode((640, 480)) # creates display window
        self.display = pygame.Surface((320, 240)) # render onto this. basically loads in a plain image at set size, which is half of display in this scenario

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8,15))

        self.tilemap = Tilemap(self, tile_size=16)
        self.load_level(0)


    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawner = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawner.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13)) # rect is x,y,width,height  

        # cant spawn enemies on grid or RuntimeError: dictionary changed size during iteration
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0: # variant 1 of spanwes is player
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8,15)))

        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0,0] # coordinates are top left of screen

    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0,0))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30 # without subtracting the character would be in the top left of the screen
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() / 2 - self.scroll[1]) / 30 # further player is faster scroll will move bc of /30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1])) # to help with character jidderness

            for rect in self.leaf_spawner:
                if random.random() * 49999 < rect.width * rect.height: # random.random() - random float between 0 and 1 # multiplying by 49999 makes sure it doesnt spawn leaves every frame if it wasnt multiplied it would spawn every frame
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height) # rect.x + random.random() * rect.width makes sure they spawn in rect
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))


            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0,0))
                enemy.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            #[[x, y], direction, timer]
            for projectile in self.projectiles.copy(): # have to copy if removing from list otherwise runtime error
                projectile[0][0] += projectile[1] # adding direction to projectile
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1])) # half of width centers it in respect to rendering
                if self.tilemap.solid_check(projectile[0]): # checking location of projectile
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(self.projectiles[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random())) # shoot sparks left only if projectile is going right
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50: # as long as you arent in the moving part of dash
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)


            for particle in self.particles.copy(): # doing copy bc were removing during iteration
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3 # creates a more natural patternbc of sin graph # multiply by 0.035 to decrease how fast it bobs left and right # multiply by 0.3 to decrease force # sin func gives number between -1 and 1
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump() 
                    if event.key == pygame.K_x:  #self.player.velocity[1] = -3 # adds a smooth jump cause velo is 'backwards'
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60) #  makes game run at 60 fps

Game().run()