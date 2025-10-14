import pygame
import random
import math

pygame.init()

# ----- Window -----
W, H = 700, 450
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Avoid the Block")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# ----- Colors -----
WHITE = (255, 255, 255)
RED   = (230, 40, 40)
BLUE  = (60, 160, 255)
YELLOW= (255, 230, 0)

# ----- Stars -----
stars = []
for _ in range(70):
    stars.append({
        "x": random.randint(0, W),
        "y": random.randint(0, H),
        "speed": random.uniform(0.5, 1.5),
        "size": random.randint(1, 3),
        "t": random.uniform(0, 2 * math.pi)
    })

# ----- Player -----
player_x = W // 2
player_y = H - 60
player_w = 40
player_h = 40
player_speed = 5

# ----- Enemy -----
enemy_x = random.randint(0, W - 40)
enemy_y = -40
enemy_size = 40
enemy_speed = 2.0   # will slowly increase as score grows

# ----- Score / Game -----
score = 0
high_score = 0
game_over = False

# ----- Main Loop -----
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        # Move player
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        player_x = max(0, min(W - player_w, player_x))

        # Move enemy
        enemy_y += enemy_speed

        # If enemy leaves screen, respawn and add score
        if enemy_y > H:
            enemy_y = -enemy_size
            enemy_x = random.randint(0, W - enemy_size)
            score += 1
            # small difficulty ramp
            if enemy_speed < 6:
                enemy_speed += 0.2

        # Collision
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
        enemy_rect  = pygame.Rect(enemy_x, enemy_y, enemy_size, enemy_size)
        if player_rect.colliderect(enemy_rect):
            game_over = True
            if score > high_score:
                high_score = score

    # Restart
    if game_over and keys[pygame.K_r]:
        enemy_x = random.randint(0, W - enemy_size)
        enemy_y = -enemy_size
        enemy_speed = 2.0
        score = 0
        player_x = W // 2
        game_over = False

    # ---------- DRAW BACKGROUND (gradient + stars) ----------
    for y in range(H):
        t = y / H
        r = int(10 * (1 - t) + 2 * t)
        g = int(10 * (1 - t) + 2 * t)
        b = int(35 * (1 - t) + 10 * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (W, y))

    for s in stars:
        s["y"] += s["speed"]
        if s["y"] > H:
            s["y"] = 0
            s["x"] = random.randint(0, W)
        s["t"] += 0.05
        brightness = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(s["t"]))
        color = (int(200 * brightness), int(200 * brightness), 255)
        pygame.draw.circle(screen, color, (int(s["x"]), int(s["y"])), s["size"])

    # ---------- DRAW GAME OBJECTS ----------
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_w, player_h))
    pygame.draw.polygon(screen, YELLOW, [
        (player_x + player_w//2, player_y + player_h),
        (player_x + player_w//2 - 5, player_y + player_h + 10),
        (player_x + player_w//2 + 5, player_y + player_h + 10)
    ])
    pygame.draw.rect(screen, RED, (enemy_x, enemy_y, enemy_size, enemy_size))

    # ---------- UI ----------
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Best: {high_score}", True, WHITE), (10, 40))
    if game_over:
        msg = font.render("Crashed! Press R to Restart", True, WHITE)
        screen.blit(msg, msg.get_rect(center=(W//2, H//2)))

    pygame.display.flip()

pygame.quit()
