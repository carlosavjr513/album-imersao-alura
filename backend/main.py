# Importa a classe FastAPI (cria a aplicação web) e HTTPException
# (usada para devolver erros HTTP, como o 404)
from fastapi import FastAPI, HTTPException

# Cria a instância da aplicação — é ela que o uvicorn executa
app = FastAPI()

# Lista de figurinhas do álbum.
# Dados fixos por enquanto; mais adiante virão de um banco de dados
FIGURINHAS = [
    {"id": 1, "nome": "Alan Turing", "categoria": "IA"},
    {"id": 2, "nome": "John McCarthy", "categoria": "IA"},
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
    return FIGURINHAS


# O trecho entre chaves na rota é um parâmetro dinâmico: o valor da URL
# chega na função pelo argumento de mesmo nome.
# Como "figurinha_id" está anotado como int, o FastAPI converte o texto da
# URL para inteiro e responde 422 sozinho se vier algo que não seja número
@app.get("/figurinhas/{figurinha_id}")
def buscar_figurinha(figurinha_id: int):
    # Percorre a lista procurando a figurinha com o id pedido
    for figurinha in FIGURINHAS:
        if figurinha["id"] == figurinha_id:
            return figurinha

    # Nenhuma correspondência: interrompe a função e devolve 404.
    # O texto de "detail" aparece no corpo da resposta como {"detail": "..."}
    raise HTTPException(status_code=404, detail="Figurinha não encontrada")
