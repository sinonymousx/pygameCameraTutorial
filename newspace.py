import pygame
import sys
from random import randint
from pygame.math import Vector2

def limit(vector, max_len):
    if vector.length() > max_len:
        vector.scale_to_length(max_len)
    return vector

class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a small white surface for the star.
        self.image = pygame.Surface((2, 2))
        self.image.fill((255, 255, 255))
        # Place the star randomly within a larger world.
        x = randint(0, 2000)
        y = randint(0, 2000)
        self.rect = self.image.get_rect(topleft=(x, y))
        # Parallax factor: lower values move less (appear further away)
        self.parallax = randint(1, 50) / 100  # between 0.01 and 0.50

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, world_rect):
        super().__init__()
        # Create a red surface for the player.
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        # Store the world boundaries for clamping.
        self.world_rect = world_rect
        #Movement
        self.v = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.friction = Vector2(0, 0)
        self.bullets = []

    def update(self):
        # Basic player movement.
        self.acc *= 0
        max_speed = 10
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.acc.y = -0.5
        if keys[pygame.K_s]:
            self.acc.y = 0.5
        if keys[pygame.K_a]:
            self.acc.x = -0.5
        if keys[pygame.K_d]:
            self.acc.x = 0.5
        if pygame.mouse.get_pressed()[0]:
            self.bullets.append(Bullet(self.rect.x, self.rect.y))
        self.v += self.acc
        limit(self.v, 10)
        self.friction = self.v.copy()
        self.friction *= -0.05
        self.v += self.friction
        if self.v.length() > max_speed:
            self.v.normalize_ip()
            self.v *= max_speed
        self.rect.x += self.v.x
        self.rect.y += self.v.y
        # Clamp the player's position within the world boundaries.
        self.rect.clamp_ip(self.world_rect)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a red surface for the bullet.
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))

        self.life = 0
        #Movement
        self.v = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.friction = Vector2(0, 0)

        mouse_pos = Vector2(pygame.mouse.get_pos())
        self.v = mouse_pos - Vector2(self.rect.x, self.rect.y)

    def update(self):
        self.acc *= 0
        self.v += self.acc
        self.rect.x += self.v.x
        self.rect.y += self.v.y
        if self.life > 180:
            self.kill()
        self.life += 1
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, world_rect):
        super().__init__()
        # Create a purple surface for the enemy.
        self.image = pygame.Surface((20, 20))
        self.image.fill((250, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.v = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        # Store the world boundaries for clamping.
        self.world_rect = world_rect

    def update(self):
        # Basic enemy movement.
        self.v += self.acc
        limit(self.v, 10)
        self.rect.x += self.v.x
        self.rect.y += self.v.y
        self.acc *= 0
        # Clamp the enemy's position within the world boundaries.
        self.rect.clamp_ip(self.world_rect)
    
    def chase(self, target):
        desired = Vector2(target.x - self.rect.x, target.y - self.rect.y)
        desired.scale_to_length(10)
        steer = desired - self.v
        limit(steer, 0.51)
        self.acc += steer


class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # Get the display surface.
        self.display_surface = pygame.display.get_surface()
        # Offset determines how much the world is shifted on screen.
        self.offset = Vector2(0, 0)
        # Centering values.
        self.half_w = self.display_surface.get_width() / 2
        self.half_h = self.display_surface.get_height() / 2

    def center_target(self, target):
        """
        Adjusts the offset so that the target (typically the player)
        is centered on the screen.
        """
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self):
        """
        Draws all sprites in the group with an offset based on the target's
        position. For sprites with a 'parallax' attribute, the offset is
        scaled accordingly.
        """
        # Update the camera's offset to center on the target.
        #self.center_target(target)

        # Optionally, sort sprites (e.g., by vertical position) for layering.
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_rect = sprite.rect.copy()
            # If the sprite has a parallax attribute, use it.
            if hasattr(sprite, 'parallax'):
                offset_rect.topleft -= self.offset * sprite.parallax
            else:
                offset_rect.topleft -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)

def main():
    pygame.init()

    # Screen and world setup.
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Camera Group with Parallax")
    font = pygame.font.Font("pixel.ttf", 32)
    clock = pygame.time.Clock()

    deaths = 0

    # Define world boundaries.
    world_rect = pygame.Rect(0, 0, 2000, 2000)

    # Create the camera group.
    camera = Camera()

    # Create a player sprite and pass in the world boundaries.
    player = Player(400, 300, world_rect)
    camera.add(player)

    # Create an enemy sprite and pass in the world boundaries.
    enemy = Enemy(200, 200, world_rect)
    camera.add(enemy)

    # Create bullet sprites.
    bullets = []
    for i in range(len(player.bullets)):
        bullets.append(player.bullets[i])
        camera.add(bullets[i])

    # Create stars and add them to the camera group.
    for _ in range(5000):
        star = Star()
        camera.add(star)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update the player (which now handles its own clamping).
        player.update()

        # Update the enemy.
        enemy.update()
        enemy.chase(player.rect)

        # Update bullets.
        for bullet in bullets:
            bullet.update()

        # Drawing.
        screen.fill((50, 50, 50))
        # The camera group draws every sprite with the appropriate offset.
        camera.center_target(player)
        camera.custom_draw()

        # Render text
        score_text = font.render("Deaths: " + str(deaths), True, (255, 255, 255))
        #inv_text = font.render("Bullets: " + str(player.left), True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        #screen.blit(inv_text, (600, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
