# -*- coding: utf-8 -*-
"""Tratamento das FOTOS REAIS da Marcia (o unico insumo do projeto que acaba).

Era `gerar_estatico.py`, que tambem carregava os dois templates antigos (`capa`
e `editorial`). Os dois foram aposentados em 14/08/2026: os dois exigiam foto do
rosto dela e faziam 100% do feed consumir o banco de 10 fotos. O que sobrou aqui
e o util — corrigir letterbox, uniformizar luz e recortar com foco no rosto —
usado pelo formato `retrato` e pelas cenas de retrato do Reels.
"""
from __future__ import annotations

from PIL import Image, ImageEnhance


def tratar(img: Image.Image) -> Image.Image:
    """Ajuste leve para uniformizar a luz entre fotos de origens diferentes."""
    img = cortar_barras(img)
    img = ImageEnhance.Brightness(img).enhance(1.04)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(1.06)
    img = ImageEnhance.Sharpness(img).enhance(1.08)
    return img


def cortar_barras(img: Image.Image) -> Image.Image:
    """Remove barras pretas laterais/verticais (algumas fotos vieram do IG com
    letterbox). Varre as bordas enquanto a linha/coluna for quase preta."""
    img = img.convert("RGB")
    cinza = img.convert("L")
    larg, alt = img.size
    px = cinza.load()

    def escura_col(x):
        amostra = [px[x, y] for y in range(0, alt, max(1, alt // 40))]
        return sum(amostra) / len(amostra) < 22

    def escura_lin(y):
        amostra = [px[x, y] for x in range(0, larg, max(1, larg // 40))]
        return sum(amostra) / len(amostra) < 22

    e = 0
    while e < larg // 4 and escura_col(e):
        e += 1
    dd = larg - 1
    while dd > larg * 3 // 4 and escura_col(dd):
        dd -= 1
    t = 0
    while t < alt // 4 and escura_lin(t):
        t += 1
    b = alt - 1
    while b > alt * 3 // 4 and escura_lin(b):
        b -= 1

    if (e, t, dd + 1, b + 1) != (0, 0, larg, alt):
        img = img.crop((e, t, dd + 1, b + 1))
    return img


def cobrir(img: Image.Image, larg: int, alt: int, foco_y: float = 0.38) -> Image.Image:
    """Recorta a foto para cobrir larg x alt, centrando em x e no foco_y em y
    (0=topo, 1=base). Rosto costuma estar no terco superior -> foco 0.38."""
    img = img.convert("RGB")
    escala = max(larg / img.width, alt / img.height)
    nova = (round(img.width * escala), round(img.height * escala))
    img = img.resize(nova, Image.LANCZOS)
    x = (img.width - larg) // 2
    y = int((img.height - alt) * foco_y)
    y = max(0, min(y, img.height - alt))
    return img.crop((x, y, x + larg, y + alt))
