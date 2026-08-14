# -*- coding: utf-8 -*-
"""Peças comuns aos dois publicadores: API, git, fila e estado.

Separado para o publicar_estatico.py e o publicar_reels.py nao repetirem codigo
— foi a licao do vendanaobra, onde publicar.py e publicar_miniaula.py duplicam
a mesma logica de container/commit.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import config

# O console do Windows abre em cp1252 e estoura em emoji (as legendas tem
# varios). Nao afeta o que vai para a API — que e UTF-8 — mas derruba o
# --ensaio e o log. Reconfigura na importacao, uma vez, para os dois
# publicadores.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLICADOS = os.path.join(BASE, "publicados.json")
ESTADO = os.path.join(BASE, "estado_ciclo.json")

FUSO_BR = timezone(timedelta(hours=-3))


def log(msg: str) -> None:
    print(f"[{datetime.now(FUSO_BR):%H:%M:%S}] {msg}", flush=True)


def hoje() -> str:
    return datetime.now(FUSO_BR).strftime("%Y-%m-%d")


# ------------------------------------------------------------------ API
def _post(endpoint: str, campos: dict) -> dict:
    dados = urllib.parse.urlencode(campos).encode()
    req = urllib.request.Request(f"{config.API}/{endpoint}", data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API falhou em {endpoint}: {e.read().decode(errors='replace')}")


def _get(endpoint: str, campos: dict) -> dict:
    url = f"{config.API}/{endpoint}?" + urllib.parse.urlencode(campos)
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API falhou em {endpoint}: {e.read().decode(errors='replace')}")


def conferir_token(tok: str) -> None:
    """Falha cedo e com mensagem clara se o token morreu."""
    r = _get("me", {"fields": "username", "access_token": tok})
    log(f"token ok — @{r.get('username')}")


def esperar(container_id: str, tok: str, tentativas: int = 60) -> None:
    """A API precisa baixar a midia antes de deixar publicar. Video demora mais
    que imagem — por isso 60 tentativas (ate ~4 min)."""
    for _ in range(tentativas):
        r = _get(container_id, {"fields": "status_code,status", "access_token": tok})
        estado = r.get("status_code")
        if estado == "FINISHED":
            return
        if estado == "ERROR":
            raise SystemExit(f"Container {container_id} falhou: {r.get('status')}")
        time.sleep(4)
    raise SystemExit(f"Container {container_id} nao ficou pronto a tempo")


def publicar_container(criacao: dict, tok: str) -> str:
    """Cria o container, espera ficar pronto e publica. Devolve o media_id."""
    criacao = {**criacao, "access_token": tok}
    cid = _post(f"{config.IG_USER_ID}/media", criacao)["id"]
    log(f"container {cid}")
    esperar(cid, tok)
    post = _post(f"{config.IG_USER_ID}/media_publish",
                 {"creation_id": cid, "access_token": tok})
    log(f"PUBLICADO: {post['id']}")
    return post["id"]


# ------------------------------------------------------------------ git
def git(*args: str) -> None:
    subprocess.run(["git", *args], cwd=BASE, check=True)


def commitar(mensagem: str, *caminhos: str) -> None:
    """Commita e sobe. Silencioso quando nao ha nada novo."""
    git("add", *caminhos)
    tem = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=BASE).returncode != 0
    if tem:
        git("-c", "user.name=aurabela-bot", "-c", "user.email=bot@aurabela.local",
            "commit", "-m", mensagem)
    git("push", "origin", "main")


# ------------------------------------------------------------------ estado
def carregar(caminho: str, padrao):
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar(caminho: str, dados) -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")


def registro() -> dict:
    return carregar(PUBLICADOS, {"posts": []})


def ja_publicou_hoje(tipo: str) -> bool:
    """Evita post duplicado quando a rede de seguranca roda depois do normal."""
    h = hoje()
    return any(p["data"] == h and p.get("tipo") == tipo for p in registro()["posts"])


def anotar(tipo: str, item_id: int, media_id: str, cta: str, pilar: str,
           **extras) -> None:
    """Registra a peca publicada.

    Os extras (formato, tom, foto, produto, rosto) nao sao enfeite de log: sao a
    memoria que a curadoria le para nao repetir formato, nao repetir tom e,
    principalmente, para saber quando o rosto da Marcia pode voltar a aparecer.
    """
    reg = registro()
    reg["posts"].append({
        "tipo": tipo, "id": item_id, "data": hoje(),
        "media_id": media_id, "cta": cta, "pilar": pilar,
        **{k: v for k, v in extras.items() if v},
    })
    salvar(PUBLICADOS, reg)


def fila(banco: list[dict], tipo: str) -> list[dict]:
    """Banco menos o que ja saiu, preservando a ordem do banco."""
    ja = {p["id"] for p in registro()["posts"] if p.get("tipo") == tipo}
    return [x for x in banco if x["id"] not in ja]
