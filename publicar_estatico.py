# -*- coding: utf-8 -*-
"""Peca do feed das 19h BRT na @aurabelastore_on — carrossel ou imagem unica.

O nome do arquivo ficou de quando o slot so publicava imagem unica; hoje ele
alterna com CARROSSEL, que e o formato de maior salvamento do Instagram. Quem
decide qual sai e `curadoria.dia_de_carrossel` + o conteudo ter `slides`.

Fluxo:
  1. CTA e pilar do dia (ciclos com memoria em estado_ciclo.json)
  2. a CURADORIA escolhe o conteudo, o formato, o tom e — se for o caso — qual
     foto ou qual produto entra (ver curadoria.py: rosto e recurso escasso)
  3. gera a arte (1 imagem, ou os slides do carrossel)
  4. commita/sobe as imagens (a API exige URL https publica)
  5. publica, registra (com formato/tom/foto/produto) e grava o estado
  6. story de reforco (no carrossel, a capa)

Uso:
    python publicar_estatico.py --ensaio     # gera a arte e para
    python publicar_estatico.py              # proximo da fila
    python publicar_estatico.py --id 7       # conteudo especifico
    python publicar_estatico.py --garantir   # so publica se ainda nao saiu hoje
"""
from __future__ import annotations

import argparse
import os

import carrossel
import config
import curadoria
import formatos
import legenda
import publicador as pb

BASE = pb.BASE
CONTEUDOS = os.path.join(BASE, "conteudos.json")
PRODUTOS = os.path.join(BASE, "produtos.json")
TIPO = "estatico"

FORMATOS = ("frase", "produto", "ritual", "mito", "dado", "retrato")


def gerar_arte(c: dict, formato: str, tom: dict, rodape: str, destino: str,
               foto: str | None, prod: dict | None) -> str:
    """Despacha para o formato. Um lugar so — quem cria formato novo mexe aqui."""
    etiqueta = c.get("etiqueta")

    if formato == "ritual":
        return formatos.ritual(c["gancho"], c["passos"], destino, tom,
                               etiqueta=etiqueta or "rotina", rodape=rodape)
    if formato == "mito":
        return formatos.mito(c["mito"], c["verdade"], destino, rodape=rodape)
    if formato == "dado":
        return formatos.dado(c["numero"], c["frase"], destino, tom,
                             etiqueta=etiqueta, rodape=rodape)
    if formato == "produto" and prod:
        return formatos.produto(prod["arquivo"], prod["nome"], destino,
                                beneficio=c.get("beneficio"), linha=prod.get("linha"),
                                tom=tom, rodape=rodape)
    if formato == "retrato" and foto:
        return formatos.retrato(os.path.join(BASE, "fotos", foto), c["gancho"],
                                destino, etiqueta=etiqueta, rodape=rodape,
                                foco_y=c.get("foco_y", 0.32))
    # frase e tambem o plano B de qualquer formato sem o insumo que ele pede
    return formatos.frase(c["gancho"], destino, tom, etiqueta=etiqueta,
                          rodape=rodape, assinatura=c.get("assinatura"))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", type=int, default=None)
    p.add_argument("--ensaio", action="store_true")
    p.add_argument("--garantir", action="store_true",
                   help="rede de seguranca: publica so se o post do dia nao saiu")
    p.add_argument("--carrossel", action="store_true",
                   help="forca carrossel (se o conteudo tiver slides)")
    p.add_argument("--unico", action="store_true", help="forca imagem unica")
    a = p.parse_args()

    if a.garantir and pb.ja_publicou_hoje(TIPO):
        pb.log("estatico do dia ja esta no ar — nada a fazer")
        return

    estado = pb.carregar(pb.ESTADO, {})
    i_cta, cta = legenda.cta_do_dia(estado)
    i_pilar, pilar = legenda.pilar_do_dia(estado)

    banco = pb.carregar(CONTEUDOS, {"posts": []})["posts"]
    publicados = pb.registro()

    quer_carrossel = curadoria.dia_de_carrossel(publicados)

    if a.id is not None:
        c = next((x for x in banco if x["id"] == a.id), None)
        if not c:
            raise SystemExit(f"Conteudo id={a.id} nao existe")
    else:
        restantes = pb.fila(banco, TIPO)
        if len(restantes) <= 8:
            pb.log(f"AVISO: so restam {len(restantes)} conteudos no banco.")
        c = curadoria.escolher_conteudo(restantes, publicados, pilar,
                                        preferir_carrossel=quer_carrossel)

    if a.carrossel:
        quer_carrossel = True
    if a.unico:
        quer_carrossel = False
    eh_carrossel = bool(quer_carrossel and c.get("slides"))

    formato = "carrossel" if eh_carrossel else curadoria.formato_efetivo(c, publicados)
    if not eh_carrossel and formato != c.get("formato"):
        pb.log(f"orcamento de rosto esgotado: {c.get('formato')} -> {formato}")
    tom = curadoria.escolher_tom(c, publicados, formato)

    foto = prod = None
    if formato == "retrato":
        fotos = sorted(os.listdir(os.path.join(BASE, "fotos")))
        foto = curadoria.escolher_foto(fotos, publicados, c.get("foto"))
    if formato == "produto":
        catalogo = pb.carregar(PRODUTOS, {"produtos": []})["produtos"]
        prod = curadoria.escolher_produto(catalogo, publicados, c.get("produto"))

    hoje = pb.hoje()
    slug = f"{hoje}-est{c['id']:03d}"
    pasta = os.path.join(BASE, "imagens", hoje)
    rodape = legenda.rodape_do_cta(cta)

    if eh_carrossel:
        pecas = carrossel.montar(c, tom, rodape, pasta, slug)
        arte = pecas[0]  # a capa e o que ocupa a grade e vira story
        pb.log(f"carrossel: {len(pecas)} slides | tom {tom['nome']} | "
               f"pilar {pilar} | CTA {cta}")
    else:
        pecas = None
        arte = gerar_arte(c, formato, tom, rodape,
                          os.path.join(pasta, f"{slug}.jpg"), foto, prod)
        pb.log(f"arte: {os.path.basename(arte)} | {formato}/{tom['nome']} | "
               f"pilar {pilar} | CTA {cta}"
               + (f" | foto {foto}" if foto else "")
               + (f" | produto {prod['nome']}" if prod else ""))

    promocao = estado.get("promocao") or None
    # A legenda abre pelo que a pessoa acabou de ler na peca. No carrossel isso
    # e o titulo da CAPA, que nem sempre e o `gancho` do banco.
    conteudo = {**c, "gancho": c["slides"][0]["titulo"]} if eh_carrossel else c
    texto = legenda.montar(conteudo, cta, promocao)

    if a.ensaio:
        print("\n--- legenda ---\n" + texto + "\n---------------\n")
        pb.log("ensaio: parando antes de publicar")
        return

    tok = config.token()
    pb.conferir_token(tok)

    pb.commitar(f"arte do post {slug}", "imagens")
    import time
    time.sleep(5)  # folga para o CDN do raw responder

    if eh_carrossel:
        urls = [f"{config.REPO_RAW}/imagens/{hoje}/{os.path.basename(p)}"
                for p in pecas]
        pb.log(f"slides no ar: {urls[0]} … (+{len(urls) - 1})")
        media_id = pb.publicar_carrossel(urls, texto, tok)
    else:
        url = f"{config.REPO_RAW}/imagens/{hoje}/{os.path.basename(arte)}"
        pb.log(f"imagem no ar: {url}")
        media_id = pb.publicar_container({"image_url": url, "caption": texto}, tok)

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

    pb.anotar(TIPO, c["id"], media_id, cta, pilar, formato=formato,
              tom=tom["nome"], foto=foto, produto=prod["arquivo"] if prod else None,
              rosto=(formato == "retrato"))
    estado = pb.carregar(pb.ESTADO, {})
    estado.update({"cta_indice": i_cta, "cta": cta,
                   "pilar_indice": i_pilar, "pilar": pilar, "data": hoje})
    pb.salvar(pb.ESTADO, estado)
    pb.commitar(f"post {slug} publicado", "publicados.json", "estado_ciclo.json")


if __name__ == "__main__":
    main()
