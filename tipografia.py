# -*- coding: utf-8 -*-
"""Tipografia e paleta da AuraBela.

Duas famílias, o par clássico de conteúdo de beleza:
  - Playfair Display (serifada display) para os ganchos — elegância, "editorial".
  - Montserrat (sans geométrica) para corpo, selos e CTA — limpeza e leitura.

As duas sao fontes VARIAVEIS (um arquivo por familia, eixo de peso 400-900). O
peso e escolhido em runtime com set_variation_by_axes — cada chamada devolve um
objeto de fonte novo, entao nunca ha dois pesos disputando o mesmo objeto (a
armadilha que o vendanaobra evitou usando estaticas; aqui isolamos por chamada).
"""
from __future__ import annotations

import os
from functools import lru_cache
from PIL import ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(BASE, "fontes")

SERIF = os.path.join(FONTES, "PlayfairDisplay-Bold.ttf")   # variavel 400-900
SANS = os.path.join(FONTES, "Montserrat-Regular.ttf")      # variavel 400-900


@lru_cache(maxsize=256)
def serif(tamanho: int, peso: int = 700) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(SERIF, tamanho)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


@lru_cache(maxsize=256)
def sans(tamanho: int, peso: int = 500) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(SANS, tamanho)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


# --------------------------------------------------------------------- paleta
# Territorio de cor de beleza/skincare: nude, rosa suave, marrom-café, off-white.
# Amostrado do universo Mary Kay + dos perfis de referencia (rosa/nude/marrom).
class Cor:
    OFFWHITE = (247, 242, 238)     # fundo claro cremoso
    NUDE = (226, 205, 193)         # nude/pele
    ROSA = (214, 150, 150)         # rosa seco (rosé)
    ROSA_FORTE = (193, 106, 112)   # rosa/vinho para destaque
    CAFE = (74, 58, 52)            # marrom-café (texto escuro, elegante)
    CAFE_CLARO = (120, 98, 88)     # marrom médio
    CREME = (240, 228, 218)        # creme para tarjas
    BRANCO = (255, 255, 255)
    PRETO_SUAVE = (33, 28, 26)     # "preto" quente, nunca 000
    DOURADO = (183, 142, 92)       # acento dourado discreto

    # gradiente escuro sobre foto (para texto legivel em cima de imagem)
    VEU_TOPO = (33, 28, 26, 0)
    VEU_BASE = (33, 28, 26, 200)
