import sys
import pygame
import random
import math
import os
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.FloatText import FloatingText


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Ziggy's Revenge")
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE) # creates display window
        self.display = pygame.Surface((320, 240) , pygame.SRCALPHA) # render onto this. basically loads in a plain image at set size, which is half of display in this scenario
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]
        self.font = pygame.font.SysFont("Arial", 16)
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_images('backgrounds'),
            'clouds': load_images('clouds'),
            'torii': load_images('tiles/torii_gates'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=6),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'bullet': load_image('projectiles/bullet.png'),
            'bone': load_image('projectiles/bone.png'),
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
            'throw': pygame.mixer.Sound('data/sfx/throw.wav')
        }

        self.sfx['ambience'].set_volume(0.3)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(.5)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8,15))
        self.floating_texts= []
        self.txtscore = self.font.render(str(self.player.score), True, (255,255,255))
        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 4
        self.load_level(self.level)

        self.screenshake = 0


    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        tree_type_numbers = [3, 4, 5, 8] # 8 bc jungle torii gate needs leaves falling from it

        self.leaf_spawner = []
        for number in tree_type_numbers:
            for tree in self.tilemap.extract([('large_decor', number)], keep=True):
                self.leaf_spawner.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13)) # rect is x,y,width,height  

        # cant spawn enemies on grid or RuntimeError: dictionary changed size during iteration
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0: # variant 1 of spanwes is player
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8,15)))

        self.projectiles = [] # enemy projectiles
        self.hero_projectiles =[] # ziggy projectiles
        self.particles = []
        self.sparks = []

        self.scroll = [0,0] # coordinates are top left of screen
        self.dead = 0
        self.transition = -30
        self.angle = 0
        self.random_background = random.randint(0, len(os.listdir('data/images/backgrounds'))-1) # cycles between different backgrounds in game

    def run(self):
        pygame.mixer.music.load('data/music.wav') # wav files seems to be better with executables
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1) # takes a number of loops, -1 loops forever

        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'][self.random_background], (0,0)) 

            # Render the Score and outline
            
            outline_color = (0, 0, 0)  # Black color for the outline
            main_color = (255, 255, 255)  # White color for the main text

            outline_positions = [
                (-1, -1), (0, -1), (1, -1),  # Top-left, Top, Top-right
                (-1, 0),          (1, 0),   # Left, Right
                (-1, 1), (0, 1), (1, 1)    # Bottom-left, Bottom, Bottom-right
            ]

            # Render the black outline
            for offset in outline_positions:
                outline_surface = self.font.render(f"{self.player.score:06}", True, outline_color)
                self.display_2.blit(outline_surface, (10 + offset[0], 5 + offset[1]))

            # Render the main text
            self.txtscore = self.font.render(f"{self.player.score:06}", True, main_color)
            self.display_2.blit(self.txtscore, (10, 5))
            self.display_2.blit(self.txtscore, (10, 5))  # Position it at the top-left corner of the display
            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1) # will prevent from crashing if go above amount of maps
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1


            if self.dead >= 2:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1) # want transition to go to highest number without level transition
                if self.dead > 40: # causes a 40 frame wait time till level restart
                    self.load_level(self.level)

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30 # without subtracting the character would be in the top left of the screen
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() / 2 - self.scroll[1]) / 30 # further player is faster scroll will move bc of /30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1])) # to help with character jidderness

            for rect in self.leaf_spawner:
                if random.random() * 49999 < rect.width * rect.height: # random.random() - random float between 0 and 1 # multiplying by 49999 makes sure it doesnt spawn leaves every frame if it wasnt multiplied it would spawn every frame
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height) # rect.x + random.random() * rect.width makes sure they spawn in rect
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))


            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            # Update floating texts
            for text in self.floating_texts[:]:
                if not text.update():  # If text has expired
                    self.floating_texts.remove(text)
                if not len(self.enemies):
                    self.floating_texts.remove(text) 

            # Render floating texts
            for text in self.floating_texts:
                text.render(self.display_2)
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0,0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
                    self.player.score+=100
                    #enemy_x, enemy_y = enemy.position  # Get enemy's position
                    self.floating_texts.append(FloatingText((self.player.pos[0] - self.scroll[0]) - 5, (self.player.pos[1] - self.scroll[1]) - 15, "+100")) #This no work it spawns up in the sky
                    #print(self.player.score)

            if self.dead <= 2:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            #[[x, y], direction, timer]
            for projectile in self.projectiles.copy(): # have to copy if removing from list otherwise runtime error
                projectile[0][0] += projectile[1] # adding direction to projectile
                projectile[2] += 1
                img = self.assets['bullet']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1])) # half of width centers it in respect to rendering
                if self.tilemap.solid_check(projectile[0]): # checking location of projectile
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random())) # shoot sparks left only if projectile is going right
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50: # as long as you arent in the moving part of dash
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
            
            self.angle += 2
            self.angle %= 360

            #[[x, y], direction, timer]
            # tells when the hero projectiles need to be removed from the screen
            for projectile in self.hero_projectiles.copy(): # have to copy if removing from list otherwise runtime error
                projectile[0][0] += projectile[1] # adding direction to projectile
                projectile[2] += 1
                img = self.assets['bone']
                img = pygame.transform.rotate(img, self.angle)
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1])) # half of width centers it in respect to rendering
                if self.tilemap.solid_check(projectile[0]): # checking location of projectile
                    self.hero_projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random())) # shoot sparks left only if projectile is going right
                elif projectile[2] > 360:
                    self.hero_projectiles.remove(projectile)

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_silhouette = display_mask.to_surface(setcolor=(0 ,0, 0, 180), unsetcolor=(0, 0, 0, 0)) # (red, green, blue, alpha(transparency)) 0 is fully transparent, 255 is max
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # render 4 times with an offset of 1 pixel # basically creates an outline
                self.display_2.blit(display_silhouette, offset)


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
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:  #self.player.velocity[1] = -3 # adds a smooth jump cause velo is 'backwards'
                        self.player.dash()
                    if event.key == pygame.K_SPACE:
                        self.player.throw()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size()) # creates black surface the size of display
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8) # x8 makes ure circle can expand to proper size
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            
            scaled_display = pygame.transform.scale(self.display, self.screen.get_size())
            self.screen.blit(scaled_display, (0, 0))  # Blit the scaled content to the screen
            pygame.display.update()
            self.clock.tick(60) #  makes game run at 60 fps

Game().run()

# for executable PyInstaller game.py --noconsole -- onefile
# game.py bc its main executable, noconsole so that the client doesnt see the console, and one file for 1 file
# windows flags things made with pyinstaller bc people make hacks with pyinstaller