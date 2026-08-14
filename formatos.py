# -*- coding: utf-8 -*-
"""Os formatos de arte do feed — 1080x1350 (4:5).

Regra que criou este arquivo: o rosto da Marcia e um ativo ESCASSO (10 fotos) e
estava sendo gasto em 100% das pecas. Aqui entram os formatos que NAO consomem o
rosto dela e que sustentam o feed no dia a dia:

    frase    — cartao tipografico (autocuidado, frase de beleza)
    produto  — packshot Mary Kay sobre fundo de cor (o pilar produto)
    ritual   — passo a passo numerado, o "educativo que se salva"
    mito     — mito x verdade, o formato que mais se compartilha
    dado     — um numero grande + a explicacao (autoridade em 1 segundo)
    retrato  — a foto real dela, sangrando na peca inteira — RARO

Todos usam as mesmas primitivas de `arte.py`, entao mudam juntos e o grid
continua parecendo um sistema so.
"""
from __future__ import annotations

import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import arte
from arte import Tom, MARGEM
from tipografia import serif, sans, Cor

LARG, ALT = 1080, 1350
BASE = os.path.dirname(os.path.abspath(__file__))
PRODUTOS = os.path.join(BASE, "produtos")


# --------------------------------------------------------------------- frase
def frase(texto: str, destino: str, tom: dict = Tom.AREIA, etiqueta: str | None = None,
          rodape: str | None = None, assinatura: str | None = None) -> str:
    """Cartao tipografico. Sem foto nenhuma — puro texto respirando.

    E o formato mais barato de produzir e o que mais salva quando a frase e boa.
    A aspa ornamental grande em marca d'agua da o ar editorial; o texto fica
    centrado no eixo optico (um pouco acima do centro geometrico), que e onde o
    olho espera encontrar num cartao.
    """
    img = arte.fundo(LARG, ALT, tom)
    d = ImageDraw.Draw(img)

    larg_txt = LARG - 2 * MARGEM
    f = arte.caber(d, texto, larg_txt, 620, [92, 80, 70, 62, 54])
    h_texto = arte.altura(d, texto, f, larg_txt, 1.22)

    # O bloco inteiro (aspa + texto + filete + assinatura) e centrado como UMA
    # peca no eixo optico (48% da altura, nao 50%): ancorar so o texto deixava um
    # vazio grande embaixo, o defeito da 1a amostra.
    h_bloco = 250 + h_texto + 57 + (44 if assinatura else 0)
    y_topo = max(190, int(ALT * 0.48 - h_bloco / 2))

    fa = serif(300, 900)
    caixa = d.textbbox((0, 0), "“", font=fa)
    d.text((MARGEM - 12 - caixa[0], y_topo + 60 - caixa[1]), "“", font=fa,
           fill=_mistura(tom["fundo"], tom["texto"], 0.11))

    if etiqueta:
        arte.espacado(d, (MARGEM, y_topo - 62), etiqueta.upper(), sans(27, 700),
                      tom["acento"], 4.6)

    y = arte.bloco(d, texto, f, tom["texto"], MARGEM, y_topo + 250, larg_txt, 1.22)

    arte.filete(d, MARGEM, y + 54, 96, tom["acento"])
    if assinatura:
        arte.espacado(d, (MARGEM, y + 92), assinatura.upper(), sans(25, 600),
                      tom["fraco"], 3.4)

    arte.selo(d, tom, LARG, ALT, rodape)
    return arte.salvar(img, destino)


# ------------------------------------------------------------------- produto
def produto(arquivo: str, nome: str, destino: str, beneficio: str | None = None,
            linha: str | None = None, tom: dict = Tom.CREME,
            rodape: str | None = None) -> str:
    """Packshot oficial sobre fundo de cor — composto em MULTIPLY.

    Multiply e o truque que resolve packshot de e-commerce: o branco do estudio
    vira transparente sozinho (branco x fundo = fundo), a sombra cinza do
    proprio packshot vira sombra de verdade sobre a cor, e a tampa branca do
    frasco continua inteira — coisa que nenhum recorte automatico entrega.

    O preco: so funciona sobre fundo CLARO. Em fundo cafe a peca inteira
    escureceria, entao o tom escuro e trocado antes de compor.
    """
    if not tom["claro"]:
        tom = Tom.CREME

    img = arte.fundo(LARG, ALT, tom)

    # halo tonal atras do produto: separa o frasco do fundo sem moldura
    halo = Image.new("L", (LARG, ALT), 0)
    ImageDraw.Draw(halo).ellipse((LARG * 0.10, 200, LARG * 0.90, 200 + 700), fill=255)
    halo = halo.filter(ImageFilter.GaussianBlur(90))
    img = Image.composite(
        Image.new("RGB", (LARG, ALT), _mistura(tom["fundo"], tom["acento"], 0.14)),
        img, halo)

    caminho = arquivo if os.path.isabs(arquivo) else os.path.join(PRODUTOS, arquivo)
    pack = Image.open(caminho).convert("RGB")
    alvo_h = 660
    escala = min(alvo_h / pack.height, (LARG - 2 * MARGEM - 60) / pack.width)
    pack = pack.resize((max(1, round(pack.width * escala)),
                        max(1, round(pack.height * escala))), Image.LANCZOS)

    px = (LARG - pack.width) // 2
    py = 220 + (alvo_h - pack.height) // 2
    caixa = (px, py, px + pack.width, py + pack.height)
    img.paste(ImageChops.multiply(img.crop(caixa), pack), caixa)

    d = ImageDraw.Draw(img)

    if linha:
        arte.espacado(d, (LARG / 2, 160), linha.upper(), sans(27, 700),
                      tom["acento"], 5.0, centro=True)

    # O nome nao repete a linha que ja esta no rotulo em cima ("TimeWise" duas
    # vezes na mesma arte parecia erro de montagem).
    if linha:
        nome = " ".join(p for p in nome.split()
                        if p.lower().strip("®™") != linha.lower().strip("®™")).strip()

    larg_txt = LARG - 2 * MARGEM
    fn = arte.caber(d, nome, larg_txt, 190, [62, 54, 48, 42, 38], evitar_orfao=True)
    y = arte.bloco(d, nome, fn, tom["texto"], MARGEM, 972, larg_txt, 1.14,
                   centro=True)

    if beneficio:
        arte.bloco(d, beneficio, sans(31, 500), tom["fraco"], MARGEM, y + 24,
                   larg_txt, 1.34, centro=True)

    arte.selo(d, tom, LARG, ALT, rodape)
    return arte.salvar(img, destino)


# --------------------------------------------------------------------- ritual
def ritual(titulo: str, passos: list[str], destino: str, tom: dict = Tom.CREME,
           etiqueta: str = "rotina", rodape: str | None = "salva pra não esquecer") -> str:
    """Passo a passo numerado — a peca que a pessoa salva para consultar depois.

    Numero em serif grande no acento, texto em sans, filete separando: e o
    layout de infografico de revista, e le em 2 segundos no feed.
    """
    img = arte.fundo(LARG, ALT, tom)
    d = ImageDraw.Draw(img)
    arte.espacado(d, (MARGEM, 128), etiqueta.upper(), sans(27, 700),
                  tom["acento"], 4.6)

    larg_txt = LARG - 2 * MARGEM
    ft = arte.caber(d, titulo, larg_txt, 240, [74, 64, 56, 48])
    y = arte.bloco(d, titulo, ft, tom["texto"], MARGEM, 186, larg_txt, 1.14)

    # A lista OCUPA o espaco que sobra em vez de usar altura fixa: com 3 passos
    # o rodape ficava boiando a 400px do ultimo item.
    y += 56
    disponivel = (ALT - 160) - y
    passo_h = max(96, int(disponivel / max(1, len(passos))))
    y += max(0, (disponivel - passo_h * len(passos)) // 2)

    fn = serif(min(72, max(40, int(passo_h * 0.44))), 800)
    fp = sans(min(34, max(26, int(passo_h * 0.225))), 500)
    linha_cor = _mistura(tom["fundo"], tom["texto"], 0.16)

    for i, p in enumerate(passos, 1):
        arte.filete(d, MARGEM, y, larg_txt, linha_cor, 2)
        alto_txt = arte.altura(d, p, fp, larg_txt - 96, 1.24)
        centro = y + (passo_h - alto_txt) / 2
        # topo do algarismo alinhado com o topo da 1a linha do texto
        cx = d.textbbox((0, 0), f"{i}", font=fn)
        d.text((MARGEM, centro + fp.size * 0.16 - cx[1]), f"{i}", font=fn,
               fill=tom["acento"])
        arte.bloco(d, p, fp, tom["texto"], MARGEM + 96, centro, larg_txt - 96, 1.24)
        y += passo_h

    arte.selo(d, tom, LARG, ALT, rodape)
    return arte.salvar(img, destino)


# ----------------------------------------------------------------------- mito
def mito(mito_txt: str, verdade: str, destino: str,
         rodape: str | None = "compartilha com quem precisa") -> str:
    """Bloco escuro (mito) sobre bloco claro (verdade).

    Contraste em bloco e o formato que mais viaja em compartilhamento: a pessoa
    reconhece o proprio erro na metade de cima e manda para a amiga.
    """
    corte = int(ALT * 0.46)
    escuro = arte.fundo(LARG, corte, Tom.CAFE, diagonal=False)
    claro = arte.fundo(LARG, ALT - corte, Tom.AREIA, diagonal=False)
    img = Image.new("RGB", (LARG, ALT))
    img.paste(escuro, (0, 0))
    img.paste(claro, (0, corte))

    d = ImageDraw.Draw(img)
    larg_txt = LARG - 2 * MARGEM

    # Cada metade centra o proprio conteudo (rotulo + texto): ancorar no topo
    # deixava um buraco no pe de cada bloco quando o texto era curto.
    fm = arte.caber(d, mito_txt, larg_txt, corte - 250, [70, 60, 52, 46])
    hm = arte.altura(d, mito_txt, fm, larg_txt) + 68
    ym = max(96, int((corte - hm) / 2))
    arte.espacado(d, (MARGEM, ym), "MITO", sans(28, 700), Tom.CAFE["acento"], 6.0)
    arte.bloco(d, mito_txt, fm, Tom.CAFE["texto"], MARGEM, ym + 68, larg_txt, 1.16)

    fv = arte.caber(d, verdade, larg_txt, ALT - corte - 250, [70, 60, 52, 46, 40])
    hv = arte.altura(d, verdade, fv, larg_txt) + 68
    yv = corte + max(78, int((ALT - corte - 120 - hv) / 2))
    arte.espacado(d, (MARGEM, yv), "VERDADE", sans(28, 700), Tom.AREIA["acento"], 6.0)
    arte.bloco(d, verdade, fv, Tom.AREIA["texto"], MARGEM, yv + 68, larg_txt, 1.16)

    arte.selo(d, Tom.AREIA, LARG, ALT, rodape)
    return arte.salvar(img, destino)


# ----------------------------------------------------------------------- dado
def dado(numero: str, texto: str, destino: str, tom: dict = Tom.CAFE,
         etiqueta: str | None = None, rodape: str | None = None) -> str:
    """Um numero enorme + a frase que o explica. Autoridade em 1 segundo de scroll."""
    img = arte.vinheta(arte.fundo(LARG, ALT, tom))
    d = ImageDraw.Draw(img)

    larg_txt = LARG - 2 * MARGEM - 40
    fn = serif(300 if len(numero) <= 3 else 220, 900)
    f = arte.caber(d, texto, larg_txt, 340, [58, 50, 44, 38], peso=600)

    # Bloco unico (rotulo + numero + filete + frase) centrado no eixo optico.
    h_num = fn.size * 0.78
    h_txt = arte.altura(d, texto, f, larg_txt, 1.28)
    h_bloco = 78 + h_num + 96 + h_txt
    y = max(150, int(ALT * 0.47 - h_bloco / 2))

    if etiqueta:
        arte.espacado(d, (LARG / 2, y), etiqueta.upper(), sans(27, 700),
                      tom["acento"], 5.0, centro=True)
    y += 78

    caixa = d.textbbox((0, 0), numero, font=fn)
    d.text(((LARG - (caixa[2] - caixa[0])) / 2 - caixa[0], y - caixa[1]), numero,
           font=fn, fill=tom["texto"])
    y += h_num + 48

    arte.filete(d, (LARG - 96) // 2, int(y), 96, tom["acento"])
    y += 48

    arte.bloco(d, texto, f, tom["fraco"], MARGEM + 20, int(y), larg_txt, 1.28,
               centro=True)

    arte.selo(d, tom, LARG, ALT, rodape)
    return arte.salvar(img, destino)


# ------------------------------------------------------------------- retrato
def retrato(foto: str, gancho: str, destino: str, etiqueta: str | None = None,
            rodape: str | None = None, foco_y: float = 0.34) -> str:
    """A foto real dela, sangrando na peca inteira. Formato RARO — ver curadoria.py.

    Reescrito sobre `arte.py` (nao mais sobre gerar_estatico.capa) para o selo
    cair na MESMA linha dos outros formatos: no grid, um post com a assinatura
    fora de lugar denuncia que sao dois sistemas diferentes.
    """
    from foto import tratar, cobrir

    base = cobrir(tratar(Image.open(foto)), LARG, ALT, foco_y)

    # veu de baixo para cima (texto) + toque no topo (respiro)
    # O veu tem de estar CHEIO onde o texto comeca (~68% da altura), nao so no
    # rodape: na 1a versao o gancho caia sobre uma blusa clara e sumia.
    veu = Image.new("L", (1, ALT), 0)
    px = veu.load()
    inicio, fim = int(ALT * 0.34), int(ALT * 0.68)
    for y in range(ALT):
        if y <= inicio:
            v = 0
        elif y >= fim:
            v = 234
        else:
            v = int((((y - inicio) / (fim - inicio)) ** 1.2) * 234)
        if y < 150:
            v = max(v, int((1 - y / 150) * 70))
        px[0, y] = v
    base = Image.composite(Image.new("RGB", (LARG, ALT), Cor.PRETO_SUAVE), base,
                           veu.resize((LARG, ALT)))

    d = ImageDraw.Draw(base)
    tom = Tom.CAFE
    larg_txt = LARG - 2 * MARGEM

    fg = arte.caber(d, gancho, larg_txt, 400, [88, 76, 66, 58, 50])
    y = ALT - 150 - arte.altura(d, gancho, fg, larg_txt, 1.14)
    if etiqueta:
        arte.espacado(d, (MARGEM, y - 62), etiqueta.upper(), sans(27, 700),
                      Cor.NUDE, 4.6)
    arte.bloco(d, gancho, fg, (255, 255, 255), MARGEM, y, larg_txt, 1.14)

    arte.selo(d, tom, LARG, ALT, rodape)
    return arte.salvar(base, destino)


# ------------------------------------------------------------------ utilidade
def _mistura(a, b, t: float):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
