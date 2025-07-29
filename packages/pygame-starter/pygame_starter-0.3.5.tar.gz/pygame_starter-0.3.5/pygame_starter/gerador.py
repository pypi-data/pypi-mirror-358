import os
import json

def criar_projeto(nome_projeto, largura, altura, cor_fundo):
    estrutura = {
        f"{nome_projeto}/": [
            "main.py",
            "config.py",
            "recorde.json"
        ],
        f"{nome_projeto}/assets/sprites/": [],
        f"{nome_projeto}/assets/sons/": [],
        f"{nome_projeto}/assets/fontes/": []
    }

    template_config = f'''
largura_tela = {largura}
altura_tela = {altura}
FPS = 60
COR_FUNDO = {cor_fundo}  # RGB
'''

    template_main = f'''import pygame
import sys
import json
from config import largura_tela, altura_tela, FPS, COR_FUNDO

def salvar_recorde(pontos):
    try:
        with open("recorde.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {{"recorde": 0}}

    if pontos > data.get("recorde", 0):
        data["recorde"] = pontos
        with open("recorde.json", "w") as f:
            json.dump(data, f)

def carregar_recorde():
    try:
        with open("recorde.json", "r") as f:
            data = json.load(f)
            return data.get("recorde", 0)
    except FileNotFoundError:
        return 0

def menu_inicial(tela, relogio):
    fonte = pygame.font.Font(None, 50)
    while True:
        tela.fill(COR_FUNDO)
        texto = fonte.render("Pressione ENTER para jogar", True, (255, 255, 255))
        tela.blit(texto, (largura_tela//2 - texto.get_width()//2, altura_tela//2))
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return

        relogio.tick(FPS)

def main():
    pygame.init()
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    pygame.display.set_caption("Meu Jogo")

    relogio = pygame.time.Clock()
    menu_inicial(tela, relogio)

    recorde = carregar_recorde()
    pontos = 0

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        tela.fill(COR_FUNDO)

        # Aqui o código do jogo (exemplo simples)
        fonte = pygame.font.Font(None, 36)
        texto_pontos = fonte.render(f"Pontos: {{pontos}}", True, (255, 255, 255))
        texto_recorde = fonte.render(f"Recorde: {{recorde}}", True, (255, 255, 255))
        tela.blit(texto_pontos, (10, 10))
        tela.blit(texto_recorde, (10, 50))

        pygame.display.update()
        relogio.tick(FPS)

        # Simula aumento de pontos
        pontos += 1
        if pontos > recorde:
            salvar_recorde(pontos)

    pygame.quit()

if __name__ == "__main__":
    main()
'''

    template_recorde = '{"recorde": 0}'

    templates = {
        "config.py": template_config,
        "main.py": template_main,
        "recorde.json": template_recorde,
    }

    for pasta, arquivos in estrutura.items():
        os.makedirs(pasta, exist_ok=True)
        for arquivo in arquivos:
            caminho = os.path.join(pasta, arquivo)
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(templates[arquivo])

    print(f"\n✅ Projeto '{nome_projeto}' criado com sucesso!")
    print(f"➡ Para começar: cd {nome_projeto} && python main.py")

def validar_nome(nome):
    caracteres_invalidos = set("0123456789!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~` ")
    if not nome or any(char in caracteres_invalidos for char in nome):
        return False
    return True

def pedir_int(mensagem, minimo, maximo):
    while True:
        try:
            valor = int(input(mensagem))
            if minimo <= valor <= maximo:
                return valor
            else:
                print(f"Por favor, insira um número entre {minimo} e {maximo}.")
        except ValueError:
            print("Entrada inválida, digite um número inteiro.")

def pedir_cor():
    while True:
        entrada = input("Digite a cor de fundo RGB separada por vírgulas (ex: 0,0,0 para preto): ")
        partes = entrada.split(",")
        if len(partes) != 3:
            print("Digite exatamente 3 valores separados por vírgulas.")
            continue
        try:
            r, g, b = [int(p.strip()) for p in partes]
            if all(0 <= v <= 255 for v in (r, g, b)):
                return (r, g, b)
            else:
                print("Valores RGB devem estar entre 0 e 255.")
        except ValueError:
            print("Por favor, digite números inteiros válidos.")

def main():
    print("=== Gerador de Projeto Pygame ===")
    nome = input("Nome do projeto: ").strip()
    if not validar_nome(nome):
        print("Nome inválido: não pode conter números, símbolos ou espaços.")
        return

    largura = pedir_int("Largura da tela (ex: 800): ", 100, 3840)
    altura = pedir_int("Altura da tela (ex: 600): ", 100, 2160)
    cor_fundo = pedir_cor()

    criar_projeto(nome, largura, altura, cor_fundo)

if __name__ == "__main__":
    main()
