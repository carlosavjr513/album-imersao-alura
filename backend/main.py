# Importa a classe FastAPI (cria a aplicação web) e HTTPException
# (usada para devolver erros HTTP, como o 404)
from fastapi import FastAPI, HTTPException

# StaticFiles serve arquivos do disco (imagens, css, etc.) diretamente
from fastapi.staticfiles import StaticFiles

# O módulo os é usado para montar caminhos de pasta
import os

# Cria a instância da aplicação — é ela que o uvicorn executa
app = FastAPI()

# Caminho absoluto até a pasta onde este arquivo está.
# __file__ é o caminho deste main.py; abspath resolve para o caminho completo
# e dirname remove o nome do arquivo, sobrando só a pasta
PASTA_BASE = os.path.dirname(os.path.abspath(__file__))

# Caminho absoluto da pasta com as imagens das figurinhas.
# Usar caminho absoluto garante que o servidor ache a pasta
# independente do diretório de onde o uvicorn foi executado
PASTA_IMAGENS = os.path.join(PASTA_BASE, "figurinhas")

# "Monta" a pasta de imagens na rota /imgs.
# A partir daqui, o arquivo figurinhas/01-alan-turing.jpg
# fica acessível pela URL /imgs/01-alan-turing.jpg.
# O name="imgs" é o apelido interno da rota, usado para gerar URLs
app.mount("/imgs", StaticFiles(directory=PASTA_IMAGENS), name="imgs")

# Lista de figurinhas do álbum.
# Dados fixos por enquanto; mais adiante virão de um banco de dados.
# O campo imagem_url aponta para a rota estática montada acima
figurinhas = [
    {
        "id": 1,
        "nome": "Alan Turing",
        "categoria": "IA",
        "imagem_url": "/imgs/01-alan-turing.jpg",
    },
    {
        "id": 2,
        "nome": "John McCarthy",
        "categoria": "IA",
        "imagem_url": "/imgs/02-john-mccarthy.jpg",
    },
]


# O decorador @app.get("/") registra a função abaixo como a resposta
# para requisições HTTP GET na rota raiz ("/")
@app.get("/")
def hello_world():
    # O dicionário retornado é convertido automaticamente em JSON
    return {"mensagem": "Olá, mundo! 🌍"}


# Rota que devolve todas as figurinhas do álbum
@app.get("/figurinhas")
def listar_figurinhas():
    # A lista de dicionários vira um array JSON na resposta
    return figurinhas


# O trecho entre chaves na rota é um parâmetro dinâmico: o valor da URL
# chega na função pelo argumento de mesmo nome.
# Como "figurinha_id" está anotado como int, o FastAPI converte o texto da
# URL para inteiro e responde 422 sozinho se vier algo que não seja número
@app.get("/figurinhas/{figurinha_id}")
def buscar_figurinha(figurinha_id: int):
    # Percorre a lista procurando a figurinha com o id pedido
    for figurinha in figurinhas:
        if figurinha["id"] == figurinha_id:
            return figurinha

    # Nenhuma correspondência: interrompe a função e devolve 404.
    # O texto de "detail" aparece no corpo da resposta como {"detail": "..."}
    raise HTTPException(status_code=404, detail="Figurinha não encontrada")
