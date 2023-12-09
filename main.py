import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/trackkk.png"), 0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-borderrr.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH = pygame.transform.scale(FINISH, (79, 20))
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (715, 663)
MENU_BG = scale_image(pygame.image.load("imgs/menu.png"), 0.88)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.45)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.45)
player_car_2 = scale_image(pygame.image.load("imgs/green-car.png"), 0.45)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)
SMALL_FONT = pygame.font.SysFont("comicsans", 20)
BOLD_FONT = pygame.font.SysFont('comicsans', 50, bold=True)

FPS = 60
PATH = [(737, 163), (669, 57), (573, 69), (570, 204), (504, 241), (400, 122), (207, 66), (95, 70), (77, 180), (121, 234), (199, 236), (277, 228), (319, 318), (249, 368), (148, 332), (54, 372), (79, 476), (242, 495), (392, 363), (478, 323), (590, 343), (569, 422), (502, 450), (481, 521), (540, 519), (609, 533), (631, 609), (593, 636), (485, 639), (216, 568), (112, 579), (69, 651), (82, 734), (151, 759), (229, 732), (306, 709), (660, 764), (735, 745), (735, 720), (750, 630)]

def draw_menu(selected_option):
    WIN.blit(MENU_BG, (-50, 0))

    title_text = BOLD_FONT.render("NFS from the dollar store", True, (255, 150, 0))
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 35))

    for i, option in enumerate(["Play against PC", "Play with Friend"]):
        if i == selected_option:
            option_text = BOLD_FONT.render(option, True, (255, 0, 0))
        else:
            option_text = MAIN_FONT.render(option, True, (102, 204, 0))
        WIN.blit(option_text, (WIDTH // 1.95 - option_text.get_width() // 2, 140 + i * 50))

    pygame.display.update()


def show_start_menu():
    selected_option = 0 
    menu_run = True

    while menu_run:
        draw_menu(selected_option)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected_option > 0:
                    selected_option -= 1
                elif event.key == pygame.K_DOWN and selected_option < 1:
                    selected_option += 1
                elif event.key == pygame.K_RETURN:
                    menu_run = False
                    break
    return selected_option


class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)


    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    def __init__(self, max_vel, rotation_vel, img, start_pos):
        self.IMG = img
        self.START_POS = start_pos
        super().__init__(max_vel, rotation_vel)


    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()
    
    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()



class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (722, 615)

    def __init__(self, max_vel, rotation_vel, path=[], auto_control=True):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.auto_control = auto_control
        self.current_point = 0

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def calculate_angle(self):
        if not self.auto_control:
            return

        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        if not self.auto_control:
            return

        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.auto_control:
            if self.current_point >= len(self.path):
                return
            self.calculate_angle()
            self.update_path_point()
            self.move_forward()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        print("New level:", level, "Velocity:", self.vel)  # Debugging line
        self.current_point = 0


def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(
        f"{game_info.level}", 1, (0,255,0))
    win.blit(level_text, (160, HEIGHT - level_text.get_height()-7 ))

    time_text = MAIN_FONT.render(
        f"{game_info.get_level_time()}s", 1, (0,255,0))
    win.blit(time_text, (430, HEIGHT - time_text.get_height()-7))

    vel_text = MAIN_FONT.render(f"{round(player_car.vel, 1)}", True, (0,255,0))
    win.blit(vel_text, (732, HEIGHT - vel_text.get_height()-7))

    if game_mode == 0:
        player_car.draw(win)
        computer_car.draw(win)
        pygame.display.update()
    
    elif game_mode == 1:
        player_car.draw(win)
        player_car_2.draw(win)
        pygame.display.update()


def move_players(player_car, player_car_2, game_mode):
    keys = pygame.key.get_pressed()
    moved = False

    # Player 1 Controls (W, A, S, D keys)
    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        player_car.move_forward()
    if keys[pygame.K_s]:
        player_car.move_backward()

    # Player 2 Controls Arrow keys
    if game_mode == 1:
        if keys[pygame.K_LEFT]:
            player_car_2.rotate(left=True)
        if keys[pygame.K_RIGHT]:
            player_car_2.rotate(right=True)
        if keys[pygame.K_UP]:
            player_car_2.move_forward()
        if keys[pygame.K_DOWN]:
            player_car_2.move_backward()


def handle_collision(player_car, player_car_2, computer_car, game_info, game_mode):

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()
    if game_mode == 1 and player_car_2.collide(TRACK_BORDER_MASK) != None:
        player_car_2.bounce()

    # Handle finish line for player 1
    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            if game_mode == 1:
                player_car_2.reset()
                blit_text_center(WIN, MAIN_FONT, "Red won!")
                pygame.display.update()
                pygame.time.wait(3000)
                pygame.quit()
            if game_mode == 0:
                computer_car.next_level(game_info.level)

    # Handle finish line for player 2 in two-player mode
    if game_mode == 1:
        player_2_finish_poi_collide = player_car_2.collide(FINISH_MASK, *FINISH_POSITION)
        if player_2_finish_poi_collide != None:
            if player_2_finish_poi_collide[1] == 0:
                player_car_2.bounce()
            else:
                player_car.reset()
                blit_text_center(WIN, MAIN_FONT, "Green won!")
                pygame.display.update()
                pygame.time.wait(3000)

                # Reset the game state
                game_info.reset()
                player_car.reset()
                player_car_2.reset()
                computer_car.reset()
                # Return to the main menu
                return True
                
    # Handle computer car in single-player mode
    if game_mode == 0:
        computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
        if computer_finish_poi_collide != None:
            blit_text_center(WIN, MAIN_FONT, "You lost!")
            pygame.display.update()
            pygame.time.wait(3000)
            game_info.reset()
            player_car.reset()
            computer_car.reset()
            pygame.quit()


gameloop = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

# Call the start menu and get the selected game mode
game_mode = show_start_menu()
auto_control = game_mode == 0
player_car = PlayerCar(3, 4, RED_CAR, (762, 615))
player_car_2 = PlayerCar(3, 4, player_car_2, (722, 615))  
computer_car = ComputerCar(2, 4, PATH, auto_control)
game_info = GameInfo()  # 0 for "Play against PC", 1 for "Play with Friend"

while gameloop:
    clock.tick(FPS)
    draw(WIN, images, player_car, computer_car, game_info)

    # Handle the level start
    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameloop = False
            break


    if game_mode == 0:  # Play against PC
        move_players(player_car, computer_car, game_mode)
        computer_car.move()
        computer_car.draw(WIN)
        handle_collision(player_car, player_car_2, computer_car, game_info, game_mode)

    if game_mode == 1:  # Play with Friend
        move_players(player_car, player_car_2, game_mode)
        if handle_collision(player_car, player_car_2, computer_car, game_info, game_mode):
            break
        player_car.draw(WIN)
        

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

pygame.quit()


