import pygame
import random

# Import pygame locals
from pygame.locals import (
	K_q,
	K_r,
	K_UP,
	K_DOWN,
	K_LEFT,
	K_RIGHT,
	K_ESCAPE,
	KEYDOWN,
	KEYUP,
	QUIT,
)

# Define a player object by extending pygame.sprite.Sprite
# the surface drwn on the screen is an attribute of player
class Player(pygame.sprite.Sprite):
	def __init__(self):
		super(Player, self).__init__()
		self.surf = pygame.Surface((75, 40))
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect(center = (100, SCREEN_HEIGHT/2))

	# Move the sprite based on user input
	def update(self, pressed_keys):
		if pressed_keys[K_UP]:
			self.rect.move_ip(0, -5)
		if pressed_keys[K_DOWN]:
			self.rect.move_ip(0, 5)
		if pressed_keys[K_LEFT]:
			self.rect.move_ip(-5, 0)
		if pressed_keys[K_RIGHT]:
			self.rect.move_ip(5, 0)

		# Keep player on the screen
		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > SCREEN_WIDTH:
			self.rect.right = SCREEN_WIDTH
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT

# Define the enemy object by extending Sprite
# The surface drawn is an attribute of enemy 
class Enemy(pygame.sprite.Sprite):
	def __init__(self):
		super(Enemy, self).__init__()
		self.surf = pygame.Surface((20,10))
		self.surf.fill((255, 255, 255))
		self.rect = self.surf.get_rect(
			center = (
				random.randint(SCREEN_WIDTH +20, SCREEN_WIDTH + 100),
				random.randint(0, SCREEN_HEIGHT),
			)
		)
		self.speed = random.randint(3, 7)

	# Move the sprite based on speed
	# Remove the sprite when the reaches the end of the screen
	def update(self):
		self.rect.move_ip(-self.speed, 0)
		if self.rect.right < 0:
			self.kill()

class Score_Count():
	def __init__(self, text = ""):
		self.surf = pygame.Surface((100, 60))
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect(center = (SCREEN_WIDTH - 50, 0))
		self.text = text

	def draw_score(self):
		font = pygame.font.SysFont('comicsans', 30)
		text = font.render(self.text, 1, (255, 255, 255))
		screen.blit(text, (650 + (100/2 - text.get_width()/2), 0 + (60/2 - text.get_height()/2)))


# Initialize pygame
pygame.mixer.init()
pygame.init()

# Load sound effects
# Source: https://opengameart.org/content/100-plus-game-sound-effects-wavoggm4a
# Credit: https://opengameart.org/users/damaged-panda
level_up_sound = pygame.mixer.Sound("game_fx/levelup.ogg")
explosion_sound = pygame.mixer.Sound("game_fx/explosion.ogg")
points_sound = pygame.mixer.Sound("game_fx/points.ogg")

# 'GAME OVER' font
font_one = pygame.font.Font(None, 100)
font_two = pygame.font.Font(None, 50)

# Create screen object
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create groups to hold enemy sprites and all sprites
# - enemies used for colision detection and position upadtes
# - all sprites_sprites is used for rendering
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Initiate score count
score_count = Score_Count()

# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1

# Start here with every new game
running = True
while running:

	# Set enemy speed
	ENEMY_LOW_SPEED = 2
	ENEMY_HIGH_SPEED = 4
	ADDENEMY_SPEED = 500

	# Set speed for enemy spawn rate
	pygame.time.set_timer(ADDENEMY, ADDENEMY_SPEED)

	# Instantiate player
	player = Player()
	all_sprites.add(player)

	# Set start values for variables
	score = 0
	checkpoint = 0
	bg = (0, 0, 0)
	game_over = False

	### GAME LOOP START ###
	loop = True
	while loop:
		screen.fill(bg)
		score_count.text = ("Score: " + str(score))
		score_count.draw_score()

		### EVENTS LOOP START ####

		for event in pygame.event.get():

			if event.type == KEYDOWN:

				if event.key == K_ESCAPE:
					loop = False
					running = False

				if game_over:

					if event.key == K_q:
						loop = False
						running = False
					elif event.key == K_r:
						loop = False

			elif event.type == QUIT:
				loop = False
				running = False

			if event.type == ADDENEMY and not game_over:

				points_sound.play()
				#If high score rapidly change colour
				if score > 2500:
					bg = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
				score = score + 10

				# Create new enemy and add it to sprite groups
				new_enemy = Enemy()
				new_enemy.speed = random.randint(ENEMY_LOW_SPEED, ENEMY_HIGH_SPEED)
				enemies.add(new_enemy)
				all_sprites.add(new_enemy)

		### EVENTS LOOP END ###

		if not game_over:

			# If checkpoint has been reached
			if score == (checkpoint + 500):
				# Play level up sound
				if score < 3000:
					level_up_sound.play()

				# Change background color
				bg = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

				# Increase enemy speed
				if ENEMY_LOW_SPEED < 7:
					ENEMY_LOW_SPEED = ENEMY_LOW_SPEED + 1
				if ENEMY_HIGH_SPEED < 9:
					ENEMY_HIGH_SPEED = ENEMY_HIGH_SPEED + 2

				# Increase enemy spawn rate
				if ADDENEMY_SPEED > 100:
					ADDENEMY_SPEED = ADDENEMY_SPEED - 75
					pygame.time.set_timer(ADDENEMY, ADDENEMY_SPEED)

				# Advance checkpoint	
				checkpoint = checkpoint + 500

			# Get the set of pressed keys
			pressed_keys = pygame.key.get_pressed()

			# Update players position based on keys pressed
			player.update(pressed_keys)

			# Update enemy positions
			for enemy in enemies:
				enemy.update()

			# Check if any enemies have collided with the player
			if pygame.sprite.spritecollideany(player, enemies):
				# If so kill the player and end game
				explosion_sound.play()
				game_over = True

		if game_over:
			# If game over is true, draw game over
			text_one = font_one.render("GAME OVER", True, (255,255,255))
			text_one_rect = text_one.get_rect()
			text_x = screen.get_width() / 2 - text_one_rect.width / 2
			text_one_y = screen.get_height() / 2 - text_one_rect.height / 2
			screen.blit(text_one, [text_x, text_one_y])

			text_two = font_two.render("R to play again, Q to quit", True, (255,255,255))
			text_two_rect = text_two.get_rect()
			text_two_y = text_one_y +75
			screen.blit(text_two, ([text_x, text_two_y]))

		#  Draw for all sprites
		for entity in all_sprites:
			screen.blit(entity.surf, entity.rect)
		
		# Update the display
		pygame.display.flip()
		pygame.display.update()

	### GAME LOOP END ###

	# Remove everything on the screen
	player.kill()
	for enemy in enemies:
		enemy.kill()

pygame.mixer.music.stop()
pygame.mixer.quit()
pygame.quit()

print('score -', score)
print('enemy high speed -', ENEMY_HIGH_SPEED)
print('enemy spawn rate -', ADDENEMY_SPEED)