// ===================================================
// CONFIGURAÇÃO DA API
// Quando o frontend for servido pelo FastAPI (Dia 3), a API está
// no mesmo servidor — usamos uma URL relativa ou o endereço completo.
// ===================================================
const API_BASE_URL = "http://localhost:8000";

// ===================================================
// MODO CLARO / ESCURO
// Trocado só pelo atributo data-mode no <html>. O CSS resolve
// o resto via variáveis, então nada aqui precisa conhecer cores
// nem re-inicializar o PageFlip.
//
// Atenção: MODO não é FACÇÃO. A facção (azul Autobot / roxo
// Decepticon) é fixa por página, declarada no data-faction do
// HTML. O modo só decide se o papel é claro ou escuro.
// ===================================================
const MODO_KEY = "alura-album-modo";
const MODO_PADRAO = "autobot";

// ===================================================
// FIGURINHAS: colar, descolar e contar
// O estado de cada figurinha mora no backend. O frontend só
// dispara a ação e redesenha o slot com a resposta.
// ===================================================

// Acha o slot do álbum correspondente a um id de figurinha
function slotDe(id) {
    return document.querySelector(`.sticker-slot[data-id="${id}"]`);
}

// Insere a imagem no slot (o "colar" visual)
function pintarSlot(slot, figurinha) {
    // Evita empilhar imagens se a função for chamada duas vezes
    if (slot.querySelector(".sticker-img")) return;

    const img = document.createElement("img");
    img.src = `${API_BASE_URL}${figurinha.imagem_url}`;
    img.alt = figurinha.nome;
    img.className = "sticker-img";

    // A classe só entra quando a imagem realmente carregou: imagem
    // quebrada nunca deve virar um slot "colado"
    img.onload = () => slot.classList.add("slot-preenchido");
    img.onerror = () => {
        console.warn(`Imagem não encontrada: ${figurinha.nome}`);
        img.remove();
    };

    slot.insertBefore(img, slot.firstChild);
}

// Remove a imagem do slot (o "descolar" visual)
function limparSlot(slot) {
    const img = slot.querySelector(".sticker-img");
    if (img) img.remove();
    slot.classList.remove("slot-preenchido");
}

// Lê GET /figurinhas/total e escreve o contador no topo da tela.
// É o uso real do endpoint de estatísticas do backend
async function atualizarContador() {
    const alvo = document.getElementById("contador-valor");

    try {
        const response = await fetch(`${API_BASE_URL}/figurinhas/total`);

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }

        const { coladas, total_album } = await response.json();

        // padStart deixa "2" como "02", para o contador não mudar de
        // largura e sacudir o layout a cada figurinha colada
        alvo.textContent = `${String(coladas).padStart(2, "0")}/${total_album}`;

    } catch (erro) {
        // API fora do ar: o álbum continua navegável, só sem números
        alvo.textContent = "--/30";
    }
}

// Carrega o estado do álbum e desenha os slots já colados
async function carregarAlbum() {
    try {
        const response = await fetch(`${API_BASE_URL}/figurinhas`);

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }

        // A API devolve as 30 figurinhas sempre; o campo "colada"
        // é que diz quais já estão no álbum
        const figurinhas = await response.json();

        for (const figurinha of figurinhas) {
            const slot = slotDe(figurinha.id);
            if (!slot) continue;

            if (figurinha.colada) {
                pintarSlot(slot, figurinha);
            } else {
                limparSlot(slot);
            }
        }

    } catch (erro) {
        console.warn("⚠️  Não foi possível conectar à API do backend:", erro.message);
        console.info("ℹ️  Inicie o servidor: cd backend && uvicorn main:app --reload");
    }

    atualizarContador();
}

// Cola ou descola uma figurinha. As duas ações são a mesma requisição
// com um verbo diferente na URL, então uma função só dá conta
async function alternarFigurinha(id, acao) {
    try {
        const response = await fetch(`${API_BASE_URL}/figurinhas/${id}/${acao}`, {
            method: "POST",
        });

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }

        // O backend devolve a figurinha já atualizada, então o slot é
        // redesenhado a partir da verdade do servidor — e não de um
        // palpite do frontend sobre o que deveria ter acontecido
        const figurinha = await response.json();
        const slot = slotDe(id);

        if (figurinha.colada) {
            pintarSlot(slot, figurinha);
        } else {
            limparSlot(slot);
        }

        atualizarContador();

    } catch (erro) {
        console.warn(`⚠️  Não foi possível ${acao} a figurinha ${id}:`, erro.message);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const bookElement = document.getElementById("book");
    const btnPrev = document.getElementById("btn-prev");
    const btnNext = document.getElementById("btn-next");
    const soundToggle = document.getElementById("sound-toggle");
    const iconOn = soundToggle.querySelector(".sound-icon-on");
    const iconOff = soundToggle.querySelector(".sound-icon-off");

    const themeToggle = document.getElementById("theme-toggle");
    const iconAutobot = themeToggle.querySelector(".faction-icon-autobot");
    const iconDecepticon = themeToggle.querySelector(".faction-icon-decepticon");

    let isMuted = false;
    let pageFlip = null;

    // 0. Modo: aplica o modo salvo antes de montar o livro
    function aplicarModo(modo) {
        document.documentElement.dataset.mode = modo;

        // O ícone mostrado é o do modo ATIVO
        iconAutobot.classList.toggle("hidden", modo === "decepticon");
        iconDecepticon.classList.toggle("hidden", modo !== "decepticon");

        try {
            localStorage.setItem(MODO_KEY, modo);
        } catch (e) {
            console.warn("Não foi possível salvar o modo escolhido:", e.message);
        }
    }

    function lerModoSalvo() {
        try {
            return localStorage.getItem(MODO_KEY) || MODO_PADRAO;
        } catch (e) {
            return MODO_PADRAO;
        }
    }

    aplicarModo(lerModoSalvo());

    themeToggle.addEventListener("click", () => {
        const atual = document.documentElement.dataset.mode;
        aplicarModo(atual === "decepticon" ? "autobot" : "decepticon");
    });

    // 0.1 Colar / descolar figurinha.
    // Um listener só no documento, em vez de 60 (dois botões por slot).
    // Fica no document porque a lib PageFlip realoca as .page no DOM
    document.addEventListener("click", (e) => {
        const botaoColar = e.target.closest(".slot-number");
        if (botaoColar) {
            alternarFigurinha(botaoColar.closest(".sticker-slot").dataset.id, "colar");
            return;
        }

        const botaoDescolar = e.target.closest(".slot-remove");
        if (botaoDescolar) {
            alternarFigurinha(botaoDescolar.closest(".sticker-slot").dataset.id, "descolar");
        }
    });

    // 1. Initialize St.PageFlip
    try {
        pageFlip = new St.PageFlip(bookElement, {
            width: 550, // Base page width
            height: 800, // Base page height
            size: "stretch",
            minWidth: 315,
            maxWidth: 1000,
            minHeight: 420,
            maxHeight: 1350,
            drawShadow: true,
            maxShadowOpacity: 0.4, // Aumenta levemente contraste da sombra
            showCover: true,
            mobileScrollSupport: true,
            useMouseEvents: false, // Desativa gestos padrão do StPageFlip para evitar cliques indesejados nas bordas/páginas
            showPageCorners: false, // Remove dobras dos cantos no hover
            disableFlipByClick: true, // Garante que a virada por cliques simples esteja desativada
            flippingTime: 800 // Transição mais ágil e snappier (800ms em vez de 1000ms)
        });

        // Load pages from HTML
        pageFlip.loadFromHTML(document.querySelectorAll(".page"));

        // Estado de arraste personalizado
        let activeDragPage = null;
        let isClicking = false;
        let startX = 0;
        let startY = 0;
        let dragStarted = false;

        // Monitora o mousedown/touchstart em cada página para iniciar a intenção de arraste
        document.querySelectorAll(".page").forEach((page, index) => {
            page.addEventListener("mousedown", (e) => {
                if (e.target.closest("button") || e.target.closest("a")) return;
                isClicking = true;
                startX = e.clientX;
                startY = e.clientY;
                dragStarted = false;
                activeDragPage = { page, index };
            });

            page.addEventListener("touchstart", (e) => {
                if (e.target.closest("button") || e.target.closest("a")) return;
                const touch = e.touches[0];
                isClicking = true;
                startX = touch.clientX;
                startY = touch.clientY;
                dragStarted = false;
                activeDragPage = { page, index };
            });
        });

        // Executa o movimento de dobra apenas se o mouse/dedo se mover além de um limiar (threshold)
        const handleMove = (clientX, clientY, isTouch = false) => {
            if (!isClicking || !activeDragPage) return;
            
            const deltaX = clientX - startX;
            const deltaY = clientY - startY;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            
            const bookRect = bookElement.getBoundingClientRect();

            // Só ativa o flip se mover mais de 10px (evita disparar ao clicar e soltar estático)
            if (distance > 10 && !dragStarted) {
                dragStarted = true;
                let cornerX, cornerY;
                
                // Determina canto vertical (topo vs base) em coordenadas relativas ao livro
                const centerY = bookRect.top + bookRect.height / 2;
                if (startY < centerY) {
                    cornerY = 0; // Canto superior
                } else {
                    cornerY = bookRect.height; // Canto inferior
                }

                // Determina canto horizontal (direita vs esquerda) em coordenadas relativas ao livro
                if (activeDragPage.index % 2 === 0) {
                    cornerX = bookRect.width; // Canto direito
                } else {
                    cornerX = 0; // Canto esquerdo
                }
                
                document.body.classList.add("dragging");
                pageFlip.startUserTouch({ x: cornerX, y: cornerY });
            }
            
            if (dragStarted) {
                const relX = clientX - bookRect.left;
                const relY = clientY - bookRect.top;
                pageFlip.userMove({ x: relX, y: relY }, isTouch);
            }
        };

        const handleRelease = (clientX, clientY, isTouch = false) => {
            if (dragStarted) {
                const bookRect = bookElement.getBoundingClientRect();
                const relX = clientX - bookRect.left;
                const relY = clientY - bookRect.top;
                pageFlip.userStop({ x: relX, y: relY }, isTouch);
            }
            isClicking = false;
            dragStarted = false;
            activeDragPage = null;
            document.body.classList.remove("dragging");
        };

        window.addEventListener("mousemove", (e) => {
            handleMove(e.clientX, e.clientY, false);
        });

        window.addEventListener("touchmove", (e) => {
            if (e.touches.length > 0) {
                const touch = e.touches[0];
                handleMove(touch.clientX, touch.clientY, true);
            }
        });

        window.addEventListener("mouseup", (e) => {
            handleRelease(e.clientX, e.clientY, false);
        });

        window.addEventListener("touchend", (e) => {
            const touch = e.changedTouches[0] || e.touches[0];
            if (touch) {
                handleRelease(touch.clientX, touch.clientY, true);
            } else {
                handleRelease(startX, startY, true);
            }
        });

        // Show book after successful initialization
        bookElement.style.display = "block";

        // Busca o estado do álbum na API e preenche os slots já colados.
        // A função é async, chamamos sem await para não bloquear a inicialização do álbum
        carregarAlbum();

    } catch (error) {
        console.error("Erro ao inicializar a biblioteca PageFlip:", error);
    }

    // 2. Sound Effect Generator (Web Audio API)
    function playPaperTurnSound() {
        if (isMuted) return;

        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;

            const audioCtx = new AudioContext();
            const duration = 0.45; // seconds
            const sampleRate = audioCtx.sampleRate;
            const bufferSize = sampleRate * duration;
            const buffer = audioCtx.createBuffer(1, bufferSize, sampleRate);
            const data = buffer.getChannelData(0);

            // Synthesize white noise with a custom page-flip volume envelope
            for (let i = 0; i < bufferSize; i++) {
                const progress = i / bufferSize;
                // Noise value between -1 and 1
                const noise = Math.random() * 2 - 1;

                // Volume envelope: smooth curve that peaks around 30% of the duration
                let envelope = 0;
                if (progress < 0.3) {
                    envelope = progress / 0.3; // Rapid ramp up
                } else {
                    envelope = (1 - progress) / 0.7; // Smooth decay
                }

                // Add minor irregular spikes to simulate paper friction/crackle
                const paperCrackle = Math.random() > 0.985 ? (Math.random() * 2 - 1) * 0.35 : 0;

                data[i] = (noise * 0.65 + paperCrackle) * envelope * 0.12;
            }

            // Create nodes
            const noiseNode = audioCtx.createBufferSource();
            noiseNode.buffer = buffer;

            // Bandpass filter to extract the "whoosh" sound of paper shuffling
            const bandpassFilter = audioCtx.createBiquadFilter();
            bandpassFilter.type = "bandpass";
            bandpassFilter.Q.value = 2.0;

            // Dynamic frequency sweep: starts at 1500Hz, sweeps down to 350Hz (sound of page moving away)
            bandpassFilter.frequency.setValueAtTime(1500, audioCtx.currentTime);
            bandpassFilter.frequency.exponentialRampToValueAtTime(350, audioCtx.currentTime + duration);

            // Lowpass filter to remove harsh high-frequency digital artifacts
            const lowpassFilter = audioCtx.createBiquadFilter();
            lowpassFilter.type = "lowpass";
            lowpassFilter.frequency.setValueAtTime(3800, audioCtx.currentTime);

            // Connect graph: Source -> Bandpass -> Lowpass -> Destination
            noiseNode.connect(bandpassFilter);
            bandpassFilter.connect(lowpassFilter);
            lowpassFilter.connect(audioCtx.destination);

            noiseNode.start();
        } catch (e) {
            console.warn("Falha ao tocar som de virada de página:", e);
        }
    }

    // 3. Audio State Controls
    soundToggle.addEventListener("click", () => {
        isMuted = !isMuted;
        if (isMuted) {
            iconOn.classList.add("hidden");
            iconOff.classList.remove("hidden");
        } else {
            iconOn.classList.remove("hidden");
            iconOff.classList.add("hidden");
        }
    });

    // 4. Navigation controls and events
    if (pageFlip) {
        // Play turn sound when page starts flipping
        pageFlip.on("changeState", (e) => {
            if (e.data === "flipping") {
                playPaperTurnSound();
            }
        });

        // Discrete arrow toggle depending on current page
        pageFlip.on("flip", (e) => {
            const currentPage = e.data;
            const totalPages = pageFlip.getPageCount();

            // Hide left button on cover page
            if (currentPage === 0) {
                btnPrev.classList.add("hidden");
            } else {
                btnPrev.classList.remove("hidden");
            }

            // Hide right button on back cover
            if (currentPage === totalPages - 1) {
                btnNext.classList.add("hidden");
            } else {
                btnNext.classList.remove("hidden");
            }
        });

        // Click events for navigational arrows
        btnPrev.addEventListener("click", () => {
            pageFlip.flipPrev();
        });

        btnNext.addEventListener("click", () => {
            pageFlip.flipNext();
        });

        // Keyboard events for navigational arrows
        document.addEventListener("keydown", (e) => {
            if (e.key === "ArrowLeft") {
                pageFlip.flipPrev();
            } else if (e.key === "ArrowRight") {
                pageFlip.flipNext();
            }
        });

        // Hide left button initially since start page is 0
        btnPrev.classList.add("hidden");
    }
});
