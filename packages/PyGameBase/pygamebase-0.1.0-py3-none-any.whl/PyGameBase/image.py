import os
import json
import re
from collections import defaultdict
from PIL import Image
class Imagemsplite:
    def __init__(self,pasta):
        self.folder = pasta
        pasta_abs = os.path.abspath(self.folder)
        diretorio_pai = os.path.dirname(pasta_abs)
        nome_pasta = os.path.basename(pasta_abs)
        self.pasta_saida = os.path.join(diretorio_pai, nome_pasta + "_spritesheets")
        if not os.path.exists(self.pasta_saida):
            os.makedirs(self.pasta_saida)
    def copilacao(self):
        def criarsplites(imagens, largura_total, altura_fixa=300, cor_divisoria=(255, 0, 0, 255)):
            quantidade = len(imagens)
            largura_individual = largura_total // quantidade
            largura_divisoria = 1
            nova_largura_total = (largura_individual * quantidade) + (largura_divisoria * (quantidade - 1))
            
            imagens_redimensionadas = []
            
            for img_path in imagens:
                img = Image.open(img_path).convert("RGBA")
                proporcao = altura_fixa / img.height
                nova_largura = int(img.width * proporcao)
                img = img.resize((nova_largura, altura_fixa))

                img = img.resize((largura_individual, altura_fixa))
                imagens_redimensionadas.append(img)
            
            nova_imagem = Image.new("RGBA", (nova_largura_total, altura_fixa), (0, 0, 0, 0))
            
            x = 0
            for i, img in enumerate(imagens_redimensionadas):
                nova_imagem.paste(img, (x, 0), img)  
                x += largura_individual
                if i < quantidade - 1:
                    for y in range(altura_fixa):
                        nova_imagem.putpixel((x, y), cor_divisoria)
                    x += largura_divisoria

            return nova_imagem
        padrao = re.compile(r'^([a-zA-Z]+)[0-9]+\.png$')
        imagens_dict = defaultdict(list)

        for arquivo in os.listdir(self.folder):
            if arquivo.endswith(".png"):
                match = padrao.match(arquivo)
                if match:
                    prefixo = match.group(1)
                    imagens_dict[prefixo].append(arquivo)
        for chave in imagens_dict:
            imagens_dict[chave].sort()
        dicionario = {}
        for cv,vl in imagens_dict.items():
            largurat = []
            alturat = []
            for abrir in vl:
                imagem = Image.open(os.path.join(self.folder, abrir)) 
                largura, altura = imagem.size
                largurat.append(largura)
                alturat.append(altura)
            L_img = sum(largurat) // len(largurat)
            A_img = sum(alturat) // len(alturat)
            N = {cv:{
                "pl":L_img * len(largurat) + (len(largurat) - 1),
                "pa":A_img,
                "pd":L_img,
                "lcl":os.path.join(self.pasta_saida, f"{cv}.png"),
                "flames":len(largurat)
            }}
            caminhos_completos = [os.path.join(self.folder, v) for v in vl]
            resultado = criarsplites(caminhos_completos, largura_total=(L_img * len(largurat)), altura_fixa=A_img)
            resultado.save(os.path.join(self.pasta_saida, f"{cv}.png"))
            dicionario.update(N)
        with open(os.path.join(self.pasta_saida, f"data.json"), "w", encoding="UTF-8") as arq:
            json.dump(dicionario,arq,indent=4)
        return self.pasta_saida

