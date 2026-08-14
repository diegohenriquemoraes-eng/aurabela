# -*- coding: utf-8 -*-
"""Carrossel do feed — o formato que o sistema estava deixando na mesa.

Por que ele entrou (pesquisa de 14/08/2026): carrossel e o formato de maior
SALVAMENTO do Instagram (2-3x o Reels), e salvamento e hoje o sinal que mais
pesa no ranqueamento. O sinal dominante do carrossel e o tempo no post — cada
slide que a pessoa passa soma segundos —, entao a peca precisa dar vontade de
arrastar ate o fim.

Estrutura que a pesquisa aponta e que este arquivo implementa:
  slide 1  capa    -> gancho curto e grande + pista de arraste
  2..n-1   miolo   -> UMA ideia por slide, corpo curto
  slide n  CTA     -> pedido de acao explicito (salvar / comentar / link)

Sete slides e o ponto doce (acima de ~10 cai a taxa de conclusao, e a API para
em 10). O carrossel NAO tem banco proprio: ele e uma leitura mais funda do
conteudo que ja existe em conteudos.json — quem tem `slides` vira carrossel.
"""
from __future__ import annotations

import os

from PIL import Image, ImageChops, ImageDraw

import arte
from arte import Tom, MARGEM
from tipografia import serif, sans

LARG, ALT = 1080, 1350
MAX_SLIDES = 10  # limite duro da API


# ------------------------------------------------------------------ enfeites
def _progresso(d: ImageDraw.ImageDraw, tom: dict, i: int, total: int) -> None:
    """Pontinhos no topo: mostra onde a pessoa esta e quanto falta.

    Parece detalhe e nao e: saber que faltam 2 slides segura o arraste ate o
    fim, e conclusao e o que o algoritmo le como 'valeu a pena'.
    """
    r, gap = 7, 22
    larg = total * gap - (gap - 2 * r)
    x = (LARG - larg) / 2
    y = 96
    for k in range(total):
        cheio = k == i
        cor = tom["acento"] if cheio else _mistura(tom["fundo"], tom["texto"], 0.22)
        raio = r if cheio else r - 2
        d.ellipse((x + k * gap - raio + r, y - raio, x + k * gap + raio + r, y + raio),
                  fill=cor)


def _arraste(d: ImageDraw.ImageDraw, tom: dict) -> None:
    """Pista de arraste no rodape da capa, do lado direito (onde o polegar vai)."""
    y = ALT - 84
    txt = "ARRASTA"
    f = sans(25, 700)
    w = sum(d.textlength(c, font=f) + 2.6 for c in txt) - 2.6
    x = LARG - MARGEM - w - 34
    arte.espacado(d, (x, y), txt, f, tom["acento"], 2.6)
    # seta
    px, py = LARG - MARGEM - 22, y + 13
    d.line((px - 16, py, px, py), fill=tom["acento"], width=3)
    d.line((px - 7, py - 7, px, py), fill=tom["acento"], width=3)
    d.line((px - 7, py + 7, px, py), fill=tom["acento"], width=3)


# -------------------------------------------------------------------- slides
def capa(titulo: str, destino: str, tom: dict, etiqueta: str | None = None,
         apoio: str | None = None, i: int = 0, total: int = 7,
         produto: str | None = None) -> str:
    """Slide 1. Gancho grande e curto — e ele que decide se alguem arrasta.

    Com `produto`, a capa leva o packshot em cima do gancho. Nao e enfeite: a
    capa do carrossel ocupa um quadradinho da grade do perfil, e uma grade so de
    cartao tipografico fica monotona por mais bonita que cada peca seja.
    """
    img = arte.fundo(LARG, ALT, tom)

    if produto:
        if not tom["claro"]:
            tom = Tom.CREME  # multiply so funciona sobre fundo claro
            img = arte.fundo(LARG, ALT, tom)
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "produtos", produto)
        pack = Image.open(caminho).convert("RGB")
        e = min(470 / pack.height, (LARG - 2 * MARGEM - 160) / pack.width)
        pack = pack.resize((max(1, round(pack.width * e)),
                            max(1, round(pack.height * e))), Image.LANCZOS)
        px, py = (LARG - pack.width) // 2, 200 + (470 - pack.height) // 2
        caixa = (px, py, px + pack.width, py + pack.height)
        img.paste(ImageChops.multiply(img.crop(caixa), pack), caixa)

    d = ImageDraw.Draw(img)
    _progresso(d, tom, i, total)

    larg_txt = LARG - 2 * MARGEM
    teto = 380 if produto else 580
    f = arte.caber(d, titulo, larg_txt, teto,
                   [86, 76, 66, 58] if produto else [112, 98, 86, 74, 64])
    h = arte.altura(d, titulo, f, larg_txt, 1.12)
    h_bloco = h + (110 if apoio else 0)
    y = 748 if produto else max(240, int(ALT * 0.49 - h_bloco / 2))

    if etiqueta:
        arte.espacado(d, (MARGEM, y - 66), etiqueta.upper(), sans(27, 700),
                      tom["acento"], 4.6)
    y = arte.bloco(d, titulo, f, tom["texto"], MARGEM, y, larg_txt, 1.12)

    if apoio:
        arte.filete(d, MARGEM, y + 44, 96, tom["acento"])
        arte.bloco(d, apoio, sans(38, 500), tom["fraco"], MARGEM, y + 80,
                   larg_txt, 1.34)

    arte.espacado(d, (MARGEM, ALT - 84), arte.SELO, sans(26, 600), tom["fraco"], 2.2)
    _arraste(d, tom)
    return arte.salvar(img, destino)


def passo(numero: int, titulo: str, texto: str, destino: str, tom: dict,
          i: int, total: int) -> str:
    """Slide de miolo: UMA ideia. Numero grande, titulo serif, corpo curto."""
    img = arte.fundo(LARG, ALT, tom)
    d = ImageDraw.Draw(img)
    _progresso(d, tom, i, total)

    larg_txt = LARG - 2 * MARGEM
    fn = serif(190, 900)
    ft = arte.caber(d, titulo, larg_txt, 250, [88, 76, 66, 56])
    fc = sans(42, 500)

    # Bloco inteiro (numero + filete + titulo + corpo) centrado, igual aos
    # slides de nota e de fecho: ancorar no topo fazia o olho pular de altura a
    # cada arraste, e sobrava meia peca vazia embaixo.
    h_num = int(fn.size * 0.80) + 34
    h_tit = arte.altura(d, titulo, ft, larg_txt, 1.12)
    h_txt = (arte.altura(d, texto, fc, larg_txt, 1.40) + 34) if texto else 0
    y = max(230, int(ALT * 0.51 - (h_num + 52 + h_tit + h_txt) / 2))

    caixa = d.textbbox((0, 0), str(numero), font=fn)
    d.text((MARGEM - caixa[0], y - caixa[1]), str(numero), font=fn,
           fill=_mistura(tom["fundo"], tom["acento"], 0.55))
    y += h_num

    arte.filete(d, MARGEM, y, 96, tom["acento"])
    y += 52

    y = arte.bloco(d, titulo, ft, tom["texto"], MARGEM, y, larg_txt, 1.12)
    if texto:
        arte.bloco(d, texto, fc, tom["fraco"], MARGEM, y + 34, larg_txt, 1.40)

    arte.espacado(d, (MARGEM, ALT - 84), arte.SELO, sans(26, 600), tom["fraco"], 2.2)
    return arte.salvar(img, destino)


def nota(titulo: str, texto: str, destino: str, tom: dict, i: int, total: int,
         etiqueta: str | None = None) -> str:
    """Slide de miolo sem numero — para virada de raciocinio ou aviso."""
    img = arte.fundo(LARG, ALT, tom)
    d = ImageDraw.Draw(img)
    _progresso(d, tom, i, total)

    larg_txt = LARG - 2 * MARGEM
    ft = arte.caber(d, titulo, larg_txt, 360, [88, 78, 68, 58])
    h = arte.altura(d, titulo, ft, larg_txt, 1.12)
    h_txt = arte.altura(d, texto, sans(42, 500), larg_txt, 1.40) if texto else 0
    y = max(250, int(ALT * 0.51 - (h + 34 + h_txt) / 2))

    if etiqueta:
        arte.espacado(d, (MARGEM, y - 62), etiqueta.upper(), sans(27, 700),
                      tom["acento"], 4.6)
    y = arte.bloco(d, titulo, ft, tom["texto"], MARGEM, y, larg_txt, 1.12)
    if texto:
        arte.bloco(d, texto, sans(42, 500), tom["fraco"], MARGEM, y + 34,
                   larg_txt, 1.40)

    arte.espacado(d, (MARGEM, ALT - 84), arte.SELO, sans(26, 600), tom["fraco"], 2.2)
    return arte.salvar(img, destino)


def fechamento(titulo: str, texto: str, rodape: str, destino: str,
               i: int, total: int) -> str:
    """Ultimo slide: sempre escuro, sempre com pedido de acao.

    Carrossel sem CTA no fim morre sem engajamento — e o slide final e o unico
    momento em que a pessoa ja consumiu tudo e esta disposta a agir.
    """
    tom = Tom.CAFE
    img = arte.vinheta(arte.fundo(LARG, ALT, tom), 40)
    d = ImageDraw.Draw(img)
    _progresso(d, tom, i, total)

    larg_txt = LARG - 2 * MARGEM
    ft = arte.caber(d, titulo, larg_txt, 400, [92, 80, 70, 60])
    h = arte.altura(d, titulo, ft, larg_txt, 1.12)
    h_txt = arte.altura(d, texto, sans(42, 500), larg_txt, 1.40) if texto else 0
    y = max(280, int(ALT * 0.47 - (h + 40 + h_txt) / 2))

    y = arte.bloco(d, titulo, ft, tom["texto"], MARGEM, y, larg_txt, 1.12)
    if texto:
        y = arte.bloco(d, texto, sans(42, 500), tom["fraco"], MARGEM, y + 40,
                       larg_txt, 1.40)

    arte.filete(d, MARGEM, y + 56, 96, tom["acento"])
    arte.selo(d, tom, LARG, ALT, rodape)
    return arte.salvar(img, destino)


# ------------------------------------------------------------------- montagem
def montar(c: dict, tom: dict, rodape: str, pasta: str, slug: str) -> list[str]:
    """Gera os arquivos do carrossel a partir do conteudo. Devolve os caminhos.

    Ritmo de tom pensado para a sequencia: capa no tom do dia, miolo num claro
    constante (para o olho ler a lista como uma coisa so) e fecho no escuro, que
    marca o fim e destaca o CTA.
    """
    slides = c["slides"][:MAX_SLIDES - 1]
    if not slides or slides[0].get("tipo") != "capa":
        raise SystemExit(f"conteudo {c['id']}: o carrossel precisa comecar por 'capa'")
    if not any(s.get("tipo") == "cta" for s in slides):
        slides = slides + [{"tipo": "cta",
                            "titulo": "Salva esse post pra não esquecer.",
                            "texto": "E me chama no Direct se ficar qualquer dúvida."}]

    total = len(slides)
    tom_miolo = Tom.CREME if tom["nome"] != "creme" else Tom.AREIA
    caminhos, numero = [], 0

    for i, s in enumerate(slides):
        alvo = os.path.join(pasta, f"{slug}-{i + 1:02d}.jpg")
        tipo = s.get("tipo", "passo")
        if tipo == "capa":
            capa(s["titulo"], alvo, tom, etiqueta=s.get("etiqueta") or c.get("etiqueta"),
                 apoio=s.get("texto"), i=i, total=total,
                 produto=s.get("produto"))
        elif tipo == "cta":
            fechamento(s["titulo"], s.get("texto", ""), rodape, alvo, i, total)
        elif tipo == "nota":
            nota(s["titulo"], s.get("texto", ""), alvo, tom_miolo, i, total,
                 etiqueta=s.get("etiqueta"))
        else:
            numero += 1
            passo(numero, s["titulo"], s.get("texto", ""), alvo, tom_miolo, i, total)
        caminhos.append(alvo)

    return caminhos


def _mistura(a, b, t: float):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
