import os
import pygame
import time
import random

# pygame font initializer
pygame.font.init()
# pygame mixer/sound initializer
pygame.mixer.init()
# pygame window dimensions
WIDTH = 500
HEIGHT = 800

# resources put into constants
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("resources", "bird1.png"))),
			pygame.transform.scale2x(pygame.image.load(os.path.join("resources", "bird2.png"))),
			pygame.transform.scale2x(pygame.image.load(os.path.join("resources", "bird3.png")))
		]
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("resources", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("resources", "base.png")))
BG = pygame.transform.scale2x(pygame.image.load(os.path.join("resources", "bg.png")))

SCORE_FONT = pygame.font.SysFont("helvetica", 50)

# class for the actual bird
class Bird:
	IMAGES = BIRD_IMAGES
	MAX_ROTATION = 20
	ROTATION_VELOCITY = 20
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.velocity = 0
		self.height = self.y
		self.image_count = 0
		self.image = self.IMAGES[0]

	def jump(self):
		self.velocity = -10.5
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1

		disp = self.velocity * self.tick_count + 1.5 * self.tick_count**2

		if disp >= 16:
			disp = 16

		if disp < 0:
			disp -= 2

		self.y = self.y + disp 

		if disp < 0 or self.y < self.height + 50: 
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt > -90:
				self.tilt -= self.ROTATION_VELOCITY

	def draw(self, window):
		self.image_count += 1

		if self.image_count < self.ANIMATION_TIME:
			self.image = self.IMAGES[0]
		elif self.image_count < self.ANIMATION_TIME * 2:
			self.image = self.IMAGES[1]
		elif self.image_count < self.ANIMATION_TIME * 3:
			self.image = self.IMAGES[2]
		elif self.image_count < self.ANIMATION_TIME * 4:
			self.image = self.IMAGES[1]
		elif self.image_count == self.ANIMATION_TIME * 4 + 1:
			self.image = self.IMAGES[0]
			self.image_count = 0

		if self.tilt <= -80:
			self.image = self.IMAGES[1]
			self.image_count = self.ANIMATION_TIME * 2

		rotated_image = pygame.transform.rotate(self.image, self.tilt)
		new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft = (self.x, self.y)).center)
		window.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.image)

class Pipe:
	GAP = 250
	VELOCITY = 5

	def __init__(self, x):
		self.x = x
		self.height = 0
		self.gap = 100

		self.top = 0
		self.bot = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
		self.PIPE_BOT = PIPE_IMAGE

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bot = self.height + self.GAP

	def move(self):
		self.x -= self.VELOCITY

	def draw(self, window):
		window.blit(self.PIPE_TOP, (self.x, self.top))
		window.blit(self.PIPE_BOT, (self.x, self.bot))

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bot_mask = pygame.mask.from_surface(self.PIPE_BOT)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bot_offset = (self.x - bird.x, self.bot - round(bird.y))

		# retuns None if nothing collides
		b_point = bird_mask.overlap(bot_mask, bot_offset)
		t_poimt = bird_mask.overlap(top_mask, top_offset)

		if t_poimt or b_point:
			return True

		return False

class Base:
	VELOCITY = 5
	BASE_WIDTH = BASE_IMAGE.get_width()

	IMAGE = BASE_IMAGE

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.BASE_WIDTH

	def move(self):
		self.x1 -= self.VELOCITY
		self.x2 -= self.VELOCITY

		if self.x1 + self.BASE_WIDTH < 0:
			self.x1 = self.x2 + self.BASE_WIDTH

		if self.x2 + self.BASE_WIDTH < 0:
			self.x2 = self.x1 + self.BASE_WIDTH

	def draw(self, window):
		window.blit(self.IMAGE, (self.x1, self.y))
		window.blit(self.IMAGE, (self.x2, self.y))


def draw_window(window, bird, pipes, base, score):
	window.blit(BG, (0,0))
	for pipe in pipes:
		pipe.draw(window)

	text = SCORE_FONT.render(str(score), 1, (255, 255, 255))
	window.blit(text, (WIDTH - 10 - text.get_width(), 10))
	base.draw(window)
	bird.draw(window)
	pygame.display.update()	

def main():
	bird = Bird(230,350)
	base = Base(730)
	pipes = [Pipe(600)]
	window = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()

	flappy = True

	score = 0
	clock_tick = 40

	while flappy:
		clock.tick(clock_tick)
		for event in pygame.event.get():
			if event.type == pygame.KEYUP:
				bird.jump()
			if event.type == pygame.QUIT:
				flappy = False
		bird.move()

		remove = []
		add_pipe = False


		for pipe in pipes:
			# if bird collides with pipe, restart
			if pipe.collide(bird):
				main()

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				remove.append(pipe)

			if not pipe.passed and pipe.x < bird.x:
				pipe.passed = True
				add_pipe = True

			pipe.move()

		# adding a new pipe means the bird passed the pipe
		if add_pipe:
			# small coin sfx 
			pygame.mixer.music.load(os.path.join("resources", "coinsound.mp3"))
			pygame.mixer.music.play(0)
			# increase score
			score += 1
			# add another random pipe to the window
			pipes.append(Pipe(600))

		for r in remove:
			pipes.remove(r)

		# if bird hits base, restart
		if bird.y + bird.image.get_height() >= 730:
			main()

		# if bird goes over the top, restart
		if bird.y + bird.image.get_height() < -10:
			main()	

		base.move()

		draw_window(window, bird, pipes, base, score)

	pygame.quit()
	quit()


main()



