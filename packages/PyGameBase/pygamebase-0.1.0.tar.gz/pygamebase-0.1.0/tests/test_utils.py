import pygame
import sys

pygame.init()

# Configurações da tela
tela = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Botão 3D no Pygame")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA_CLARO = (200, 200, 200)
CINZA_ESCURO = (100, 100, 100)
VERDE = (0, 200, 0)

# Função para desenhar o botão 3D
def desenhar_botao(tela, x, y, largura, altura, texto, pressionado):
    if pressionado:
        # Bordas para dar efeito de profundidade
        pygame.draw.rect(tela, CINZA_ESCURO, (x, y, largura, altura))
        pygame.draw.rect(tela, VERDE, (x + 4, y + 4, largura - 4, altura - 4))
    else:
        pygame.draw.rect(tela, BRANCO, (x, y, largura, altura))
        pygame.draw.rect(tela, CINZA_CLARO, (x + 4, y + 4, largura - 4, altura - 4))

    # Desenhar o texto
    fonte = pygame.font.SysFont(None, 36)
    texto_renderizado = fonte.render(texto, True, PRETO)
    texto_ret = texto_renderizado.get_rect(center=(x + largura // 2, y + altura // 2))
    tela.blit(texto_renderizado, texto_ret)

# Loop principal
rodando = True
while rodando:
    pressionado = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if 150 <= evento.pos[0] <= 350 and 150 <= evento.pos[1] <= 220:
                    pressionado = True

    tela.fill(PRETO)

    # Desenhar botão
    desenhar_botao(tela, 150, 150, 200, 70, "Clique Aqui", pressionado)

    pygame.display.flip()
