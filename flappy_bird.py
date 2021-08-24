import pygame
from pygame.locals import *
from random import randint
import os

def load_image(path, image):
    img = os.path.join(path, image)
    return pygame.image.load(img)

def pick_background(path:str, choice:int): #select the background image based on choice index
    backgrounds = [file for file in os.listdir(path) if file.startswith("background")]
    return load_image(path, backgrounds[choice])

def load_flap_animation(bird_images, frame_durations):
    global flap_animation
    flap_animation = list(zip(bird_images,frame_durations))

def check_frame(frame, flap_animation):
    if frame < flap_animation[0][1]:
        return flap_animation[0][0]
    elif frame - flap_animation[0][1] < flap_animation[1][1]:
        return flap_animation[1][0]
    else: 
        return flap_animation[2][0]
def pick_bird(path:str, colour:str):
    bird_images = [file for file in os.listdir(path) if file.startswith(colour)]
    return bird_images

def pick_pipe(path:str):
    pipe_images = [file for file in os.listdir(path) if file.startswith("pipe")]
    return os.path.join(path, pipe_images[randint(0,1)])

def check_boundary(bird):
    if bird.rect.top <= 0:
        bird.rect.top = 0

def checkcollision(bird, base, pipes):
    for pipe in pipes:
        if pipe.colliderect(bird.collide_rect):
            bird.hit_sound.play()
            bird.death_sound.play()
            bird.momentum = 0
            bird.shake = 20
            return 2
    if base.colliderect(bird.collide_rect):
        bird.shake = 10
        bird.momentum = 0
        return 2
     
    else:
        return 1
def generate_pipes(pipe, width, display_size):
    pipes = []
    for i in range(1,7):
        if i == 5:
            break
        else:
            pipe_height = int(round((display_size/7)*(i+1))) -60
            other_pipe_height = int(round(display_size - pipe_height - 150 ))
            new_pipe = pygame.transform.scale(pipe,(width,pipe_height))
            other_pipe = pygame.transform.scale(pipe,(width,other_pipe_height))
            other_pipe = pygame.transform.flip(other_pipe, False, True)
            pipes.append((new_pipe, other_pipe))
    return pipes

def render_pipes(pipes, scroll, distance = 1):
    length = len(pipes)
    index = randint(0,length-1)
    rendered_pipes = pipes[index]
    pipe_rects = tuple([pipe.get_rect() for pipe in rendered_pipes])
    pipe_rects[0].x = scroll + round(display_size[0]*distance)
    pipe_rects[1].x = scroll + round(display_size[0]*distance)
    pipe_rects[0].bottom = display_size[1] - 60
    pipe_rects[1].top = 0
    return list(zip(rendered_pipes, pipe_rects))

def generate_score_rect(pipe_rects):
    score_rects = []
    for item in pipe_rects:
        score_rect = pygame.Rect.copy(item[0][1])
        score_rects.append(score_rect)
    return score_rects

def check_score(score_rects, bird, scroll):
    points = 0
    if bird.rect.x > score_rects[0].x:
        score_rects.pop(0)
        bird.point_sound.play()
        points = 1
    else:
        for score in score_rects:
            score.x -= scroll
    return score_rects, points

def generate_score_dict(sprite_path):
    score_dict = {}
    for i in range(10):
        path = os.path.join(sprite_path, str(i)+".png")
        score_dict[str(i)] = pygame.image.load(path)
    return score_dict

def display_score(score_dict, score):
    string_score = str(score)
    surfaces = []
    rects = []
    for number in string_score:
        surface = score_dict[number]
        rect = surface.get_rect()
        surfaces.append(surface)
        rects.append(rect)
    return list(zip(surfaces, rects))


class Bird():
    def __init__(self, colour):
        self.path = sprites_path
        self.colour = colour
        self.images = pick_bird(self.path, self.colour)
        initial_image = os.path.join(self.path,self.images[1])
        self.original_img = pygame.image.load(initial_image)
        self.image = self.original_img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = int((display_size[0]/2)-20), int(display_size[1]/2)
        self.collide_rect = pygame.Rect((0, 0), (30, 20))
        self.collide_rect.center = self.rect.center
        self.momentum = 0.2
        self.flap_sound = pygame.mixer.Sound(audio_path+ r"\wing.wav")
        self.flap_sound.set_volume(0.5)
        self.death_sound = pygame.mixer.Sound(audio_path + r"\die.wav")
        self.hit_sound = pygame.mixer.Sound(audio_path + r"\hit.wav")
        self.hit_sound.set_volume(0.5)
        self.swoosh_sound = pygame.mixer.Sound(audio_path + r"\swoosh.wav")
        self.point_sound = pygame.mixer.Sound(audio_path + r"\point.wav")
        self.point_sound.set_volume(0.5)
        self.frame = 0
        self.angle = 0
        self.shake = 0
    
    def flap(self):
        self.momentum = -4
        self.flap_sound.play()

    def gravity(self):
        self.rect.y += self.momentum
        self.momentum += 0.22
        if self.momentum >= 12:
            self.momentum = 12
    
    def check_frame(self, flap_animation):
        if self.frame < flap_animation[0][1]:
            return flap_animation[0][0]
        elif self.frame - flap_animation[0][1] < flap_animation[1][1]:
            return flap_animation[1][0]
        else:
            self.frame = 0 
            return flap_animation[2][0]
    
    def rotate(self, direction):
        if direction == 'Back':
            self.angle += 5 % 360
            if self.angle >= 20:
                self.angle = 20
            rotated_image = pygame.transform.rotate(self.original_img, self.angle)
            self.image = rotated_image
            x, y = self.rect.center
            self.rect = self.image.get_rect()  # Replace old rect with new rect.
            self.rect.center = (x, y)  # Put the new rect's center at old center.
            self.collide_rect.center = self.rect.center
        else:
            self.angle -= 5 % 360
            if self.angle <= -80:
                self.angle = -80
            rotated_image = pygame.transform.rotate(self.original_img, self.angle)
            self.image = rotated_image
            x, y = self.rect.center
            self.rect = self.image.get_rect()  # Replace old rect with new rect.
            self.rect.center = (x, y)  # Put the new rect's center at old center
            self.collide_rect.center = self.rect.center
def run(screen, window_size, display, clock, background, base_data, pipes, bird, old_score):
    scroll = 0
    rendered_pipes = []
    pipe_pairs = render_pipes(pipes, scroll, 2)
    rendered_pipes.append(pipe_pairs)
    pipe_pairs = render_pipes(pipes, scroll, 2.7)
    rendered_pipes.append(pipe_pairs)
    score_rects = generate_score_rect(rendered_pipes)
    score = 0
    frame = 0
    navigation = 1
    buffer_period = 0
    alpha = 255
    flap = False
    death = True
    score_dict = generate_score_dict(sprites_path)
    load_flap_animation(bird.images, [8,8,8])
    while True:
        if navigation == 1:
            scroll = 2
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    bird.flap()
                    flap = True
                    frame = 0
                    bird.frame = 0
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            exit()
                        if event.key == pygame.K_SPACE:
                            bird.flap()
                            flap = True
                            frame = 0
                            bird.frame = 0
            if flap == True:
                bird.frame += 1
                frame += 1
                flap_img = bird.check_frame(flap_animation)
                bird.original_img = load_image(sprites_path, flap_img)
                bird.rotate('Back')
                if frame > (flap_animation[0][1] + flap_animation[1][1] + flap_animation[2][1]) + 10:
                    frame = 0
                    bird.frame = 0
                    flap = False
            else:
                bird.original_img = load_image(sprites_path, flap_animation[1][0])
                bird.rotate('forward')
            if rendered_pipes[0][0][1].x  < -50:
                rendered_pipes.pop(0)
                pipe_pairs = render_pipes(pipes, scroll, 1.3)
                rendered_pipes.append(pipe_pairs)
                score_rects = generate_score_rect(rendered_pipes)
            score_rects, add_score = check_score(score_rects, bird, scroll)
            score += add_score
            score_list = display_score(score_dict, score)
            relative_lower_pipe_pos1 = ((rendered_pipes[0][0][1].x ), rendered_pipes[0][0][1].y)
            relative_higher_pipe_pos1 = ((rendered_pipes[0][1][1].x ), rendered_pipes[0][1][1].y)
            relative_lower_pipe_pos2 = ((rendered_pipes[1][0][1].x ), rendered_pipes[1][0][1].y)
            relative_higher_pipe_pos2 = ((rendered_pipes[1][1][1].x), rendered_pipes[1][1][1].y)
            rendered_pipes[0][0][1].x -= scroll
            rendered_pipes[0][1][1].x -= scroll
            rendered_pipes[1][0][1].x -= scroll
            rendered_pipes[1][1][1].x -= scroll
            relative_pipe_rects = [rendered_pipes[0][0][1], rendered_pipes[0][1][1], rendered_pipes[1][0][1], rendered_pipes[1][1][1]]
            navigation = checkcollision(bird, base_data[1], relative_pipe_rects)
            check_boundary(bird)
            display.blit(background,(0,0))
            display.blit(*base_data)
            display.blit(bird.image, bird.rect)
            display.blit(rendered_pipes[0][0][0], relative_lower_pipe_pos1)
            display.blit(rendered_pipes[0][1][0], relative_higher_pipe_pos1)
            display.blit(rendered_pipes[1][0][0], relative_lower_pipe_pos2)
            display.blit(rendered_pipes[1][1][0], relative_higher_pipe_pos2)
            for i in range(len(score_list)):
                score_list[i][1].center = (((display_size[0]/2) + i*24 - 6*len(score_list)), 20)
                display.blit(score_list[i][0], score_list[i][1])
            bird.gravity()
            screen.blit(pygame.transform.scale(display,window_size),(0,0))
            pygame.display.update()
            clock.tick(60)

        elif navigation == 2:
            highscore = max(old_score, score)
            game_over = pygame.image.load(os.path.join(sprites_path,"gameover.png"))
            game_over_rect = game_over.get_rect()
            game_over_rect.center = (round(display_size[0]/2),round(display_size[1]*1/4))
            font = pygame.font.SysFont('Tahoma', 25, True, False)
            highscore_msg = font.render(f'Highscore is {highscore}', True, (255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if score>old_score:
                        with open(r'C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\Highscore\score.txt', 'w') as f:
                            f.write(str(score))
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if score>old_score:
                                with open(r'C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\Highscore\score.txt', 'w') as f:
                                    f.write(str(score))
                            pygame.quit()
                            exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buffer_period == 1:
                        if score>old_score:
                            with open(r'C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\Highscore\score.txt', 'w') as f:
                                f.write(str(score))
                        main()
            display.blit(background,(0,0))
            display.blit(*base_data)
            display.blit(rendered_pipes[0][0][0], (rendered_pipes[0][0][1].x , rendered_pipes[0][0][1].y))
            display.blit(rendered_pipes[0][1][0], (rendered_pipes[0][1][1].x , rendered_pipes[0][1][1].y))
            display.blit(rendered_pipes[1][0][0], (rendered_pipes[1][0][1].x, rendered_pipes[1][0][1].y))
            display.blit(rendered_pipes[1][1][0], (rendered_pipes[1][1][1].x, rendered_pipes[1][1][1].y))
            display.blit(bird.image, bird.rect)
            white_flash = pygame.Surface(display_size)
            white_flash.fill((255,255,255))
            white_flash.set_alpha(alpha)
            display.blit(white_flash, (0,0))
            alpha -= 5
            bird.gravity()
            bird.rotate('forward')
            if base_data[1].colliderect(bird.collide_rect):
                bird.momentum = 0
                display.blit(game_over, game_over_rect)
                display.blit(highscore_msg, (50,round(display_size[1]*3/7)))
                buffer_period = 1
            if death:
                if bird.rect.bottom > base_data[1].top:
                    bird.swoosh_sound.play()
                    death = False
            if bird.shake >0 :
                bird.shake -= 1
            render_offset = [0,0]
            if bird.shake:
                render_offset[0] = randint(0,8) - 4
                render_offset[1] = randint(0,8) - 4
            screen.blit(pygame.transform.scale(display,window_size),render_offset)
            pygame.display.update()
            clock.tick(60)


def main():
    global window_size, display_size, audio_path, sprites_path
    pygame.init()
    window_size = (576,1024)
    display_size = (288,512)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Flappy bird')
    clock = pygame.time.Clock()
    display = pygame.Surface(display_size)
    sprites_path = r"C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\sprites"
    audio_path = r"C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\audio"
    gameIcon = pygame.image.load(os.path.join(r"C:\Users\Kayse\Games\FlappyBird","favicon.ico"))
    pygame.display.set_icon(gameIcon)
    colours = ["red","yellow","blue"]
    bird = Bird(colours[randint(0,2)])
    background = pick_background(sprites_path, randint(0,1))
    base = load_image(sprites_path, "base.png")
    base_rect = base.get_rect(topleft = (0,(display_size[1]-60)))
    base_data = (base, base_rect)
    pipe = pygame.image.load(pick_pipe(sprites_path))
    pipes = generate_pipes(pipe, 52, display_size[1])
    if len(os.listdir(r"C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\Highscore")) == 0:
        old_score = 0
        with open(r'C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\Highscore\score.txt', 'w') as f:
            f.write(str(old_score))
    else:
        with open(r'C:\Users\Kayse\Games\FlappyBird\flappy-bird-assets\Highscore\score.txt', 'r') as f:
            old_score = f.read()
            old_score = int(old_score)
    run(screen, window_size, display, clock, background, base_data, pipes, bird, old_score)

if __name__ == "__main__":
    main()