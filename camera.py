import pygame, sys
from random import randint

class Tree(pygame.sprite.Sprite):
	def __init__(self, pos, group):
		super().__init__(group)
		self.image = pygame.image.load('graphics/tree.png').convert_alpha()
		self.rect = self.image.get_rect(topleft=pos)

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, group):
		super().__init__(group)
		self.image = pygame.image.load('graphics/player.png').convert_alpha()
		self.rect = self.image.get_rect(center=pos)
		self.direction = pygame.math.Vector2(0,0)
		self.speed = 5

	def input(self):
		keys = pygame.key.get_pressed()
		self.direction = pygame.math.Vector2(0,0)
		if keys[pygame.K_a]:
			self.direction.x = -1
		if keys[pygame.K_d]:
			self.direction.x = 1
		if keys[pygame.K_w]:
			self.direction.y = -1
		if keys[pygame.K_s]:
			self.direction.y = 1

	def update(self):
		self.input()
		self.rect.move_ip(self.direction * self.speed)

		#clamp player to screen
		self.rect.clamp_ip(screen.get_rect())

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()

		#camera offset init
		self.offset = pygame.math.Vector2(0,0)
		self.half_screen = pygame.math.Vector2(self.display_surface.get_size()) / 2


		#ground init
		self.ground_surface = pygame.image.load('graphics/ground.png').convert_alpha()
		self.ground_rect = self.ground_surface.get_rect(topleft=(0,0))
	
	def center_target_camera(self, target):
		#center camera on target
		self.offset = self.half_screen - target.rect.center

	def custom_draw(self, player):

		#center camera on player
		self.center_target_camera(player)

		#ground
		ground_offset = self.ground_rect.topleft + self.offset
		self.display_surface.blit(self.ground_surface, ground_offset)

		#sprites
		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft + self.offset
			self.display_surface.blit(sprite.image, offset_pos)

#init pygame    
pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

#setup
camera_group = CameraGroup()
player = Player((640,360), camera_group)

#generate trees
for i in range(20):
	Tree((randint(0,1000),randint(0,700)), camera_group)

#game loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	
	#fill screen with sky blue
	screen.fill('#71ddee')

	#update and draw camera group
	camera_group.update()
	camera_group.custom_draw(player)

	#update display and tick clock
	pygame.display.update()
	clock.tick(60)
