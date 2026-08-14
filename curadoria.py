# -*- coding: utf-8 -*-
"""Curadoria do feed: quem entra hoje, em que formato e em que tom.

O problema que este arquivo resolve (14/08/2026): o rosto da Marcia e um ativo
ESCASSO — sao 10 fotos — e estava sendo gasto em 100% das pecas. Na conta antiga
(1 foto por estatico + 5 por Reels) o feed queimava ~42 usos de foto por semana
em 10 arquivos: cada foto dela reaparecia 4x por semana. Em um mes o perfil
inteiro seria a mesma cara repetida, e o banco estaria morto.

A regra nova: o rosto e RARO e o resto do feed vive de formatos que nao dependem
dele (frase, produto, ritual, mito, dado). O rosto passa a valer o que vale —
quando ela aparece, e porque a peca PRECISA dela (prova, antes/depois,
autocuidado no olho, "sou eu quem testa").

Tudo aqui e deterministico e auditavel: mesmo historico, mesma escolha. Nada de
sorteio — sorteio repete e ninguem consegue explicar por que repetiu.
"""
from __future__ import annotations

from arte import Tom

# ------------------------------------------------------------------ orcamento
# 1 peca com o rosto dela a cada 6 publicadas (Reels + estatico contam juntos —
# os dois ocupam a mesma grade do perfil). Com 14 pecas/semana isso da ~2
# aparicoes por semana e ~10 usos por mes distribuidos em 10 fotos: cada foto
# volta a aparecer a cada ~3 semanas, e o banco dura o ano.
ORCAMENTO_ROSTO = 6

COOLDOWN_FORMATO = 3    # nao repetir formato dentro das 3 ultimas pecas
COOLDOWN_TOM = 2        # nem o tom de fundo dentro das 2 ultimas
COOLDOWN_FOTO = 21      # uma foto dela so volta depois de 21 pecas
COOLDOWN_PRODUTO = 8    # nem o mesmo produto dentro de 8

FORMATOS_SEM_ROSTO = ("frase", "produto", "ritual", "mito", "dado", "editorial")


# ------------------------------------------------------------------ historico
def recentes(publicados: dict, n: int) -> list[dict]:
    """As n ultimas pecas publicadas (Reels e estatico na mesma linha do tempo).

    O feed e um so: contar so os estaticos deixaria o Reels queimar foto sem
    aparecer no orcamento.
    """
    return publicados.get("posts", [])[-n:]


def pode_rosto(publicados: dict) -> bool:
    return not any(p.get("rosto") for p in recentes(publicados, ORCAMENTO_ROSTO))


def _usados(publicados: dict, campo: str, n: int) -> set:
    return {p.get(campo) for p in recentes(publicados, n) if p.get(campo)}


# ------------------------------------------------------------------ conteudo
def escolher_conteudo(fila: list[dict], publicados: dict, pilar: str) -> dict:
    """Proximo conteudo: casa com o pilar do dia e respeita o orcamento de rosto.

    Ordem de preferencia:
      1. mesmo pilar, formato fora do cooldown, e permitido pelo orcamento
      2. mesmo pilar, ignorando o cooldown de formato (constancia > perfeicao)
      3. qualquer pilar permitido pelo orcamento
      4. o primeiro da fila — mas ai o rosto e substituido em `formato_efetivo`

    Publicar todo dia vale mais que a curadoria perfeita; o unico limite que
    NUNCA cede e o do rosto, porque esse gasta um recurso que nao se repoe.
    """
    if not fila:
        raise SystemExit("Banco de conteudos esgotado — repor conteudos.json.")

    rosto_ok = pode_rosto(publicados)
    formatos_travados = _usados(publicados, "formato", COOLDOWN_FORMATO)

    def permitido(c):
        return rosto_ok or c.get("formato") != "retrato"

    do_pilar = [c for c in fila if c.get("pilar") == pilar]
    for lote in (do_pilar, fila):
        folgados = [c for c in lote
                    if permitido(c) and c.get("formato") not in formatos_travados]
        if folgados:
            return folgados[0]
    for lote in (do_pilar, fila):
        livres = [c for c in lote if permitido(c)]
        if livres:
            return livres[0]
    return (do_pilar or fila)[0]


def formato_efetivo(c: dict, publicados: dict) -> str:
    """O formato que a peca vai usar de fato.

    Se o conteudo pede o rosto e o orcamento nao permite, ele NAO vira uma foto
    a mais: vira cartao de frase com o mesmo gancho. Fica bonito, entrega a
    mesma mensagem e nao gasta o que nao da para repor. Este e o unico ponto do
    sistema em que a regra do rosto pode ser lida — se mudar aqui, muda tudo.
    """
    fmt = c.get("formato", "frase")
    if fmt == "retrato" and not pode_rosto(publicados):
        return "frase"
    return fmt


# ---------------------------------------------------------------------- foto
def escolher_foto(fotos: list[str], publicados: dict, preferida: str | None = None) -> str:
    """Foto do rosto menos usada recentemente (LRU), respeitando o cooldown.

    A preferida do banco so vale se estiver fora do cooldown — o banco foi
    escrito a mao e nao sabe o que ja saiu esta semana.
    """
    travadas = _usados(publicados, "foto", COOLDOWN_FOTO)
    if preferida and preferida in fotos and preferida not in travadas:
        return preferida

    livres = [f for f in fotos if f not in travadas]
    candidatas = livres or fotos

    ordem = [p.get("foto") for p in publicados.get("posts", []) if p.get("foto")]
    def usada_em(f):
        return len(ordem) - 1 - ordem[::-1].index(f) if f in ordem else -1
    return sorted(candidatas, key=usada_em)[0]


# ------------------------------------------------------------------- produto
def escolher_produto(produtos: list[dict], publicados: dict,
                     preferido: str | None = None) -> dict | None:
    """Produto do dia: o preferido do conteudo, ou o menos exibido recentemente."""
    if not produtos:
        return None
    travados = _usados(publicados, "produto", COOLDOWN_PRODUTO)

    if preferido:
        for p in produtos:
            if preferido in (p["arquivo"], p["nome"], p.get("id")):
                if p["arquivo"] not in travados:
                    return p
                break

    ordem = [p.get("produto") for p in publicados.get("posts", []) if p.get("produto")]
    def usado_em(p):
        a = p["arquivo"]
        return len(ordem) - 1 - ordem[::-1].index(a) if a in ordem else -1
    livres = [p for p in produtos if p["arquivo"] not in travados] or produtos
    return sorted(livres, key=usado_em)[0]


# ----------------------------------------------------------------------- tom
def escolher_tom(c: dict, publicados: dict, formato: str) -> dict:
    """Tom de fundo — o que da RITMO ao mosaico do perfil.

    Duas travas: nao repetir o tom das ultimas pecas e nao empilhar duas pecas
    escuras (ou escura logo depois de retrato, que tambem le como escura). Um
    grid so de cartao claro parece catalogo; um so de escuro parece funeral.
    """
    if c.get("tom"):
        return Tom.por_nome(c["tom"])
    if formato == "mito":
        return Tom.AREIA  # o mito ja e bicolor por dentro

    ultimas = recentes(publicados, COOLDOWN_TOM)
    travados = {p.get("tom") for p in ultimas if p.get("tom")}
    veio_escuro = any(p.get("tom") == "cafe" or p.get("formato") == "retrato"
                      for p in recentes(publicados, 1))

    ordem = [p.get("tom") for p in publicados.get("posts", []) if p.get("tom")]
    def usado_em(t):
        n = t["nome"]
        return len(ordem) - 1 - ordem[::-1].index(n) if n in ordem else -1

    livres = [t for t in Tom.TODOS if t["nome"] not in travados] or Tom.TODOS
    if veio_escuro:
        claros = [t for t in livres if t["claro"]]
        livres = claros or livres
    return sorted(livres, key=usado_em)[0]


def sequencia_de_tons(publicados: dict, n: int) -> list[dict]:
    """Tons das cenas de um Reels, alternando claro e escuro.

    Um Reels inteiro no mesmo fundo parece que travou no play. Alternar da
    batida visual sem precisar de transicao nenhuma.
    """
    base = escolher_tom({}, publicados, "texto")
    contraste = Tom.CAFE if base["claro"] else Tom.AREIA
    apoio = Tom.CREME if base["nome"] != "creme" else Tom.ROSE
    ciclo = [base, contraste, apoio, contraste]
    return [ciclo[i % len(ciclo)] for i in range(n)]
