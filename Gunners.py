# Imported, necessary for the entire game. 
import pygame
# imported to load sounds
from pygame import mixer
import random
# Imported to access pygame.display, key, time, and event().
from pygame.locals import *
# Imported to read files and used to load animations
import os

pygame.init()
pygame.mixer.init()

global game_over
game_over=0 #-1 lose, 0 ongoing, 1 win
global pressed
pressed=False
global score
score=0

# Game Variables
fps = 60
clock = pygame.time.Clock()

# Color variables
white = (255, 255, 255)

# Screen
screen_width = 1080
screen_height = 600
#panel = 150
screen = pygame.display.set_mode((screen_width, screen_height))

# Sound effects
alien_struck_fx = pygame.mixer.Sound(r".\music\mixkit-small-hit-in-a-game-2072.wav")
alien_struck_fx.set_volume(0.5)

shoot_fx = pygame.mixer.Sound(".\music\mixkit-short-laser-gun-shot-1670.wav")
shoot_fx.set_volume(0.5)

# Font and font sizes
pixelfont = pygame.font.Font("arcadeclassic\ARCADECLASSIC.TTF", 96)
smallfont = pygame.font.Font("arcadeclassic\ARCADECLASSIC.TTF", 48)

# Load images
bg = pygame.image.load("./background/fullbg.png")
#panel = pygame.image.load("./background/panel.png")
bg = pygame.transform.scale(bg, (screen_width, screen_height))
#panel = pygame.transform.scale(panel, (screen_width, 150))

parent = os.getcwd()

# Gunner class for our animation
# Classes should be characteristics and interactions (movmeent, animation, frames, hp, etc). 
class Gunner(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        self.frame_index = 0 
        self.action = 2

        # Jump variables
        self.speed = 16
        self.isJump = False
        self.vel_y = 10

        # Loading in the animations
        templist = []
        os.chdir(f"{parent}\Gunner")
        for folders in os.listdir():
            for images in os.listdir(folders):
                img = pygame.image.load(f"./{folders}/{images}")
                img = pygame.transform.scale(img, (img.get_width()*3, img.get_height()*3))
                templist.append(img)
            self.animation_list.append(templist)
            templist = []
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=[x,y])

    def update(self):
        global pressed
        global game_over
        global score
        animation_cooldown=100

        keys = pygame.key.get_pressed()
        # Since we're frequently changing through animations, some animations may have more frames than others. Thus, when we switch, we'll run into an error. 
        # Instead of closing the game and sending the error, the frame index will be set to 0. 
        try: self.image = self.animation_list[self.action][self.frame_index]
        except: self.image = self.animation_list[self.action][0]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index+=1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.idle()

        if self.isJump is False and keys[K_SPACE]:
            self.isJump=True

        if self.isJump is True:
            self.action=3
            self.rect.centery-=self.vel_y*4
            self.vel_y-=0.5
            if self.vel_y < -10:
                self.isJump=False
                self.vel_y = 10

        if keys[K_d]:
            self.right_run()
        
        elif keys[K_a]:
            self.left_run()
        
        if pressed:
            bullet = Bullets(self.rect.centerx+5, self.rect.centery-9)
            bullet_group.add(bullet)
            pressed=False
            shoot_fx.play()

        # If the character is out of the screen from the left, it's an automatic lost. 
        # if self.rect.centerx < 0:
        #     self.kill()
        #     game_over=-1
        
        # If the character collides with an Alien jelly, the game is lost. 
        if pygame.sprite.spritecollide(self, alien_group, False, pygame.sprite.collide_mask):
            self.kill()
            game_over=-1

    def idle(self):
        self.action=2
        self.frame_index=0

    def right_run(self):
        if self.rect.right < screen_width:
            self.action=4
            self.rect.x+=self.speed
    
    def left_run(self):
        if self.rect.left > -120:
            self.action=4
            self.rect.x-=self.speed

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        os.chdir(f"{parent}/assets")
        self.image = pygame.image.load(f".\SpongeBullet.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*7, self.image.get_height()*7))
        self.rect = self.image.get_rect(center=[x,y])

    def update(self):  
        global score
        # Bullet speed
        self.rect.x+=60
        # If the bullets collide with an alien, kill the alien (third parameter is set to True for that) and kill the bullet. Add 1 to the score.
        if pygame.sprite.spritecollide(self, alien_group, True):
            alien_struck_fx.play()
            score+=1
            self.kill()
        # Once the bullet exits the view of the screen, kill the bullet. 
        if self.rect.right > screen_width:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        self.frame_index=0
        os.chdir(f"{parent}/aliens")
        for image in os.listdir():
            img = pygame.image.load(f"./{image}").convert_alpha()
            img = pygame.transform.scale(img, (img.get_width()*5, img.get_height()*5))
            self.animation_list.append(img)
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect(center=[x,y])
        self.update_time = pygame.time.get_ticks()

    def update(self):
        animation_cooldown = 100
        try: self.image = self.animation_list[self.frame_index]
        except: self.image = self.animation_list[0]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index+=1

        if self.frame_index >= len(self.animation_list):
            self.frame_index=0
        
        # The jelly slowly moves across the screen from right to left. 
        self.rect.x-=5
        # If the jelly is out of the screen from the left, kill the jelly. 
        if self.rect.centerx < 0:
            self.kill()

# Sprite Groups
# The sprite groups have their own draw functions, therefore we do not need to make any draw functions for the classes move. 
gunner_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()

# Create and add player to the gunner sprite group
player = Gunner(240, 560)
gunner_group.add(player)

# Function to draw the moving background and score on the top middle of the screen. 
i=0
def bg_draw(x):
    screen.blit(bg, (x,0))
    #screen.blit(panel, (0,600))
    score_render = pixelfont.render(str(score), False, white)
    score_rect = score_render.get_rect(center=(screen_width/2, screen_height//10))
    screen.blit(score_render, score_rect)

# Other game variables
start=False
run=True
# Alien spawn rate (1200milliseconds -> 1.2 seconds)
spawn_cooldown=1200
# Alien last spawn time
last_spawn = pygame.time.get_ticks()

while run:
    clock.tick(fps)
    
    bg_draw(i)
    # Make the character visible on screen before start to avoid any complications. 
    gunner_group.draw(screen)

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            pressed=True
        if keys[K_SPACE] and (game_over!=-1 or game_over!=1):
            start=True
        # If the game has ended (the player has lost) then if they press enter, reset all game variables and restart. 
        if keys[K_RETURN] and game_over==-1:
            # Re-add player to the gunner sprite group
            i=0
            # Respawn the character since it was killed and add it back to its group (for the draw function). 
            player = Gunner(240, 560)
            gunner_group.add(player)
            # Game is now "ongoing"
            game_over=0
            # Reset the score
            score=0
            # Empty the sprite groups to avoid Aliens from spawning on the exact spots before the game restarted. 
            alien_group.empty()
            bullet_group.empty()

    # If the game hasn't started yet and the scores are still 0, pause the game and allow the user to pick the time to start by hitting ENTER.
    if start==False and score==0 and game_over!=-1:
        # Simple text in the top middle of the screen to indicate which key to press to start.
        start_text = smallfont.render("Hit   SPACE   to   start", False, white)
        start_rect = start_text.get_rect(center=(screen_width/2, screen_height/2-125))
        screen.blit(start_text, start_rect)

    # Game started
    if start and game_over==0:
        # Draw background
        screen.fill((0,0,0))
        bg_draw(i)
        bg_draw(screen_width+i)
        if i==-screen_width:
            bg_draw(screen_width+i)
            i=0
        i-=10 
        player.rect.centerx-=6

        # Spawn the Aliens on the right of the screen after x time (cooldown).
        if pygame.time.get_ticks() - last_spawn > spawn_cooldown:
            # Randomly spawn the Jelly from any vertical position from the right side of the screen.
            alien = Alien(screen_width, random.randint(50, screen_height-50))
            # Add the Jelly to its group for sprite collision, draw, etc. 
            alien_group.add(alien)
            # Update the last spawn cooldown.
            last_spawn = pygame.time.get_ticks()

        # Draw sprites
        gunner_group.draw(screen)
        bullet_group.draw(screen)
        alien_group.draw(screen)

        # Update sprites
        gunner_group.update()
        bullet_group.update()
        alien_group.update()

    # If the character died to an Alien, stop the game and display the loss and restart messages.
    if game_over==-1:
        start=False
        end_text = pixelfont.render("You   lost!", False, white)
        end_rect = end_text.get_rect(center=(screen_width/2+25, screen_height/2-75))
        screen.blit(end_text, end_rect)
        restart = smallfont.render("Hit   ENTER   to   restart", False, white)
        restart_rect = end_text.get_rect(center=(screen_width/2, screen_height/2-125))
        screen.blit(restart, restart_rect)

    # Update the display.
    pygame.display.update()

pygame.mixer.quit()
# Exit pygame
pygame.quit()