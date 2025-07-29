# no PyGameBase/cli.py

import sys

def main():
    if len(sys.argv) < 2:
        print("Uso: pygamebase nome_do_projeto")
        sys.exit(1)
    nome = sys.argv[1]
    criar_projeto(nome)

def criar_projeto(nome):
    import os
    TEMPLATE = '''\
#modulos
from PyGameBase import desing as ds
import pygame
pygame.init()
#variaveis Grobais
close_control = ds.Close()
screen_loop = ds.Screen_loop("main", close_control)
#classe principal
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800,600),pygame.RESIZABLE)
        self.cena = 0
    def test1(self):
        for event in pygame.event.get():
            close_control.check(event)

        screen_loop.add_cena(screen=self.screen, bg_color=ds.Colors.LIGHT_GRAY, elements=[])
        pygame.time.Clock().tick(60)
        return True,self.cena
  
#chamando a classe
game = Game()
screen_loop.initiation(scene=0,scenes=[game.test1])
pygame.quit()
'''
    os.makedirs(nome, exist_ok=True)
    with open(os.path.join(nome, 'main.py'), 'w', encoding='utf-8') as f:
        f.write(TEMPLATE)
    print(f"Projeto criado em: {nome}/main.py")

if __name__ == "__main__":
    main()
