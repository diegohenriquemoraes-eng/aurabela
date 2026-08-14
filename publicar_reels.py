# -*- coding: utf-8 -*-
"""Reels do dia (09h BRT) no feed da @aurabelastore_on.

Mesma espinha do publicar_estatico.py, com duas diferencas:
  - a midia e um mp4 montado localmente com ffmpeg (Ken Burns sobre as fotos
    reais dela) — sem IA de video, para nunca parar por limite de credito;
  - o container usa media_type=REELS e video_url; a API demora mais para
    processar video, entao esperar() tem folga maior.

Uso:
    python publicar_reels.py --ensaio      # monta o mp4 e para
    python publicar_reels.py               # proximo da fila
    python publicar_reels.py --id 3        # roteiro especifico
    python publicar_reels.py --garantir    # so publica se ainda nao saiu hoje
"""
from __future__ import annotations

import argparse
import os
import time

import config
import curadoria
import legenda
import publicador as pb
from arte import Tom
from gerar_reels import gerar_reels

BASE = pb.BASE
ROTEIROS = os.path.join(BASE, "reels.json")
TIPO = "reels"


def escolher(banco: list[dict], id_forcado: int | None, pilar: str,
             publicados: dict) -> dict:
    if id_forcado is not None:
        for r in banco:
            if r["id"] == id_forcado:
                return r
        raise SystemExit(f"Roteiro id={id_forcado} nao existe")

    restantes = pb.fila(banco, TIPO)
    if not restantes:
        raise SystemExit("Banco de roteiros esgotado — repor reels.json.")
    if len(restantes) <= 4:
        pb.log(f"AVISO: so restam {len(restantes)} roteiros no banco.")

    # Quando o orcamento de rosto esta gasto, prefere um roteiro que ja nao
    # pedia rosto — assim o Reels sai inteiro como foi escrito, em vez de ter a
    # cena da Marcia rebaixada para cartao de texto.
    if not curadoria.pode_rosto(publicados):
        sem_rosto = [r for r in restantes
                     if not any(c.get("tipo") == "retrato" for c in r["cenas"])]
        if sem_rosto:
            restantes = sem_rosto

    for r in restantes:
        if r.get("pilar") == pilar:
            return r
    pb.log(f"pilar {pilar}: nenhum roteiro casa, seguindo a fila")
    return restantes[0]


def montar_cenas(r: dict, cta: str, publicados: dict) -> tuple[list[dict], str | None]:
    """Converte o roteiro em cenas prontas. Devolve (cenas, foto usada).

    Duas travas de curadoria aqui:
      - no maximo UMA cena de rosto por Reels (o roteiro so tem uma; se alguem
        escrever duas, a segunda vira cartao de texto);
      - se o orcamento de rosto do feed estiver gasto, nenhuma.

    Era aqui que o banco de fotos morria: cada Reels usava 5 fotos do rosto dela
    e o banco inteiro tem 10.
    """
    tons = curadoria.sequencia_de_tons(publicados, len(r["cenas"]))
    rosto_liberado = curadoria.pode_rosto(publicados)
    foto_usada = None
    cenas = []

    escuro_antes = False
    for i, c in enumerate(r["cenas"]):
        tipo = c.get("tipo", "texto")
        tom = Tom.por_nome(c.get("tom") or tons[i]["nome"])
        # Duas cenas escuras seguidas fazem o Reels parecer travado no play — a
        # trava vale inclusive contra o tom escrito a mao no roteiro.
        if not tom["claro"] and escuro_antes and tipo != "retrato":
            tom = Tom.AREIA
        escuro_antes = not tom["claro"] or tipo == "retrato"

        cena = {
            "tipo": tipo,
            "texto": c["texto"],
            "etiqueta": c.get("etiqueta"),
            "rodape": c.get("rodape"),
            "dur": c.get("dur", 3.0),
            "tom": tom["nome"],
        }

        if tipo == "retrato":
            if rosto_liberado and not foto_usada:
                fotos = sorted(os.listdir(os.path.join(BASE, "fotos")))
                foto_usada = curadoria.escolher_foto(fotos, publicados, c.get("foto"))
                cena["foto"] = os.path.join(BASE, "fotos", foto_usada)
                cena["foco_y"] = c.get("foco_y", 0.32)
            else:
                cena["tipo"] = "texto"
                pb.log("orcamento de rosto: cena de retrato virou cartao de texto")
        elif tipo == "produto":
            cena["produto"] = c["produto"]

        if i == len(r["cenas"]) - 1 and not cena["rodape"]:
            cena["rodape"] = legenda.rodape_do_cta(cta)
        cenas.append(cena)

    return cenas, foto_usada


def trilha() -> str | None:
    """Primeira faixa de audio/ disponivel. Sem trilha o gerar_reels embute
    silencio — o Instagram recusa video sem faixa de audio nenhuma."""
    pasta = os.path.join(BASE, "audio")
    if not os.path.isdir(pasta):
        return None
    faixas = sorted(f for f in os.listdir(pasta) if f.lower().endswith((".mp3", ".m4a", ".aac")))
    return os.path.join(pasta, faixas[0]) if faixas else None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", type=int, default=None)
    p.add_argument("--ensaio", action="store_true")
    p.add_argument("--garantir", action="store_true")
    a = p.parse_args()

    if a.garantir and pb.ja_publicou_hoje(TIPO):
        pb.log("reels do dia ja esta no ar — nada a fazer")
        return

    estado = pb.carregar(pb.ESTADO, {})
    i_cta, cta = legenda.cta_do_dia(estado)
    i_pilar, pilar = legenda.pilar_do_dia(estado)

    banco = pb.carregar(ROTEIROS, {"reels": []})["reels"]
    publicados = pb.registro()
    r = escolher(banco, a.id, pilar, publicados)

    hoje = pb.hoje()
    slug = f"{hoje}-reel{r['id']:03d}"
    destino = os.path.join(BASE, "imagens", hoje, f"{slug}.mp4")

    cenas, foto = montar_cenas(r, cta, publicados)
    pb.log(f"montando o video ({len(cenas)} cenas)...")
    video = gerar_reels(cenas, destino, audio=trilha())
    tam = os.path.getsize(video) / 1024 / 1024
    pb.log(f"video: {os.path.basename(video)} ({tam:.1f} MB) | pilar {pilar} | "
           f"CTA {cta}" + (f" | foto {foto}" if foto else " | sem rosto"))

    promocao = estado.get("promocao") or None
    conteudo = {"gancho": r["cenas"][0]["texto"], "corpo": r["corpo"],
                "pilar": r.get("pilar", "educativo")}
    texto = legenda.montar(conteudo, cta, promocao)

    if a.ensaio:
        print("\n--- legenda ---\n" + texto + "\n---------------\n")
        pb.log("ensaio: parando antes de publicar")
        return

    tok = config.token()
    pb.conferir_token(tok)

    pb.commitar(f"video do reels {slug}", "imagens")
    url = f"{config.REPO_RAW}/imagens/{hoje}/{os.path.basename(video)}"
    pb.log(f"video no ar: {url}")
    time.sleep(6)  # folga maior: arquivo grande no CDN do raw

    media_id = pb.publicar_container(
        {"media_type": "REELS", "video_url": url, "caption": texto}, tok)

    # O tom gravado e o da CAPA (cena 1): e ele que ocupa o quadradinho da
    # grade do perfil, entao e ele que a curadoria precisa alternar.
    pb.anotar(TIPO, r["id"], media_id, cta, pilar, foto=foto, rosto=bool(foto),
              tom=cenas[0]["tom"],
              produto=next((c["produto"] for c in cenas if c.get("produto")), None))
    estado = pb.carregar(pb.ESTADO, {})
    estado.update({"cta_indice": i_cta, "cta": cta,
                   "pilar_indice": i_pilar, "pilar": pilar, "data": hoje})
    pb.salvar(pb.ESTADO, estado)
    pb.commitar(f"reels {slug} publicado", "publicados.json", "estado_ciclo.json")


if __name__ == "__main__":
    main()
