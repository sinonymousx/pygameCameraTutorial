import pygame
import sys
from random import randint

class Star:
    def __init__(self):
        self.rect = pygame.Rect(randint(0, 2000), randint(0, 2000), 2, 2)
        self.parallax = randint(1, 50) / 100

class Camera:
    def __init__(self, width, height, world_width, world_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.world = pygame.Rect(0, 0, world_width, world_height)
        self.speed = 0.1
    
    def apply(self, entity):
        """
        Returns a shifted rect so that it appears in the correct position 
        relative to the camera's viewport.
        """
        return entity.move(-self.camera.x, -self.camera.y)
    
    def update(self, target):
        """
        Center the camera on the target (player) while keeping it within possible bounds.
        """
        desired_center = target.center
        current_center = self.camera.center

        #interpolate between current and desired center
        new_center_x = current_center[0] + (desired_center[0] - current_center[0]) * self.speed
        new_center_y = current_center[1] + (desired_center[1] - current_center[1]) * self.speed

        self.camera.center = (new_center_x, new_center_y)
        
        #limit scrolling to map size
        self.camera.clamp_ip(self.world)


def main():
    pygame.init()

    #screen
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Outer Space')
    clock = pygame.time.Clock()

    #player
    player = pygame.Rect(400, 300, 20, 20)

    #stars
    stars = [Star() for _ in range(5000)]

    #camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, 2000, 2000)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        #input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.y -= 5
        if keys[pygame.K_a]:
            player.x -= 5
        if keys[pygame.K_s]:
            player.y += 5
        if keys[pygame.K_d]:
            player.x += 5

        #bounds
        player.clamp_ip((0,0,2000,2000))
        
        #camera follow player
        camera.update(player)

        #draw  
        screen.fill((50,50,50))

        #parallax stars
        for star in stars:
            star_screen_x = star.rect.x - camera.camera.x * (1 - star.parallax)
            star_screen_y = star.rect.y - camera.camera.y * (1 - star.parallax)
            pygame.draw.rect(screen, (255,255,255), (star_screen_x, star_screen_y, star.rect.width, star.rect.height))


        #player
        shifted_player = camera.apply(player) #shift player rect to camera viewport
        pygame.draw.rect(screen, (255,0,0), shifted_player)

        #update
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()