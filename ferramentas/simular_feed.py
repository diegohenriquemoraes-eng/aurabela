# -*- coding: utf-8 -*-
"""Simula N dias de feed SEM publicar e monta o mosaico do perfil.

Serve para responder a unica pergunta que importa antes de deixar o robo solto:
"como fica a grade do perfil depois de duas semanas?" — e para provar, com
numero, quantas vezes o rosto da Marcia aparece e quantas fotos do banco foram
gastas.

Uso:
    python ferramentas/simular_feed.py 14      # 14 dias (28 pecas)
"""
from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

import curadoria
import formatos
import legenda
from arte import Tom
from gerar_reels import _quadro, _quadro_produto, _quadro_texto

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(BASE, "saida-amostra", "simulacao")


def _ler(nome):
    with open(os.path.join(BASE, nome), encoding="utf-8") as f:
        return json.load(f)


def capa_do_reels(r: dict, publicados: dict, cta: str, destino: str) -> tuple[str, str | None]:
    """Monta as cenas de verdade (publicar_reels.montar_cenas) e desenha a 1a.

    Usa a funcao real, e nao uma copia, para o numero de rosto sair honesto: a
    cena com a Marcia costuma ser a 2a ou a 3a do roteiro, nao a capa. Contar so
    a capa daria a ilusao de que o Reels nao gasta foto.
    """
    import publicar_reels as pr

    cenas, foto = pr.montar_cenas(r, cta, publicados)
    c = cenas[0]
    tom = Tom.por_nome(c.get("tom"))
    if c["tipo"] == "retrato":
        _quadro(c["foto"], c["texto"], destino, etiqueta=c.get("etiqueta"),
                rodape=c.get("rodape"))
    elif c["tipo"] == "produto":
        _quadro_produto(c["produto"], c["texto"], destino, tom,
                        etiqueta=c.get("etiqueta"), rodape=c.get("rodape"))
    else:
        _quadro_texto(c["texto"], destino, tom, etiqueta=c.get("etiqueta"),
                      rodape=c.get("rodape"), centralizar=True)
    return destino, foto, c["tom"]


def main() -> None:
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    posts = _ler("conteudos.json")["posts"]
    reels = _ler("reels.json")["reels"]
    catalogo = _ler("produtos.json")["produtos"]

    os.makedirs(SAIDA, exist_ok=True)
    publicados = {"posts": []}
    estado = {}
    grade, relatorio = [], []

    for dia in range(dias):
        for tipo in ("reels", "estatico"):
            i_cta, cta = legenda.cta_do_dia(estado)
            i_pilar, pilar = legenda.pilar_do_dia(estado)
            estado.update({"cta_indice": i_cta, "pilar_indice": i_pilar})
            usados = {p["id"] for p in publicados["posts"] if p["tipo"] == tipo}
            n = len(publicados["posts"])
            alvo = os.path.join(SAIDA, f"{n:03d}-{tipo}.jpg")

            if tipo == "reels":
                fila = [r for r in reels if r["id"] not in usados] or reels
                if not curadoria.pode_rosto(publicados):
                    sem = [r for r in fila
                           if not any(c.get("tipo") == "retrato" for c in r["cenas"])]
                    fila = sem or fila
                r = next((x for x in fila if x.get("pilar") == pilar), fila[0])
                png = alvo.replace(".jpg", ".png")
                _, foto, tom_capa = capa_do_reels(r, publicados, cta, png)
                Image.open(png).convert("RGB").save(alvo, "JPEG", quality=90)
                os.remove(png)
                registro = {"tipo": tipo, "id": r["id"], "pilar": pilar,
                            "formato": "reels", "foto": foto, "rosto": bool(foto),
                            "tom": tom_capa}
            else:
                fila = [c for c in posts if c["id"] not in usados] or posts
                c = curadoria.escolher_conteudo(fila, publicados, pilar)
                formato = curadoria.formato_efetivo(c, publicados)
                tom = curadoria.escolher_tom(c, publicados, formato)
                foto = prod = None
                if formato == "retrato":
                    fotos = sorted(os.listdir(os.path.join(BASE, "fotos")))
                    foto = curadoria.escolher_foto(fotos, publicados, c.get("foto"))
                if formato == "produto":
                    prod = curadoria.escolher_produto(catalogo, publicados,
                                                      c.get("produto"))
                import publicar_estatico as pe
                pe.gerar_arte(c, formato, tom, legenda.rodape_do_cta(cta), alvo,
                              foto, prod)
                registro = {"tipo": tipo, "id": c["id"], "pilar": pilar,
                            "formato": formato, "tom": tom["nome"], "foto": foto,
                            "produto": prod["arquivo"] if prod else None,
                            "rosto": formato == "retrato"}

            publicados["posts"].append(registro)
            grade.append(alvo)
            relatorio.append(registro)

    # --------------------------------------------------------------- mosaico
    # 3 colunas, mais novo em cima, miniatura 4:5 — desde 2025 a grade do perfil
    # e 4:5, nao quadrada. O estatico entra inteiro; o Reels (9:16) e cortado no
    # miolo, que e por isso que a capa dele leva o texto centralizado.
    larg_m, alt_m = 300, 375
    linhas = (len(grade) + 2) // 3
    mosaico = Image.new("RGB", (3 * larg_m + 8, linhas * alt_m + (linhas - 1) * 4),
                        (255, 255, 255))
    for i, caminho in enumerate(reversed(grade)):
        im = Image.open(caminho).convert("RGB")
        alvo_prop = larg_m / alt_m
        if im.width / im.height > alvo_prop:
            corte_l = int(im.height * alvo_prop)
            im = im.crop(((im.width - corte_l) // 2, 0,
                          (im.width - corte_l) // 2 + corte_l, im.height))
        else:
            corte_a = int(im.width / alvo_prop)
            topo = int((im.height - corte_a) * 0.5)
            im = im.crop((0, topo, im.width, topo + corte_a))
        im = im.resize((larg_m, alt_m), Image.LANCZOS)
        mosaico.paste(im, ((i % 3) * (larg_m + 4), (i // 3) * (alt_m + 4)))
    mosaico.save(os.path.join(SAIDA, "00-perfil.jpg"), quality=92)

    # -------------------------------------------------------------- numeros
    total = len(relatorio)
    rostos = [r for r in relatorio if r["rosto"]]
    print(f"\n{dias} dias · {total} pecas")
    print(f"rosto da Marcia: {len(rostos)} pecas ({len(rostos)*100//total}%)"
          f" — 1 a cada {total // max(1, len(rostos))}")
    print("fotos gastas:", dict(collections.Counter(r["foto"] for r in rostos)))
    print("formatos:", dict(collections.Counter(r["formato"] for r in relatorio)))
    print("tons:", dict(collections.Counter(r.get("tom") for r in relatorio
                                            if r.get("tom"))))
    print("pilares:", dict(collections.Counter(r["pilar"] for r in relatorio)))
    print(f"\nmosaico: {os.path.join(SAIDA, '00-perfil.jpg')}")


if __name__ == "__main__":
    main()
