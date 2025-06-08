import json
import os

CAMINHO_USUARIOS = "usuarios.json"

def carregar_usuarios():
    if os.path.exists(CAMINHO_USUARIOS):
        with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_usuario(novo_usuario):
    usuarios = carregar_usuarios()
    usuario_novo = novo_usuario["usuario"].lower()

    for u in usuarios:
        if u["usuario"].lower() == usuario_novo:
            return False

    novo_usuario_formatado = {
        "nome": novo_usuario["nome"],
        "usuario": usuario_novo,
        "senha": novo_usuario["senha"]
    }

    usuarios.append(novo_usuario_formatado)

    with open(CAMINHO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

    return True 

def verificar_login(usuario, senha):
    usuarios = carregar_usuarios()
    usuario = usuario.lower()  # ignora maiúsculas/minúsculas no login

    for u in usuarios:
        if u["usuario"].lower() == usuario and u["senha"] == senha:
            return True
    return False

CAMINHO_DADOS = "dados.json"

def carregar_dados():
    if os.path.exists(CAMINHO_DADOS):
        with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def adicionar_midia(usuario, tipo, midia):
    dados = carregar_dados()
    if usuario not in dados:
        dados[usuario] = {"filmes": [], "series": []}

    dados[usuario][tipo + "s"].append(midia)
    salvar_dados(dados)
