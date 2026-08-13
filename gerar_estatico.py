# -*- coding: utf-8 -*-
"""Post estatico 1080x1350 (4:5) a partir de uma FOTO REAL da Marcia.

O rosto real dela e sempre a base — nunca gerado por IA. Por cima vai a arte no
territorio de beleza (nude/rosa/cafe, Playfair + Montserrat), no capricho dos
grandes perfis de skincare.

Dois templates:
  - "capa": foto full-bleed + veu cafe subindo + gancho serif branco embaixo.
            Para prova, emocional, oferta. E o que mais retem no feed.
  - "editorial": cartao off-white, rotulo + gancho serif em cima, foto emoldurada
            embaixo. Para conteudo educativo (a "aula" que se salva).

Tratamento leve da foto (brilho/contraste/saturacao suaves) para uniformizar a
luz entre fotos de origens diferentes.
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from tipografia import serif, sans, Cor

LARG, ALT = 1080, 1350
MARGEM = 90
SELO = "@aurabelastore_on"


# ------------------------------------------------------------------ foto
def _tratar(img: Image.Image) -> Image.Image:
    img = _cortar_barras(img)
    img = ImageEnhance.Brightness(img).enhance(1.04)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(1.06)
    img = ImageEnhance.Sharpness(img).enhance(1.08)
    return img


def _cortar_barras(img: Image.Image) -> Image.Image:
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


def _cobrir(img: Image.Image, larg: int, alt: int, foco_y: float = 0.38) -> Image.Image:
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


def _veu(alt_img: int, inicio: float = 0.40, forca: int = 210) -> Image.Image:
    """Gradiente cafe transparente->opaco de cima pra baixo (legibilidade)."""
    veu = Image.new("L", (1, alt_img), 0)
    px = veu.load()
    corte = int(alt_img * inicio)
    for y in range(alt_img):
        if y < corte:
            px[0, y] = 0
        else:
            t = (y - corte) / (alt_img - corte)
            px[0, y] = int((t ** 1.4) * forca)
    veu = veu.resize((LARG, alt_img))
    base = Image.new("RGB", (LARG, alt_img), Cor.PRETO_SUAVE)
    return base, veu


# ------------------------------------------------------------------ texto
def _quebrar(d, texto, fonte, larg):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=fonte) <= larg:
            atual = t
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def _desenhar_gancho(d, texto, fonte, cor, x, y, larg, entrelinha=1.14):
    linhas = _quebrar(d, texto, fonte, larg)
    lh = int(fonte.size * entrelinha)
    for ln in linhas:
        d.text((x, y), ln, font=fonte, fill=cor)
        y += lh
    return y


def _altura_bloco(d, texto, fonte, larg, entrelinha=1.14) -> int:
    return len(_quebrar(d, texto, fonte, larg)) * int(fonte.size * entrelinha)


# ------------------------------------------------------------------ templates
def _tam_gancho(texto: str) -> int:
    n = len(texto)
    if n <= 42:
        return 92
    if n <= 70:
        return 78
    if n <= 100:
        return 66
    return 56


def capa(foto: str, gancho: str, destino: str, etiqueta: str | None = None,
         rodape: str | None = None, foco_y: float = 0.34) -> str:
    base = _cobrir(_tratar(Image.open(foto)), LARG, ALT, foco_y)
    fundo, mask = _veu(ALT, inicio=0.30, forca=242)
    base = Image.composite(fundo, base, mask)
    d = ImageDraw.Draw(base)

    # selo topo
    d.text((MARGEM, 60), SELO, font=sans(30, 600), fill=(255, 255, 255))
    tw = d.textlength(SELO, font=sans(30, 600))
    d.line((MARGEM, 104, MARGEM + tw, 104), fill=Cor.DOURADO, width=3)

    # Ancoragem de BAIXO para CIMA: o rodape tem lugar fixo e o gancho cresce
    # para cima a partir dele. Assim gancho longo nunca invade o rodape — o
    # defeito que apareceu na 1a amostra.
    rod = rodape or "salva pra não esquecer"
    y_rod = ALT - 92
    d.text((MARGEM, y_rod), rod, font=sans(30, 600), fill=Cor.CREME)

    larg_txt = LARG - 2 * MARGEM
    fg = serif(_tam_gancho(gancho), 800)
    h_gancho = _altura_bloco(d, gancho, fg, larg_txt)
    y_gancho = y_rod - 46 - h_gancho

    if etiqueta:
        et = etiqueta.upper()
        d.text((MARGEM, y_gancho - 56), et, font=sans(28, 700), fill=Cor.NUDE)

    _desenhar_gancho(d, gancho, fg, (255, 255, 255), MARGEM, y_gancho, larg_txt)
    return _salvar(base, destino)


def editorial(foto: str, gancho: str, destino: str, etiqueta: str = "SKINCARE",
              rodape: str | None = None, foco_y: float = 0.30) -> str:
    base = Image.new("RGB", (LARG, ALT), Cor.OFFWHITE)
    d = ImageDraw.Draw(base)

    # rotulo
    et = f"{etiqueta.upper()}"
    d.text((MARGEM, 92), et, font=sans(30, 700), fill=Cor.ROSA_FORTE)
    d.line((MARGEM, 138, MARGEM + d.textlength(et, font=sans(30, 700)), 138),
           fill=Cor.ROSA_FORTE, width=3)

    # gancho serif cafe
    fg = serif(_tam_gancho(gancho) - 8, 800)
    y = _desenhar_gancho(d, gancho, fg, Cor.CAFE, MARGEM, 176,
                         LARG - 2 * MARGEM)

    # foto emoldurada embaixo
    topo_foto = int(y + 44)
    alt_foto = ALT - topo_foto - 150
    foto_img = _cobrir(_tratar(Image.open(foto)), LARG - 2 * MARGEM, alt_foto, foco_y)
    cartao = _arredondar(foto_img, 36)
    base.paste(cartao, (MARGEM, topo_foto), cartao)

    # selo + rodape
    d.text((MARGEM, ALT - 92), SELO, font=sans(28, 600), fill=Cor.CAFE_CLARO)
    if rodape:
        rw = d.textlength(rodape, font=sans(28, 700))
        d.text((LARG - MARGEM - rw, ALT - 92), rodape, font=sans(28, 700),
               fill=Cor.ROSA_FORTE)
    return _salvar(base, destino)


def _arredondar(img: Image.Image, raio: int) -> Image.Image:
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width, img.height),
                                           radius=raio, fill=255)
    img.putalpha(mask)
    return img


def _salvar(img: Image.Image, destino: str) -> str:
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    img.convert("RGB").save(destino, "JPEG", quality=94, subsampling=0, optimize=True)
    return destino


if __name__ == "__main__":
    import sys
    saida = os.path.join(os.path.dirname(__file__), "saida-amostra")
    capa("fotos/ref-03-closeup-oculos-boina.jpg",
         "Você foi ensinada a cuidar de todos, menos de você.",
         os.path.join(saida, "amostra-capa.jpg"),
         etiqueta="autocuidado 30+")
    editorial("fotos/ref-02-closeup-frontal-oculos-grau.webp",
              "A ordem certa de passar o seu skincare",
              os.path.join(saida, "amostra-editorial.jpg"),
              etiqueta="rotina", rodape="salva pra não esquecer")
    print("ok")
