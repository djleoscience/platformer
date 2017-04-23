"""
CITATIONS:

IMPORTS:
Title: Pygame
Author: Pygame
Date: 3/8/17
Code version: 1.9.2
Availability: http://www.pygame.org/download.shtml

Title: random — Generate pseudo-random numbers
Author: Python Software Foundation
Date: 3/8/17
Code version: 3.5.1
Availability: https://docs.python.org/3.0/library/random.html

Title: time — Time access and conversions
Author: Python Software Foundation
Date: 3/8/17
Code version: 3.5.1
Availability: https://docs.python.org/3.0/library/time.html

Title: os — Miscellaneous operating system interfaces
Author: Python Software Foundation
Date: 3/8/17
Code version: 3.5.1
Availability: https://docs.python.org/3.0/library/os.html


IMAGES:
Title: Platformer Graphics Deluxe
Author: www.kenney.nl
Date: 3/8/17
Availability: http://opengameart.org/content/platformer-art-deluxe
All images in game came from this package


SOUND:
Title: Happy Arcade Tune
Author: rezoner
Date: 3/8/17
Availability: http://opengameart.org/content/happy-arcade-tune

All other sound effects were generated randomly by http://www.bfxr.net/ or made by myself
"""

import pygame
import random
import time
from os import path

highscore = 0
#accessing the img folder
highScoreFile = path.join(path.dirname(__file__), 'highscore.txt')
f = open('highscore.txt', 'r')
highscore = int(f.read())
f.close()
imgDir = path.join(path.dirname(__file__), 'img')
sndDir = path.join(path.dirname(__file__), 'snd')

#setting game constants for window
WIDTH = 600
HEIGHT = 480
FPS = 60


#defining color constants for future use
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SKYBLUE = (102, 153, 255)


#initiating pygame stuff
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumpy Game!")
clock = pygame.time.Clock()


#global variables for speeding up ground/coins/spikes/clouds/how fast the guy is running
groundSpeed = 8
nowGroundTimer = 0

#Player sprite class
class Player(pygame.sprite.Sprite):
    #initialization method to create class variables
    def __init__(self):
        #initiating the Sprite superclass
        pygame.sprite.Sprite.__init__(self)
        #assigning the proper image to the sprite
        self.image = playerImages[0]
        self.rect = self.image.get_rect()
        #Animation variables to track the frame that it's on and control speed of animation
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 25-groundSpeed
        self.isJumping = False
        self.rect.bottomleft = (60, 420)

        #Physics variables for jumping
        self.yAcceleration = 1
        self.yVelocity = 0
        self.xVelocity = 0

    #update method that is called every frame, changes where sprite is
    def update(self):
        #changes how fast it's running based on the ground speed
        self.frame_rate = 25-groundSpeed
        if self.frame_rate < 4:
            self.frame_rate = 4


        #changes jumping and moving based on the keys pressed
        keystate = pygame.key.get_pressed()
        
        if keystate[pygame.K_SPACE] and not self.isJumping:
            jumpSound.play()
            self.isJumping = True
            self.yVelocity = -20
        if keystate[pygame.K_LEFT] and self.rect.left > 0:
            self.xVelocity = -5
        elif keystate[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.xVelocity = 5
        else:
            self.xVelocity = 0
            
        #changes position based on the velocity and acceleration constants

        self.rect.x += self.xVelocity
        if self.isJumping:
            self.rect.y += self.yVelocity
            self.yVelocity += self.yAcceleration
            
            if self.rect.bottom >= 422:
                self.rect.bottom = 422
                self.yVelocity = 0
                self.isJumping = False

        #changes frame based on how long it's been since last frame change
        now = pygame.time.get_ticks()

        if now-self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(playerImages):
                self.frame = 0
            center = self.rect.center
            self.image = playerImages[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = center

#Cloud sprite class for displaying clouds
class Cloud(pygame.sprite.Sprite):
    #initialization method to create class variables
    def __init__(self, fac):
        #initiating the Sprite superclass
        pygame.sprite.Sprite.__init__(self)

        #uses a factor to determine size and speed of cloud and create variation
        self.factor = fac
        self.xPos = random.randrange(0, WIDTH)

        #uses the size factor and the size of the ground to create parallax effect
        self.xSpeed = -1 * self.factor * groundSpeed / 16
        self.newStats()
        self.lastUpdate = pygame.time.get_ticks()
        self.frameRate = 30
        
    #update method that is called every frame, changes where sprite is
    def update(self):
        #changes position based on when the last change was
        now = pygame.time.get_ticks()
        if now-self.lastUpdate > self.frameRate:
            self.lastUpdate = now
            self.xPos += self.xSpeed
        if self.rect.right < 0:
            self.newStats()
            self.xPos = WIDTH + 1
        self.rect.x = self.xPos
        self.rect.y = self.yPos
        self.xSpeed = -1 * self.factor * groundSpeed / 16
        
    #creates new variable values for when a new cloud is made or when it exits the screen
    def newStats(self):
        self.image = random.choice(cloudImages)
        self.rect = self.image.get_rect()
        self.yPos = random.randrange(0, HEIGHT/3)
        self.image = pygame.transform.scale(self.image, (int(.5 * self.factor * 64), int(.5 * self.factor * 35)))


#Spike sprite class for displaying spikes
class Spike(pygame.sprite.Sprite):
    #initialization method to create class variables
    def __init__(self):
        #initiating the Sprite superclass
        pygame.sprite.Sprite.__init__(self)
        #accessing the image of the spikes
        self.image = spikeImage
        self.rect = self.image.get_rect()
        self.rect.bottom = 420
        self.rect.x = 1000 + WIDTH
        #ground speed influences the xSpeed
        self.xSpeed = -1 * groundSpeed

    #update method that is called every frame
    def update(self):
        #moves and resets spikes when they get off screen
        self.rect.x -= groundSpeed
        if self.rect.right < 0:
            self.rect.left = WIDTH + random.randrange(0, 1000)

#Coin sprite class for displaying coins
class Coin(pygame.sprite.Sprite):
    #initialization method to create class variables
    def __init__(self):
        #initializing sprite superclass
        pygame.sprite.Sprite.__init__(self)
        #setting coin image
        self.image = coinImage
        self.rect = self.image.get_rect()
        self.newCoin()

    #method to set movement 
    def update(self):
        self.rect.x -= groundSpeed
        if self.rect.right < 0:
            self.newCoin()
            
    #method to set the initial place of the coin
    def newCoin(self):
        self.rect.left = WIDTH + random.randrange(0, 1000)
        self.rect.y = random.randrange(200, 350)

#Gras sprite class for displaying grass tiles
class Grass(pygame.sprite.Sprite):
    #initialization method to create class variables
    def __init__(self, pos):
        #initializing sprite superclass
        pygame.sprite.Sprite.__init__(self)
        #set grass image and initial position on screen`
        self.image = grassTile
        self.rect = self.image.get_rect()
        self.rect.x = pos * 60
        self.rect.y = 420
        self.timer = pygame.time.get_ticks()

    def update(self):
        #uses global variable to determine where the rightmost variable
        global farthestGrassTile
        self.rect.x -= groundSpeed
        #resets if tile moves off the screen on the left
        if self.rect.x < -60:
            self.rect.x = farthestGrassTile.getX() + 30
            farthestGrassTile = self
    #method to publicly access the x coordinate of the grass tile
    def getX(self):
        return self.rect.x

#method to fill groups that are inputted with 2 different clouds of the size of the factor
def createCloudGroups(factor, group):
    for i in range(2):
        cloud = Cloud(factor)
        group.add(cloud)
        allSprites.add(cloud)
#method to easily draw text, parametter is if it's centered or not
fontName = pygame.font.match_font("Comic Sans MS")
def drawText(surface, text, size, color, x, y, center = False):
    font = pygame.font.Font(fontName, size)
    textSurface = font.render(text, True, color)
    textRect = textSurface.get_rect()
    if center:
        textRect.center = (x, y)
    else:
        textRect.topleft = (x, y)
    surface.blit(textSurface, textRect)

#method to increment the ground speed every 5 seconds
def updateGroundSpeed(boop):
    global nowGroundTimer
    global groundSpeed
    if boop - nowGroundTimer > 5000:
        nowGroundTimer = boop
        groundSpeed += 1


    
#access images for all sprites and objects
background = pygame.image.load(path.join(imgDir, 'bg.png')).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background.get_rect()

grassTile = pygame.image.load(path.join(imgDir, 'grassMid.png')).convert()
grassTile = pygame.transform.scale(grassTile, (60, 60))
grassTile.set_colorkey(BLACK)
grassTileRect = grassTile.get_rect()

spikeImage = pygame.image.load(path.join(imgDir, 'spikes.png')).convert()
spikeImage.set_colorkey(BLACK)

coinImage = pygame.image.load(path.join(imgDir, "coinGold.png")).convert()
coinImage.set_colorkey(BLACK)


playerImages = []

for i in range(1, 10):
    filename = 'p1_walk0{}.png'.format(i)
    img = pygame.image.load(path.join(imgDir, filename)).convert()
    img.set_colorkey(BLACK)
    playerImages.append(img)

for i in range(10, 12):
    filename = 'p1_walk{}.png'.format(i)
    img = pygame.image.load(path.join(imgDir, filename)).convert()
    img.set_colorkey(BLACK)
    playerImages.append(img)


cloudImages = []
for i in range(1, 4):
    filename = 'cloud{}.png'.format(i)
    img = pygame.image.load(path.join(imgDir, filename)).convert()
    img.set_colorkey(BLACK)
    cloudImages.append(img)






#accessing all of the sounds
jumpSound = pygame.mixer.Sound(path.join(sndDir, 'Jump.wav'))
coinSound = pygame.mixer.Sound(path.join(sndDir, 'Coin.wav'))
screamSound = pygame.mixer.Sound(path.join(sndDir, 'scream.wav'))
pygame.mixer.music.load(path.join(sndDir, 'happy.wav'))



#boolean variables for game loop
running = True
playSound = False
gameLoop = True

#introduction slides
screen.fill(SKYBLUE)
drawText(screen, "Welcome to the game!", 42, BLACK, WIDTH/2, HEIGHT/2, True)
pygame.display.flip()
screen.fill(SKYBLUE)
drawText(screen, "Use arrow keys to move", 42, BLACK, WIDTH/2, HEIGHT/2, True)
drawText(screen, "and space to jump", 42, BLACK, WIDTH/2, HEIGHT/2 + 60, True)
time.sleep(3)
pygame.display.flip()
screen.fill(SKYBLUE)
drawText(screen, "Ready", 42, BLACK, WIDTH/2, HEIGHT/2, True)
time.sleep(3)
pygame.display.flip()
screen.fill(SKYBLUE)
drawText(screen, "Set", 42, BLACK, WIDTH/2, HEIGHT/2, True)
time.sleep(1)
pygame.display.flip()
screen.fill(SKYBLUE)
drawText(screen, "GO!", 60, BLACK, WIDTH/2, HEIGHT/2, True)
time.sleep(1)
pygame.display.flip()
time.sleep(1)
pygame.display.flip()

#beginning of game loop, starts over from here when you die and restart
while gameLoop:
    groundSpeed = 8
    nowGroundTimer = pygame.time.get_ticks()
    score = 0

    pygame.mixer.music.play(loops = -1)


    #creating sprites and initiating sprite objects
    allSprites = pygame.sprite.Group()

    playerSprites = pygame.sprite.Group()
    player = Player()
    playerSprites.add(player)
    allSprites.add(player)

    spikeGroup = pygame.sprite.Group()
    spike = Spike()
    spikeGroup.add(spike)
    allSprites.add(spike)

    tinyClouds = pygame.sprite.Group()
    createCloudGroups(1, tinyClouds)

    smallClouds = pygame.sprite.Group()
    createCloudGroups(2, smallClouds)

    mediumClouds = pygame.sprite.Group()
    createCloudGroups(3, mediumClouds)

    bigClouds = pygame.sprite.Group()
    createCloudGroups(4, bigClouds)

    coinGroup = pygame.sprite.Group()

    grassGroup = pygame.sprite.Group()
    #create 24 grass tiles instead of 12 to be completely able to cover the screen when the speed picks up
    for x in range(24):
        grass = Grass(x)
        grassGroup.add(grass)
        if x == 23:
            farthestGrassTile = grass
        
    for i in range(4):
        coin = Coin()
        coinGroup.add(coin)
        allSprites.add(coin)



    #loop during actual gameplay, loops 30 times per second
    while running:
        
        clock.tick(FPS)

        #if the user closes out, this actually quits the application
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                gameLoop = False

                
        #update all of the sprite groups
        playerSprites.update()
        tinyClouds.update()
        smallClouds.update()
        mediumClouds.update()
        bigClouds.update()
        spikeGroup.update()
        coinGroup.update()
        grassGroup.update()
        updateGroundSpeed(pygame.time.get_ticks())

        
        #if the player sprite collides with a spike, it exits the loop
        hits = pygame.sprite.groupcollide(playerSprites, spikeGroup, True, False)
        if hits:
            running = False

        #if the player collides with a coin, it kills the coin, creates a new coin, and adds to your score
        hits = pygame.sprite.groupcollide(coinGroup, playerSprites, True, False)
        for hit in hits:
            score += 1
            coinSound.play()
            coin = Coin()
            coinGroup.add(coin)
            
            

        #fill up the screen, draw all of the updated sprites and the score
        screen.fill(SKYBLUE)
        tinyClouds.draw(screen)
        smallClouds.draw(screen)
        mediumClouds.draw(screen)
        bigClouds.draw(screen)
        coinGroup.draw(screen)
        playerSprites.draw(screen)
        spikeGroup.draw(screen)
        grassGroup.draw(screen)

        scoreText = "Score: " + str(score)
        drawText(screen, scoreText, 18, BLACK, 10, 10)
        
        #displays the drawn updated sprites on the screen
        pygame.display.flip()

    #once the loop is exited, all sprites are removed
    for sprite in allSprites:
        sprite.kill()
    #determine if the player achieved the high score
    highestScore = False
    if score > highscore:
        #if the player did get the high score, it's written in the high score file
        highestScore = True
        highscore = score
        f = open('highscore.txt', 'w')
        f.write(str(highscore))
        f.close()
    #drawing and displaying game over screen
    screen.fill(BLACK)
    drawText(screen, "YOU DIED", 42, RED, WIDTH/2, HEIGHT/2, True)
    if highestScore:
        drawText(screen, "NEW HIGH SCORE!", 36, RED, WIDTH/2, HEIGHT/2 + 70, True)
    drawText(screen, "High Score: " + str(highscore), 18, WHITE, 10, 10)
    drawText(screen, "Your Score: " + str(score), 18, WHITE, 10, 30)
    pygame.display.flip()
    pygame.mixer.music.pause()

    screamSound.play()
    time.sleep(3)

    #drawing and displaying retry screen
    screen.fill(BLACK)
    drawText(screen, "Press enter to play again.", 24, WHITE, WIDTH/2, HEIGHT/2, True)
    pygame.display.flip()
    enterNotPressed = True
    #event tracker to determine if the enter button is pressed or the player closed out
    while enterNotPressed:
        keystate = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    enterNotPressed = False
                    running = True
            if event.type == pygame.QUIT:
                gameLoop = False
                enterNotPressed = False
        


#quit pygame once main loop has ended, terminates the program
pygame.quit()
f.close()
