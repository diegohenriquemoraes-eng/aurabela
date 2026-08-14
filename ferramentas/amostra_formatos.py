# -*- coding: utf-8 -*-
"""Gera uma amostra de cada formato do feed em saida-amostra/formatos/.

Serve para conferir a arte no olho antes de deixar o robo publicar — e para ver
os formatos LADO A LADO, que e como o visitante do perfil ve.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import formatos
from arte import Tom

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(BASE, "saida-amostra", "formatos")

produtos = json.load(open(os.path.join(BASE, "produtos.json"), encoding="utf-8"))["produtos"]
serum = next(p for p in produtos if "Sérum Facial Renovador" in p["nome"])
micelar = next(p for p in produtos if "Micelar" in p["nome"])

formatos.frase(
    "Você foi ensinada a cuidar de todos, menos de você.",
    os.path.join(SAIDA, "01-frase-areia.jpg"), Tom.AREIA,
    etiqueta="autocuidado 30+", rodape="salva pra você")

formatos.frase(
    "A pele do Instagram não existe.",
    os.path.join(SAIDA, "02-frase-cafe.jpg"), Tom.CAFE,
    etiqueta="verdade", rodape="comenta PELE", assinatura="Marcia · AuraBela")

formatos.produto(
    serum["arquivo"], serum["nome"],
    os.path.join(SAIDA, "03-produto.jpg"),
    beneficio="Vitamina C + E na camada onde o creme não chega.",
    linha=serum["linha"], tom=Tom.ROSE, rodape="link na bio")

formatos.produto(
    micelar["arquivo"], micelar["nome"],
    os.path.join(SAIDA, "04-produto-creme.jpg"),
    beneficio="Tira a maquiagem sem esfregar — e sem ressecar.",
    linha=micelar["linha"], tom=Tom.CREME, rodape="link na bio")

formatos.ritual(
    "A ordem certa de passar o seu skincare",
    ["Limpar — tira a oleosidade e a poluição do dia",
     "Tônico — devolve o equilíbrio da pele",
     "Sérum — é aqui que mora o ativo",
     "Hidratante — sela tudo o que veio antes",
     "Protetor — de manhã, sempre, mesmo em casa"],
    os.path.join(SAIDA, "05-ritual.jpg"), Tom.CREME, etiqueta="rotina")

formatos.mito(
    "Pele oleosa não precisa de hidratante.",
    "Pele sem água produz MAIS óleo para se defender. Hidratar é o que desliga a oleosidade.",
    os.path.join(SAIDA, "06-mito.jpg"))

formatos.dado(
    "80%",
    "do envelhecimento da pele vem do sol — não da idade.",
    os.path.join(SAIDA, "07-dado.jpg"), Tom.CAFE,
    etiqueta="o que ninguém conta", rodape="salva pra não esquecer")

formatos.retrato(
    os.path.join(BASE, "fotos", "ref-01-closeup-frontal-sem-oculos.jpg"),
    "Minha pele aos 40, sem filtro e sem promessa milagrosa",
    os.path.join(SAIDA, "08-retrato.jpg"),
    etiqueta="sem filtro", rodape="comenta PELE")

print("amostras em", SAIDA)
