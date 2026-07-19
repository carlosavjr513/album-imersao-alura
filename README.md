# Alura Album — Copa do Mundo Tech

Álbum de figurinhas digital e interativo, feito durante a **Imersão Alura (Julho/2026)**. Reúne 30 nomes que marcaram a história da tecnologia — de Alan Turing aos criadores de conteúdo tech do Brasil — em um livro folheável no navegador, com animação de virada de página em 3D e som sintetizado de papel.

A identidade visual é inspirada em Transformers: um botão alterna o álbum inteiro entre as facções **Autobot** (azul/vermelho, páginas brancas) e **Decepticon** (roxo/prata, páginas pretas).

O último slot (`#30`) é reservado: é onde você cola a sua própria figurinha.

## Objetivo

Construir um frontend estático que renderiza o álbum e, em seguida, consumir uma API para preencher os slots vazios com as imagens das figurinhas. A parte visual funciona sozinha; a API apenas popula as imagens.

## Estrutura

```
frontend/
├── index.html   # Estrutura do álbum: capa, 6 páginas, contracapa
├── style.css    # Todo o visual, animações e responsividade
└── app.js       # Interação (folhear, som, teclado) + consumo da API

backend/
├── main.py      # Servidor FastAPI
└── venv/        # Ambiente virtual Python (não versionado)
```

### `frontend/index.html`

Define a marcação de todas as páginas do livro. Cada `div.page` é uma folha carregada pela biblioteca PageFlip; capa e contracapa usam `data-density="hard"` para simular papelão rígido.

- **Página 0 — Capa:** título com efeito glitch, esfera 3D animada e mini-cards flutuantes.
- **Páginas 1–6 — Conteúdo:** agrupadas por tema (IA, Python, Banco de Dados, Sistemas Operacionais, Brasil Vol. 1 e Vol. 2), 5 figurinhas cada.
- **Página 7 — Contracapa:** resumo do projeto e código de barras decorativo.

Cada figurinha é um `div.sticker-slot` contendo `.slot-number` (`#01`…`#30`), `.slot-name` e `.slot-role`. O número do slot é o que amarra o HTML à API — o JavaScript usa ele como chave de busca.

Também carrega os controles de UI (botões de som e navegação) e, no fim do `body`, a lib [page-flip 2.0.7](https://cdn.jsdelivr.net/npm/page-flip@2.0.7/) via CDN seguida do `app.js`.

### `frontend/style.css`

Folha de estilo única, organizada em blocos comentados:

| Bloco | O que faz |
|---|---|
| Camada 1 — paletas cruas | Valores fixos de cor (azuis, vermelhos, roxos, prata). Nenhuma regra os consome direto |
| Camada 2 — tokens semânticos | O que as regras realmente usam. Trocar de facção = trocar o valor destes tokens |
| Sound & Navigation UI | Botões flutuantes de som, facção e setas |
| Album Layout / Pages | Container do livro, fundo das páginas, sombras da lombada |
| Stickers Grid & Slots | Grade das figurinhas e o estado vazio (tracejado) |
| Slot preenchido | Ao carregar a imagem, esconde número/função, mostra a foto com o nome sobreposto e roda a animação de "colar" |
| Capa / Contracapa | Efeito glitch no título, esfera com anéis orbitais, código de barras |
| Responsiveness | Adapta o livro para telas menores |

#### Sistema de temas

O visual é controlado por duas camadas de variáveis CSS. As regras nunca escrevem uma cor literal — consomem tokens como `--theme-primary`, `--page-bg` ou `--theme-glow`. O tema Decepticon é só um bloco `[data-theme="decepticon"]` que redefine esses tokens.

Cores com transparência usam triplets RGB (`rgb(var(--rgb-primary-bright) / 0.15)`) para que o alpha também acompanhe o tema.

Dois detalhes que não são simples troca de cor:

- **Sombra da lombada** — sobre página preta, uma sombra preta some. Os tokens `--page-crease` / `--page-crease-max` invertem a dobra para luz no tema escuro.
- **Código de barras** — o retângulo branco fixo viraria um borrão na contracapa escura, então `--barcode-bg` / `--barcode-ink` se invertem.

### `frontend/app.js`

Concentra toda a lógica. Cinco responsabilidades:

**0. Troca de facção — `aplicarTema()`**

Escreve `data-theme` no `<html>` e salva em `localStorage`. Não conhece nenhuma cor: o CSS resolve tudo pelas variáveis. Como custom properties são herdadas pela árvore inteira, as páginas continuam recebendo os tokens mesmo depois da lib PageFlip movê-las para a estrutura DOM dela — nenhum re-init é necessário.

O acesso ao `localStorage` fica em `try/catch` (lança em modo privativo / `file://`). Um script inline no `<head>` do `index.html` reaplica a facção salva **antes do primeiro paint**, senão quem escolheu Decepticon vê o álbum branco piscar a cada reload.


**1. Consumo da API — `preencherFigurinhas()`**

Faz `GET {API_BASE_URL}/figurinhas`, monta um `Map` de `id → figurinha` e percorre os `.sticker-slot` do HTML. Para cada slot, extrai o número (`"#01"` → `1`) e, se houver figurinha correspondente, injeta um `<img>` apontando para `imagem_url`. A classe `slot-preenchido` só é aplicada no `onload`, então imagem quebrada nunca vira slot "colado".

A chamada é envolvida em `try/catch`: se a API estiver fora do ar, o álbum continua funcionando vazio e o console avisa como subir o backend.

```js
const API_BASE_URL = "http://localhost:8000";
```

Formato esperado da resposta:

```json
[{ "id": 1, "nome": "Alan Turing", "imagem_url": "/imgs/01-alan-turing.jpg" }]
```

**2. Inicialização do PageFlip**

Instancia `St.PageFlip` com `size: "stretch"` e carrega as páginas via `loadFromHTML()`. Os gestos nativos são desligados de propósito (`useMouseEvents: false`, `disableFlipByClick: true`, `showPageCorners: false`) para evitar viradas acidentais ao clicar.

**3. Arraste customizado**

Como os gestos padrão estão desativados, o arraste é reimplementado à mão. Em `mousedown`/`touchstart` grava-se a posição inicial; a virada só dispara depois de mover mais de **10px** — abaixo disso é clique, não arraste. O canto da dobra é escolhido pela posição do ponteiro (topo/base) e pela paridade do índice da página (direita/esquerda), e então é chamado `startUserTouch` → `userMove` → `userStop`.

**4. Som de virada — `playPaperTurnSound()`**

O som não é um arquivo: é gerado em tempo real com a Web Audio API. Ruído branco recebe um envelope de volume que sobe em 30% da duração e decai, mais estalos aleatórios simulando atrito do papel. Passa por um filtro *bandpass* com varredura de 1500Hz → 350Hz (o "whoosh" da página se afastando) e um *lowpass* em 3800Hz para tirar aspereza digital. Disparado no evento `changeState === "flipping"` e silenciável pelo botão de som.

### `backend/main.py`

API em FastAPI. Por enquanto só tem o endpoint raiz:

| Método | Rota | Retorno |
|---|---|---|
| `GET` | `/` | `{"mensagem": "Olá, mundo! 🌍"}` |

O endpoint `/figurinhas` que o `app.js` consome ainda não existe — enquanto isso, o álbum abre com os slots vazios.

## Como rodar

### Backend

Na primeira vez, criar o ambiente virtual e instalar as dependências:

```bash
cd backend
python -m venv venv
```

Ativar a venv (o comando muda conforme o terminal):

```powershell
# PowerShell
.\venv\Scripts\Activate.ps1
```

```cmd
:: CMD
venv\Scripts\activate.bat
```

```bash
# Git Bash / Linux / macOS
source venv/bin/activate      # no Windows: source venv/Scripts/activate
```

Com a venv ativa (o prompt passa a mostrar `(venv)`), instalar e subir o servidor:

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

A API sobe em `http://localhost:8000`. A flag `--reload` reinicia o servidor a cada alteração no código.

Para sair da venv: `deactivate`.

> No PowerShell, se a ativação for bloqueada por política de execução, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Documentação automática

O FastAPI gera a documentação da API sozinho, a partir das assinaturas das funções — não há nada a escrever à mão. Com o servidor rodando:

| URL | O que é |
|---|---|
| `http://localhost:8000/docs` | **Swagger UI** — lista os endpoints e permite testá-los pelo navegador, com o botão *Try it out* |
| `http://localhost:8000/redoc` | **ReDoc** — a mesma documentação em formato de leitura, mais adequada para consulta |
| `http://localhost:8000/openapi.json` | O esquema **OpenAPI** cru, usado por ambas as páginas e por geradores de client |

### Frontend

O frontend é estático — basta servi-lo por HTTP (abrir o arquivo direto via `file://` quebra o `fetch`). Em outro terminal:

```bash
cd frontend
python -m http.server 5500
```

Acesse `http://localhost:5500`.

Sem backend rodando, o álbum abre com todos os slots vazios. Com a API disponível em `http://localhost:8000`, as figurinhas são coladas automaticamente.

## Controles

| Ação | Como |
|---|---|
| Virar página | Arrastar a página, setas laterais ou `←` / `→` |
| Ligar/desligar som | Botão de alto-falante no canto |
| Trocar de facção | Botão com o símbolo Autobot/Decepticon, à esquerda do som |

## Temas

| | Autobot (padrão) | Decepticon |
|---|---|---|
| Primária | azul | roxo |
| Acento | vermelho | prata/cinza |
| Páginas | branco | preto |
| Glow da capa | ciano | violeta |

A escolha persiste entre visitas. Os símbolos das facções são SVGs inline desenhados em versão geométrica simplificada — o projeto não usa nenhum asset externo nem a arte oficial da Hasbro.
