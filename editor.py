import sys
import pygame
from scripts.utils import load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0

class Editor:
    def __init__(self, choice):
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE) # creates display window
        self.display = pygame.Surface((320, 240)) # render onto this. basically loads in a plain image at set size, which is half of display in this scenario

        self.clock = pygame.time.Clock()

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
            'torii': load_images('tiles/torii_gates'),
        }

        
        self.movement = [False, False, False, False] # want 4 movements for the camera

        self.tilemap = Tilemap(self, tile_size=16)

        try:
            choice += '.json'
            self.tilemap.load('data/maps/' + choice)
        except FileNotFoundError:
            print("Map Not Found")

        self.scroll = [0,0] # coordinates are top left of screen

        self.tile_list = list(self.assets) # when you run list on dictionaries if gives you the keys
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

        self.font = pygame.font.SysFont("Arial", 10)

        
    def draw_text(self, text, x, y):
        controls = self.font.render(text, True, (255,255,255))
        self.display.blit(controls, (x,y)) 

    def run(self):
        while True:
            self.display.fill((0,0,0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2 # self.movement[1] right, 0 is left, 3 is down, 2 is up
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100) # sets image transparency, 0 is full transparent, 255 is max

            mpos = pygame.mouse.get_pos() # gets pixels coordinates cooresponding to the window size
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE) # makes sure you get correct mouse position by how much you render the display up
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size)) #  // self.tilemap.tile_size makes sure its alligned on the grid

            if self.ongrid:
                # multiply my tilemap.tile_size to get pixels and - self.scroll[i] to get camera location
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1]* self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos): # is this tile colliding w/ mouse
                        self.tilemap.offgrid_tiles.remove(tile) # removes offgrid tiles



            self.display.blit(current_tile_img, (5,5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])}) # display space to world space
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:  # Scroll up
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:  # Scroll down
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0  # Reset to first variant when changing tile group
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0  # Reset to first variant when changing tile group


                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid # if you set a bool to not of itself it just flips it
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save(choice + '.json')
                        #print(f"saving map {choice}")
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_r:
                        #self.rotate
                        pass
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            scaled_display = pygame.transform.scale(self.display, self.screen.get_size())
            self.screen.blit(scaled_display, (0, 0))  # Blit the scaled content to the screen
            pygame.display.update()


            self.clock.tick(60) #  makes game run at 60 fps
print('What map would you like to edit?')
choice = input()

Editor(choice).run()