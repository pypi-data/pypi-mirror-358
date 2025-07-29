#modulos
import pygame
import os
import sys
#inicialização de modulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #se o pacote não estiver funcionando
from PyGameBase import desing as ds
pygame.init()
#variaveis Grobais
close_control = ds.Close()
screen_loop = ds.Screen_loop("main", close_control)
#classe principal
class Game:
    def __init__(self):
        pass
  
#chamando a classe
game = Game()
screen_loop.initiation(scene=1,scenes=[])
pygame.quit()