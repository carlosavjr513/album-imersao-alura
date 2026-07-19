# Transformers Album — Três Eras, Duas Facções

Álbum de figurinhas digital e interativo, feito durante a **Imersão Alura (Julho/2026)**. Reúne 30 personagens das três séries animadas que definiram a guerra por Cybertron, em um livro folheável no navegador com virada de página em 3D e som de papel sintetizado.

Clicar no número de um slot **cola** a figurinha; um `×` no canto **descola**. Um contador no topo mostra o quanto falta para completar o álbum.

## Objetivo

Frontend estático que renderiza o álbum, consumindo uma API FastAPI que guarda o estado de cada figurinha. A navegação do livro funciona sozinha; a API cuida de colar, descolar e contar.

## Estrutura

```
backend/
├── main.py       # API FastAPI: lista, cola, descola e conta
└── figurinhas/   # 30 imagens, uma por personagem

frontend/
├── index.html   # Estrutura do álbum: capa, 6 páginas, contracapa
├── style.css    # Tokens de tema, visual, animações e responsividade
└── app.js       # Interação (folhear, som, colar/descolar) + consumo da API
```

## O álbum

Páginas ímpares são Autobots (ou o equivalente da série). Páginas pares, Decepticons.

| Pág | Série | Facção | # | Personagens |
|---|---|---|---|---|
| 1 | Transformers G1 | Autobots | 01-05 | Optimus Prime, Bumblebee, Jazz, Ironhide, Grimlock |
| 2 | Transformers G1 | Decepticons | 06-10 | Megatron, Starscream, Soundwave, Shockwave, Devastator |
| 3 | Beast Wars | Maximals | 11-15 | Optimus Primal, Cheetor, Rattrap, Rhinox, Dinobot |
| 4 | Beast Wars | Predacons | 16-20 | Megatron, Waspinator, Tarantulas, Blackarachnia, Inferno |
| 5 | Robots in Disguise (2000) | Autobots | 21-25 | Optimus Prime, Side Burn, Prowl, X-Brawn, Ultra Magnus |
| 6 | Robots in Disguise (2000) | Predacons | 26-30 | Megatron, Sky-Byte, Slapper, Gas Skunk, Dark Scream |

### Sobre as imagens

As imagens ficam em `backend/figurinhas/`, uma por personagem, com o número na frente do nome:

```
01-optimus-prime.jpg
27-sky-byte.jpg
```

O que importa é o **número de dois dígitos no começo** — o resto do nome e a extensão são livres. A rota de imagem monta o padrão `{id:02d}[!0-9]*` e procura por glob, então trocar uma figurinha é só substituir o arquivo.

Transformers é propriedade da Hasbro; a arte aqui é de uso pessoal, para estudo.

## Como rodar

Dois servidores. Primeiro o backend:

```bash
cd backend
uvicorn main:app --reload          # :8000
```

Depois o frontend, em outro terminal (abrir o arquivo direto via `file://` quebra o `fetch`):

```bash
cd frontend
python -m http.server 5500         # :5500
```

Acesse `http://localhost:5500`. Sem o backend no ar, o álbum ainda folheia — o contador mostra `--/30` e colar não funciona.

---

## `backend/main.py`

As 30 figurinhas ficam **sempre** na lista, cada uma com um campo `colada` que começa `False`. O estado vive só na memória: reiniciar o `uvicorn` zera o álbum.

```python
{"id": 1, "nome": "Optimus Prime", "faccao": "Autobot", "serie": "G1",
 "papel": "Líder dos Autobots", "colada": False,
 "imagem_url": "/figurinhas/1/imagem"}
```

| Rota | O que faz |
|---|---|
| `GET /figurinhas` | Todas as 30, com o campo `colada` |
| `GET /figurinhas/total` | `{total_album, coladas, faltam}` |
| `GET /figurinhas/{id}` | Uma figurinha, ou 404 |
| `GET /figurinhas/{id}/imagem` | O arquivo de imagem |
| `POST /figurinhas/{id}/colar` | `colada = True` |
| `POST /figurinhas/{id}/descolar` | `colada = False` |

Colar e descolar são `POST` porque **modificam** o estado do servidor — `GET`, por convenção, só lê.

Dois detalhes que valem atenção:

- **Ordem das rotas.** `/figurinhas/total` precisa ser declarada antes de `/figurinhas/{id}`. O FastAPI testa na ordem de registro, e a rota dinâmica capturaria `"total"` tentando convertê-lo para `int` — respondendo 422.
- **`_encontrar()`.** A busca por id é usada por três rotas, então mora numa função só, que já levanta o 404.

## `frontend/index.html`

Cada `div.page` é uma folha carregada pela lib PageFlip; capa e contracapa usam `data-density="hard"` para simular papelão. Cada página interna declara sua facção:

```html
<div class="page page-left" data-faction="autobot">
```

E cada figurinha é um slot com dois botões:

```html
<div class="sticker-slot" data-id="1">
  <button class="slot-number">#01</button>   <!-- cola -->
  <button class="slot-remove">×</button>     <!-- descola -->
  <div class="slot-name">Optimus Prime</div>
  <div class="slot-role">Líder dos Autobots</div>
</div>
```

Serem `<button>` não é detalhe estético: o handler de arraste das páginas ignora cliques que venham de dentro de um botão, então clicar no número **não** vira a página.

## `frontend/style.css`

### Sistema de temas: dois eixos independentes

As regras nunca escrevem uma cor literal — consomem tokens. E os tokens se dividem em dois grupos que variam de forma independente:

**Eixo 1 — Facção (por página, fixo no HTML).** Controla o *matiz*: `--theme-primary`, `--theme-accent`, `--theme-glow`. Definido por `[data-faction]` em cada `.page`, então páginas ímpares e pares têm cores diferentes ao mesmo tempo.

**Eixo 2 — Modo (global, do botão).** Controla *claro/escuro*: `--page-bg`, `--page-text`, `--page-crease`, `--barcode-*`. Definido por `[data-mode]` no `<html>`, vindo do `localStorage`.

Como são independentes, uma página G1 Autobot em modo escuro fica **azul sobre preto** — o matiz da facção se mantém, só o papel inverte.

| | Autobot | Decepticon |
|---|---|---|
| Facção: primária | azul | roxo |
| Facção: acento | vermelho | prata |
| Facção: glow | ciano | violeta |
| Modo: páginas | branco | preto |

Cores com transparência usam triplets RGB (`rgb(var(--rgb-primary-bright) / 0.15)`) para o alpha também acompanhar o tema.

Dois casos que não são simples troca de cor:

- **Sombra da lombada** — sobre página preta, sombra preta some. `--page-crease` / `--page-crease-max` invertem a dobra para luz no modo escuro.
- **Código de barras** — o retângulo branco viraria um borrão na contracapa escura, então `--barcode-bg` / `--barcode-ink` se invertem.

## `frontend/app.js`

**1. Modo claro/escuro — `aplicarModo()`**

Escreve `data-mode` no `<html>` e salva em `localStorage`. Não conhece nenhuma cor. Como custom properties são herdadas pela árvore inteira, as páginas continuam recebendo os tokens mesmo depois da lib PageFlip movê-las — nenhum re-init é necessário.

Um script inline no `<head>` reaplica o modo salvo **antes do primeiro paint**, senão o álbum branco pisca a cada reload.

**2. Colar e descolar — `alternarFigurinha()`**

`POST` na rota e redesenho do slot a partir da resposta — o backend devolve a figurinha já atualizada, então o frontend não precisa adivinhar o que aconteceu.

Um único listener no `document` cobre os 60 botões por delegação. Fica no `document` porque a lib PageFlip realoca as `.page` no DOM.

**3. Contador — `atualizarContador()`**

Lê `GET /figurinhas/total` e escreve `${coladas}/${total_album}`. Chamado na carga e depois de cada colagem. `padStart` mantém `"02"` em vez de `"2"`, para o contador não mudar de largura e sacudir o layout.

**4. Inicialização do PageFlip**

`size: "stretch"` e páginas via `loadFromHTML()`. Os gestos nativos são desligados de propósito (`useMouseEvents: false`, `disableFlipByClick: true`) para evitar viradas acidentais.

**5. Arraste customizado**

Reimplementado à mão, já que os gestos padrão estão desligados. A virada só dispara depois de mover mais de **10px** — abaixo disso é clique, não arraste. O canto da dobra vem da posição do ponteiro e da paridade da página.

**6. Som de virada — `playPaperTurnSound()`**

Gerado em tempo real com a Web Audio API: ruído branco com envelope que sobe em 30% da duração e decai, mais estalos aleatórios simulando atrito. Passa por um *bandpass* varrendo 1500Hz → 350Hz e um *lowpass* em 3800Hz.

Todas as chamadas de rede ficam em `try/catch`: API fora do ar deixa o álbum navegável, com aviso no console.

## Controles

| Ação | Como |
|---|---|
| Virar página | Arrastar a página, setas laterais ou `←` / `→` |
| Colar figurinha | Clicar no número do slot |
| Descolar figurinha | Clicar no `×` no canto do slot |
| Modo claro/escuro | Botão com o símbolo Autobot/Decepticon |
| Ligar/desligar som | Botão de alto-falante no canto |

Os símbolos das facções são SVGs inline — o projeto não carrega nenhum asset externo além da fonte e da lib PageFlip.
