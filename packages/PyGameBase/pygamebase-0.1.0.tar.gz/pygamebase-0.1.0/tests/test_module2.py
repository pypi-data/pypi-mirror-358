import pygame

# Inicializa o Pygame
pygame.init()

# Define o tamanho inicial da janela
largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura), pygame.RESIZABLE)
pygame.display.set_caption("Janela Redimensionável")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

# Loop principal
executando = True
while executando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type == pygame.VIDEORESIZE:
            # Atualiza o tamanho da janela quando redimensionada pelo usuário
            largura, altura = evento.w, evento.h
            tela = pygame.display.set_mode((largura, altura), pygame.RESIZABLE)
    
    # Preenche a tela com preto
    tela.fill(PRETO)
    
    # Desenha um retângulo branco centralizado
    pygame.draw.rect(tela, BRANCO, (largura // 2 - 50, altura // 2 - 50, 100, 100))
    
    # Atualiza a tela
    pygame.display.flip()

# Encerra o Pygame
pygame.quit()
