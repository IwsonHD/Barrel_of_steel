import pygame
import sys
import math
import time

# Inicjalizacja pygame
pygame.init()

# Ustawienia okna
screen_width = 800
screen_height = 600
tank_width = 100
tank_height = 110
tankPick_width = 170
tankPick_height = 150
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("STALOWA LUFA")


background_color = (50, 67, 98)
gradient_color = (0, 17, 48)
gradient_factor = 1.1

background_image = pygame.image.load('./background.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
tankImage = pygame.image.load('tank_pink.png')
logoImage = pygame.image.load('logo.png')
tankGreenImage = pygame.image.load("tank_green.png")
tankBlueImage = pygame.image.load("tank_blue.png")
tankRedImage = pygame.image.load("tank_red.png")
tankPinkImage = pygame.image.load("tank_pink.png")
tankYellowImage = pygame.image.load("tank_yellow.png")

tankImage = pygame.transform.scale(tankImage, (tank_width, tank_height))
image_rect = tankImage.get_rect(center=(screen_width // 2, screen_height // 2))
logoImage = pygame.transform.scale(logoImage, (600, 400))
logo_rect = logoImage.get_rect(center=(screen_width // 2, screen_height // 5))
tankGreenImage = pygame.transform.scale(tankGreenImage, (tankPick_width, tankPick_height))
tangGreen_rect = tankGreenImage.get_rect(center=(screen_width // 2, 3 * screen_height // 5))
tankBlueImage = pygame.transform.scale(tankBlueImage, (tankPick_width, tankPick_height))
tangBlue_rect = tankBlueImage.get_rect(center=(screen_width // 2, 3 * screen_height // 5))
tankRedImage = pygame.transform.scale(tankRedImage, (tankPick_width, tankPick_height))
tankPinkImage = pygame.transform.scale(tankPinkImage, (tankPick_width, tankPick_height))
tankYellowImage = pygame.transform.scale(tankYellowImage, (tankPick_width, tankPick_height))

rect_speed = 5
rect_angle = 0


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.radius = 5

    def move(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))

    def draw(self, screen):
        pygame.draw.circle(screen, (43,43,43), (int(self.x), int(self.y)), self.radius)


bullets = []

start = False
running = True
pick = 0
pick_images = [tankBlueImage, tankGreenImage, tankRedImage, tankPinkImage, tankYellowImage]
picked_image = None
pick_num = len(pick_images)
start_time = None
score = 0


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_x = image_rect.centerx + (image_rect.width // 2) * math.cos(math.radians(rect_angle))
                bullet_y = image_rect.centery - (image_rect.height // 2) * math.sin(math.radians(rect_angle))
                bullets.append(Bullet(bullet_x, bullet_y, rect_angle))
        if not start:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    picked_image = pick_images[pick]
                    picked_image = pygame.transform.scale(picked_image, (tank_width, tank_height))
                    start = True
                    start_time = time.time()
                if event.key == pygame.K_RIGHT:
                    pick = (pick + 1) % pick_num
                if event.key == pygame.K_LEFT:
                    pick = (pick - 1) % pick_num
    if not start:
        #screen.fill((0, 17, 48))
        for y in range(screen_height):
            r = background_color[0] + (gradient_color[0] - background_color[0]) * (y / screen_height)
            g = background_color[1] + (gradient_color[1] - background_color[1]) * (y / screen_height)
            b = background_color[2] + (gradient_color[2] - background_color[2]) * (y / screen_height)
            color = (int(r), int(g), int(b))
            pygame.draw.line(screen, color, (0, y), (screen_width, y))

        screen.blit(logoImage, logo_rect.topleft)
        curr_pick = pick_images[pick]
        screen.blit(curr_pick, tangGreen_rect.topleft)

    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            rect_angle += 5
        if keys[pygame.K_RIGHT]:
            rect_angle -= 5

        if keys[pygame.K_UP]:
            new_x = image_rect.x + rect_speed * math.cos(math.radians(rect_angle))
            new_y = image_rect.y - rect_speed * math.sin(math.radians(rect_angle))
            if 0 <= new_x <= screen_width - tank_width and 0 <= new_y <= screen_height - tank_height:
                image_rect.x = new_x
                image_rect.y = new_y
        if keys[pygame.K_DOWN]:
            new_x = image_rect.x - rect_speed * math.cos(math.radians(rect_angle))
            new_y = image_rect.y + rect_speed * math.sin(math.radians(rect_angle))
            if 0 <= new_x <= screen_width - tank_width and 0 <= new_y <= screen_height - tank_height:
                image_rect.x = new_x
                image_rect.y = new_y

        #screen.fill((168,168,168))
        screen.blit(background_image, (0, 0))

        rotated_image = pygame.transform.rotate(picked_image, rect_angle+270)
        rotated_rect = rotated_image.get_rect(center=image_rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)

        for bullet in bullets[:]:
            bullet.move()
            bullet.draw(screen)
            if bullet.x < 0 or bullet.x > screen_width or bullet.y < 0 or bullet.y > screen_height:
                bullets.remove(bullet)

        # Obliczanie czasu spędzonego w grze
        elapsed_time = time.time() - start_time
        elapsed_minutes = int(elapsed_time // 60)
        elapsed_seconds = int(elapsed_time % 60)
        time_string = f"Time: {elapsed_minutes:02}:{elapsed_seconds:02}"

        score_string = f"Score: {score:04}"

        #font = pygame.font.SysFont(None, 36)
        font = pygame.font.Font("../ka1.ttf", 20)
        time_text = font.render(time_string, True, (0, 0, 0))
        score_text = font.render(score_string, True, (0, 0, 0))
        screen.blit(time_text, (10, 10))
        screen.blit(score_text, (screen_width-190, 10))

    pygame.display.flip()

    pygame.time.Clock().tick(30)

pygame.quit()
sys.exit()
