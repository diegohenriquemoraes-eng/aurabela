# -*- coding: utf-8 -*-
"""Reels 1080x1920 a partir de FOTOS REAIS da Marcia, 100% local (ffmpeg).

Por que ffmpeg e nao IA de video: os free tiers de video (Veo/Kling) tem limite
diario, exigem login manual e mudam de politica — dependencia que PARA sozinha.
Aqui o Reels e montado localmente: nunca falta credito, nunca vence token, e o
rosto e o REAL dela (nao um rosto sintetico "quase igual").

Estrutura da peca (8-20s):
  cena 1 (gancho)  -> foto com Ken Burns (zoom-in lento) + gancho grande
  cenas 2..n       -> um passo/dica por cena, foto diferente, movimento alternado
  cena final       -> CTA

Cada cena e um PNG (Pillow, mesma identidade visual do estatico) que o ffmpeg
anima com zoompan. O texto ja vem "queimado" no PNG — evita depender de fontes
no filtro drawtext do ffmpeg (que varia de build para build no Windows).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw

import arte as ar
from arte import Tom
from foto import tratar as _tratar, cobrir as _cobrir
from tipografia import serif, sans, Cor

LARG, ALT = 1080, 1920
MARGEM = 84
FPS = 30
SELO = "@aurabelastore_on"
BASE = os.path.dirname(os.path.abspath(__file__))

# Area segura do Instagram: a UI cobre ~ topo 220px e base 420px no Reels.
SEGURO_TOPO = 250
SEGURO_BASE = 430


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise SystemExit("ffmpeg nao encontrado no PATH")
    return exe


def _quadro(foto: str, texto: str, destino: str, etiqueta: str | None = None,
            rodape: str | None = None, foco_y: float = 0.32,
            escala: float = 1.14) -> str:
    """Um quadro do Reels: foto tratada + veu + texto. Renderizado maior que
    1080x1920 (escala) para o zoompan do ffmpeg ter pixels de sobra e nao
    borrar ao ampliar."""
    lw, lh = int(LARG * escala), int(ALT * escala)
    base = _cobrir(_tratar(Image.open(foto)), lw, lh, foco_y)

    # veu proprio na proporcao do quadro
    # Veu duplo: forte subindo da base (texto) + leve descendo do topo, para o
    # selo nao sumir em foto clara (defeito visto na 1a amostra).
    veu = Image.new("L", (1, lh), 0)
    px = veu.load()
    corte = int(lh * 0.26)
    topo = int(lh * 0.16)
    for y in range(lh):
        v = 0 if y < corte else int((((y - corte) / (lh - corte)) ** 1.25) * 250)
        if y < topo:
            v = max(v, int((1 - y / topo) * 96))
        px[0, y] = v
    veu = veu.resize((lw, lh))
    base = Image.composite(Image.new("RGB", (lw, lh), Cor.PRETO_SUAVE), base, veu)

    d = ImageDraw.Draw(base)
    m = int(MARGEM * escala)

    # selo no topo (dentro da area segura)
    d.text((m, int(SEGURO_TOPO * escala * 0.55)), SELO,
           font=sans(int(32 * escala), 600), fill=(255, 255, 255))

    # texto ancorado de baixo pra cima, acima da area segura inferior
    larg_txt = lw - 2 * m
    y_base = lh - int(SEGURO_BASE * escala)

    if rodape:
        fr = sans(int(34 * escala), 700)
        d.text((m, y_base), rodape, font=fr, fill=Cor.NUDE)
        y_base -= int(58 * escala)

    n = len(texto)
    tam = 96 if n <= 40 else 82 if n <= 70 else 68 if n <= 105 else 56
    ft = serif(int(tam * escala), 800)
    linhas = ar.quebrar(d, texto, ft, larg_txt)
    lh_linha = int(ft.size * 1.16)
    y = y_base - len(linhas) * lh_linha

    if etiqueta:
        # creme (nao rosa): rosa sobre roupa clara sumia — visto na 2a amostra
        d.text((m, y - int(56 * escala)), etiqueta.upper(),
               font=sans(int(30 * escala), 700), fill=Cor.CREME)

    for ln in linhas:
        d.text((m, y), ln, font=ft, fill=(255, 255, 255))
        y += lh_linha

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    base.convert("RGB").save(destino, "PNG")
    return destino


def _quadro_texto(texto: str, destino: str, tom: dict, etiqueta: str | None = None,
                  rodape: str | None = None, escala: float = 1.14,
                  centralizar: bool = False) -> str:
    """Cena tipografica — a que sustenta o Reels sem gastar foto do rosto dela.

    Mesmo territorio visual do feed (fundo de `arte.py`, Playfair no gancho), so
    que em 9:16 e respeitando a area segura da UI do Reels.

    `centralizar` e para a CAPA: a grade do perfil mostra so o miolo do 9:16, e
    gancho ancorado no rodape aparecia cortado no meio da palavra no perfil.
    """
    lw, lh = int(LARG * escala), int(ALT * escala)
    base = ar.fundo(lw, lh, tom)
    d = ImageDraw.Draw(base)
    m = int(MARGEM * escala)
    larg_txt = lw - 2 * m

    d.text((m, int(SEGURO_TOPO * escala * 0.55)), SELO,
           font=sans(int(32 * escala), 600), fill=tom["fraco"])

    y_base = lh - int(SEGURO_BASE * escala)
    if rodape:
        ar.espacado(d, (m, y_base), rodape.upper(), sans(int(34 * escala), 700),
                    tom["acento"], 3.0)
        y_base -= int(64 * escala)

    f = ar.caber(d, texto, larg_txt, int(720 * escala),
                 [int(t * escala) for t in (96, 84, 72, 62, 54)])
    h = ar.altura(d, texto, f, larg_txt, 1.16)
    y = int(lh * 0.46 - h / 2) if centralizar else y_base - h
    if etiqueta:
        ar.espacado(d, (m, y - int(60 * escala)), etiqueta.upper(),
                    sans(int(30 * escala), 700), tom["acento"], 4.6)
    ar.bloco(d, texto, f, tom["texto"], m, y, larg_txt, 1.16)

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    base.convert("RGB").save(destino, "PNG")
    return destino


def _quadro_produto(arquivo: str, texto: str, destino: str, tom: dict,
                    etiqueta: str | None = None, rodape: str | None = None,
                    escala: float = 1.14) -> str:
    """Cena de produto: packshot em multiply (ver formatos.produto) + a frase."""
    if not tom["claro"]:
        tom = Tom.CREME
    lw, lh = int(LARG * escala), int(ALT * escala)
    base = ar.fundo(lw, lh, tom)

    # A faixa livre vai do fim da area segura de cima ate onde o texto comeca;
    # o frasco ocupa essa faixa e fica CENTRADO nela (antes encostava no topo e
    # sobrava um buraco no meio do quadro).
    topo_livre = int(SEGURO_TOPO * escala) + int(40 * escala)
    base_livre = lh - int((SEGURO_BASE + 470) * escala)
    faixa = max(int(400 * escala), base_livre - topo_livre)

    caminho = arquivo if os.path.isabs(arquivo) else os.path.join(BASE, "produtos", arquivo)
    pack = Image.open(caminho).convert("RGB")
    e = min(faixa / pack.height, (lw - int(220 * escala)) / pack.width)
    pack = pack.resize((max(1, round(pack.width * e)), max(1, round(pack.height * e))),
                       Image.LANCZOS)
    px = (lw - pack.width) // 2
    py = topo_livre + max(0, (faixa - pack.height) // 2)
    caixa = (px, py, px + pack.width, py + pack.height)
    base.paste(ImageChops.multiply(base.crop(caixa), pack), caixa)

    d = ImageDraw.Draw(base)
    m = int(MARGEM * escala)
    larg_txt = lw - 2 * m
    d.text((m, int(SEGURO_TOPO * escala * 0.55)), SELO,
           font=sans(int(32 * escala), 600), fill=tom["fraco"])

    y_base = lh - int(SEGURO_BASE * escala)
    if rodape:
        ar.espacado(d, (m, y_base), rodape.upper(), sans(int(34 * escala), 700),
                    tom["acento"], 3.0)
        y_base -= int(64 * escala)

    f = ar.caber(d, texto, larg_txt, int(400 * escala),
                 [int(t * escala) for t in (78, 68, 58, 50)])
    y = y_base - ar.altura(d, texto, f, larg_txt, 1.16)
    if etiqueta:
        ar.espacado(d, (m, y - int(60 * escala)), etiqueta.upper(),
                    sans(int(30 * escala), 700), tom["acento"], 4.6)
    ar.bloco(d, texto, f, tom["texto"], m, y, larg_txt, 1.16)

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    base.convert("RGB").save(destino, "PNG")
    return destino


def _zoompan(entrada: str, saida: str, dur: float, sentido: str) -> None:
    """Ken Burns: zoom lento in/out com leve pan. dur em segundos."""
    frames = max(1, int(dur * FPS))
    if sentido == "in":
        z = f"min(zoom+0.0009,1.16)"
    else:
        z = f"if(lte(zoom,1.0),1.16,max(1.001,zoom-0.0009))"
    vf = (
        f"zoompan=z='{z}':d={frames}:s={LARG}x{ALT}:fps={FPS}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',"
        f"format=yuv420p"
    )
    subprocess.run(
        [_ffmpeg(), "-y", "-loglevel", "error", "-loop", "1", "-i", entrada,
         "-vf", vf, "-t", f"{dur}", "-r", str(FPS), "-c:v", "libx264",
         "-preset", "medium", "-crf", "18", saida],
        check=True,
    )


def gerar_reels(cenas: list[dict], destino: str, audio: str | None = None) -> str:
    """cenas: [{tipo, texto, ...}]. Devolve o caminho do mp4.

    tipo = "texto" (padrao) | "produto" | "retrato". So o retrato usa foto da
    Marcia — antes TODA cena usava, e um Reels queimava 5 fotos do banco de 10.

    O Instagram exige mp4/mov, H.264, AAC. Sempre embutimos uma faixa de audio
    (silenciosa se nao houver trilha) — Reels sem trilha de audio nenhuma pode
    ser recusado pela Graph API.
    """
    tmp = tempfile.mkdtemp(prefix="aurabela-reels-")
    try:
        partes = []
        for i, c in enumerate(cenas):
            alvo = os.path.join(tmp, f"q{i}.png")
            tom = Tom.por_nome(c.get("tom"))
            tipo = c.get("tipo") or ("retrato" if c.get("foto") else "texto")
            if tipo == "retrato" and c.get("foto"):
                png = _quadro(c["foto"], c["texto"], alvo,
                              etiqueta=c.get("etiqueta"), rodape=c.get("rodape"),
                              foco_y=c.get("foco_y", 0.32))
            elif tipo == "produto" and c.get("produto"):
                png = _quadro_produto(c["produto"], c["texto"], alvo, tom,
                                      etiqueta=c.get("etiqueta"), rodape=c.get("rodape"))
            else:
                png = _quadro_texto(c["texto"], alvo, tom,
                                    etiqueta=c.get("etiqueta"), rodape=c.get("rodape"),
                                    centralizar=(i == 0))
            mp4 = os.path.join(tmp, f"c{i}.mp4")
            _zoompan(png, mp4, c.get("dur", 3.2), "in" if i % 2 == 0 else "out")
            partes.append(mp4)

        lista = os.path.join(tmp, "lista.txt")
        with open(lista, "w", encoding="utf-8") as f:
            for p in partes:
                f.write(f"file '{p.replace(os.sep, '/')}'\n")

        os.makedirs(os.path.dirname(destino), exist_ok=True)
        cmd = [_ffmpeg(), "-y", "-loglevel", "error",
               "-f", "concat", "-safe", "0", "-i", lista]
        if audio and os.path.exists(audio):
            cmd += ["-i", audio, "-shortest"]
        else:
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", destino]
        subprocess.run(cmd, check=True)
        return destino
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    saida = os.path.join(os.path.dirname(__file__), "saida-amostra")
    caminho = gerar_reels(
        [
            {"foto": "fotos/ref-01-closeup-frontal-sem-oculos.jpg",
             "texto": "Sua pele não precisa de 10 produtos.",
             "etiqueta": "rotina simples", "dur": 3.0, "foco_y": 0.30},
            {"foto": "fotos/ref-03-closeup-oculos-boina.jpg",
             "texto": "Precisa de 3 — na ordem certa.",
             "rodape": "1. limpar", "dur": 3.0},
            {"foto": "fotos/ref-04-sorrindo-oculos-restaurante.jpg",
             "texto": "Hidratar sela a água na pele.",
             "rodape": "2. hidratar", "dur": 3.0},
            {"foto": "fotos/ref-12-selfie-oculos-sol-sorrindo.jpg",
             "texto": "E o protetor é o que segura o tempo.",
             "rodape": "3. proteger", "dur": 3.0},
            {"foto": "fotos/ref-02-closeup-frontal-oculos-grau.webp",
             "texto": "Comenta PELE que eu monto a sua.",
             "etiqueta": "seu ritual", "dur": 3.2, "foco_y": 0.28},
        ],
        os.path.join(saida, "amostra-reels.mp4"),
    )
    print(caminho)
