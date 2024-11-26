import pygame
import random
import sys
import time
import json
import os

# Inicializar o pygame
pygame.init()

# Configurações principais
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
GRID_SIZE = 13
BLOCK_SIZE = 60
COLORS = {
    "Azul": (0, 0, 255),
    "Ciano": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Amarelo": (255, 255, 0),
    "Laranja": (255, 165, 0),
    "Vermelho": (255, 0, 0),
    "Roxo": (128, 0, 128),
    "Verde": (0, 255, 0),
}
HIGH_SCORE_FILE = "high_score.json"

# Funções auxiliares
def carregar_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            data = json.load(file)
            return data.get("high_score", 0)
    else:
        return 0

def salvar_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as file:
        json.dump({"high_score": score}, file)

def gerar_grade():
    return [[random.choice(list(COLORS.keys())) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def desenhar_grade(screen, grid):
    for y, row in enumerate(grid):
        for x, color_name in enumerate(row):
            color = COLORS[color_name]
            pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, (0, 0, 0), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def encontrar_combinacoes(grid):
    combinacoes = []
    # Horizontal
    for y in range(GRID_SIZE):
        count = 1
        for x in range(1, GRID_SIZE):
            if grid[y][x] == grid[y][x - 1]:
                count += 1
            else:
                if count >= 3:
                    combinacoes.append([(y, x - i - 1) for i in range(count)])
                count = 1
        if count >= 3:
            combinacoes.append([(y, GRID_SIZE - i - 1) for i in range(count)])
    # Vertical
    for x in range(GRID_SIZE):
        count = 1
        for y in range(1, GRID_SIZE):
            if grid[y][x] == grid[y - 1][x]:
                count += 1
            else:
                if count >= 3:
                    combinacoes.append([(y - i - 1, x) for i in range(count)])
                count = 1
        if count >= 3:
            combinacoes.append([(GRID_SIZE - i - 1, x) for i in range(count)])
    return combinacoes

def remover_combinacoes(grid, combinacoes):
    for combinacao in combinacoes:
        for y, x in combinacao:
            grid[y][x] = None
    for x in range(GRID_SIZE):
        coluna = [grid[y][x] for y in range(GRID_SIZE) if grid[y][x] is not None]
        coluna = [None] * (GRID_SIZE - len(coluna)) + coluna
        for y in range(GRID_SIZE):
            grid[y][x] = coluna[y]

def trocar_blocos(grid, pos1, pos2):
    y1, x1 = pos1
    y2, x2 = pos2
    grid[y1][x1], grid[y2][x2] = grid[y2][x2], grid[y1][x1]

def posicao_clicada(mouse_pos):
    x, y = mouse_pos
    return y // BLOCK_SIZE, x // BLOCK_SIZE

# Configuração inicial do jogo
# Atualizar a altura da tela
SCREEN_HEIGHT = GRID_SIZE * BLOCK_SIZE + 100  # Incremento para acomodar os textos
screen = pygame.display.set_mode((GRID_SIZE * BLOCK_SIZE, SCREEN_HEIGHT))
pygame.display.set_caption("Block Puzzle")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Estado do jogo
grade = gerar_grade()
pontos = 0
pontos_totais = 0
nivel = 1
tempo_restante = 150
ultimo_tempo = time.time()
high_score = carregar_high_score()
selecionado = None

# Loop principal
while True:
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = posicao_clicada(pygame.mouse.get_pos())
            if selecionado is None:
                selecionado = pos
            else:
                if abs(selecionado[0] - pos[0]) + abs(selecionado[1] - pos[1]) == 1:  # Checar se são adjacentes
                    trocar_blocos(grade, selecionado, pos)
                    if not encontrar_combinacoes(grade):  # Reverter se não houver combinações
                        trocar_blocos(grade, selecionado, pos)
                    else:
                        selecionado = None
                else:
                    selecionado = pos

    # Atualizar tempo
    tempo_atual = time.time()
    tempo_restante -= tempo_atual - ultimo_tempo
    ultimo_tempo = tempo_atual

    # Encontrar e remover combinações
    combinacoes = encontrar_combinacoes(grade)
    if combinacoes:
        pontos += sum(len(c) for c in combinacoes)
        pontos_totais += sum(len(c) for c in combinacoes)
        remover_combinacoes(grade, combinacoes)
        grade = [[random.choice(list(COLORS.keys())) if cell is None else cell for cell in row] for row in grade]

    # Verificar condições de vitória ou derrota
    if pontos >= 100:  # Passar para o próximo nível
        nivel += 1
        pontos = 0
        tempo_restante = 150
        grade = gerar_grade()
    elif tempo_restante <= 0:  # Fim de jogo
        if pontos_totais > high_score:
            high_score = pontos_totais
            salvar_high_score(high_score)
        screen.fill((0, 0, 0))
        texto_game_over = font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(texto_game_over, (SCREEN_WIDTH // 2 - texto_game_over.get_width() // 0.53, SCREEN_HEIGHT // 2 - 20))
        texto_high_score = font.render(f"High Score: {high_score}", True, (255, 255, 255))
        screen.blit(texto_high_score, (SCREEN_WIDTH // 2 - texto_high_score.get_width() // 0.60, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    # Renderizar
    screen.fill((0, 0, 0))
    desenhar_grade(screen, grade)

    # Renderizar textos
    texto_pontos = font.render(f"Pontos: {pontos}", True, (255, 255, 255))
    texto_nivel = font.render(f"Nível: {nivel}", True, (255, 255, 255))
    texto_tempo = font.render(f"Tempo: {int(tempo_restante)}", True, (255, 255, 255))
    texto_pontos_totais = font.render(f"Pontos Totais: {pontos_totais}", True, (255, 255, 255))
    texto_high_score = font.render(f"High Score: {high_score}", True, (255, 255, 255))

    # Primeira linha de informações (topo)
    screen.blit(texto_pontos, (10, GRID_SIZE * BLOCK_SIZE + 10))
    screen.blit(texto_nivel, (350, GRID_SIZE * BLOCK_SIZE + 10))
    screen.blit(texto_tempo, (625, GRID_SIZE * BLOCK_SIZE + 10))

    # Segunda linha de informações (abaixo)
    screen.blit(texto_pontos_totais, (10, GRID_SIZE * BLOCK_SIZE + 40))
    screen.blit(texto_high_score, (500, GRID_SIZE * BLOCK_SIZE + 40))

    pygame.display.flip()
    clock.tick(30)
