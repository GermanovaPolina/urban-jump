import pygame
import os
import sys
import random


pygame.init()
pygame.mixer.music.load(os.path.join('data', 'music.mp3'))
pygame.mixer.music.play(-1)
size = width, height = 800, 550
screen = pygame.display.set_mode(size)
screen.fill((255, 255, 255))

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

FPS = 50

def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["URBAN JUMP", "",
                  "Избегайте труб, используя пробел для прыжка",
                  "Escape - меню", "Пузырики - защитный барьер",
                  "Часы - замедляют время"]

    fon = pygame.transform.scale(load_image('background.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 40)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, (0, 0, 0))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    button = pygame.transform.scale(load_image('start.jpg'), (180, 80))
    screen.blit(button, (310, 400))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 310 <= pygame.mouse.get_pos()[0] <= 490 and 400 <= pygame.mouse.get_pos()[1] <= 480:
                    return
        pygame.display.flip()
        clock.tick(FPS)

clock = pygame.time.Clock()
start_screen()


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(border_group, all_sprites)
        self.add(border_group)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Point(pygame.sprite.Sprite):
    def __init__(self, x_pos):
        super().__init__(point_group, all_sprites)
        self.add(point_group)
        self.image = pygame.Surface((1, height), pygame.SRCALPHA)
        self.rect = pygame.Rect(x_pos, 0, 1, height)

    def update(self):
        if self.rect.x <= 0:
            self.kill()
            return
        if pygame.sprite.spritecollideany(self, player_group):
            global points
            if points[1] is not self:
                points[0] += 1
                points[1] = self
        self.rect = self.rect.move(-pspeed, 0)
             

class Pipe(pygame.sprite.Sprite):
    image = load_image('pipe1.png')
    gap = 150
    def __init__(self, pos_x, first=True, pheight=None):
        super().__init__(pipe_group, all_sprites)
        if pheight is None:
            pheight = random.randint(0, height - Pipe.gap)
        self.image = pygame.transform.scale(Pipe.image, (70, pheight))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        if first:
            self.rect = self.rect.move(pos_x, height - pheight)
            Pipe(pos_x, False, height - pheight - Pipe.gap)
            Point(pos_x + 35)
        else:
            self.rect = self.rect.move(pos_x, 0)
    
    def update(self):
        if self.rect.x <= -70:
            self.kill()
            return
        self.rect = self.rect.move(-pspeed, 0)


class Player(pygame.sprite.Sprite):
    image = load_image('character.png')
    gravity = 3
    def __init__(self):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.flip(pygame.transform.scale(Player.image, (60, 60)), True, False)
        self.rect = self.image.get_rect().move(10, 175)
        self.mask = pygame.mask.from_surface(self.image)
        self.v = 10
        self.shield = [False, None]
    
    def update(self):
        global failed, shield_flag, pspeed
        if pygame.sprite.spritecollideany(self, shield_group):
            pygame.sprite.spritecollideany(self, shield_group).active = True
            self.shield[0] = True
        if pygame.sprite.spritecollideany(self, border_group):
            failed = True
            return
        elif pygame.sprite.spritecollideany(self, slow_group):
            pygame.sprite.spritecollideany(self, slow_group).kill()
            pspeed -= 5
        elif pygame.sprite.spritecollideany(self, pipe_group):
            if self.shield[0]:
                for sh in shield_group.sprites():
                    if sh.active:
                        sh.kill()
                        shield_flag = False
                        break
                self.shield[0] = False
                self.shield[1] = pygame.sprite.spritecollideany(self, pipe_group)
            if pygame.sprite.spritecollideany(self, pipe_group) == self.shield[1]:
                pass
            else:
                failed = True
                return
        self.rect = self.rect.move(0,  self.v)
        self.v += Player.gravity

screen_rect = (0, 0, width, height)
 
class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))
 
    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 3
 
    def update(self):
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()
 
class Shield(pygame.sprite.Sprite):
    image = load_image('shield.png')
    
    def __init__(self, x, y):
        super().__init__(shield_group, all_sprites)
        self.image = pygame.transform.scale(Shield.image, (60, 60))
        self.rect = self.image.get_rect().move(x, y)
        self.active = False
        
    def update(self):
        if self.rect.x <= -50:
            self.kill()
            return
        if not self.active:
            self.rect = self.rect.move(-pspeed, 0)
        else:
            self.image = pygame.transform.scale(Shield.image, (100, 100))
            self.rect = player.rect.move(-20, -20)
            

class Slow(pygame.sprite.Sprite):
    image = load_image('clock.png')
    
    def __init__(self, x, y):
        super().__init__(slow_group, all_sprites)
        self.image = pygame.transform.scale(Slow.image, (60, 60))
        self.rect = self.image.get_rect().move(x, y)
        
    def update(self):
        if self.rect.x <= -60:
            self.kill()
            return
        self.rect = self.rect.move(-pspeed, 0)

            
def create_particles(position):
    particle_count = 7
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))

def menu():
    global ponts
    fon = pygame.transform.scale(load_image('menu.jpg'), (600, 350))
    screen.blit(fon, (100, 70))
    name = os.path.join('data', 'results.txt')
    paused = True
    maxp = int(open(name, 'r').read())
    if points[0] > maxp:
        maxp = points[0]
        file = open(name, 'w')
        file.write(str(maxp))
        file.close()
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 266 <= event.pos[0] <= 507:
                    if 195 <= event.pos[1] <= 262:
                        if not failed:
                            return
                        else:
                            start_game()
                    if 281 <= event.pos[1] <= 347:
                        start_game()
        font = pygame.font.Font(None, 40)
        string_rendered = font.render(str(maxp), 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 420
        intro_rect.y = 120
        screen.blit(string_rendered, intro_rect)          
        pygame.display.flip()

def start_game():
    global player, pspeed, all_sprites, pipe_group, border_group, player_group, failed, points, point_group, shield_group, shield_flag, slow_group
    clock = pygame.time.Clock()
    points = [0, 0]
    all_sprites = pygame.sprite.Group()
    pipe_group = pygame.sprite.Group()
    point_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    border_group = pygame.sprite.Group()
    shield_group = pygame.sprite.Group()   
    slow_group = pygame.sprite.Group()
    running = True
    count = 1
    count_t = 1
    shield_flag = False
    shield_pops = random.randint(4, 7)
    time_pops = random.randint(5, 8)
    fon = pygame.transform.scale(load_image('background.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    Pipe(250)
    FPS = 30
    player = Player()
    Border(0, 0, width, 0)
    Border(0, height, width, height)
    tapped = False
    pspeed = 5
    failed = False
    MYEVENTTYPE = 30
    pygame.time.set_timer(MYEVENTTYPE, 1000)
    
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == 32:
                create_particles((player.rect.center))
                tapped = True
                player.v = -15
            if event.type == MYEVENTTYPE and not failed:
                pspeed += 1
                if width - (pipe_group.sprites()[-1].rect.x + 70) >= 250:
                    Pipe(width)
                    if not shield_flag:
                        count += 1
                        if count == shield_pops:
                            count = 0
                            shield_pops = random.randint(4, 7)
                            Shield(width - 200, random.randint(240, 310))
                            shield_flag = True
                    count_t += 1
                    if count_t == time_pops:
                        count_t = 0
                        time_pops = random.randint(5, 8)
                        Slow(width - 270, random.randint(240, 310))                        
            if event.type == pygame.KEYDOWN and event.key == 27:
                menu()
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 70)
        string_rendered = font.render(str(points[0]), 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 400
        intro_rect.y = 20
        screen.blit(string_rendered, intro_rect)
        if tapped and not failed:
            all_sprites.update()
        elif failed:
            menu()
        all_sprites.draw(screen)
        pygame.display.flip()

start_game()
pygame.quit()