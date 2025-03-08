import pygame
import sys
from random import randint
from pygame.math import Vector2

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

    def update(self):
        # Basic player movement.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= 5
        if keys[pygame.K_s]:
            self.rect.y += 5
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_d]:
            self.rect.x += 5
        # Clamp the player's position within the world boundaries.
        self.rect.clamp_ip(self.world_rect)

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

    def custom_draw(self, target):
        """
        Draws all sprites in the group with an offset based on the target's
        position. For sprites with a 'parallax' attribute, the offset is
        scaled accordingly.
        """
        # Update the camera's offset to center on the target.
        self.center_target(target)

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
    clock = pygame.time.Clock()

    # Define world boundaries.
    world_rect = pygame.Rect(0, 0, 2000, 2000)

    # Create the camera group.
    camera = Camera()

    # Create a player sprite and pass in the world boundaries.
    player = Player(400, 300, world_rect)
    camera.add(player)

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

        # Drawing.
        screen.fill((50, 50, 50))
        # The camera group draws every sprite with the appropriate offset.
        camera.custom_draw(player)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
