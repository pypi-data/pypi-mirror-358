import pygame
import os
import json
class Desable:
    def __init__(self,up=True,down=True,left=True,right=True):
        self.UP = up
        self.DOWN = down
        self.LEFT = left
        self.RIGHT = right
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    LIGHT_GRAY = (211, 211, 211)
    LIGHT_BLUE = (173, 216, 230)
    LIGHT_GREEN = (144, 238, 144)
    LIGHT_YELLOW = (255, 255, 224)
    LIGHT_PINK = (255, 182, 193)
    DARK_GRAY = (169, 169, 169)
    DARK_BLUE = (0, 0, 139)
    DARK_GREEN = (0, 100, 0)
    DARK_RED = (139, 0, 0)
    DARK_PURPLE = (75, 0, 130)
    BROWN = (139, 69, 19)
    SADDLEBROWN = (139, 34, 82)
    SADDLE_BROWN = (139, 69, 19)
    BEIGE = (245, 245, 220)
    WHEAT = (245, 222, 179)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    BRONZE = (205, 127, 50)
    VIOLET = (238, 130, 238)
    TURQUOISE = (64, 224, 208)
    CORAL = (255, 127, 80)
    SEASHELL = (255, 245, 238)
    GRAY = (169, 169, 169)  
class Screen_image:
    def __init__(self,image,screen):
     self.imagem = pygame.image.load(image)
     self.imagem = pygame.transform.scale(self.imagem, (screen.get_width(),screen.get_height()))
    def add_elements(self,tela):
        tela.blit(self.imagem,(0,0))
class Text_box:
    def __init__(self,screen,text, position_x=0, position_y=0, width=150, height=50, 
                 atived_color=Colors.BLUE, desatived_color=Colors.BLACK, 
                 text_color=Colors.BLACK, modelpy=None, sizepy=30, italicpy=False, 
                 boldpy=False, strikethrough=False, Underlinedpy=False):

        self.text = text
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.color = [atived_color, desatived_color]
        self.text_color = text_color
        self.modelpy = modelpy
        self.sizepy = sizepy
        self.italicpy = italicpy
        self.boldpy = boldpy
        self.strikethrough = strikethrough
        self.Underlinedpy = Underlinedpy
        self.input_box = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        self.cor_caixa = self.color[1] 
        self.ativo = False
        if position_x == "center":
            self.position_x = (screen.get_width() - self.width) // 2
            print(self.position_x)
        if self.modelpy:
            self.fonte = pygame.font.Font(self.modelpy, self.sizepy)
        else:
            self.fonte = pygame.font.SysFont(None, self.sizepy)
        
        self.fonte.set_bold(self.boldpy)
        self.fonte.set_italic(self.italicpy)
        self.fonte.set_underline(self.Underlinedpy)
    
    def To_write(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.ativo = not self.ativo  
            else:
                self.ativo = False
            self.cor_caixa = self.color[0] if self.ativo else self.color[1]
        
        if event.type == pygame.KEYDOWN:
            if self.ativo:
                if event.key == pygame.K_RETURN:
                    print(f"Texto digitado: {self.text}")
                    self.text = ""  
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    max_caracteres = int(((self.width * 25) / 300) - 3)
                    max_coluns = int(((self.height * 3) / 100))
                    print(max_coluns)
                    print(max_caracteres)
                    if len(self.text.split("\n")[-1]) < max_caracteres:
                        self.text += event.unicode
                        print("ok" + str(len(self.text.split("\n")[-1])))
                    elif len(self.text.split("\n")) >= max_coluns:
                        pass  
                    else:
                        self.text += "\n" + event.unicode


    
    def add_elements(self, screen):
        pygame.draw.rect(screen, self.cor_caixa, self.input_box, border_radius=10,width=2)
        linhas = self.text.split('\n',)
        for i, linha in enumerate(linhas):
            superficie_texto = self.fonte.render(linha, True, self.text_color)
            screen.blit(superficie_texto, (self.input_box.x + 10, self.input_box.y + 10 + i * 25))
class Collection:
    def __init__(self, grupo=[]):
        self.grupo = grupo
    def add_textures(self, texture_):
        for i in self.grupo:
            i.texture = texture_
            i.pygameload = pygame.image.load(texture_)
            i.pygameload = pygame.transform.scale(i.pygameload, (i.width, i.height))

    def add_elements(self, screen):
        for i in self.grupo:
            i.add_elements(screen)
class Entity:
    def __init__(self,Collection:Collection,width,height,position_x,position_y,directory=None,colision=False,not_Penetrate=[],padding_image=None,name_animation=None,width_image=None,height_image=None,colision_color=True):
        self.width = width
        self.height = height
        self.colision_color = colision_color
        self.padding_image = padding_image
        self.width_image = width_image
        self.height_image = height_image
        self.name_animation = name_animation
        self.imagem = directory
        if self.imagem is not None:
            self.animation = AnimationImage()
            self.p = self.animation.load(directory,self.name_animation,width=self.width_image,height=self.height_image)
        self.not_penetrate = not_Penetrate
        self.position_x = position_x
        self.position_y = position_y
        self.colision = colision
        self.collection = Collection
        self.pular = False
    def Physical(self, gravity=0.2):
        for j in self.not_penetrate:
            if not j.colision and not self.colision:
                continue

            px, py, pw, ph = self.position_x, self.position_y, self.width, self.height
            ox, oy, ow, oh = j.position_x, j.position_y, j.width, j.height
            colidiu_y = py + ph >= oy and py < oy + oh
            colidiu_x = px + pw > ox and px < ox + ow

            if colidiu_x and colidiu_y:
                centro_self = px + pw / 2
                centro_j = ox + ow / 2

                if centro_self < centro_j:
                    self.position_x -= gravity
                else:
                    self.position_x += gravity

        for i in self.collection.grupo:
            if not i.colision:
                continue
            px, py, pw, ph = self.position_x, self.position_y, self.width, self.height
            ox, oy, ow, oh = i.position_x, i.position_y, i.width, i.height
            colidiu_y = py + ph >= oy and py < oy + oh
            colidiu_x = px + pw > ox and px < ox + ow

            if colidiu_x and colidiu_y:
                
                break  

        else:
            if self.pular == False:
                self.position_y += gravity 

    def add_elements(self, screen):
        if self.colision_color == True:
            pygame.draw.rect(
                screen,
                Colors.BLUE,
                (self.position_x, self.position_y, self.width, self.height),
                width=1
            )

        if hasattr(self, "animation") and self.animation:
            screen.blit(self.animation.play_animation(), (self.position_x - self.padding_image, self.position_y))
class Point_function:
    def __init__(self,radius,position_x,position_y):
        self.radius = radius
        self.position_y = position_y
        self.position_x = position_x
class box:
    def __init__(self,width,height,position_x,position_y,colision=True,texture=None,colision_color=True):
        self.width = width
        self.height = height
        self.colision_color = colision_color
        self.position_x = position_x
        self.texture = texture
        self.position_y = position_y
        self.pygameload = None 
        self.colision = colision
        if self.texture is not None:
            self.pygameload = pygame.image.load(self.texture)
            self.pygameload = pygame.transform.scale(self.pygameload, (self.width, self.height)) 
    def customize_function(self,functions):
        if callable(functions):
            functions()
    def jump_block(self,objects):
        for i in objects:
            px, py, pw, ph = self.position_x, self.position_y, self.width, self.height
            ox, oy, ow, oh = i.position_x, i.position_y, i.width, i.height

            colidiu_y = py + ph > oy and py < oy + oh
            colidiu_x = px + pw > ox and px < ox + ow

            if colidiu_x and colidiu_y:
                i.position_y -= 500
    def add_elements(self,screen):
        if self.colision_color == True:
            pygame.draw.rect(
                screen,
                Colors.BLUE,
                (self.position_x, self.position_y, self.width, self.height),
            )
        if self.texture is not None:
           screen.blit(self.pygameload,(self.position_x,self.position_y))
class AnimationImage: 
    def __init__(self):
        self.frames = []
        self.current_frame = 0
        self.frame_count = 0
        self.frame_width = 0
        self.frame_height = 0
        self.sprite_sheet = None
        self.animation_speed = 5
        self.counter = 0
    def stop(self):
        self.current_frame = 0
        self.counter = 0
    def load(self, directory, name, width=None, height=None):
        # Carrega dados do JSON
        with open(os.path.join(directory, "data.json"), "r", encoding="utf-8") as f:
            script = json.load(f)

        anim_data = script[name]
        altura_total = anim_data["pa"]
        frame_count = anim_data.get("flames", 1)  
        caminho_img = anim_data["lcl"]
        largura_total = anim_data["pl"]
        largura_frame = anim_data["pd"]

        # Calcula o espaçamento entre quadros
        if frame_count > 1:
            espacamento = (largura_total - (largura_frame * frame_count)) // (frame_count - 1)
        else:
            espacamento = 0

        self.sprite_sheet = pygame.image.load(caminho_img).convert_alpha()
        self.frame_count = frame_count
        self.frame_width = largura_frame
        self.frame_height = altura_total
        self.frames = []

        for i in range(frame_count):
            x = i * (largura_frame + espacamento)
            frame = self.sprite_sheet.subsurface((x, 0, largura_frame, altura_total))
            
            # Redimensiona se necessário
            if height is not None and width is not None:
                frame = pygame.transform.scale(frame, (width, height))
            self.frames.append(frame)

    def play_animation(self):
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.current_frame = (self.current_frame + 1) % self.frame_count
        return self.frames[self.current_frame]


class Characters(AnimationImage):
    def __init__(self,jump=True,Collection:Collection=None,width=200,height=200,position_x=0,position_y=0,colision=False,directory=None,animation_name=None,height_image=None,width_image=None,padding_image=50,colision_color=True):
        self.width = width
        self.jump = jump
        self.colision_color = colision_color
        self.padding_image = padding_image
        self.button_desabilide = [False,False,False,False]
        self.height = height
        self.position_x = position_x
        self.height_image = height_image
        self.width_image = width_image
        self.position_y = position_y
        self.directory = directory
        self.name_animation = animation_name
        if directory is not None:
            self.animation = AnimationImage()
            self.p = self.animation.load(directory,self.name_animation,width=self.width_image,height=self.height_image)
        self.colision = colision
        self.collection = Collection
        self.pular = False
    def Physical(self, gravity=0.2, function=None, barrier=False, desable_button=False,desable_jump=True):
        if desable_jump is not True:
           self.jump = False
        self.button_desabilide = [False, False, False, False]
        colidiu = False

        old_x = self.position_x
        old_y = self.position_y

        for i in self.collection.grupo:
            if not i.colision:
                continue

            px, py, pw, ph = self.position_x, self.position_y, self.width, self.height
            ox, oy, ow, oh = i.position_x, i.position_y, i.width, i.height

            colidiu_y = py + ph > oy and py < oy + oh
            colidiu_x = px + pw > ox and px < ox + ow

            if colidiu_x and colidiu_y:
                self.jump = True
                colidiu = True

                meio_jogador_x = px + pw / 2
                meio_bloc_x = ox + ow / 2
                meio_jogador_y = py + ph / 2
                meio_bloc_y = oy + oh / 2

                dx = meio_jogador_x - meio_bloc_x
                dy = meio_jogador_y - meio_bloc_y

                if desable_button:
                    dif_top = abs((py + ph) - oy)
                    dif_bottom = abs(py - (oy + oh))
                    dif_left = abs((px + pw) - ox)
                    dif_right = abs(px - (ox + ow))

                    min_dif = min(dif_top, dif_bottom, dif_left, dif_right)
                    
                    if min_dif == dif_top:
                        self.position_y = oy - ph
                        self.button_desabilide[1] = True  
                        self.position_y += 1
                    elif min_dif == dif_bottom:
                        self.position_y = oy + oh
                        self.button_desabilide[0] = True 
                    elif min_dif == dif_left:
                        self.position_x = ox - pw
                        self.button_desabilide[3] = True  
                    elif min_dif == dif_right:
                        self.position_x = ox + ow
                        self.button_desabilide[2] = True


                if barrier:
                    self.position_x = old_x
                    self.position_y = old_y
                break

        if not colidiu:
            if not self.pular:
                if callable(function):
                    function()
                else:
                    self.position_y += gravity

    def handle_key_release(self, evento,animation_name):
        if evento.type == pygame.KEYUP:
            if evento.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                self.animation.stop()
                self.animation.load(self.directory,animation_name, width=self.width_image, height=self.height_image)

    def button_functions_on_press(self, disable: Desable = None, potencia=[1, 1, 1, 1],animation_UP=None,animation_left=None,animation_right=None,animation_down=None):
        teclas = pygame.key.get_pressed()
        self.pular = False

        if self.button_desabilide == True:
            return
        if disable is None:
            disable = Desable(False, False, False, False)
            
        if teclas[pygame.K_UP] and not disable.UP and self.button_desabilide[0] == False:
            if animation_UP is not None:
                   self.animation.load(self.directory,animation_UP,width=self.width_image,height=self.height_image)
            self.position_y -= potencia[0]
            self.pular = True
        if teclas[pygame.K_DOWN] and not disable.DOWN and self.button_desabilide[1] == False:
            if animation_down is not None:
                   self.animation.load(self.directory,animation_down,width=self.width_image,height=self.height_image)
            self.position_y += potencia[1]
        if teclas[pygame.K_LEFT] and not disable.LEFT and self.button_desabilide[2] == False:
            if animation_left is not None:
                   self.animation.load(self.directory,animation_left,width=self.width_image,height=self.height_image)
            self.position_x -= potencia[2]
        if teclas[pygame.K_RIGHT] and not disable.RIGHT and self.button_desabilide[3] == False:
            if animation_right is not None:
               self.animation.load(self.directory,animation_right,width=self.width_image,height=self.height_image)
            self.position_x += potencia[3]
    def button_functions_on_clicked(self, evento, disable: Desable = None, potencia=[1, 1, 1, 1], strength=(1, 1, 10, 1),solid_detector=False):
        self.pular = False
        if disable is None:
            disable = Desable(False, False, False, False)
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT and not disable.LEFT:
                for i in range(strength[2]):
                    self.position_x -= potencia[2] + i

            elif evento.key == pygame.K_RIGHT and not disable.RIGHT:
                for i in range(strength[3]):
                    self.position_x += potencia[3] + i

            elif evento.key == pygame.K_UP and not disable.UP and self.jump == True:
                self.pular = True
                for i in range(strength[0]):
                    self.position_y -= potencia[0] + i

            elif evento.key == pygame.K_DOWN and not disable.DOWN:
                for i in range(strength[1]):
                    self.position_y += potencia[1] + i

    def add_elements(self,screen):
        if self.colision_color == True:
            pygame.draw.rect(
                    screen,
                    Colors.BLUE,
                    (self.position_x, self.position_y, self.width, self.height),
                    width=1
                )
        if hasattr(self, "animation") and self.animation:
           screen.blit(self.animation.play_animation(),(self.position_x-self.padding_image,self.position_y))
class ButtonElement:
    def __init__(self,screen,text, position_x=0, position_y=0, width=150, height=50, 
        color=Colors.BLUE, text_color=Colors.BLACK, modelpy=None, sizepy=30, 
        italicpy=False, boldpy=False, strikethrough=False, Underlinedpy=False,hover=Colors.RED,space_inside=0,image=None,responsive_magin=0.5,border_radius=0):
        self.text = text
        if width == "responsive":
            width = int(screen.get_width() * responsive_magin)  
        self.width = width

        if height == "responsive":
            height = (screen.get_height() * responsive_magin)
        self.height = height

        if position_x == "center":
            position_x = (screen.get_width() - self.width) // 2
        self.position_x = position_x

        if position_y == "center":
            position_y = (screen.get_height() - self.height) // 2
        self.position_y = position_y
        self.width = width
        self.hover = hover
        self.height = height
        self.color = color
        self.imagem = None
        if position_x == "center":
            self.position_x = (screen.get_width() - self.width) // 2
        if image is not None:
            self.imagem = pygame.image.load(image)  
            self.imagem = pygame.transform.scale(self.imagem, (self.width, self.height)) 
        self.border_radius = border_radius
        self.text_color = text_color
        self.modelpy = modelpy
        self.sizepy = sizepy
        self.italicpy = italicpy
        self.boldpy = boldpy
        self.strikethrough = strikethrough
        self.Underlinedpy = Underlinedpy

        
        self.font = pygame.font.Font(self.modelpy, self.sizepy)
        self.font.set_bold(self.boldpy)
        self.font.set_italic(self.italicpy)
        self.font.set_underline(self.Underlinedpy)
        self.font.set_strikethrough(self.strikethrough)

       
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(self.position_x + self.width // 2, 
                                                           self.position_y + self.height // 2))

    def add_elements(self, screen):
        if self.color is not None:
           pygame.draw.rect(screen, self.color, (self.position_x, self.position_y, self.width, self.height),border_radius=self.border_radius)
        if self.imagem is not None:
            screen.blit(self.imagem,(self.position_x,self.position_y))
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (self.position_x <= mouse_x <= self.position_x + self.width and
                self.position_y <= mouse_y <= self.position_y + self.height):
                return True
        return False
    def animation(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        if self.text_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                self.color = self.color
            else:
                self.color = self.hover 
        else:
            self.color = self.color
class Font_text:
    def __init__(self, screen, text, italicpy=False, boldpy=False, strikethrough=False, Underlinedpy=False,
                 modelpy=None, position_x=0, position_y=0, sizepy=30, color=Colors.BLACK):
        self.color = color
        self.italicpy = italicpy
        self.boldpy = boldpy
        self.strikethrough = strikethrough
        self.Underlinedpy = Underlinedpy
        self.modelpy = modelpy
        self.position_x = position_x
        self.position_y = position_y
        self.sizepy = sizepy
        self.text = text

        font = pygame.font.Font(self.modelpy, self.sizepy)
        font.set_bold(self.boldpy)
        font.set_italic(self.italicpy)
        font.set_underline(self.Underlinedpy)
        font.set_strikethrough(self.strikethrough)
        self.text_surface = font.render(self.text, True, self.color)
        self.width = self.text_surface.get_width()
        if position_x == "center":
            self.position_x = (screen.get_width() - self.width) // 2
        self.text_rect = self.text_surface.get_rect(topleft=(self.position_x, self.position_y))

    def add_elements(self, screen):
        screen.blit(self.text_surface, self.text_rect)
class Close:
    def __init__(self):
        self.running = True

    def check(self,event):
            if event.type == pygame.QUIT:
                self.running = False
class Screen_loop:
    def __init__(self, current_scene, close_control:Close):
        self.current_scene = current_scene
        self.close_control = close_control
    def initiation(self, scene: int, scenes: list):
        running = True
        while self.close_control.running and running:
            if 0 <= scene < len(scenes):
                running, scene = scenes[scene]()  

    def screen_locking(self,screen,objetos):
        x = screen.get_width()
        y = screen.get_height()
        for i in [objetos]:
            if i.position_x + i.width >= x:
                print("passou")
    def add_cena(self, screen, elements, bg_color):
        screen.fill(bg_color)
        for element in elements:
            element.add_elements(screen)
        pygame.display.flip()
    @staticmethod
    def VerticalStack(controls, position_y=0, spacing=10):
        for i, c in enumerate(controls):
            c.position_y = position_y + (i * spacing)
    @staticmethod
    def HorizontalStack(controls, position_x=0, spacing=10):
        for i, c in enumerate(controls):
            c.position_x = position_x + (i * spacing)
class Square:
    def __init__(self, screen, position_x=0, position_y=0, width=200, height=100, color=Colors.BLACK, space_inside=0,responsive_magin=0.5):
        self.space = space_inside

        
        if width == "responsive":
            width = int(screen.get_width() * responsive_magin)  
        self.width = width

        if height == "responsive":
            height = (screen.get_height() * responsive_magin)
        self.height = height

        if position_x == "center":
            position_x = (screen.get_width() - self.width) // 2
        self.position_x = position_x

        if position_y == "center":
            position_y = (screen.get_height() - self.height) // 2
        self.position_y = position_y

        self.height = height
        self.bgcolor = color

    def add_elements(self, screen):
        pygame.draw.rect(
            screen,
            self.bgcolor,
            (self.position_x, self.position_y, self.width, self.height),
            width=self.space
        )

        