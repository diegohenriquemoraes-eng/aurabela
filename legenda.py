# -*- coding: utf-8 -*-
"""Ciclo de CTA + ciclo de pilar + montagem da legenda (com SEO).

Duas rotacoes independentes, as duas com memoria em estado_ciclo.json:

  CICLO_CTA   — o que o post PEDE (seguir, PELE, vitrine, oferta, CONSULTORA)
  CICLO_PILAR — o que o post ENTREGA (educativo, prova, autocuidado, produto,
                renda-extra)

Por que separados: se o pilar e o CTA andassem juntos, todo post de produto
cairia sempre no mesmo pedido e o perfil viraria vitrine. Girando em ciclos de
tamanhos diferentes (7 e 7, mas com composicoes distintas), a combinacao varia
naturalmente e o feed nunca fica repetitivo.

Como no vendanaobra, o avanco e pela POSICAO gravada, nunca pelo nome — nomes
repetem dentro do ciclo e list.index() acharia sempre a 1a ocorrencia, prendendo
a rotacao num sub-loop.

Conversao: no Instagram o link so e clicavel no Direct e na bio, nunca na
legenda do feed. Entao todo CTA de conversao pede uma PALAVRA no comentario
(comment-to-DM) e a bio guarda o link permanente da vitrine.
"""
from __future__ import annotations

VITRINE = "loja.marykay.com.br/minha-vitrine?slug=aurabela"

# --------------------------------------------------------------------- ciclos
# FOCO UNICO: VENDER PRODUTO. Decidido pelo Diego em 12/08/2026 — o perfil e
# loja, nao recrutamento. Perfil com dois focos (comprar E virar consultora)
# converte pior nos dois: a pessoa que quer comprar nao entende se aquilo e
# uma vitrine ou uma oportunidade de negocio. Por isso o CTA "consultora" e o
# pilar "renda-extra" saem do ciclo. Se um dia ela quiser reativar o
# recrutamento, basta recolocar as duas entradas — o resto do codigo aguenta.
CICLO_CTA = [
    "seguir",      # 0 · valor puro, constroi audiencia
    "pele",        # 1 · comment-to-DM: monta o ritual (captura + segmenta)
    "vitrine",     # 2 · link da bio
    "pele",        # 3
    "oferta",      # 4 · combo/promocao do mes
    "vitrine",     # 5
    "seguir",      # 6
]

CICLO_PILAR = [
    "educativo",    # 0
    "prova",        # 1
    "produto",      # 2
    "autocuidado",  # 3
    "educativo",    # 4
    "produto",      # 5
    "prova",        # 6
]

# --------------------------------------------------------------------- pecas
CTA = {
    "seguir": {
        "rodape": "salva pra não esquecer",
        "legenda": (
            "Se isso te ajudou, me segue aqui — todo dia tem dica de pele "
            "de verdade, sem enrolação e sem promessa milagrosa. 💛"
        ),
    },
    "pele": {
        "rodape": "comenta PELE",
        "legenda": (
            "Quer saber o que a SUA pele precisa (e o que ela não precisa)?\n"
            "Comenta *PELE* aqui embaixo que eu te chamo no Direct e monto seu "
            "ritual — de graça, sem compromisso nenhum."
        ),
    },
    "vitrine": {
        "rodape": "link na bio",
        "legenda": (
            "Os produtos que eu uso e indico estão na minha vitrine oficial — "
            "link na bio. 🛍️\nQualquer dúvida antes de comprar, me chama: eu "
            "prefiro te indicar o certo do que te vender o caro."
        ),
    },
    "oferta": {
        "rodape": "comenta EU QUERO",
        "legenda": (
            "Comenta *EU QUERO* que eu te mando os valores e as condições no "
            "Direct. 💌"
        ),
    },
}

# Hashtags: o Instagram conta ate ~5 com eficacia; mais que isso vira ruido.
# Em 2026 palavra-chave na legenda pesa mais que hashtag (SEO).
HASHTAGS = {
    "educativo": ["#skincare", "#cuidadoscomapele", "#pelemadura", "#rotinadeskincare", "#marykay"],
    "prova": ["#skincare", "#antesedepois", "#pele30mais", "#autocuidado", "#marykay"],
    "produto": ["#marykay", "#skincare", "#cosmeticos", "#peleiluminada", "#autocuidado"],
    "autocuidado": ["#autocuidado", "#amorproprio", "#mulheres40", "#autoestima", "#skincare"],
}


def avancar(estado: dict, chave: str, ciclo: list[str]) -> tuple[int, str]:
    """Proxima posicao do ciclo depois da ultima publicada.

    Avanca pela POSICAO (`{chave}_indice`), nunca pelo nome: nomes repetem no
    ciclo e buscar por nome prenderia a rotacao no inicio. Um dia que falhe nao
    adianta o ciclo — o estado so e gravado quando o post publica de fato.
    """
    i = estado.get(f"{chave}_indice")
    if not isinstance(i, int) or not 0 <= i < len(ciclo):
        i = -1
    prox = (i + 1) % len(ciclo)
    return prox, ciclo[prox]


def cta_do_dia(estado: dict) -> tuple[int, str]:
    return avancar(estado, "cta", CICLO_CTA)


def pilar_do_dia(estado: dict) -> tuple[int, str]:
    return avancar(estado, "pilar", CICLO_PILAR)


def rodape_do_cta(cta: str) -> str:
    return CTA[cta]["rodape"]


def montar(conteudo: dict, cta: str, promocao: str | None = None) -> str:
    """Legenda do post: gancho + corpo + (promocao) + CTA + hashtags.

    O corpo ja vem escrito a mao no banco (portugues revisado). A promocao,
    quando existir, entra ANTES do CTA — a oferta precisa aparecer enquanto a
    pessoa ainda esta lendo, nao depois do pedido de acao.
    """
    partes = [conteudo["gancho"], "", conteudo["corpo"]]

    if promocao:
        partes += ["", f"🎁 {promocao}"]

    partes += ["", CTA[cta]["legenda"]]

    tags = HASHTAGS.get(conteudo.get("pilar", "educativo"), HASHTAGS["educativo"])
    partes += ["", " ".join(tags)]

    return "\n".join(partes)
