import pygame
import random
import time

pygame.init()

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
FPS = 500
size = (1500, 800)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
done = False
pygame.display.set_caption('Minesweeper')

def normal_font(size):
    return pygame.font.Font('./font/NotoSansKR-Regular.otf', size)
def pixel_font(size):
    return pygame.font.Font('./font/PressStart2P-Regular.ttf', size)

button_png = pygame.image.load('./img/button.png')

class button():
    def __init__(self, img, center_pos, scale):
        self.center = center_pos
        self.scale = scale
        self.img = pygame.transform.scale(img, scale)

    def print_button(self, str = "", font_size = 30):
        screen.blit(self.img, (self.center[0] - self.scale[0]//2, self.center[1] - self.scale[1]//2))
        if str:
            button_txt = normal_font(font_size).render(str, True, WHITE)
            # pixel = pygame.font.Font('./font/PressStart2P-Regular.ttf', 30)
            # button_txt = pixel.render(str, True, WHITE)
            button_txtRect = button_txt.get_rect()
            button_txtRect.center = self.center
            screen.blit(button_txt, button_txtRect)

    def detect_press(self, cursor_pos):
        if cursor_pos[0] >= self.center[0] - self.scale[0]//2 and cursor_pos[0] < self.center[0] + self.scale[0]//2:
            if cursor_pos[1] >= self.center[1] - self.scale[1]//2 and cursor_pos[1] < self.center[1] + self.scale[1]//2:
                return True
        return False

def play_game(difficulty):
    global done
    playing = True
    first_click = True
    menu_txt_flag = True
    play_time = [0, 0] # 분, 초
    if difficulty == "easy": flag_num = 10
    elif difficulty == "mid": flag_num = 40
    else: flag_num = 99

    if difficulty == "easy":
        board_size = [576, 576]
        block_num = [9, 9, 81]
        block_scale = 64
        num_scale = 25
        mine_num = 10
    elif difficulty == "mid":
        board_size = [576, 576]
        block_num = [16, 16, 256]
        block_scale = 36
        num_scale = 20
        mine_num = 40
    elif difficulty == "hard":
        board_size = [1080, 576]
        block_num = [30, 16, 480]
        block_scale = 36
        num_scale = 20
        mine_num = 99
    board_pos = [750 - board_size[0]//2, 400 - board_size[1]//2]

    block_png = pygame.image.load('./img/block.png')
    flag_png = pygame.image.load('./img/flag.png')
    mine_png = pygame.image.load('./img/mine.png')
    blank1_png = pygame.image.load('./img/blank1.png')
    blank2_png = pygame.image.load('./img/blank2.png')
    blind_png = pygame.image.load('./img/blind.png')
    menu_png = pygame.image.load('./img/menu.png')

    block_img = pygame.transform.scale(block_png, (block_scale, block_scale))
    flag_img = pygame.transform.scale(flag_png, (block_scale, block_scale))
    mine_img = pygame.transform.scale(mine_png, (block_scale, block_scale))
    blank1_img = pygame.transform.scale(blank1_png, (100, 50))
    blank2_img = pygame.transform.scale(blank2_png, (64, 50))
    blind_img = pygame.transform.scale(blind_png, size)
    menu_img = pygame.transform.scale(menu_png, (500, 400))

    pause_png = pygame.image.load('./img/pause.png')
    continue_png = pygame.image.load('./img/continue.png')
    home_png = pygame.image.load('./img/home.png')
    retry_png = pygame.image.load('./img/retry.png')

    pause_button = button(pause_png, (board_pos[0]+board_size[0]-35, board_pos[1]//2), (80, 50))
    continue_button = button(continue_png, (size[0]//2, size[1]//2), (360, 80))
    home_button = button(home_png, (size[0]//2 - 100, size[1]//2 + 100), (160, 80))
    retry_button = button(retry_png, (size[0]//2 + 100, size[1]//2 + 100), (160, 80))

    class block_class():
        def __init__(self, coord):
            self.state = "closed"
            self.coord = coord
            self.close_mine = 0

        def detect_click(self, cursor_pos):
            if cursor_pos[0] >= self.coord[0] and cursor_pos[0] < self.coord[0] + block_scale:
                if cursor_pos[1] >= self.coord[1] and cursor_pos[1] < self.coord[1] + block_scale:
                    return True
            return False

        def print_block(self, playing):
            if self.close_mine == 9:
                screen.blit(mine_img, self.coord)
            if self.state != "opened":
                screen.blit(block_img, self.coord)
            elif self.close_mine != 0 and self.close_mine != 9:
                close_mine_txt = pixel_font(num_scale).render(f'{self.close_mine}', True, WHITE)
                close_mine_txtRect = close_mine_txt.get_rect()
                close_mine_txtRect.center = (self.coord[0] + block_scale//2 + 1, self.coord[1] + block_scale//2 + 2)
                screen.blit(close_mine_txt, close_mine_txtRect)
            if self.state == "flag":
                screen.blit(flag_img, self.coord)
            if (not playing) and (self.close_mine == 9):
                screen.blit(mine_img, self.coord)

    block = []
    x, y = 0, 0
    for i in range(block_num[2]):
        coord = [board_pos[0] + block_scale * x, board_pos[1] + block_scale * y]
        block.append(block_class(coord))
        x += 1
        if x >= block_num[0]:
            x = 0
            y += 1

    def print_img(playing, blind_alpha = 0, play_time = [0, 0], flag_num = 0):
        # 테두리 출력
        pygame.draw.rect(screen, GRAY, (0, 0, size[0], size[1]))
        pygame.draw.rect(screen, BLACK, (board_pos[0]-4, board_pos[1]-4, board_size[0]+9, board_size[1]+9), 5)
        for i in range(block_num[0]):
            pygame.draw.rect(screen, BLACK, (board_pos[0] + block_scale*i, board_pos[1], 2, board_size[1]))
        for i in range(block_num[1]):
            pygame.draw.rect(screen, BLACK, (board_pos[0], board_pos[1] + block_scale*i, board_size[0], 2))
        
        # block, mine, flag 출력
        for i in block:
            i.print_block(playing)

        # 시간
        screen.blit(blank1_img, (board_pos[0]-5, board_pos[1]//2 - 25))
        play_time_txt = '%02d : %02d' %(play_time[0], play_time[1])
        play_time_txt = normal_font(25).render(play_time_txt, True, WHITE)
        play_time_txtRect = play_time_txt.get_rect()
        play_time_txtRect.center = (board_pos[0] + 45, board_pos[1]//2)
        screen.blit(play_time_txt, play_time_txtRect)

        # 남은 깃발 개수
        screen.blit(blank2_img, (size[0]//2 - 32, board_pos[1]//2 - 25))
        flag_txt = normal_font(25).render(f"{flag_num}", True, WHITE)
        flag_txtRect = flag_txt.get_rect()
        flag_txtRect.center = (size[0]//2, board_pos[1]//2)
        screen.blit(flag_txt, flag_txtRect)

        # 일시정지
        pause_button.print_button()
        blind_img.set_alpha(blind_alpha)
        screen.blit(blind_img, (0, 0))
        
    def get_surrounding_block(std_num, include_std = False):
        block_number = []
        check_x = [3, None]
        check_y = [3, None]

        for i in range(block_num[1]):
            if std_num == block_num[0]*i:
                check_x = [2, -1]
            if std_num == block_num[0]*(i+1)-1:
                check_x = [2, 1] #
        for i in range(block_num[0]):
            if std_num == i:
                check_y = [2, -1] #
            if std_num == block_num[2] - (i+1):
                check_y = [2, 1]

        for i in range(3):
            i -= 1
            if i == check_y[1]:
                continue
            for j in range(3):
                j -= 1
                if j == check_x[1]:
                    continue
                if i == 0 and j == 0 and not include_std:
                    continue
                num = std_num + block_num[0]*i + j
                block_number.append(num)
        return block_number

    def assign_mine(clicked_block):
        mine_candi = random.sample(list(range(block_num[2])), mine_num+9)
        for i in get_surrounding_block(clicked_block, True):
            try:
                index = mine_candi.index(i)
                del mine_candi[index]
            except:
                pass
        return random.sample(mine_candi, mine_num)

    def open_block(opened_block):
        block[opened_block].state = "opened"
        if block[opened_block].close_mine != 9:
            for i in get_surrounding_block(opened_block):
                if block[i].state != "flag":
                    if block[i].close_mine == 0 and block[i].state != "opened":
                        open_block(i)
                    else:
                        block[i].state = "opened"

    def left_click(cursor_pos, first_click):
        index = None
        for i in block:
            if i.detect_click(cursor_pos) and i.state != "flag":
                index = block.index(i)
                break
        if type(index) != int:
            return []

        if first_click:
            mine_pos = assign_mine(index)
            for i in mine_pos:
                block[i].close_mine = 9
            for i in block:
                if i.close_mine != 9:
                    close_block = get_surrounding_block(block.index(i))
                    for j in close_block:
                        if block[j].close_mine == 9:
                            i.close_mine += 1
            open_block(index)
            return mine_pos
        
        if block[index].state == "opened":
            surround_flag = 0
            for i in get_surrounding_block(index):
                if block[i].state == "flag":
                    surround_flag += 1
            if surround_flag == block[index].close_mine:
                open_block(index)

        if block[index].state == "closed":
            if block[index].close_mine == 0:
                open_block(index)
            else:
                block[index].state = "opened"

    def right_click(cursor_pos, flag_num):
        for i in block:
            if i.detect_click(cursor_pos):
                if i.state == "closed" and flag_num > 0:
                    i.state = "flag"
                    flag_num -= 1
                elif i.state == "flag":
                    i.state = "closed"
                    flag_num += 1
        return flag_num

    def pause(play_time):
        paused = True

        while paused:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "escape"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cursor_pos = pygame.mouse.get_pos()
                    if continue_button.detect_press(cursor_pos):
                        return "escape"
                    if retry_button.detect_press(cursor_pos):
                        return "retry"
                    if home_button.detect_press(cursor_pos):
                        return "go main"

            print_img(playing, 128, play_time, flag_num)
            screen.blit(menu_img, (size[0]//2 - 250, size[1]//2 - 200))
            continue_button.print_button()
            home_button.print_button()
            retry_button.print_button()

            pause_txt = pixel_font(50).render("PAUSE", True, WHITE)
            pause_txtRect = pause_txt.get_rect()
            pause_txtRect.center = (size[0]//2, size[1]//2 - 120)
            screen.blit(pause_txt, pause_txtRect)

            pygame.display.update()

    while playing:
        clock.tick(FPS)
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                break
            
            if event.type == pygame.KEYDOWN:
                cursor_pos = pygame.mouse.get_pos()
                if event.key == pygame.K_ESCAPE:
                    returned = pause((play_time[0], play_time[1]))
                    if returned == "quit":
                        done = True
                        break
                    elif returned == "retry":
                        return None
                    elif returned == "go main":
                        return "go main"
                if event.key == dig_key:
                    if first_click:
                        mine_pos = left_click(cursor_pos, first_click)
                        if len(mine_pos):
                            first_click = False
                            start_t = time.time()
                    else: left_click(cursor_pos, first_click)

                    if pause_button.detect_press(cursor_pos):
                        returned = pause((play_time[0], play_time[1]))
                        if returned == "quit":
                            done = True
                            break
                        elif returned == "retry":
                            return None
                        elif returned == "go main":
                            return "go main"
                if event.key == flag_key and not first_click:
                    flag_num = right_click(cursor_pos, flag_num)
                if event.key == pygame.K_SPACE and not first_click:
                    for i in block:
                        i.state = "opened"

            if event.type == pygame.MOUSEBUTTONDOWN:
                cursor_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if first_click:
                        mine_pos = left_click(cursor_pos, first_click)
                        if len(mine_pos):
                            first_click = False
                            start_t = time.time()
                    else: left_click(cursor_pos, first_click)

                    if pause_button.detect_press(cursor_pos):
                        returned = pause((play_time[0], play_time[1]))
                        if returned == "quit":
                            done = True
                            break
                        elif returned == "retry":
                            return None
                        elif returned == "go main":
                            return "go main"
                if event.button == 3 and not first_click:
                    flag_num = right_click(cursor_pos, flag_num)
        if done:
            return None

        if not first_click:
            if time.time() - start_t >= 1:
                play_time[1] += 1
                start_t = time.time()
        if play_time[1] >= 60:
            play_time[0] += 1
            play_time[1] = 0

        if not first_click:
            for i in mine_pos:
                if block[i].state == "opened":
                    playing = False
                    result = "lost"

        close_count = 0
        for i in block:
            if i.state == "closed" or i.state == "flag":
                close_count += 1
        if close_count == mine_num:
            playing = False
            result = "won"
        
        print_img(playing, 0, (play_time[0], play_time[1]), flag_num)
        pygame.display.update()

    while not playing:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return None
                if event.key == pygame.K_q:
                    return "go main"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cursor_pos = pygame.mouse.get_pos()
                if retry_button.detect_press(cursor_pos):
                    return "retry"
                if home_button.detect_press(cursor_pos):
                    return "go main"
        if done:
            return None

        print_img(playing, 128, play_time, flag_num)
        screen.blit(menu_img, (size[0]//2 - 250, size[1]//2 - 200))
        home_button.print_button()
        retry_button.print_button()
        if result == "lost":
            result_txt = pixel_font(50).render("YOU LOST", True, WHITE)
            if menu_txt_flag:
                menu_text = random.choice(["It's okay", "Don't give up!", 'You can win next time', 'Oops!'])
                menu_txt_flag = False
        elif result == "won":
            result_txt = pixel_font(50).render("YOU WON", True, WHITE)
            menu_text = f"play time - {play_time[0]} : {play_time[1]}"
        result_txtRect = result_txt.get_rect()
        result_txtRect.center = (size[0]//2, size[1]//2 - 120)
        screen.blit(result_txt, result_txtRect)
        menu_txt = normal_font(30).render(menu_text, True, WHITE)
        menu_txtRect = menu_txt.get_rect()
        menu_txtRect.center = continue_button.center
        screen.blit(menu_txt, menu_txtRect)

        pygame.display.update()


easy_button = button(button_png, (1000, 100), (150, 75))
mid_button = button(button_png, (1000, 200), (150, 75))
hard_button = button(button_png, (1000, 300), (150, 75))
setting_button = button(button_png, (1000, 400), (150, 75))
setting = False
change_flag = False
dig_key = 122
flag_key = 120

while not done:
    clock.tick(FPS)
    screen.fill(GRAY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cursor_pos = pygame.mouse.get_pos()
            if easy_button.detect_press(cursor_pos):
                while not done:
                    if setting: break
                    if play_game("easy") == "go main":
                        break
            elif mid_button.detect_press(cursor_pos):
                while not done:
                    if setting: break
                    if play_game("mid") == "go main":
                        break
            elif hard_button.detect_press(cursor_pos):
                while not done:
                    if setting: break
                    if play_game("hard") == "go main":
                        break
            elif setting_button.detect_press(cursor_pos):
                setting = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            setting = False
    
    easy_button.print_button("easy")
    mid_button.print_button("middle")
    hard_button.print_button("hard")
    setting_button.print_button("setting")

    if setting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    setting = False
                    break
                if not change_flag:
                    dig_key = event.key
                    change_flag = True
                elif change_flag:
                    flag_key = event.key
                    change_flag = False
                    setting = False

    pygame.display.update()

pygame.quit()