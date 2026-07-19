# Importa a classe FastAPI (cria a aplicação web) e HTTPException
# (usada para devolver erros HTTP, como o 404)
from fastapi import FastAPI, HTTPException

# FileResponse envia um arquivo do disco como resposta da requisição
from fastapi.responses import FileResponse

# CORSMiddleware libera o acesso à API a partir de outras origens (portas/domínios)
from fastapi.middleware.cors import CORSMiddleware

# O módulo os é usado para montar caminhos de pasta
import os

# O módulo glob procura arquivos no disco a partir de um padrão de nome
import glob

# Cria a instância da aplicação — é ela que o uvicorn executa
app = FastAPI()

# Configura o CORS. Sem isso, o navegador bloqueia o frontend (servido em
# outra porta, ex. :5500) de ler a resposta desta API (:8000).
# allow_origins=["*"] aceita requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho absoluto até a pasta onde este arquivo está.
# __file__ é o caminho deste main.py; abspath resolve para o caminho completo
# e dirname remove o nome do arquivo, sobrando só a pasta
PASTA_BASE = os.path.dirname(os.path.abspath(__file__))

# Caminho absoluto da pasta com as imagens das figurinhas.
# Usar caminho absoluto garante que o servidor ache a pasta
# independente do diretório de onde o uvicorn foi executado
PASTA_IMAGENS = os.path.join(PASTA_BASE, "figurinhas")

# Quantidade de slots do álbum. É uma constante porque o álbum tem tamanho
# fixo: 30 slots, estejam eles preenchidos ou não
TOTAL_ALBUM = 30

# Lista de figurinhas do álbum — 30 no total, agrupadas por categoria.
# Só ficam ativas as figurinhas cuja imagem já existe na pasta figurinhas/.
# As demais estão comentadas: basta adicionar o arquivo (ex. 03-sam-altman.jpg)
# e descomentar a linha correspondente.
# O imagem_url aponta para a rota que serve a imagem, definida no fim do arquivo
figurinhas = [
    # --- Pioneiros da Inteligência Artificial ---
    {"id": 1, "nome": "Alan Turing", "categoria": "IA", "imagem_url": "/figurinhas/1/imagem"},
    {"id": 2, "nome": "John McCarthy", "categoria": "IA", "imagem_url": "/figurinhas/2/imagem"},
    # {"id": 3, "nome": "Sam Altman", "categoria": "IA", "imagem_url": "/figurinhas/3/imagem"},
    # {"id": 4, "nome": "Geoffrey Hinton", "categoria": "IA", "imagem_url": "/figurinhas/4/imagem"},
    # {"id": 5, "nome": "Yann LeCun", "categoria": "IA", "imagem_url": "/figurinhas/5/imagem"},
    # --- Arquitetos da Simplicidade (Python) ---
    # {"id": 6, "nome": "Guido van Rossum", "categoria": "Python", "imagem_url": "/figurinhas/6/imagem"},
    # {"id": 7, "nome": "Tim Peters", "categoria": "Python", "imagem_url": "/figurinhas/7/imagem"},
    # {"id": 8, "nome": "Raymond Hettinger", "categoria": "Python", "imagem_url": "/figurinhas/8/imagem"},
    # {"id": 9, "nome": "Travis Oliphant", "categoria": "Python", "imagem_url": "/figurinhas/9/imagem"},
    # {"id": 10, "nome": "Wes McKinney", "categoria": "Python", "imagem_url": "/figurinhas/10/imagem"},
    # --- Arquitetos de Bancos de Dados ---
    # {"id": 11, "nome": "Edgar F. Codd", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/11/imagem"},
    # {"id": 12, "nome": "Larry Ellison", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/12/imagem"},
    # {"id": 13, "nome": "Michael Widenius", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/13/imagem"},
    # {"id": 14, "nome": "Salvatore Sanfilippo", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/14/imagem"},
    # {"id": 15, "nome": "Eliot Horowitz", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/15/imagem"},
    # --- Arquitetos da Computação Moderna ---
    # {"id": 16, "nome": "Linus Torvalds", "categoria": "Sistemas Operacionais", "imagem_url": "/figurinhas/16/imagem"},
    # {"id": 17, "nome": "Dennis Ritchie", "categoria": "Sistemas Operacionais", "imagem_url": "/figurinhas/17/imagem"},
    # {"id": 18, "nome": "Richard Stallman", "categoria": "Sistemas Operacionais", "imagem_url": "/figurinhas/18/imagem"},
    # {"id": 19, "nome": "Bill Gates", "categoria": "Sistemas Operacionais", "imagem_url": "/figurinhas/19/imagem"},
    # {"id": 20, "nome": "Steve Jobs", "categoria": "Sistemas Operacionais", "imagem_url": "/figurinhas/20/imagem"},
    # --- Celebridades Tech - Vol. 1 ---
    # {"id": 21, "nome": "Paulo Silveira", "categoria": "Brasil", "imagem_url": "/figurinhas/21/imagem"},
    # {"id": 22, "nome": "Guilherme Silveira", "categoria": "Brasil", "imagem_url": "/figurinhas/22/imagem"},
    # {"id": 23, "nome": "Gustavo Guanabara", "categoria": "Brasil", "imagem_url": "/figurinhas/23/imagem"},
    # {"id": 24, "nome": "Maurício Aniche", "categoria": "Brasil", "imagem_url": "/figurinhas/24/imagem"},
    # {"id": 25, "nome": "Andre David", "categoria": "Brasil", "imagem_url": "/figurinhas/25/imagem"},
    # --- Celebridades Tech - Vol. 2 ---
    # {"id": 26, "nome": "Guilherme Lima", "categoria": "Brasil", "imagem_url": "/figurinhas/26/imagem"},
    # {"id": 27, "nome": "Gi Space Coding", "categoria": "Brasil", "imagem_url": "/figurinhas/27/imagem"},
    # {"id": 28, "nome": "Vinicius Neves", "categoria": "Brasil", "imagem_url": "/figurinhas/28/imagem"},
    # {"id": 29, "nome": "Rafaela Ballerini", "categoria": "Brasil", "imagem_url": "/figurinhas/29/imagem"},
    # {"id": 30, "nome": "Você", "categoria": "Brasil", "imagem_url": "/figurinhas/30/imagem"},
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


# Rota com as estatísticas do álbum.
# ATENÇÃO à ordem: esta rota precisa ser declarada ANTES de
# /figurinhas/{figurinha_id}. O FastAPI testa as rotas na ordem em que foram
# registradas, então a rota dinâmica capturaria "total" e tentaria convertê-lo
# para int, respondendo 422 em vez de chegar aqui
@app.get("/figurinhas/total")
def estatisticas_album():
    # len() conta quantas figurinhas estão na lista neste momento.
    # Como o número é calculado, basta adicionar um item à lista para a
    # estatística se atualizar sozinha — nada precisa ser ajustado aqui
    coladas = len(figurinhas)

    return {
        "total_album": TOTAL_ALBUM,
        "coladas": coladas,
        "faltam": TOTAL_ALBUM - coladas,
    }


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


# Rota que serve o arquivo de imagem da figurinha
@app.get("/figurinhas/{figurinha_id}/imagem")
def imagem_figurinha(figurinha_id: int):
    # Monta o padrão de busca: o id com 2 dígitos (01, 02, ... 30) seguido de
    # um caractere que NÃO seja número. Esse [!0-9] impede que o id 1 ("01")
    # case com um arquivo de numeração maior como "011-...". O resto do nome
    # e a extensão ficam livres (.jpg, .png)
    padrao = os.path.join(PASTA_IMAGENS, f"{figurinha_id:02d}[!0-9]*")

    # glob devolve a lista de arquivos que batem com o padrão
    arquivos = glob.glob(padrao)

    # Nenhum arquivo encontrado: a figurinha ainda não tem imagem
    if not arquivos:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")

    # Envia o primeiro arquivo encontrado.
    # O FileResponse cuida sozinho do tipo do conteúdo (image/jpeg, image/png)
    return FileResponse(arquivos[0])
