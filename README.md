# Alura Album — Copa do Mundo Tech

Álbum de figurinhas digital e interativo, feito durante a **Imersão Alura (Julho/2026)**. Reúne 30 nomes que marcaram a história da tecnologia — de Alan Turing aos criadores de conteúdo tech do Brasil — em um livro folheável no navegador, com animação de virada de página em 3D e som sintetizado de papel.

O último slot (`#30`) é reservado: é onde você cola a sua própria figurinha.

## Objetivo

Construir um frontend estático que renderiza o álbum e, em seguida, consumir uma API para preencher os slots vazios com as imagens das figurinhas. A parte visual funciona sozinha; a API apenas popula as imagens.

## Estrutura

```
frontend/
├── index.html   # Estrutura do álbum: capa, 6 páginas, contracapa
├── style.css    # Todo o visual, animações e responsividade
└── app.js       # Interação (folhear, som, teclado) + consumo da API
```

### `frontend/index.html`

Define a marcação de todas as páginas do livro. Cada `div.page` é uma folha carregada pela biblioteca PageFlip; capa e contracapa usam `data-density="hard"` para simular papelão rígido.

- **Página 0 — Capa:** título com efeito glitch, esfera 3D animada e mini-cards flutuantes.
- **Páginas 1–6 — Conteúdo:** agrupadas por tema (IA, Python, Banco de Dados, Sistemas Operacionais, Brasil Vol. 1 e Vol. 2), 5 figurinhas cada.
- **Página 7 — Contracapa:** resumo do projeto e código de barras decorativo.

Cada figurinha é um `div.sticker-slot` contendo `.slot-number` (`#01`…`#30`), `.slot-name` e `.slot-role`. O número do slot é o que amarra o HTML à API — o JavaScript usa ele como chave de busca.

Também carrega os controles de UI (botões de som e navegação) e, no fim do `body`, a lib [page-flip 2.0.7](https://cdn.jsdelivr.net/npm/page-flip@2.0.7/) via CDN seguida do `app.js`.

### `frontend/style.css`

Folha de estilo única (~980 linhas), organizada em blocos comentados:

| Bloco | O que faz |
|---|---|
| Sound & Navigation UI | Botões flutuantes de som e setas |
| Album Layout / Pages | Container do livro, textura de papel, sombras da lombada |
| Stickers Grid & Slots | Grade das figurinhas e o estado vazio (tracejado) |
| Slot preenchido | Ao carregar a imagem, esconde número/função, mostra a foto com o nome sobreposto e roda a animação de "colar" |
| Capa / Contracapa | Efeito glitch no título, esfera com anéis orbitais, código de barras |
| Responsiveness | Adapta o livro para telas menores |

### `frontend/app.js`

Concentra toda a lógica. Quatro responsabilidades:

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

## Como rodar

O frontend é estático — basta servi-lo por HTTP (abrir o arquivo direto via `file://` quebra o `fetch`):

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
