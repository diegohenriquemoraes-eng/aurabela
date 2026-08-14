# -*- coding: utf-8 -*-
"""Baixa o catalogo de skincare da Mary Kay para o banco local `produtos/`.

Por que existe: o feed nao pode viver das 10 fotos do rosto da Marcia — elas
acabam. Produto e o unico ativo VISUAL infinito que ela ja tem: sao 48 packshots
oficiais em alta, com nome e preco, servidos pela loja (plataforma VTEX, catalogo
publico em /api/catalog_system/pub/products/search).

Roda LOCAL, uma vez a cada tantos meses. O runner do GitHub Actions nunca chama
esta ferramenta: ele so le `produtos/` e `produtos.json`, que vao commitados.
Assim o caminho critico continua sem dependencia de rede alem da propria API do
Instagram.

Uso:
    python ferramentas/baixar_produtos.py            # baixa o que falta
    python ferramentas/baixar_produtos.py --forcar   # rebaixa tudo

O recorte do fundo branco (`_recortar_fundo`) e o que permite compor o produto
sobre fundo colorido sem aquele quadrado branco denunciando montagem amadora.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import unicodedata

import requests
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(BASE, "produtos")
BANCO = os.path.join(BASE, "produtos.json")

LOJA = "https://loja.marykay.com.br"
CATEGORIAS = ["Cuidados-Faciais"]
LADO = 1400  # lado maior do PNG salvo — sobra para o zoom do Reels

SESSAO = requests.Session()
SESSAO.headers["User-Agent"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


# ------------------------------------------------------------------ catalogo
def buscar(categoria: str) -> list[dict]:
    """Pagina o catalogo publico da VTEX (o endpoint devolve no maximo 50)."""
    itens, de = [], 0
    while True:
        r = SESSAO.get(
            f"{LOJA}/api/catalog_system/pub/products/search/{categoria}",
            params={"_from": de, "_to": de + 49}, timeout=40,
        )
        if r.status_code not in (200, 206):
            break
        lote = r.json()
        if not lote:
            break
        itens += lote
        total = r.headers.get("resources", "")
        fim = int(total.split("/")[-1]) if "/" in total else len(itens)
        de += 50
        if de >= fim:
            break
    return itens


# ------------------------------------------------------------------ imagem
def _tirar_selo(img: Image.Image) -> Image.Image:
    """Corta a tarja lilas "Melhor avaliado" que a loja embute no packshot.

    Sao 4 produtos do catalogo. A tarja e da VITRINE, nao do produto: publicada
    no feed vira um post da Mary Kay dentro do post dela — e ainda promete uma
    avaliacao que nao e da Marcia.
    """
    img = img.convert("RGB")
    larg, alt = img.size
    passo = max(1, larg // 60)

    def lilas(y):
        linha = [img.getpixel((x, y)) for x in range(0, larg, passo)]
        vale = sum(1 for p in linha if p[2] - p[0] > 4 and min(p) > 190)
        return vale / len(linha) > 0.25

    topo = None
    for y in range(alt - 1, int(alt * 0.6), -1):
        if lilas(y):
            topo = y
        elif topo is not None:
            break
    return img.crop((0, 0, larg, max(1, topo - 8))) if topo else img


def _normalizar_branco(img: Image.Image) -> Image.Image:
    """Puxa o fundo do packshot para branco 255 puro, canal a canal.

    A Mary Kay serve os packshots com fundo cinza (241,241,243) — nao branco. Em
    multiply isso vira um RETANGULO cinza visivel em volta do frasco, que foi
    exatamente o defeito da 2a amostra. Normalizar o fundo para 255 faz o
    retangulo desaparecer e ainda tira o veu cinza de cima do produto.
    """
    larg, alt = img.size
    faixa = 6
    borda = (list(img.crop((0, 0, larg, faixa)).getdata())
             + list(img.crop((0, alt - faixa, larg, alt)).getdata())
             + list(img.crop((0, 0, faixa, alt)).getdata())
             + list(img.crop((larg - faixa, 0, larg, alt)).getdata()))
    if not borda:
        return img
    fundo = [sorted(c[i] for c in borda)[len(borda) // 2] for i in range(3)]
    if min(fundo) < 200:
        return img  # nao e packshot em fundo claro — nao mexer

    lut = []
    for canal in fundo:
        for v in range(256):
            n = min(255, round(v * 255 / canal))
            lut.append(255 if n >= 249 else n)
    return img.point(lut)


def _aparar(img: Image.Image, limiar: int = 246, folga: int = 24) -> Image.Image:
    """Corta a moldura branca do packshot, mantendo o fundo branco.

    NAO recorta o produto em PNG transparente de proposito. Tentei: o flood fill
    a partir das quinas come a TAMPA BRANCA do frasco (ela e branca e encosta no
    fundo branco — sao o mesmo pixel para o algoritmo) e deixa a sombra cinza do
    estudio como um retangulo fantasma em volta. As duas coisas apareceram na
    primeira amostra.

    A arte resolve isso na composicao: `formatos.produto` sobrepoe o packshot em
    MULTIPLY. Branco vira transparente sozinho, a sombra cinza do estudio vira
    sombra de verdade sobre o fundo colorido, e a tampa branca continua inteira.
    """
    fundo = Image.new("RGB", img.size, (255, 255, 255))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fundo.paste(img, mask=img.split()[3])
    else:
        fundo = img.convert("RGB")

    fundo = _normalizar_branco(_tirar_selo(fundo))
    conteudo = fundo.convert("L").point(lambda v: 255 if v < limiar else 0)
    caixa = conteudo.getbbox()
    if caixa:
        e, t, d, b = caixa
        fundo = fundo.crop((max(0, e - folga), max(0, t - folga),
                            min(fundo.width, d + folga), min(fundo.height, b + folga)))
    return fundo


def baixar_imagem(url: str, destino: str) -> bool:
    r = SESSAO.get(url, timeout=60)
    if r.status_code != 200 or len(r.content) < 4000:
        return False
    img = Image.open(io.BytesIO(r.content))
    img = _aparar(img)
    escala = LADO / max(img.size)
    if escala < 1:
        img = img.resize((round(img.width * escala), round(img.height * escala)),
                         Image.LANCZOS)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    img.save(destino, "PNG")
    return True


# ------------------------------------------------------------------ nomes
def _slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:60]


def _curto(nome: str) -> str:
    """Nome que cabe na arte: sem gramatura, sem marca repetida, sem (R)."""
    n = re.sub(r"\s*\d+(,\d+)?\s?(g|gr|ml|G|ML)\b", "", nome)
    n = n.replace("®", "").replace("™", "").replace("Mary Kay", "").strip(" -–,")
    return re.sub(r"\s{2,}", " ", n).strip()


def _linha(categorias: list[str]) -> str:
    """Linha do produto (TimeWise, Clear Proof...) — vira a etiqueta da arte."""
    for c in categorias:
        partes = [p for p in c.split("/") if p]
        if len(partes) > 1:
            return partes[1].replace("®", "").replace("™", "").strip()
    return "Mary Kay"


def main() -> None:
    forcar = "--forcar" in sys.argv
    vistos, banco = set(), []

    for cat in CATEGORIAS:
        for p in buscar(cat):
            item = (p.get("items") or [{}])[0]
            imgs = item.get("images") or []
            if not imgs or p["productId"] in vistos:
                continue
            vistos.add(p["productId"])

            nome = _curto(p["productName"])
            arquivo = f"{_slug(nome)}.png"
            caminho = os.path.join(DESTINO, arquivo)

            if forcar or not os.path.exists(caminho):
                if not baixar_imagem(imgs[0]["imageUrl"], caminho):
                    print(f"  falhou: {nome}")
                    continue
                print(f"  ok: {arquivo}")

            oferta = ((item.get("sellers") or [{}])[0].get("commertialOffer") or {})
            banco.append({
                "id": p["productId"],
                "nome": nome,
                "nome_completo": p["productName"],
                "linha": _linha(p.get("categories", [])),
                "arquivo": arquivo,
                "preco": oferta.get("Price"),
                "link": f"{LOJA}/{p['linkText']}/p",
            })

    banco.sort(key=lambda x: (x["linha"], x["nome"]))
    with open(BANCO, "w", encoding="utf-8") as f:
        json.dump({
            "_leia": ("Catalogo de skincare Mary Kay baixado por "
                      "ferramentas/baixar_produtos.py. As artes de produto leem "
                      "daqui pelo campo 'arquivo' (packshot aparado em fundo "
                      "branco, dentro de produtos/; a arte compoe em multiply)."),
            "produtos": banco,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n{len(banco)} produtos no banco.")


if __name__ == "__main__":
    main()
