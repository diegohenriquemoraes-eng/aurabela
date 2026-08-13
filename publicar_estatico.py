# -*- coding: utf-8 -*-
"""Post estatico do dia (19h BRT) no feed da @aurabelastore_on.

Fluxo:
  1. CTA e pilar do dia (ciclos com memoria em estado_ciclo.json)
  2. escolhe o conteudo que casa com o pilar (conteudos.json menos publicados)
  3. gera a arte sobre a FOTO REAL dela
  4. commita/sobe a imagem (a API exige URL https publica)
  5. publica, registra e grava o estado
  6. story de reforco

Uso:
    python publicar_estatico.py --ensaio     # gera a arte e para
    python publicar_estatico.py              # proximo da fila
    python publicar_estatico.py --id 7       # conteudo especifico
    python publicar_estatico.py --garantir   # so publica se ainda nao saiu hoje
"""
from __future__ import annotations

import argparse
import os

import config
import legenda
import publicador as pb
from gerar_estatico import capa, editorial

BASE = pb.BASE
CONTEUDOS = os.path.join(BASE, "conteudos.json")
TIPO = "estatico"


def escolher(banco: list[dict], id_forcado: int | None, pilar: str) -> dict:
    if id_forcado is not None:
        for c in banco:
            if c["id"] == id_forcado:
                return c
        raise SystemExit(f"Conteudo id={id_forcado} nao existe")

    restantes = pb.fila(banco, TIPO)
    if not restantes:
        raise SystemExit("Banco de conteudos esgotado — repor conteudos.json.")
    if len(restantes) <= 8:
        pb.log(f"AVISO: so restam {len(restantes)} conteudos no banco.")

    # O pilar do dia manda: puxa para a frente o proximo conteudo daquele pilar.
    # Se nao houver, segue a fila (melhor publicar fora do pilar do que nao
    # publicar — a constancia vale mais que a ordem perfeita).
    for c in restantes:
        if c.get("pilar") == pilar:
            return c
    pb.log(f"pilar {pilar}: nenhum conteudo casa, seguindo a fila")
    return restantes[0]


def gerar_arte(c: dict, cta: str, destino: str) -> str:
    foto = os.path.join(BASE, "fotos", c["foto"])
    rodape = legenda.rodape_do_cta(cta)
    comum = dict(etiqueta=c.get("etiqueta", ""), rodape=rodape,
                 foco_y=c.get("foco_y", 0.32))
    if c.get("template") == "editorial":
        return editorial(foto, c["gancho"], destino, **comum)
    return capa(foto, c["gancho"], destino, **comum)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", type=int, default=None)
    p.add_argument("--ensaio", action="store_true")
    p.add_argument("--garantir", action="store_true",
                   help="rede de seguranca: publica so se o post do dia nao saiu")
    a = p.parse_args()

    if a.garantir and pb.ja_publicou_hoje(TIPO):
        pb.log("estatico do dia ja esta no ar — nada a fazer")
        return

    estado = pb.carregar(pb.ESTADO, {})
    i_cta, cta = legenda.cta_do_dia(estado)
    i_pilar, pilar = legenda.pilar_do_dia(estado)

    banco = pb.carregar(CONTEUDOS, {"posts": []})["posts"]
    c = escolher(banco, a.id, pilar)

    hoje = pb.hoje()
    slug = f"{hoje}-est{c['id']:03d}"
    destino = os.path.join(BASE, "imagens", hoje, f"{slug}.jpg")
    arte = gerar_arte(c, cta, destino)
    pb.log(f"arte: {os.path.basename(arte)} | pilar {pilar} | CTA {cta}")

    promocao = pb.carregar(pb.ESTADO, {}).get("promocao") or None
    texto = legenda.montar(c, cta, promocao)

    if a.ensaio:
        print("\n--- legenda ---\n" + texto + "\n---------------\n")
        pb.log("ensaio: parando antes de publicar")
        return

    tok = config.token()
    pb.conferir_token(tok)

    pb.commitar(f"arte do post {slug}", "imagens")
    url = f"{config.REPO_RAW}/imagens/{hoje}/{os.path.basename(arte)}"
    pb.log(f"imagem no ar: {url}")
    import time
    time.sleep(5)  # folga para o CDN do raw responder

    media_id = pb.publicar_container(
        {"image_url": url, "caption": texto}, tok)

    # story de reforco: se falhar, o feed ja esta no ar — avisa e segue
    try:
        from gerar_story import gerar_story
        st = os.path.join(BASE, "imagens", hoje, f"{slug}-story.jpg")
        gerar_story(arte, st)
        pb.commitar(f"story do post {slug}", "imagens")
        st_url = f"{config.REPO_RAW}/imagens/{hoje}/{os.path.basename(st)}"
        time.sleep(4)
        pb.publicar_container({"media_type": "STORIES", "image_url": st_url}, tok)
    except SystemExit as e:
        pb.log(f"AVISO: story falhou ({e}); o post do feed esta no ar")

    pb.anotar(TIPO, c["id"], media_id, cta, pilar)
    estado = pb.carregar(pb.ESTADO, {})
    estado.update({"cta_indice": i_cta, "cta": cta,
                   "pilar_indice": i_pilar, "pilar": pilar, "data": hoje})
    pb.salvar(pb.ESTADO, estado)
    pb.commitar(f"post {slug} publicado", "publicados.json", "estado_ciclo.json")


if __name__ == "__main__":
    main()
