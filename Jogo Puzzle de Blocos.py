import pygame
import random
import sys
import json

# Configurações básicas
pygame.init()
WIDTH, HEIGHT = 600, 680
BLOCK_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE - 2
FONT = pygame.font.SysFont(None, 36)

# Cores disponíveis para os blocos
COLORS = ["blue", "green", "pink", "red", "cyan", "yellow", "magenta", "orange", "purple"]

# Tela do jogo e configurações de pontuação
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puzzle de Blocos")
clock = pygame.time.Clock()
score = 0
game_over = False
high_score = 0

# Caminho do arquivo para armazenar o high score
high_score_file = "high_score.json"

# Função para carregar o highscore do arquivo JSON
def load_high_score():
    global high_score
    try:
        with open(high_score_file, "r") as f:
            data = json.load(f)
            high_score = data.get("high_score", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        high_score = 0

# Função para salvar o highscore no arquivo JSON
def save_high_score():
    global high_score
    with open(high_score_file, "w") as f:
        json.dump({"high_score": high_score}, f)

# Função para gerar uma grade de blocos com cores aleatórias
def create_grid():
    grid = []
    for y in range(GRID_HEIGHT):
        row = []
        for x in range(GRID_WIDTH):
            color = random.choice(COLORS)
            row.append(color)
        grid.append(row)
    return grid

# Função para desenhar a grade na tela
def draw_grid(grid):
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(screen, pygame.Color(color), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, pygame.Color("black"), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

# Função para encontrar blocos adjacentes da mesma cor
def get_adjacent_blocks(x, y, color, grid, visited=None):
    if visited is None:
        visited = set()
    if (x, y) in visited or x < 0 or y < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or grid[y][x] != color:
        return visited
    visited.add((x, y))
    get_adjacent_blocks(x + 1, y, color, grid, visited)
    get_adjacent_blocks(x - 1, y, color, grid, visited)
    get_adjacent_blocks(x, y + 1, color, grid, visited)
    get_adjacent_blocks(x, y - 1, color, grid, visited)
    return visited

# Função para remover blocos combinados e marcar pontuação
def remove_blocks(blocks, grid):
    global score
    if len(blocks) >= 2:
        score += len(blocks)
        for x, y in blocks:
            grid[y][x] = None

# Função para aplicar gravidade na grade (blocos caem para baixo)
def apply_gravity(grid):
    for x in range(GRID_WIDTH):
        column = [grid[y][x] for y in range(GRID_HEIGHT) if grid[y][x] is not None]
        for y in range(GRID_HEIGHT - len(column)):
            grid[y][x] = None
        for y, color in enumerate(column):
            grid[GRID_HEIGHT - len(column) + y][x] = color

# Função para verificar se todos os blocos foram eliminados
def check_grid_empty(grid):
    for row in grid:
        if any(row):
            return False
    return True

# Função para verificar se há movimentos válidos disponíveis
def check_possible_moves(grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = grid[y][x]
            if color:
                # Checa movimentos adjacentes para combinações
                if x + 1 < GRID_WIDTH and grid[y][x + 1] == color:
                    return True
                if y + 1 < GRID_HEIGHT and grid[y + 1][x] == color:
                    return True
    return False

# Função principal do jogo
def main():
    global score, high_score, game_over
    grid = create_grid()
    dragging = False
    selected_block = None
    load_high_score()  # Carrega o high score ao iniciar o jogo

    while True:
        screen.fill((255, 255, 255))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()  # Salva o high score ao sair do jogo
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mx, my = pygame.mouse.get_pos()
                bx, by = mx // BLOCK_SIZE, my // BLOCK_SIZE
                if bx < GRID_WIDTH and by < GRID_HEIGHT and grid[by][bx]:
                    selected_block = (bx, by)
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                if selected_block:
                    # Pega a posição final do arraste
                    mx, my = pygame.mouse.get_pos()
                    ex, ey = mx // BLOCK_SIZE, my // BLOCK_SIZE
                    bx, by = selected_block
                    # Se for adjacente ao bloco selecionado, tenta trocar e verificar combinação
                    if abs(ex - bx) + abs(ey - by) == 1 and ex < GRID_WIDTH and ey < GRID_HEIGHT:
                        # Realiza a troca temporária
                        grid[ey][ex], grid[by][bx] = grid[by][bx], grid[ey][ex]
                        color = grid[ey][ex]
                        blocks_to_remove = get_adjacent_blocks(ex, ey, color, grid)
                        if len(blocks_to_remove) >= 2:
                            remove_blocks(blocks_to_remove, grid)
                            apply_gravity(grid)
                            # Verifica se todos os blocos foram eliminados e reinicia a grade
                            if check_grid_empty(grid):
                                # Atualiza o high score se a pontuação atual for maior
                                high_score = max(high_score, score)
                                score = 0
                                grid = create_grid()
                        else:
                            # Reverte a troca se não houver combinação
                            grid[ey][ex], grid[by][bx] = grid[by][bx], grid[ey][ex]
                    dragging = False
                    selected_block = None

                    # Verifica se o jogo terminou
                    if not check_possible_moves(grid):
                        # Atualiza o high score antes de finalizar o jogo
                        high_score = max(high_score, score)
                        game_over = True

        # Desenha a grade e pontuação
        draw_grid(grid)
        score_text = FONT.render(f"Score: {score}", True, (0, 0, 0))
        high_score_text = FONT.render(f"High Score: {high_score}", True, (0, 0, 0))
        screen.blit(score_text, (10, HEIGHT - 70))
        screen.blit(high_score_text, (10, HEIGHT - 40))

        # Exibe mensagem de fim de jogo se não houver mais movimentos
        if game_over:
            game_over_text = FONT.render("Fim de Jogo! Sem movimentos possíveis.", True, (255, 0, 0))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
