# -*- coding: utf-8 -*-
"""Confere os bancos antes de o robo publicar. Sai com codigo 1 se achar problema.

Nasceu de um defeito que so apareceu no mosaico da simulacao: o mesmo gancho
escrito em `conteudos.json` e em `reels.json` produzia DUAS pecas praticamente
iguais na grade do perfil, com dias de diferenca. Cada banco estava certo
sozinho; o erro so existia entre eles.

Confere:
  1. capas repetidas ou parecidas demais entre os dois bancos (o que o visitante
     ve lado a lado na grade)
  2. arquivos referenciados que nao existem (produto, foto)
  3. campos obrigatorios de cada formato
  4. pilar valido e roteiro de carrossel bem formado

Uso:
    python ferramentas/conferir_bancos.py
"""
from __future__ import annotations

import difflib
import json
import os
import re
import sys
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import legenda  # noqa: E402

SEMELHANCA = 0.72  # acima disso, duas capas leem como a mesma peca na grade

OBRIGATORIOS = {
    "ritual": ("gancho", "passos"),
    "mito": ("mito", "verdade"),
    "dado": ("numero", "frase"),
    "produto": ("gancho", "produto"),
    "retrato": ("gancho", "foto"),
    "frase": ("gancho",),
}


def _chave(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", "", t).strip()


def main() -> None:
    with open(os.path.join(BASE, "conteudos.json"), encoding="utf-8") as f:
        posts = json.load(f)["posts"]
    with open(os.path.join(BASE, "reels.json"), encoding="utf-8") as f:
        reels = json.load(f)["reels"]
    with open(os.path.join(BASE, "produtos.json"), encoding="utf-8") as f:
        produtos = {p["arquivo"] for p in json.load(f)["produtos"]}
    fotos = set(os.listdir(os.path.join(BASE, "fotos")))

    erros, avisos = [], []

    # ------------------------------------------------------------ 1. capas
    capas = []
    for p in posts:
        capas.append((f"post {p['id']}", p["gancho"]))
        if p.get("slides"):
            capas.append((f"post {p['id']} (capa do carrossel)",
                          p["slides"][0]["titulo"]))
    for r in reels:
        capas.append((f"reels {r['id']}", r["cenas"][0]["texto"]))

    for i, (onde_a, txt_a) in enumerate(capas):
        for onde_b, txt_b in capas[i + 1:]:
            if onde_a.split(" (")[0] == onde_b.split(" (")[0]:
                continue  # capa e gancho do mesmo post podem se parecer
            r = difflib.SequenceMatcher(None, _chave(txt_a), _chave(txt_b)).ratio()
            if r >= SEMELHANCA:
                erros.append(f"capas parecidas ({r:.0%}) — {onde_a}: \"{txt_a}\" "
                             f"× {onde_b}: \"{txt_b}\"")

    # ------------------------------------------- 2 e 3. campos e referencias
    for p in posts:
        fmt = p.get("formato")
        if fmt not in OBRIGATORIOS:
            erros.append(f"post {p['id']}: formato desconhecido '{fmt}'")
        else:
            faltam = [c for c in OBRIGATORIOS[fmt] if not p.get(c)]
            if faltam:
                erros.append(f"post {p['id']} ({fmt}): faltam {faltam}")
        if p.get("pilar") not in legenda.CICLO_PILAR:
            erros.append(f"post {p['id']}: pilar '{p.get('pilar')}' fora do ciclo")
        if p.get("produto") and p["produto"] not in produtos:
            erros.append(f"post {p['id']}: produto inexistente {p['produto']}")
        if p.get("foto") and p["foto"] not in fotos:
            erros.append(f"post {p['id']}: foto inexistente {p['foto']}")

        # ------------------------------------------------- 4. carrossel
        if p.get("slides"):
            s = p["slides"]
            if s[0].get("tipo") != "capa":
                erros.append(f"post {p['id']}: carrossel nao comeca por 'capa'")
            if len(s) > 10:
                erros.append(f"post {p['id']}: {len(s)} slides (a API para em 10)")
            if len(s) < 4:
                avisos.append(f"post {p['id']}: so {len(s)} slides — carrossel curto")
            for k, sl in enumerate(s, 1):
                if not sl.get("titulo"):
                    erros.append(f"post {p['id']} slide {k}: sem titulo")
                if sl.get("produto") and sl["produto"] not in produtos:
                    erros.append(f"post {p['id']} slide {k}: produto inexistente")

    for r in reels:
        if r.get("pilar") not in legenda.CICLO_PILAR:
            erros.append(f"reels {r['id']}: pilar '{r.get('pilar')}' fora do ciclo")
        rostos = [c for c in r["cenas"] if c.get("tipo") == "retrato"]
        if len(rostos) > 1:
            erros.append(f"reels {r['id']}: {len(rostos)} cenas de rosto (max 1)")
        for k, c in enumerate(r["cenas"], 1):
            if c.get("tipo") == "produto" and c.get("produto") not in produtos:
                erros.append(f"reels {r['id']} cena {k}: produto inexistente")
            if c.get("tipo") == "retrato" and c.get("foto") not in fotos:
                erros.append(f"reels {r['id']} cena {k}: foto inexistente")

    # -------------------------------------------------------------- relatorio
    com_slides = [p for p in posts if p.get("slides")]
    print(f"{len(posts)} posts ({len(com_slides)} viram carrossel) · "
          f"{len(reels)} roteiros de Reels")
    for a in avisos:
        print(f"  aviso: {a}")
    for e in erros:
        print(f"  ERRO: {e}")
    if erros:
        sys.exit(f"\n{len(erros)} problema(s).")
    print("bancos ok.")


if __name__ == "__main__":
    main()
