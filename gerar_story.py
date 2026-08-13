# -*- coding: utf-8 -*-
"""Story 1080x1920 de reforco: a arte do dia emoldurada num fundo da marca.

O story nao repete o post — ele CHAMA para o post ("novo no feed"), que e o que
leva a pessoa ao perfil. Fundo nude com a peca centralizada e leve sombra.
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFilter

from tipografia import serif, sans, Cor

LARG, ALT = 1080, 1920


def gerar_story(arte: str, destino: str, chamada: str = "novo no feed",
                rodape: str = "arrasta pra cima") -> str:
    fundo = Image.new("RGB", (LARG, ALT), Cor.OFFWHITE)

    # fundo: a propria arte borrada e escurecida, para dar profundidade
    base = Image.open(arte).convert("RGB")
    escala = max(LARG / base.width, ALT / base.height)
    borrado = base.resize((round(base.width * escala), round(base.height * escala)),
                          Image.LANCZOS)
    x = (borrado.width - LARG) // 2
    y = (borrado.height - ALT) // 2
    borrado = borrado.crop((x, y, x + LARG, y + ALT)).filter(ImageFilter.GaussianBlur(38))
    veu = Image.new("RGB", (LARG, ALT), Cor.PRETO_SUAVE)
    fundo = Image.blend(borrado, veu, 0.55)

    # a arte centralizada
    larg_arte = 840
    arte_img = Image.open(arte).convert("RGB")
    prop = larg_arte / arte_img.width
    arte_img = arte_img.resize((larg_arte, round(arte_img.height * prop)), Image.LANCZOS)

    cx = (LARG - larg_arte) // 2
    cy = (ALT - arte_img.height) // 2

    sombra = Image.new("RGBA", (LARG, ALT), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle(
        (cx - 6, cy - 6, cx + larg_arte + 6, cy + arte_img.height + 6),
        radius=32, fill=(0, 0, 0, 120))
    sombra = sombra.filter(ImageFilter.GaussianBlur(22))
    fundo = Image.alpha_composite(fundo.convert("RGBA"), sombra).convert("RGB")

    mask = Image.new("L", arte_img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *arte_img.size), radius=28, fill=255)
    fundo.paste(arte_img, (cx, cy), mask)

    d = ImageDraw.Draw(fundo)
    d.text((LARG / 2, cy - 130), chamada.upper(), font=sans(34, 700),
           fill=Cor.NUDE, anchor="ma")
    d.text((LARG / 2, cy + arte_img.height + 74), rodape, font=serif(50, 700),
           fill=(255, 255, 255), anchor="ma")

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    fundo.save(destino, "JPEG", quality=93, subsampling=0, optimize=True)
    return destino


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    print(gerar_story(os.path.join(base, "saida-amostra", "amostra-capa.jpg"),
                      os.path.join(base, "saida-amostra", "amostra-story.jpg")))
