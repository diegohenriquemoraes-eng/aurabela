# -*- coding: utf-8 -*-
"""Reels do dia (09h BRT) no feed da @aurabelastore_on.

Mesma espinha do publicar_estatico.py, com duas diferencas:
  - a midia e um mp4 montado localmente com ffmpeg (Ken Burns sobre as fotos
    reais dela) — sem IA de video, para nunca parar por limite de credito;
  - o container usa media_type=REELS e video_url; a API demora mais para
    processar video, entao esperar() tem folga maior.

Uso:
    python publicar_reels.py --ensaio      # monta o mp4 e para
    python publicar_reels.py               # proximo da fila
    python publicar_reels.py --id 3        # roteiro especifico
    python publicar_reels.py --garantir    # so publica se ainda nao saiu hoje
"""
from __future__ import annotations

import argparse
import os
import time

import config
import legenda
import publicador as pb
from gerar_reels import gerar_reels

BASE = pb.BASE
ROTEIROS = os.path.join(BASE, "reels.json")
TIPO = "reels"


def escolher(banco: list[dict], id_forcado: int | None, pilar: str) -> dict:
    if id_forcado is not None:
        for r in banco:
            if r["id"] == id_forcado:
                return r
        raise SystemExit(f"Roteiro id={id_forcado} nao existe")

    restantes = pb.fila(banco, TIPO)
    if not restantes:
        raise SystemExit("Banco de roteiros esgotado — repor reels.json.")
    if len(restantes) <= 4:
        pb.log(f"AVISO: so restam {len(restantes)} roteiros no banco.")

    for r in restantes:
        if r.get("pilar") == pilar:
            return r
    pb.log(f"pilar {pilar}: nenhum roteiro casa, seguindo a fila")
    return restantes[0]


def montar_cenas(r: dict, cta: str) -> list[dict]:
    """Converte o roteiro em cenas com caminho absoluto da foto.

    A ultima cena ganha o rodape do CTA do dia, se ela ja nao trouxer um — e ali
    que o pedido de acao aparece no video.
    """
    cenas = []
    for i, c in enumerate(r["cenas"]):
        cena = {
            "foto": os.path.join(BASE, "fotos", c["foto"]),
            "texto": c["texto"],
            "etiqueta": c.get("etiqueta"),
            "rodape": c.get("rodape"),
            "dur": c.get("dur", 3.0),
            "foco_y": c.get("foco_y", 0.32),
        }
        if i == len(r["cenas"]) - 1 and not cena["rodape"]:
            cena["rodape"] = legenda.rodape_do_cta(cta)
        cenas.append(cena)
    return cenas


def trilha() -> str | None:
    """Primeira faixa de audio/ disponivel. Sem trilha o gerar_reels embute
    silencio — o Instagram recusa video sem faixa de audio nenhuma."""
    pasta = os.path.join(BASE, "audio")
    if not os.path.isdir(pasta):
        return None
    faixas = sorted(f for f in os.listdir(pasta) if f.lower().endswith((".mp3", ".m4a", ".aac")))
    return os.path.join(pasta, faixas[0]) if faixas else None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", type=int, default=None)
    p.add_argument("--ensaio", action="store_true")
    p.add_argument("--garantir", action="store_true")
    a = p.parse_args()

    if a.garantir and pb.ja_publicou_hoje(TIPO):
        pb.log("reels do dia ja esta no ar — nada a fazer")
        return

    estado = pb.carregar(pb.ESTADO, {})
    i_cta, cta = legenda.cta_do_dia(estado)
    i_pilar, pilar = legenda.pilar_do_dia(estado)

    banco = pb.carregar(ROTEIROS, {"reels": []})["reels"]
    r = escolher(banco, a.id, pilar)

    hoje = pb.hoje()
    slug = f"{hoje}-reel{r['id']:03d}"
    destino = os.path.join(BASE, "imagens", hoje, f"{slug}.mp4")

    pb.log(f"montando o video ({len(r['cenas'])} cenas)...")
    video = gerar_reels(montar_cenas(r, cta), destino, audio=trilha())
    tam = os.path.getsize(video) / 1024 / 1024
    pb.log(f"video: {os.path.basename(video)} ({tam:.1f} MB) | pilar {pilar} | CTA {cta}")

    promocao = estado.get("promocao") or None
    conteudo = {"gancho": r["cenas"][0]["texto"], "corpo": r["corpo"],
                "pilar": r.get("pilar", "educativo")}
    texto = legenda.montar(conteudo, cta, promocao)

    if a.ensaio:
        print("\n--- legenda ---\n" + texto + "\n---------------\n")
        pb.log("ensaio: parando antes de publicar")
        return

    tok = config.token()
    pb.conferir_token(tok)

    pb.commitar(f"video do reels {slug}", "imagens")
    url = f"{config.REPO_RAW}/imagens/{hoje}/{os.path.basename(video)}"
    pb.log(f"video no ar: {url}")
    time.sleep(6)  # folga maior: arquivo grande no CDN do raw

    media_id = pb.publicar_container(
        {"media_type": "REELS", "video_url": url, "caption": texto}, tok)

    pb.anotar(TIPO, r["id"], media_id, cta, pilar)
    estado = pb.carregar(pb.ESTADO, {})
    estado.update({"cta_indice": i_cta, "cta": cta,
                   "pilar_indice": i_pilar, "pilar": pilar, "data": hoje})
    pb.salvar(pb.ESTADO, estado)
    pb.commitar(f"reels {slug} publicado", "publicados.json", "estado_ciclo.json")


if __name__ == "__main__":
    main()
