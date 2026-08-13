# -*- coding: utf-8 -*-
"""Renova o token de longa duracao da conta da Marcia.

Por que existe: a API do Instagram com Instagram Login emite token de 60 dias
(diferente do System User do vendanaobra, que nunca expira). Um token vencido
mataria o projeto em silencio — que e exatamente o que aconteceu com o blog do
vendanaobra. Entao renovamos TODO MES, com folga de 30 dias.

Como funciona: `GET /refresh_access_token` devolve um token novo de mais 60
dias. Exige que o token atual tenha pelo menos 24h de vida e ainda esteja
valido.

O workflow token-renovar.yml roda dia 1 de cada mes, grava o token novo no
secret do repositorio (via GitHub API) e abre issue se falhar.

Uso:
    python renovar_token.py            # renova e imprime quanto tempo sobrou
    python renovar_token.py --checar   # so informa a validade, nao renova
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

import config

BASE = os.path.dirname(os.path.abspath(__file__))

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def _get(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Falhou: {e.read().decode(errors='replace')}")


def validade(tok: str) -> dict:
    """Quanto tempo o token ainda tem. Serve de alarme antecipado."""
    url = "https://graph.instagram.com/me?" + urllib.parse.urlencode(
        {"fields": "username", "access_token": tok})
    r = _get(url)
    return r


def renovar(tok: str) -> dict:
    url = "https://graph.instagram.com/refresh_access_token?" + urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": tok})
    return _get(url)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--checar", action="store_true",
                   help="so confere se o token esta vivo, nao renova")
    a = p.parse_args()

    tok = config.token()
    quem = validade(tok)
    print(f"token vivo — @{quem.get('username')}")

    if a.checar:
        return

    novo = renovar(tok)
    dias = int(novo.get("expires_in", 0)) // 86400
    print(f"token renovado — vale por mais {dias} dias")

    # Na nuvem, o workflow le esta saida e grava o secret. Local, salva no
    # arquivo para o proximo uso manual.
    saida = os.environ.get("GITHUB_OUTPUT")
    if saida:
        with open(saida, "a", encoding="utf-8") as f:
            f.write(f"token={novo['access_token']}\n")
            f.write(f"dias={dias}\n")
    elif os.path.exists(config.ARQUIVO_TOKEN):
        with open(config.ARQUIVO_TOKEN, "w", encoding="utf-8") as f:
            f.write(novo["access_token"])
        print(f"gravado em {config.ARQUIVO_TOKEN}")


if __name__ == "__main__":
    main()
