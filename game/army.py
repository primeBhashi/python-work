import pygame
import random
import os
import time

# Initialize
pygame.init()
pygame.mixer.init()  # Initialize sound mixer
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Human vs Aliens 👽")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Load images (with error handling)
def load_image(name, default_color=(255, 0, 0), default_size=(50, 50)):
    try:
        img = pygame.image.load(f"game/{name}")
        return img
    except:
        # Create a fallback surface if image can't be loaded
        surf = pygame.Surface(default_size)
        surf.fill(default_color)
        return surf

# Load images
player_img = load_image("human.png")
alien_img = load_image("alien.png")
bullet_img = load_image("bullet.png", WHITE, (10, 20))
boss_img = load_image("alien.png", RED, (100, 100))

# Load power-up images or create colored replacements
health_img = load_image("health.png", GREEN, (30, 30))
shield_img = load_image("shield.png", BLUE, (30, 30))
rapid_fire_img = load_image("rapid.png", YELLOW, (30, 30))
bomb_img = load_image("bomb.png", RED, (30, 30))

# Background image (or create a starfield)
try:
    background = pygame.image.load("game/background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)
    # Create stars
    for i in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        pygame.draw.circle(background, WHITE, (x, y), size)

# Scale images
player_img = pygame.transform.scale(player_img, (50, 60)) 
alien_img = pygame.transform.scale(alien_img, (50, 50))
bullet_img = pygame.transform.scale(bullet_img, (10, 20))
boss_img = pygame.transform.scale(boss_img, (100, 100))
health_img = pygame.transform.scale(health_img, (30, 30))
shield_img = pygame.transform.scale(shield_img, (30, 30))
rapid_fire_img = pygame.transform.scale(rapid_fire_img, (30, 30))
bomb_img = pygame.transform.scale(bomb_img, (30, 30))

# Try to load sounds, with fallback
def load_sound(name):
    try:
        sound = pygame.mixer.Sound(f"game/{name}")
        return sound
    except:
        return None

# Load sounds
shoot_sound = load_sound("shoot.wav")
explosion_sound = load_sound("explosion.wav")
powerup_sound = load_sound("powerup.wav")
game_over_sound = load_sound("gameover.wav")
level_up_sound = load_sound("levelup.wav")

# Game clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)
big_font = pygame.font.SysFont("consolas", 48)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 5
        self.health = 100
        self.lives = 3
        self.rapid_fire = False
        self.rapid_fire_time = 0
        self.shield = False
        self.shield_time = 0
        self.shoot_delay = 500  # Milliseconds between shots
        self.last_shot = pygame.time.get_ticks()
        self.original_image = self.image.copy()
        self.shield_image = self.create_shield_image()
        
    def create_shield_image(self):
        """Create shield visual effect around player"""
        shield_img = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shield_img, (0, 100, 255, 128), shield_img.get_rect())
        return shield_img

    def update(self):
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        
        # Add up/down movement
        if keys[pygame.K_UP] and self.rect.top > HEIGHT // 2:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            
        # Auto shoot in rapid fire mode
        now = pygame.time.get_ticks()
        if self.rapid_fire:
            if now - self.rapid_fire_time > 5000:  # 5 second duration
                self.rapid_fire = False
            elif now - self.last_shot > 100:  # Rapid fire rate
                self.shoot()
                self.last_shot = now
                
        # Check shield status
        if self.shield:
            if now - self.shield_time > 7000:  # 7 seconds duration
                self.shield = False
                
        # Apply shield visual if active
        if self.shield:
            self.image = self.original_image.copy()
            temp_shield = pygame.transform.scale(self.shield_image, 
                                            (self.rect.width + 10, self.rect.height + 10))
            self.image.blit(temp_shield, (-5, -5))
        else:
            self.image = self.original_image.copy()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            
            # Create bullet(s)
            if self.rapid_fire:
                # Triple shot in rapid fire mode
                for offset in [-10, 0, 10]:
                    bullet = Bullet(self.rect.centerx + offset, self.rect.top)
                    bullets.add(bullet)
                    all_sprites.add(bullet)
            else:
                # Normal single shot
                bullet = Bullet(self.rect.centerx, self.rect.top)
                bullets.add(bullet)
                all_sprites.add(bullet)
                
            # Play sound
            if shoot_sound:
                shoot_sound.play()
    
    def activate_rapid_fire(self):
        self.rapid_fire = True
        self.rapid_fire_time = pygame.time.get_ticks()
        
    def activate_shield(self):
        self.shield = True
        self.shield_time = pygame.time.get_ticks()
        
    def get_hit(self, damage):
        if not self.shield:  # Shield prevents damage
            self.health -= damage
            if self.health <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    return True  # Game over
                else:
                    self.health = 100  # Reset health for next life
                    
        return False  # Still alive

class Alien(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.image = alien_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-150, -40)
        
        # Speed increases with level
        self.level = level
        self.base_speed = random.randint(2, 4)
        self.speed = self.base_speed + 0.5 * (level - 1)
        
        # Occasionally aliens shoot back at higher levels
        self.can_shoot = level > 2 and random.random() < 0.3
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(1000, 3000)
        
    def update(self):
        self.rect.y += self.speed
        
        # Loop back to top when it goes off-screen
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            
        # Shoot if able
        if self.can_shoot:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot()
                
    def shoot(self):
        # Aliens shoot downward
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        enemy_bullets.add(enemy_bullet)
        all_sprites.add(enemy_bullet)

class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = boss_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.top = 50
        self.health = 50 * level
        self.max_health = 50 * level
        self.level = level
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 2 + 0.5 * (level - 1)
        self.shoot_delay = 1000 - 50 * (level - 1)  # Shoot faster at higher levels
        self.last_shot = pygame.time.get_ticks()
        
    def update(self):
        # Move side to side
        self.rect.x += self.speed * self.direction
        
        # Change direction if hitting the edge
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.direction *= -1
            
        # Shoot regularly
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()
            
    def shoot(self):
        # Boss shoots three bullets in a spread pattern
        for offset in [-20, 0, 20]:
            enemy_bullet = EnemyBullet(self.rect.centerx + offset, self.rect.bottom)
            enemy_bullets.add(enemy_bullet)
            all_sprites.add(enemy_bullet)
            
    def draw_health_bar(self, surface):
        # Health bar for boss
        health_ratio = self.health / self.max_health
        bar_width = self.rect.width
        bar_height = 10
        
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 15, int(bar_width * health_ratio), bar_height)
        
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(bullet_img, (8, 16))
        self.image = pygame.transform.rotate(self.image, 180)  # Flip bullet image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 7

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.frame = 0
        self.frames = []
        
        # Create simple explosion animation using circles
        for i in range(5):
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(frame, (255, 255 - i*40, 0, 255 - i*40), 
                              (size//2, size//2), size//2 - i*3)
            self.frames.append(frame)
            
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.frames):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.frames[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(['shield', 'health', 'rapid', 'bomb'])
        
        if self.type == 'shield':
            self.image = shield_img
        elif self.type == 'health':
            self.image = health_img
        elif self.type == 'rapid':
            self.image = rapid_fire_img
        elif self.type == 'bomb':
            self.image = bomb_img
            
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 3
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Game functions
def draw_text(surf, text, size, x, y, color=WHITE):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surf, text_rect)

def draw_health_bar(surf, x, y, health, lives):
    if health < 0:
        health = 0
    BAR_LENGTH = 200
    BAR_HEIGHT = 20
    fill = (health / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)
    
    # Draw lives
    for i in range(lives):
        life_icon = pygame.transform.scale(player_img, (20, 25))
        surf.blit(life_icon, (x + BAR_LENGTH + 20 + i * 30, y - 2))

def spawn_enemies(num_aliens, level):
    for _ in range(num_aliens):
        alien = Alien(level)
        all_sprites.add(alien)
        aliens.add(alien)

def show_title_screen():
    screen.blit(background, (0, 0))
    draw_text(screen, "HUMAN VS ALIENS 👽", 64, WIDTH // 2, HEIGHT // 4, WHITE)
    draw_text(screen, "Arrow keys to move, SPACE to shoot", 22, WIDTH // 2, HEIGHT // 2, WHITE)
    draw_text(screen, "Press any key to begin", 18, WIDTH // 2, HEIGHT * 3 / 4, WHITE)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True

def show_game_over_screen(score):
    screen.blit(background, (0, 0))
    draw_text(screen, "GAME OVER", 64, WIDTH // 2, HEIGHT // 4, RED)
    draw_text(screen, f"Final Score: {score}", 36, WIDTH // 2, HEIGHT // 2, WHITE)
    draw_text(screen, "Press any key to play again", 22, WIDTH // 2, HEIGHT * 3 / 4, WHITE)
    pygame.display.flip()
    
    # Play game over sound
    if game_over_sound:
        game_over_sound.play()
    
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True

def show_level_screen(level):
    screen.blit(background, (0, 0))
    draw_text(screen, f"LEVEL {level}", 64, WIDTH // 2, HEIGHT // 2, YELLOW)
    pygame.display.flip()
    
    # Play level up sound
    if level_up_sound:
        level_up_sound.play()
    
    # Pause briefly to show level
    pygame.time.wait(2000)
    return True

# Main game loop
def main():
    # Game variables
    score = 0
    level = 1
    boss_level = False
    game_over = False
    running = True
    
    # Show title screen
    if not show_title_screen():
        return
    
    # Sprite groups
    global all_sprites, aliens, bullets, enemy_bullets, powerups
    all_sprites = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Start with level 1 enemies
    spawn_enemies(6, level)
    
    # Game loop
    while running:
        clock.tick(60)  # 60 FPS
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Shoot bullet
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
        
        # Only update game objects if not game over
        if not game_over:
            # Update all sprites
            all_sprites.update()
            
            # Check for collisions between player bullets and aliens
            hits = pygame.sprite.groupcollide(aliens, bullets, True, True)
            for hit in hits:
                # Increase score
                score += 10 * level
                
                # Create explosion
                expl = Explosion(hit.rect.center, 40)
                all_sprites.add(expl)
                
                # Play explosion sound
                if explosion_sound:
                    explosion_sound.play()
                
                # Random chance to drop a power-up
                if random.random() < 0.1:  # 10% chance
                    power = PowerUp(hit.rect.center)
                    all_sprites.add(power)
                    powerups.add(power)
                
                # Spawn replacement alien if not boss level
                if not boss_level:
                    alien = Alien(level)
                    all_sprites.add(alien)
                    aliens.add(alien)
            
            # Check for collisions between player bullets and boss
            if boss_level and boss in all_sprites:
                boss_hits = pygame.sprite.spritecollide(boss, bullets, True)
                for hit in boss_hits:
                    boss.health -= 10
                    
                    # Create small explosion
                    expl = Explosion(hit.rect.center, 20)
                    all_sprites.add(expl)
                    
                    # Check if boss is defeated
                    if boss.health <= 0:
                        # Big explosion
                        expl = Explosion(boss.rect.center, 100)
                        all_sprites.add(expl)
                        
                        # Play explosion sound
                        if explosion_sound:
                            explosion_sound.play()
                            
                        # Remove boss
                        boss.kill()
                        
                        # Add score bonus
                        score += 100 * level
                        
                        # End boss level, go to next level
                        boss_level = False
                        level += 1
                        
                        # Show level screen
                        show_level_screen(level)
                        
                        # Clear all bullets
                        for bullet in bullets:
                            bullet.kill()
                        for bullet in enemy_bullets:
                            bullet.kill()
                            
                        # Spawn enemies for new level
                        spawn_enemies(6 + level, level)
            
            # Check for collisions between player and alien bullets
            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                game_over = player.get_hit(25)  # Enemy bullets do 25 damage
                
                # Create small explosion at player position
                expl = Explosion(player.rect.center, 30)
                all_sprites.add(expl)
            
            # Check if aliens hit player
            hits = pygame.sprite.spritecollide(player, aliens, True)
            if hits:
                # Player takes damage
                game_over = player.get_hit(50)  # Collisions do 50 damage
                
                # Create explosion
                expl = Explosion(hits[0].rect.center, 40)
                all_sprites.add(expl)
                
                # Play explosion sound
                if explosion_sound:
                    explosion_sound.play()
                
                # Spawn replacement alien
                alien = Alien(level)
                all_sprites.add(alien)
                aliens.add(alien)
            
            # Check if player got power-up
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'shield':
                    player.activate_shield()
                elif hit.type == 'health':
                    player.health = min(100, player.health + 30)  # Add 30 health, max 100
                elif hit.type == 'rapid':
                    player.activate_rapid_fire()
                elif hit.type == 'bomb':
                    # Destroy all enemies on screen
                    for alien in aliens:
                        # Create explosion at each alien
                        expl = Explosion(alien.rect.center, 40)
                        all_sprites.add(expl)
                        # Add score
                        score += 10 * level
                    # Kill all aliens
                    for alien in aliens:
                        alien.kill()
                    # Repopulate aliens
                    if not boss_level:
                        spawn_enemies(6 + level, level)
                
                # Play power-up sound
                if powerup_sound:
                    powerup_sound.play()
            
            # Check if all aliens are defeated and not in boss level
            if len(aliens) == 0 and not boss_level:
                # Every 3 levels is a boss level
                if level % 3 == 0:
                    boss_level = True
                    boss = Boss(level // 3)  # Boss strength increases
                    all_sprites.add(boss)
                else:
                    # Regular level up
                    level += 1
                    show_level_screen(level)
                    spawn_enemies(6 + level, level)  # More aliens each level
        
        # Draw / render
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        
        # Draw boss health bar if boss level
        if boss_level and 'boss' in locals() and boss in all_sprites:
            boss.draw_health_bar(screen)
        
        # Display score and level
        draw_text(screen, f"Score: {score}", 24, 120, 10)
        draw_text(screen, f"Level: {level}", 24, WIDTH - 90, 10)
        
        # Draw health bar and lives
        draw_health_bar(screen, 10, 40, player.health, player.lives)
        
        # If game over, show game over screen
        if game_over:
            if show_game_over_screen(score):
                # Restart the game
                return main()
            else:
                running = False
        
        pygame.display.flip()
    
    # Clean up
    pygame.quit()

# Start the game
if __name__ == "__main__":
    main()