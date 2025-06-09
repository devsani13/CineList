# Importa bibliotecas necessárias
import json
import os

# Caminho do arquivo com os usuários
CAMINHO_USUARIOS = "usuarios.json"

# Carrega a lista de usuários do arquivo
def carregar_usuarios():
    if os.path.exists(CAMINHO_USUARIOS):
        with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Salva um novo usuário no arquivo, garantindo que o nome de usuário seja único
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

# Verifica se o usuário e a senha correspondem aos dados salvos
def verificar_login(usuario, senha):
    usuarios = carregar_usuarios()
    usuario = usuario.lower()  # ignora maiúsculas/minúsculas no login

    for u in usuarios:
        if u["usuario"].lower() == usuario and u["senha"] == senha:
            return True
    return False

# Caminho do arquivo com os dados das mídias
CAMINHO_DADOS = "dados.json"


# Carrega as mídias do arquivo
def carregar_dados():
    if os.path.exists(CAMINHO_DADOS):
        with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Salva as mídias no arquivo
def salvar_dados(dados):
    with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Adiciona um novo filme ou série para o usuário
def adicionar_midia(usuario, tipo, midia):
    dados = carregar_dados()
    if usuario not in dados:
        dados[usuario] = {"filmes": [], "series": []}

    dados[usuario][tipo].append(midia)
    salvar_dados(dados)


# Atualiza uma mídia existente com novos dados
def atualizar_midia(usuario, tipo, nome_original, nova_midia):
    dados = carregar_dados()
    midias = dados.get(usuario, {}).get(tipo, [])

    for i, m in enumerate(midias):
        if m["nome"].lower() == nome_original.lower():
            midias[i] = nova_midia
            salvar_dados(dados)
            return True
    return False

# Exclui uma mídia com base no nome
def excluir_midia(usuario, tipo, nome):
    dados = carregar_dados()
    midias = dados.get(usuario, {}).get(tipo, [])

    nova_lista = [m for m in midias if m["nome"].lower() != nome.lower()]
    dados[usuario][tipo] = nova_lista
    salvar_dados(dados)