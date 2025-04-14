import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 500
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
RED = (255, 50, 50)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Runner")
clock = pygame.time.Clock()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Animation frames
        self.animations = {
            "idle": [pygame.image.load("assets\\p1_stand.png")],
            "run": [pygame.image.load("assets\\p2_walk04.png")],
            "jump": [pygame.image.load("assets\\p1_jump.png")],
            "fly": [pygame.image.load("assets\\p1_jump.png")],  # Placeholder for jetpack animation
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
        self.dash_cooldown = 0

        # Stats
        self.health = 3
        self.max_health = 3
        self.speed = 5
        self.has_shield = False
        self.double_jump = False
        self.used_double_jump = False

        # Jetpack
        self.jetpack_enabled = False
        self.jetpack_timer = 0
        self.is_flying = False

    def activate_jetpack(self, duration=300):
        self.jetpack_enabled = True
        self.jetpack_timer = duration

    def update(self):
        keys = pygame.key.get_pressed()

        # === Activate Jetpack with J ===
        if keys[pygame.K_j] and not self.jetpack_enabled:
            self.activate_jetpack()

        # === Jetpack Flying ===
        if self.jetpack_enabled and keys[pygame.K_SPACE]:
            self.velocity_y = -5
            self.is_flying = True
        else:
            self.is_flying = False

        # === Jumping (if jetpack is off) ===
        if not self.jetpack_enabled and keys[pygame.K_SPACE]:
            if self.grounded:
                self.velocity_y = self.jump_strength
                self.grounded = False
                self.used_double_jump = False
            elif self.double_jump and not self.used_double_jump:
                self.velocity_y = self.jump_strength
                self.used_double_jump = True

        # === Apply Gravity ===
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # === Boundaries ===
        if self.rect.bottom >= HEIGHT - 20:
            self.rect.bottom = HEIGHT - 20
            self.velocity_y = 0
            self.grounded = True
            self.used_double_jump = False

        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity_y = 0

        # === Jetpack timer ===
        if self.jetpack_enabled:
            self.jetpack_timer -= 1
            if self.jetpack_timer <= 0:
                self.jetpack_enabled = False

        # === Animation state ===
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

          

    def update(self):
        keys = pygame.key.get_pressed()

        # Jumping
        if keys[pygame.K_SPACE]:
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

        # Ground check
        if self.rect.bottom >= HEIGHT - 20:
            self.rect.bottom = HEIGHT - 20
            self.velocity_y = 0
            self.grounded = True
            self.used_double_jump = False


        
        # Update animation state
        if self.state != "dash":
            if not self.grounded:
                self.state = "jump"
            else:
                self.state = "run" if keys[pygame.K_RIGHT] else "idle"  

def update(self):
    keys = pygame.key.get_pressed()

    # === Jetpack control ===
    if self.jetpack_enabled and keys[pygame.K_SPACE]:
        self.velocity_y = -5
        self.is_flying = True
    else:
        self.is_flying = False



    # === Jumping (if jetpack is not active) ===
    if not self.jetpack_enabled and keys[pygame.K_SPACE]:
        if self.grounded:
            self.velocity_y = self.jump_strength
            self.grounded = False
            self.used_double_jump = False
        elif self.double_jump and not self.used_double_jump:
            self.velocity_y = self.jump_strength
            self.used_double_jump = True

    # === Gravity ===
    self.velocity_y += self.gravity
    self.rect.y += self.velocity_y

    # === Stay inside the screen ===
    if self.rect.bottom >= HEIGHT - 20:
        self.rect.bottom = HEIGHT - 20
        self.velocity_y = 0
        self.grounded = True
        self.used_double_jump = False

    if self.rect.top <= 0:
        self.rect.top = 0
        self.velocity_y = 0

    # === Animation states ===
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



    

# Obstacle class
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

# Main function
def main():
    player = Player()
    player_group = pygame.sprite.Group(player)
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

        # Update
        player_group.update()
        obstacle_group.update()

        # Obstacle generation
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

        # Scoring
        score += 1

        # Draw
        screen.fill(BLACK)
        player_group.draw(screen)
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
