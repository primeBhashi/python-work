import pygame
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Human vs Aliens 👽")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
player_img = pygame.image.load("game/human.png")
alien_img = pygame.image.load("game/alien.png")
bullet_img = pygame.image.load("game/bullet.png")

# Scale images
player_img = pygame.transform.scale(player_img, (50, 60)) 
alien_img = pygame.transform.scale(alien_img, (50, 50))
bullet_img = pygame.transform.scale(bullet_img, (10, 20))

# Game clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        bullets.add(bullet)
        all_sprites.add(bullet)

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = alien_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Sprite groups
all_sprites = pygame.sprite.Group()
aliens = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create multiple aliens
for _ in range(6):
    alien = Alien()
    all_sprites.add(alien)
    aliens.add(alien)

# Score
score = 0

# Game loop
running = True
while running:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shoot bullet
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update
    all_sprites.update()

    # Check collisions
    hits = pygame.sprite.groupcollide(aliens, bullets, True, True)
    for hit in hits:
        score += 10
        alien = Alien()
        all_sprites.add(alien)
        aliens.add(alien)

    # Check if aliens hit player
    if pygame.sprite.spritecollideany(player, aliens):
        running = False  # Game over

    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))
    pygame.display.flip()

pygame.quit()
