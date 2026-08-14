# -*- coding: utf-8 -*-
"""Primitivas visuais compartilhadas por todos os formatos do feed.

Aqui mora o que faz o grid parecer UM sistema e nao um monte de post avulso:
mesma margem, mesma escala tipografica, mesmo selo no mesmo lugar, mesmo grao
por cima. Trocar um valor daqui muda o feed inteiro de uma vez — que e
exatamente o que um perfil de marca precisa.

O grao (`grao`) e o detalhe que mais separa "arte de marca" de "template de
Canva": fundo chapado em JPEG banda (faixas visiveis no degrade) e denuncia
montagem; 3,5% de ruido quebra a banda e da textura de papel.
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFilter

from tipografia import serif, sans, Cor

SELO = "@aurabelastore_on"
MARGEM = 110


# --------------------------------------------------------------------- tons
class Tom:
    """Fundos do sistema. Cada tom leva junto a cor de texto e de acento.

    Sao quatro para o grid ter RITMO: dois claros, um medio e um escuro. Nove
    posts seguidos no mesmo tom viram uma parede — a curadoria alterna.
    """
    AREIA = {
        "nome": "areia", "claro": True,
        "fundo": (236, 226, 216), "fundo2": (245, 238, 231),
        "texto": Cor.CAFE, "fraco": Cor.CAFE_CLARO, "acento": Cor.ROSA_FORTE,
    }
    ROSE = {
        "nome": "rose", "claro": True,
        "fundo": (238, 218, 214), "fundo2": (247, 233, 229),
        "texto": (92, 55, 55), "fraco": (140, 100, 98), "acento": Cor.CAFE,
    }
    CREME = {
        "nome": "creme", "claro": True,
        "fundo": (247, 242, 238), "fundo2": (252, 249, 246),
        "texto": Cor.CAFE, "fraco": Cor.CAFE_CLARO, "acento": Cor.DOURADO,
    }
    CAFE = {
        "nome": "cafe", "claro": False,
        "fundo": (58, 45, 40), "fundo2": (78, 61, 54),
        "texto": (247, 242, 238), "fraco": (206, 189, 178), "acento": Cor.NUDE,
    }

    TODOS = [AREIA, ROSE, CREME, CAFE]

    @staticmethod
    def por_nome(nome: str | None) -> dict:
        for t in Tom.TODOS:
            if t["nome"] == nome:
                return t
        return Tom.AREIA


# --------------------------------------------------------------------- fundo
def fundo(larg: int, alt: int, tom: dict, diagonal: bool = True) -> Image.Image:
    """Degrade suave de canto a canto + grao. Nunca cor 100% chapada."""
    base = Image.new("RGB", (larg, alt), tom["fundo"])
    topo = Image.new("RGB", (larg, alt), tom["fundo2"])

    mask = Image.new("L", (larg, alt))
    px = mask.load()
    for y in range(alt):
        for x in range(0, larg, 8):
            v = ((x / larg) * 0.45 + (1 - y / alt) * 0.55) if diagonal else (1 - y / alt)
            val = int(max(0, min(1, v)) * 255)
            for dx in range(8):
                if x + dx < larg:
                    px[x + dx, y] = val
    mask = mask.filter(ImageFilter.GaussianBlur(24))

    base = Image.composite(topo, base, mask)
    return grao(base)


def grao(img: Image.Image, forca: float = 0.035) -> Image.Image:
    ruido = Image.effect_noise(img.size, 26).convert("RGB")
    return Image.blend(img, ruido, forca)


def vinheta(img: Image.Image, forca: int = 46) -> Image.Image:
    """Escurece as bordas de leve — segura o olho no centro da arte."""
    larg, alt = img.size
    mask = Image.new("L", (larg, alt), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-larg * 0.35, -alt * 0.25, larg * 1.35, alt * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(180)).point(
        lambda v: 255 - int((255 - v) * forca / 255))
    escuro = Image.new("RGB", (larg, alt), (0, 0, 0))
    return Image.composite(img, escuro, mask)


# --------------------------------------------------------------------- texto
def espacado(d: ImageDraw.ImageDraw, xy, texto: str, fonte, cor, tracking: float = 4.0,
             centro: bool = False) -> float:
    """Desenha com espacamento entre letras (o Pillow nao tem tracking).

    Rotulo em caixa alta sem tracking parece apertado e amador; com ~0.18em vira
    rotulo de revista. Devolve a largura ocupada."""
    larg = sum(d.textlength(c, font=fonte) + tracking for c in texto) - tracking
    x, y = xy
    if centro:
        x -= larg / 2
    for c in texto:
        d.text((x, y), c, font=fonte, fill=cor)
        x += d.textlength(c, font=fonte) + tracking
    return larg


def quebrar(d: ImageDraw.ImageDraw, texto: str, fonte, larg: int) -> list[str]:
    """Quebra respeitando '\n' explicito do banco."""
    linhas = []
    for bloco in texto.split("\n"):
        atual = ""
        for p in bloco.split():
            t = (atual + " " + p).strip()
            if d.textlength(t, font=fonte) <= larg:
                atual = t
            else:
                if atual:
                    linhas.append(atual)
                atual = p
        linhas.append(atual)
    return linhas


def bloco(d: ImageDraw.ImageDraw, texto: str, fonte, cor, x: int, y: int, larg: int,
          entrelinha: float = 1.16, centro: bool = False) -> int:
    linhas = quebrar(d, texto, fonte, larg)
    lh = int(fonte.size * entrelinha)
    for ln in linhas:
        px = x + (larg - d.textlength(ln, font=fonte)) / 2 if centro else x
        d.text((px, y), ln, font=fonte, fill=cor)
        y += lh
    return y


def altura(d: ImageDraw.ImageDraw, texto: str, fonte, larg: int,
           entrelinha: float = 1.16) -> int:
    return len(quebrar(d, texto, fonte, larg)) * int(fonte.size * entrelinha)


def caber(d: ImageDraw.ImageDraw, texto: str, larg: int, alt_max: int,
          tamanhos: list[int], peso: int = 800, evitar_orfao: bool = False):
    """Maior corpo serif em que o texto ainda cabe na caixa.

    Escala fixa por contagem de caracteres quebra quando o texto tem palavra
    longa ou quebra de linha; medir de verdade e o unico jeito de nunca estourar.

    `evitar_orfao` desce um degrau quando a ultima linha ficaria com uma palavra
    solta ("Sérum Facial Renovador C + / E" — o 'E' sozinho parecia erro).
    """
    cabem = [serif(t, peso) for t in tamanhos
             if altura(d, texto, serif(t, peso), larg) <= alt_max]
    if not cabem:
        return serif(tamanhos[-1], peso)
    if evitar_orfao:
        for f in cabem:
            linhas = quebrar(d, texto, f, larg)
            if len(linhas) == 1 or len(linhas[-1].split()) > 1:
                return f
    return cabem[0]


# --------------------------------------------------------------------- selo
def selo(d: ImageDraw.ImageDraw, tom: dict, larg: int, alt: int,
         rodape: str | None = None) -> None:
    """Assinatura fixa no rodape: @ na esquerda, CTA curto na direita.

    Sempre na mesma altura em TODOS os formatos — e o que costura o grid."""
    y = alt - 84
    w_selo = espacado(d, (MARGEM, y), SELO, sans(26, 600), tom["fraco"], 2.2)
    if not rodape:
        return

    # O rodape encolhe ate caber sem encostar no @ — CTA longo ("compartilha com
    # quem precisa") colava nos dois textos e parecia uma linha so.
    disponivel = larg - 2 * MARGEM - w_selo - 46
    txt = rodape.upper()
    for corpo in (26, 24, 22, 20, 18):
        f = sans(corpo, 700)
        w = sum(d.textlength(c, font=f) + 2.2 for c in txt) - 2.2
        if w <= disponivel or corpo == 18:
            espacado(d, (larg - MARGEM - w, y + (26 - corpo) // 2), txt, f,
                     tom["acento"], 2.2)
            return


def filete(d: ImageDraw.ImageDraw, x: int, y: int, larg: int, cor, esp: int = 3) -> None:
    d.line((x, y, x + larg, y), fill=cor, width=esp)


def salvar(img: Image.Image, destino: str) -> str:
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    img.convert("RGB").save(destino, "JPEG", quality=94, subsampling=0, optimize=True)
    return destino
