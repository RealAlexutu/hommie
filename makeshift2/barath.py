import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Runner")
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Animations
        self.animations = {
            "idle": [pygame.image.load("assets/p1_stand.png")],
            "run": [pygame.image.load("assets/p2_walk04.png")],
            "jump": [pygame.image.load("assets/p1_jump.png")],
            "fly": [pygame.image.load("assets/p1_jump.png")],
        }

        self.state = "idle"
        self.anim_index = 0
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT // 2)

        # Physics
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_strength = -15
        self.grounded = False
        self.double_jump = False
        self.used_double_jump = False

        # Jetpack
        self.jetpack_enabled = False
        self.jetpack_timer = 0
        self.is_flying = False

        # Load and scale jetpack (now BIGGER)
        raw_jetpack = pygame.image.load("assets/jetpack_200x200_transparent.png").convert_alpha()
        self.jetpack_img = pygame.transform.scale(raw_jetpack, (80, 80))  

        # Load and scale flame (now BIGGER)
        raw_flame = pygame.image.load("assets/flame.png").convert_alpha()
        self.flame_img = pygame.transform.scale(raw_flame, (40, 50)) 

        # Stats
        self.health = 3
        self.max_health = 3

    def activate_jetpack(self, duration=300):
        self.jetpack_enabled = True
        self.jetpack_timer = duration

    def update(self):
        keys = pygame.key.get_pressed()

        # Activate jetpack
        if keys[pygame.K_j] and not self.jetpack_enabled:
            self.activate_jetpack()

        # Flying
        if self.jetpack_enabled and keys[pygame.K_SPACE]:
            self.velocity_y = -5
            self.is_flying = True
        else:
            self.is_flying = False

        # Jumping
        if not self.jetpack_enabled and keys[pygame.K_SPACE]:
            if self.grounded:
                self.velocity_y = self.jump_strength
                self.grounded = False
                self.used_double_jump = False
            elif self.double_jump and not self.used_double_jump:
                self.velocity_y = self.jump_strength
                self.used_double_jump = True

        # Gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Boundaries
        if self.rect.bottom >= HEIGHT - 20:
            self.rect.bottom = HEIGHT - 20
            self.velocity_y = 0
            self.grounded = True
            self.used_double_jump = False

        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity_y = 0

        # Jetpack timer
        if self.jetpack_enabled:
            self.jetpack_timer -= 1
            if self.jetpack_timer <= 0:
                self.jetpack_enabled = False

        # Animation state
        if self.jetpack_enabled and self.is_flying:
            self.state = "fly"
        elif not self.grounded:
            self.state = "jump"
        else:
            self.state = "run" if keys[pygame.K_RIGHT] else "idle"

        self.animate()

    def animate(self):
        frames = self.animations[self.state]
        self.anim_index += 0.1
        if self.anim_index >= len(frames):
            self.anim_index = 0
        self.image = frames[int(self.anim_index)]

    def draw(self, surface):
        # Draw jetpack behind player (adjusted position)
        jetpack_x = self.rect.left - 45
        jetpack_y = self.rect.top +15
        surface.blit(self.jetpack_img, (jetpack_x, jetpack_y))

        # Draw flame (if flying) (adjusted position)
        if self.jetpack_enabled and self.is_flying:
            flame_x = self.rect.left - 25
            flame_y = self.rect.bottom - 25
            surface.blit(self.flame_img, (flame_x, flame_y))

        # Draw the player
        surface.blit(self.image, self.rect)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT - 60

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()


def main():
    player = Player()
    obstacle_group = pygame.sprite.Group()

    obstacle_timer = 0
    score = 0
    font = pygame.font.SysFont("Arial", 30)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update()
        obstacle_group.update()

        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer > 90:
            obstacle = Obstacle(WIDTH + random.randint(0, 200))
            obstacle_group.add(obstacle)
            obstacle_timer = 0

        # Collision detection
        if pygame.sprite.spritecollide(player, obstacle_group, False):
            player.health -= 1
            obstacle_group.empty()
            if player.health <= 0:
                running = False

        # Score
        score += 1

        # Draw
        screen.fill(BLACK)
        player.draw(screen)
        obstacle_group.draw(screen)

        # UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
