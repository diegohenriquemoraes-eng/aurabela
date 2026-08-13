# -*- coding: utf-8 -*-
"""Identificadores da conta e do app. Nada de segredo aqui — token vem do ambiente.

Levantado em 12/08/2026, com o app proprio criado para a Marcia (isolado do
vendanaobra: outro app, outro token, outro repositorio).

  App do Facebook   4100345400259383   "aurabela"
  App do Instagram  1069671342251434   "aurabela-IG"
  IG User ID        17841461553382411  @aurabelastore_on

Por que a API do Instagram com Instagram Login (e nao a Graph API classica):
a conta da Marcia NAO tem Pagina do Facebook (so o perfil pessoal dela). A Graph
API classica exige Pagina; esta nao exige. Em troca, o token dura 60 dias em vez
de nunca expirar — por isso o renovar_token.py roda todo mes e o efeito pratico
acaba sendo o mesmo: nao para.
"""
from __future__ import annotations

import os

IG_USER_ID = "17841461553382411"          # @aurabelastore_on
IG_APP_ID = "1069671342251434"            # aurabela-IG
FB_APP_ID = "4100345400259383"            # app "aurabela"

API = "https://graph.instagram.com/v21.0"

# Repositorio publico que serve as midias: a API baixa a imagem/video por URL
# https publica (nao aceita upload de arquivo local) — mesma razao do vendanaobra.
REPO_RAW = "https://raw.githubusercontent.com/diegohenriquemoraes-eng/aurabela/main"

ARQUIVO_TOKEN = r"C:\Users\NOTE\Desktop\Perffec\Claude\aurabela_token.txt"


def token() -> str:
    """Token da conta da Marcia. Ambiente primeiro (e o que vale na nuvem),
    arquivo local depois (para rodar na mao aqui)."""
    t = os.environ.get("IG_TOKEN_AURABELA", "").strip()
    if t:
        return t
    if os.path.exists(ARQUIVO_TOKEN):
        # utf-8-sig, nao utf-8: o PowerShell grava BOM por padrao, e os 3 bytes
        # invisiveis do BOM entram no comeco do token e a API responde
        # "Cannot parse access token" — erro que nao parece de encoding.
        with open(ARQUIVO_TOKEN, encoding="utf-8-sig") as f:
            return f.read().strip()
    raise SystemExit(
        "Sem token: defina IG_TOKEN_AURABELA no ambiente ou salve o token em "
        f"{ARQUIVO_TOKEN}"
    )
