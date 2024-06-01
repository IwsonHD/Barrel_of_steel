import pygame
import sys
import math
import time
import socket
import struct

MAX_PLAYERS = 3
MAX_BULLETS = 3

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Tank:
    def __init__(self, position, turnover_deg, colour, is_alive):
        self.position = position
        self.turnover_deg = turnover_deg
        #self.bullets = bullets
        self.colour = colour
        self.is_alive = is_alive

class Bullet:
    def __init__(self, position, angle, is_alive):
        self.position = position
        self.angle = angle
        self.is_alive = is_alive
        self.radius = 5

    def draw(self, screen):
        pygame.draw.circle(screen, (43, 43, 43), (int(self.position.x), int(self.position.y)), self.radius)


def recv_tanks(client_sock):
    tanks_data = client_sock.recv(MAX_PLAYERS * struct.calcsize('2f i c h' + MAX_BULLETS*' 2f h i'))
    tanks = []
    bullets_out = []
    for i in range(MAX_PLAYERS):
        offset = i * struct.calcsize('2f i c h' + MAX_BULLETS*' 2f h i')
        data = tanks_data[offset:offset + struct.calcsize('2f i c h' + MAX_BULLETS*' 2f h i')]
        position_x, position_y, turnover_deg, colour, is_alive, *bullets = struct.unpack('2f i c h' + MAX_BULLETS*' 2f h i', data)
        if is_alive == 1:
            position = Point(position_x, position_y)
            #bullet_positions = [Point(0,0) for i in range(MAX_BULLETS)]
            bullets_sub = [Bullet(Point(bullets[j*4], bullets[j*4 + 1]), bullets[j*4 + 3], bullets[j*4 + 2]) for j in range(MAX_BULLETS)]
            #bullet_positions = [Point(bullets[i*2], bullets[i*2+1]) for i in range(MAX_BULLETS)]
            tank = Tank(position, turnover_deg, colour.decode('utf-8'), is_alive)
            tanks.append(tank)
            bullets_out += bullets_sub
    return tanks, bullets_out


def main():
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

    background_image = pygame.image.load('game_logic/background.png')
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    tankImage = pygame.image.load('game_logic/tank_pink.png')
    logoImage = pygame.image.load('game_logic/logo.png')
    tankGreenImage = pygame.image.load("game_logic/tank_green.png")
    tankBlueImage = pygame.image.load("game_logic/tank_blue.png")
    tankRedImage = pygame.image.load("game_logic/tank_red.png")
    tankPinkImage = pygame.image.load("game_logic/tank_pink.png")
    tankYellowImage = pygame.image.load("game_logic/tank_yellow.png")

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
    bullets = []

    start = False
    running = True
    pick = 0
    pick_colours = ['b', 'g', 'r', 'p', 'y']
    pick_images = [tankBlueImage, tankGreenImage, tankRedImage, tankPinkImage, tankYellowImage]
    picked_image = None
    pick_num = len(pick_images)
    start_time = None
    score = 0

    server_address = ('127.0.0.1', 5001)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(server_address)
        print("Connected to server.")
    except socket.error as e:
        print("Error connecting to server:", e)
        exit()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not start:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        picked_image = pick_images[pick]
                        picked_image = pygame.transform.scale(picked_image, (tank_width, tank_height))
                        picked_colour = pick_colours[pick]
                        start = True
                        start_time = time.time()
                        try:
                            client_socket.send(picked_colour.encode('utf-8'))
                        except socket.error as e:
                            print(e)


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
            screen.blit(background_image, (0, 0))
            try:
                tanks, bullets = recv_tanks(client_socket)
            except socket.error as e:
                print(e)
                break
            for tank in tanks:
                if tank.is_alive:
                    tank_image = None
                    if tank.colour == 'b':
                        tank_image = tankBlueImage
                    elif tank.colour == 'g':
                        tank_image = tankGreenImage
                    elif tank.colour == 'r':
                        tank_image = tankRedImage
                    elif tank.colour == 'p':
                        tank_image = tankPinkImage
                    elif tank.colour == 'y':
                        tank_image = tankYellowImage
                    print(tank.position)
                    rotated_image = pygame.transform.rotate(tank_image, tank.turnover_deg + 270)
                    rotated_rect = rotated_image.get_rect(center=(tank.position.x,tank.position.y))
                    screen.blit(rotated_image, rotated_rect.topleft)
                    for bullet in bullets:
                        if bullet.is_alive:
                           bullet.draw(screen)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                client_socket.send(b'L')
            if keys[pygame.K_RIGHT]:
                client_socket.send(b'R')

            if keys[pygame.K_UP]:
                client_socket.send(b'U')
            if keys[pygame.K_DOWN]:
                client_socket.send(b'D')
            if keys[pygame.K_SPACE]:
                client_socket.send(b'S')
            #screen.fill((168,168,168))

            # Obliczanie czasu spędzonego w grze
            elapsed_time = time.time() - start_time
            elapsed_minutes = int(elapsed_time // 60)
            elapsed_seconds = int(elapsed_time % 60)
            time_string = f"Time: {elapsed_minutes:02}:{elapsed_seconds:02}"

            score_string = f"Score: {score:04}"

            #font = pygame.font.SysFont(None, 36)
            font = pygame.font.Font("ka1.ttf", 20)
            time_text = font.render(time_string, True, (0, 0, 0))
            score_text = font.render(score_string, True, (0, 0, 0))
            screen.blit(time_text, (10, 10))
            screen.blit(score_text, (screen_width-190, 10))

        pygame.display.flip()

        pygame.time.Clock().tick(30)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()