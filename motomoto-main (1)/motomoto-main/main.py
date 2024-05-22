import pygame
import sys
import random

# Inicialização do Pygame
pygame.init()

# Definição das constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GROUND_HEIGHT = 100
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Carregamento das imagens
background_image = pygame.image.load("background.png")
ground_image = pygame.image.load("ground.png")
player_image = pygame.image.load("mario.png")
player_image = pygame.transform.scale(player_image, (50, 50))  # Redimensionar a imagem do jogador
coin_image = pygame.image.load("coin.png")
coin_image = pygame.transform.scale(coin_image, (30, 30))  # Redimensionar a imagem da moeda

# Carregamento dos sons
jump_sound = pygame.mixer.Sound("jump.wav")
coin_sound = pygame.mixer.Sound("coin.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")

# Música de fundo
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)  # Definir o volume da música
pygame.mixer.music.play(-1)  # Reproduzir a música em loop

# Classe para representar o jogador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - GROUND_HEIGHT - 50)
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = 0.5
        self.jump_power = -12
        self.jump_duration = 0
        self.jump_max_duration = 15
        self.on_ground = False

    def update(self):
        self.handle_movement()
        self.apply_gravity()

    def handle_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        elif keys[pygame.K_RIGHT]:
            self.speed_x = 5
        else:
            self.speed_x = 0

        self.rect.x += self.speed_x

    def apply_gravity(self):
        if not self.on_ground:
            self.speed_y += self.gravity
            self.rect.y += self.speed_y

        if self.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
            self.on_ground = True
            self.speed_y = 0
            self.jump_duration = 0

    def jump(self):
        if self.on_ground:
            self.speed_y = self.jump_power
            self.on_ground = False
            jump_sound.play()  # Reproduzir efeito sonoro de pulo

# Classe para representar as moedas
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_image
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(100, SCREEN_WIDTH - 100), random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - GROUND_HEIGHT - 100))

    def update(self):
        pass

# Classe para representar os obstáculos
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, speed):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

# Função para desenhar o texto na tela
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# Função para rodar o jogo
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros")
    clock = pygame.time.Clock()

    # Criando os grupos de sprites
    all_sprites = pygame.sprite.Group()
    players = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    coins = pygame.sprite.Group()

    # Criando o jogador
    player = Player()
    all_sprites.add(player)
    players.add(player)

    # Definindo variáveis do jogo
    current_level = 1
    score = 0
    speed_increase_interval = 2000  # Aumenta a velocidade dos obstáculos a cada 2 segundos
    speed_increase_timer = 0
    obstacle_speed = 4

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        # Lógica do jogo
        all_sprites.update()

        # Aumentar a velocidade dos obstáculos com o tempo
        speed_increase_timer += clock.get_rawtime()
        if speed_increase_timer >= speed_increase_interval:
            obstacle_speed += 1
            speed_increase_timer = 0

        # Criar obstáculos e moedas de acordo com o nível atual
        if current_level == 1:
            if len(obstacles) < 3:
                obstacle = Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - 50, 50, 50, GREEN, obstacle_speed)
                all_sprites.add(obstacle)
                obstacles.add(obstacle)

            if len(coins) == 0 and random.randint(0, 100) < 20:  # 20% de chance de criar uma moeda
                coin = Coin()
                all_sprites.add(coin)
                coins.add(coin)
        elif current_level == 2:
            if len(obstacles) < 5:
                obstacle = Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - 50, 50, 50, GREEN, obstacle_speed)
                all_sprites.add(obstacle)
                obstacles.add(obstacle)

            if len(coins) < 2 and random.randint(0, 100) < 20:  # 20% de chance de criar uma moeda
                coin = Coin()
                all_sprites.add(coin)
                coins.add(coin)

        # Verificar colisões entre o jogador e as moedas
        coin_collisions = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_collisions:
            coin_sound.play()  # Reproduzir efeito sonoro de coleta de moeda
            score += 1

        # Verificar colisões entre o jogador e os obstáculos
        if pygame.sprite.spritecollide(player, obstacles, False):
            game_over_sound.play()  # Reproduzir efeito sonoro de fim de jogo
            running = False

        # Remover obstáculos que saíram da tela
        for obstacle in obstacles.copy():
            if obstacle.rect.right <= 0:
                obstacles.remove(obstacle)
                all_sprites.remove(obstacle)

        # Renderização
        screen.fill(WHITE)
        screen.blit(background_image, (0, 0))
        screen.blit(ground_image, (0, SCREEN_HEIGHT - GROUND_HEIGHT))

        all_sprites.draw(screen)

        draw_text(f"Score: {score}", pygame.font.Font(None, 36), RED, screen, 10, 10)

        pygame.display.flip()
        clock.tick(FPS)

        # Verificar se o jogador alcançou o fim da fase
        if current_level == 1 and player.rect.right >= SCREEN_WIDTH:
            current_level = 2
            # Reiniciar posição do jogador para a segunda fase
            player.rect.center = (100, SCREEN_HEIGHT - GROUND_HEIGHT - 50)
            # Remover todos os obstáculos e moedas da primeira fase
            obstacles.empty()
            coins.empty()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
