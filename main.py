import pygame, sys, random
from button import Button

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jurassic Jumpers")
clock = pygame.time.Clock()

BG = pygame.image.load("assets/Background.png")

pygame.mixer.init()
pygame.mixer.music.load("assets/menu_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# ✅ Load damage sound
damage_sound = pygame.mixer.Sound("assets/damage_sound.wav")
damage_sound.set_volume(0.5)

def get_font(size): 
    return pygame.font.Font("assets/font.ttf", size)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

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

        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_strength = -15
        self.grounded = False
        self.double_jump = False
        self.used_double_jump = False

        raw_jetpack = pygame.image.load("assets/jetpack_200x200_transparent.png").convert_alpha()
        self.jetpack_img = pygame.transform.scale(raw_jetpack, (80,80))

        raw_flame = pygame.image.load("assets/flame.png").convert_alpha()
        self.flame_img = pygame.transform.scale(raw_flame, (40, 50))

        self.jetpack_enabled = False
        self.jetpack_timer = 0  
        self.is_flying = False

        self.health = 3
        self.max_health = 3

    def activate_jetpack(self, duration=300):
        self.jetpack_enabled = True
        self.jetpack_timer = duration

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_j] and not self.jetpack_enabled:
            self.activate_jetpack()

        if self.jetpack_enabled and keys[pygame.K_SPACE]:
            self.velocity_y = -5
            self.is_flying = True
        else:
            self.is_flying = False

        if not self.jetpack_enabled and keys[pygame.K_SPACE]:
            if self.grounded:
                self.velocity_y = self.jump_strength
                self.grounded = False
                self.used_double_jump = False
            elif self.double_jump and not self.used_double_jump:
                self.velocity_y = self.jump_strength
                self.used_double_jump = True

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= HEIGHT - 20:
            self.rect.bottom = HEIGHT - 20
            self.velocity_y = 0
            self.grounded = True
            self.used_double_jump = False

        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity_y = 0

        if self.jetpack_enabled:
            self.jetpack_timer -= 1
            if self.jetpack_timer <= 0:
                self.jetpack_enabled = False

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
        jetpack_x = self.rect.left - 45
        jetpack_y = self.rect.top + 15
        surface.blit(self.jetpack_img, (jetpack_x, jetpack_y))

        if self.jetpack_enabled and self.is_flying:
            flame_x = self.rect.left - 25
            flame_y = self.rect.bottom - 25
            surface.blit(self.flame_img, (flame_x, flame_y))

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

def play():
    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/game_music.mp3")
    pygame.mixer.music.play(-1)

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
                pygame.quit()
                sys.exit()

        player.update()
        obstacle_group.update()

        obstacle_timer += 1
        if obstacle_timer > 90:
            obstacle = Obstacle(WIDTH + random.randint(0, 200))
            obstacle_group.add(obstacle)
            obstacle_timer = 0

        if pygame.sprite.spritecollide(player, obstacle_group, False):
            damage_sound.play()  # ✅ Play sound on damage
            player.health -= 1
            obstacle_group.empty()
            if player.health <= 0:
                running = False

        score += 1

        SCREEN.fill(BLACK)
        player.draw(SCREEN)
        obstacle_group.draw(SCREEN)

        score_text = font.render(f"Score: {score}", True, WHITE)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))
        SCREEN.blit(health_text, (10, 40))

        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/menu_music.mp3")
    pygame.mixer.music.play(-1)

    main_menu()

def options():
    slider_x = 440
    slider_y = 300
    slider_width = 400
    slider_height = 10
    handle_radius = 12
    dragging = False

    volume = pygame.mixer.music.get_volume()

    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        mouse_x, mouse_y = OPTIONS_MOUSE_POS

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("Options", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        pygame.draw.rect(SCREEN, "gray", (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(SCREEN, "green", (slider_x, slider_y, int(slider_width * volume), slider_height))

        handle_x = slider_x + int(slider_width * volume)
        pygame.draw.circle(SCREEN, "blue", (handle_x, slider_y + slider_height // 2), handle_radius)

        vol_text = get_font(30).render(f"Volume: {int(volume * 100)}%", True, "black")
        SCREEN.blit(vol_text, (slider_x, slider_y - 40))

        OPTIONS_BACK = Button(image=None, pos=(640, 500),
                              text_input="BACK", font=get_font(50), base_color="Black", hovering_color="Green")
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    return
                if abs(mouse_x - handle_x) < handle_radius and abs(mouse_y - (slider_y + slider_height // 2)) < handle_radius:
                    dragging = True

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            elif event.type == pygame.MOUSEMOTION and dragging:
                new_volume = (mouse_x - slider_x) / slider_width
                volume = max(0.0, min(1.0, new_volume))
                pygame.mixer.music.set_volume(volume)

        pygame.display.update()

def main_menu():
    pygame.mixer.music.load("assets/menu_music.mp3")
    pygame.mixer.music.play(-1)

    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(75).render("Jurassic Jumper", True, "#598006")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250),
                             text_input="PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400),
                                text_input="OPTIONS", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
                             text_input="QUIT", font=get_font(50), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()