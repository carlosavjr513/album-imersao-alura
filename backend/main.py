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

# Lista de figurinhas do álbum — as 30 estão SEMPRE presentes aqui.
# O que muda é o campo "colada": ele começa False e vira True quando o
# usuário clica no número do slot no frontend.
#
# (Antes, colar uma figurinha era descomentar a linha dela e reiniciar o
# servidor. Agora o álbum é preenchido pela interface, via POST.)
#
# O estado vive só na memória: reiniciar o uvicorn zera todas as coladas.
#
# O imagem_url aponta para a rota que serve a imagem, definida no fim do arquivo
figurinhas = [
    # --- Transformers G1 · Autobots ---
    {"id": 1, "nome": "Optimus Prime", "faccao": "Autobot", "serie": "G1", "papel": "Líder dos Autobots", "colada": False, "imagem_url": "/figurinhas/1/imagem"},
    {"id": 2, "nome": "Bumblebee", "faccao": "Autobot", "serie": "G1", "papel": "Espião e batedor", "colada": False, "imagem_url": "/figurinhas/2/imagem"},
    {"id": 3, "nome": "Jazz", "faccao": "Autobot", "serie": "G1", "papel": "Chefe de operações especiais", "colada": False, "imagem_url": "/figurinhas/3/imagem"},
    {"id": 4, "nome": "Ironhide", "faccao": "Autobot", "serie": "G1", "papel": "Segurança e armamentos", "colada": False, "imagem_url": "/figurinhas/4/imagem"},
    {"id": 5, "nome": "Grimlock", "faccao": "Autobot", "serie": "G1", "papel": "Comandante dos Dinobots", "colada": False, "imagem_url": "/figurinhas/5/imagem"},
    # --- Transformers G1 · Decepticons ---
    {"id": 6, "nome": "Megatron", "faccao": "Decepticon", "serie": "G1", "papel": "Líder dos Decepticons", "colada": False, "imagem_url": "/figurinhas/6/imagem"},
    {"id": 7, "nome": "Starscream", "faccao": "Decepticon", "serie": "G1", "papel": "Segundo em comando traiçoeiro", "colada": False, "imagem_url": "/figurinhas/7/imagem"},
    {"id": 8, "nome": "Soundwave", "faccao": "Decepticon", "serie": "G1", "papel": "Comunicações e espionagem", "colada": False, "imagem_url": "/figurinhas/8/imagem"},
    {"id": 9, "nome": "Shockwave", "faccao": "Decepticon", "serie": "G1", "papel": "Lógica implacável", "colada": False, "imagem_url": "/figurinhas/9/imagem"},
    {"id": 10, "nome": "Devastator", "faccao": "Decepticon", "serie": "G1", "papel": "Combinação dos Constructicons", "colada": False, "imagem_url": "/figurinhas/10/imagem"},
    # --- Beast Wars · Maximals ---
    {"id": 11, "nome": "Optimus Primal", "faccao": "Autobot", "serie": "Beast Wars", "papel": "Líder dos Maximals", "colada": False, "imagem_url": "/figurinhas/11/imagem"},
    {"id": 12, "nome": "Cheetor", "faccao": "Autobot", "serie": "Beast Wars", "papel": "Batedor mais veloz", "colada": False, "imagem_url": "/figurinhas/12/imagem"},
    {"id": 13, "nome": "Rattrap", "faccao": "Autobot", "serie": "Beast Wars", "papel": "Espião e demolições", "colada": False, "imagem_url": "/figurinhas/13/imagem"},
    {"id": 14, "nome": "Rhinox", "faccao": "Autobot", "serie": "Beast Wars", "papel": "Engenheiro-chefe", "colada": False, "imagem_url": "/figurinhas/14/imagem"},
    {"id": 15, "nome": "Dinobot", "faccao": "Autobot", "serie": "Beast Wars", "papel": "Guerreiro de honra", "colada": False, "imagem_url": "/figurinhas/15/imagem"},
    # --- Beast Wars · Predacons ---
    {"id": 16, "nome": "Megatron", "faccao": "Decepticon", "serie": "Beast Wars", "papel": "Líder dos Predacons", "colada": False, "imagem_url": "/figurinhas/16/imagem"},
    {"id": 17, "nome": "Waspinator", "faccao": "Decepticon", "serie": "Beast Wars", "papel": "Soldado eternamente destruído", "colada": False, "imagem_url": "/figurinhas/17/imagem"},
    {"id": 18, "nome": "Tarantulas", "faccao": "Decepticon", "serie": "Beast Wars", "papel": "Cientista conspirador", "colada": False, "imagem_url": "/figurinhas/18/imagem"},
    {"id": 19, "nome": "Blackarachnia", "faccao": "Decepticon", "serie": "Beast Wars", "papel": "Espiã de lealdade dividida", "colada": False, "imagem_url": "/figurinhas/19/imagem"},
    {"id": 20, "nome": "Inferno", "faccao": "Decepticon", "serie": "Beast Wars", "papel": "Soldado fanático", "colada": False, "imagem_url": "/figurinhas/20/imagem"},
    # --- Robots in Disguise (2000) · Autobots ---
    {"id": 21, "nome": "Optimus Prime", "faccao": "Autobot", "serie": "RiD 2000", "papel": "Líder dos Autobots", "colada": False, "imagem_url": "/figurinhas/21/imagem"},
    {"id": 22, "nome": "Side Burn", "faccao": "Autobot", "serie": "RiD 2000", "papel": "Irmão Autobot veloz", "colada": False, "imagem_url": "/figurinhas/22/imagem"},
    {"id": 23, "nome": "Prowl", "faccao": "Autobot", "serie": "RiD 2000", "papel": "Irmão Autobot estrategista", "colada": False, "imagem_url": "/figurinhas/23/imagem"},
    {"id": 24, "nome": "X-Brawn", "faccao": "Autobot", "serie": "RiD 2000", "papel": "Irmão Autobot mais forte", "colada": False, "imagem_url": "/figurinhas/24/imagem"},
    {"id": 25, "nome": "Ultra Magnus", "faccao": "Autobot", "serie": "RiD 2000", "papel": "Irmão rival de Optimus", "colada": False, "imagem_url": "/figurinhas/25/imagem"},
    # --- Robots in Disguise (2000) · Predacons ---
    {"id": 26, "nome": "Megatron", "faccao": "Decepticon", "serie": "RiD 2000", "papel": "Líder dos Predacons", "colada": False, "imagem_url": "/figurinhas/26/imagem"},
    {"id": 27, "nome": "Sky-Byte", "faccao": "Decepticon", "serie": "RiD 2000", "papel": "Tubarão poeta e general", "colada": False, "imagem_url": "/figurinhas/27/imagem"},
    {"id": 28, "nome": "Slapper", "faccao": "Decepticon", "serie": "RiD 2000", "papel": "Sapo dos ataques químicos", "colada": False, "imagem_url": "/figurinhas/28/imagem"},
    {"id": 29, "nome": "Gas Skunk", "faccao": "Decepticon", "serie": "RiD 2000", "papel": "Gambá dos gases tóxicos", "colada": False, "imagem_url": "/figurinhas/29/imagem"},
    {"id": 30, "nome": "Dark Scream", "faccao": "Decepticon", "serie": "RiD 2000", "papel": "Esquilo voador furtivo", "colada": False, "imagem_url": "/figurinhas/30/imagem"},
]


# Função auxiliar: procura uma figurinha pelo id e devolve o dicionário dela.
# Como três rotas diferentes precisam fazer exatamente isso, a busca mora
# aqui em vez de repetida em cada uma.
# O underline no começo do nome é uma convenção Python: sinaliza que a função
# é de uso interno deste arquivo, não uma rota da API
def _encontrar(figurinha_id: int):
    # Percorre a lista procurando a figurinha com o id pedido
    for figurinha in figurinhas:
        if figurinha["id"] == figurinha_id:
            return figurinha

    # Nenhuma correspondência: interrompe e devolve 404.
    # O texto de "detail" aparece no corpo da resposta como {"detail": "..."}
    raise HTTPException(status_code=404, detail="Figurinha não encontrada")


# O decorador @app.get("/") registra a função abaixo como a resposta
# para requisições HTTP GET na rota raiz ("/")
@app.get("/")
def universal_greeting():
    # O dicionário retornado é convertido automaticamente em JSON
    return {"mensagem": "Bah-weep-Graaaaagnah wheep ni ni bong"}


# Rota que devolve todas as figurinhas do álbum.
# Devolve as 30 sempre — o frontend usa o campo "colada" de cada uma
# para saber quais slots já têm imagem
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
    # Conta quantas figurinhas estão coladas neste momento.
    # O sum() soma 1 para cada figurinha que passa no teste, então o número
    # acompanha sozinho cada colagem/descolagem feita pelo frontend
    coladas = sum(1 for figurinha in figurinhas if figurinha["colada"])

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
    return _encontrar(figurinha_id)


# Cola a figurinha no álbum.
# É POST e não GET porque a requisição MODIFICA o estado do servidor —
# GET, por convenção, só lê dados
@app.post("/figurinhas/{figurinha_id}/colar")
def colar_figurinha(figurinha_id: int):
    figurinha = _encontrar(figurinha_id)
    figurinha["colada"] = True

    # Devolver a figurinha atualizada poupa o frontend de uma segunda
    # requisição só para saber como ela ficou
    return figurinha


# Descola a figurinha do álbum — o inverso da rota acima
@app.post("/figurinhas/{figurinha_id}/descolar")
def descolar_figurinha(figurinha_id: int):
    figurinha = _encontrar(figurinha_id)
    figurinha["colada"] = False

    return figurinha


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
    #
    # O Cache-Control existe por causa de um bug real: sem ele, o navegador
    # não sabe por quanto tempo a imagem vale e aplica um cache "por chute"
    # (cache heurístico) — guarda a resposta e serve dela sem sequer perguntar
    # ao servidor. Trocar o arquivo no disco não adiantava nada, a tela
    # continuava mostrando a imagem antiga.
    #
    # "no-cache" não quer dizer "não guarde": quer dizer "guarde, mas confirme
    # antes de usar". Na prática, aqui o navegador acaba baixando a imagem de
    # novo a cada carga, porque o FileResponse manda o ETag mas não trata o
    # If-None-Match que voltaria (quem faz isso no Starlette é o StaticFiles,
    # respondendo 304).
    #
    # Para um álbum servido em localhost esse rebaixamento não custa nada
    # perceptível, e garante que a imagem na tela é sempre a do disco
    return FileResponse(arquivos[0], headers={"Cache-Control": "no-cache"})
