# -*- coding: utf-8 -*-
"""Acrescenta roteiros ao banco de Reels (reels.json), sem tocar no que ja existe.

O banco de Reels e o que acaba primeiro: sao 12 roteiros para uma peca por dia,
contra 32 posts no banco de estaticos. Este script e o jeito de repor sem risco
de reescrever o arquivo inteiro a mao e perder um roteiro no meio.

Roda uma vez; ids ja presentes sao ignorados.
"""
from __future__ import annotations

import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NOVOS = [
    {
        "id": 13, "pilar": "educativo",
        "corpo": "Banho quente relaxa você e detona a sua pele.\n\nA água muito quente dissolve os lipídios que formam a barreira. Sem eles, a água que existe dentro da pele evapora — e é por isso que ela repuxa assim que você sai do box.\n\nRosto: água morna para fria, sempre. E fora do banho, se der.",
        "cenas": [
            {"tipo": "texto", "texto": "Você lava o rosto no banho quente?", "etiqueta": "barreira", "dur": 2.8},
            {"tipo": "texto", "texto": "A água quente dissolve a gordura que protege a pele.", "dur": 3.4},
            {"tipo": "texto", "texto": "Por isso ela repuxa assim que você sai do box.", "dur": 3.2},
            {"tipo": "produto", "texto": "Lava o rosto na pia, com água morna.", "produto": "gel-de-limpeza-4-em-1-timewise.png", "rodape": "fora do banho", "dur": 3.4},
            {"tipo": "texto", "texto": "Um hábito. Zero real. Muda em uma semana.", "etiqueta": "de graça", "dur": 3.2},
        ],
    },
    {
        "id": 14, "pilar": "produto",
        "corpo": "Esfregar o olho com algodão seco não tira maquiagem: espalha e machuca.\n\nA água micelar dissolve. Você encosta, espera cinco segundos e desliza — sem puxar a pele mais fina do rosto, que é justamente a da área dos olhos.\n\nCinco segundos de paciência valem anos de pálpebra.",
        "cenas": [
            {"tipo": "texto", "texto": "Você esfrega o olho pra tirar a maquiagem?", "etiqueta": "pare agora", "dur": 3.0},
            {"tipo": "texto", "texto": "A pele da pálpebra é a mais fina do rosto.", "dur": 2.8},
            {"tipo": "produto", "texto": "Encosta o algodão. Espera 5 segundos. Desliza.", "produto": "agua-micelar.png", "rodape": "sem esfregar", "dur": 3.8},
            {"tipo": "texto", "texto": "A micelar dissolve. Você não precisa de força.", "dur": 3.2},
            {"tipo": "texto", "texto": "Cinco segundos hoje. Anos de pálpebra depois.", "etiqueta": "o hábito", "dur": 3.4},
        ],
    },
    {
        "id": 15, "pilar": "autocuidado",
        "corpo": "Pele não mente. Semana de noite mal dormida, comida rápida e prazo apertado aparece no espelho na sexta.\n\nNão é culpa sua e não é falta de produto. É o corpo mostrando a conta.\n\nO que dá pra fazer é não abandonar o básico justamente na semana em que ele mais importa.",
        "cenas": [
            {"tipo": "texto", "texto": "Sua pele está mostrando a semana que você teve.", "etiqueta": "sem culpa", "dur": 3.2},
            {"tipo": "texto", "texto": "Noite mal dormida, comida rápida, prazo apertado.", "dur": 3.2},
            {"tipo": "texto", "texto": "Não é falta de produto. É o corpo mostrando a conta.", "dur": 3.6},
            {"tipo": "texto", "texto": "E é justamente aí que a gente larga a rotina.", "dur": 3.2},
            {"tipo": "texto", "texto": "Faz o básico. Só o básico. Já é muito.", "etiqueta": "hoje", "dur": 3.2},
        ],
    },
    {
        "id": 16, "pilar": "educativo",
        "corpo": "Se o seu creme acaba em três semanas, provavelmente você está usando demais.\n\nRosto inteiro: uma ervilha. Sérum: três a quatro gotas. Protetor: aí sim, dois dedos cheios — é o único em que quase todo mundo usa MENOS do que devia.\n\nProduto demais não entra: fica na superfície e some no travesseiro.",
        "cenas": [
            {"tipo": "texto", "texto": "Seu creme acaba rápido demais?", "etiqueta": "quantidade", "dur": 2.6},
            {"tipo": "texto", "texto": "Rosto inteiro: uma ervilha. Só isso.", "rodape": "hidratante", "dur": 3.0},
            {"tipo": "texto", "texto": "Sérum: três a quatro gotas.", "rodape": "sérum", "dur": 2.8},
            {"tipo": "produto", "texto": "Protetor é o contrário: dois dedos cheios.", "produto": "protetor-solar-fps-50.png", "rodape": "aqui sobra pouco", "dur": 3.6},
            {"tipo": "texto", "texto": "O que não entra fica na superfície e some no travesseiro.", "etiqueta": "sem desperdício", "dur": 3.6},
        ],
    },
    {
        "id": 17, "pilar": "prova",
        "corpo": "A pergunta que mais chega aqui: \"qual produto resolve tudo?\"\n\nA resposta honesta é nenhum. O que resolve é fazer três coisas simples todo dia, por meses. Produto bom acelera; produto bom sozinho não faz nada.\n\nSe alguém te prometer o contrário, desconfia.",
        "cenas": [
            {"tipo": "texto", "texto": "A pergunta que mais chega no meu Direct:", "etiqueta": "todo dia", "dur": 2.8},
            {"tipo": "texto", "texto": "“Qual produto resolve tudo?”", "dur": 2.6},
            {"tipo": "texto", "texto": "A resposta honesta é: nenhum.", "dur": 2.8},
            {"tipo": "texto", "texto": "O que resolve é fazer três coisas simples todo dia, por meses.", "dur": 3.8},
            {"tipo": "texto", "texto": "Produto bom acelera. Sozinho, não faz nada.", "etiqueta": "sem promessa", "dur": 3.4},
        ],
    },
    {
        "id": 18, "pilar": "produto",
        "corpo": "Esfoliação não é esfregar até arder — é acelerar a troca de células.\n\nUma a duas vezes por semana, com o rosto úmido, movimentos leves, trinta segundos. Depois, hidratante.\n\nSe ardeu ao passar o creme, você passou do ponto: dá uma semana de folga.",
        "cenas": [
            {"tipo": "texto", "texto": "Esfoliar não é esfregar até arder.", "etiqueta": "textura", "dur": 2.8},
            {"tipo": "texto", "texto": "É acelerar a troca de células — e ela tem ritmo próprio.", "dur": 3.6},
            {"tipo": "produto", "texto": "1 a 2 vezes por semana. Trinta segundos. Leve.", "produto": "esfoliante-facial.png", "rodape": "sem força", "dur": 3.6},
            {"tipo": "texto", "texto": "Depois, hidratante. Sempre.", "dur": 2.8},
            {"tipo": "texto", "texto": "Ardeu ao passar o creme? Passou do ponto.", "etiqueta": "o sinal", "dur": 3.4},
        ],
    },
    {
        "id": 19, "pilar": "educativo",
        "corpo": "Todo mundo fala em \"barreira da pele\" e quase ninguém explica o que é.\n\nÉ a camada mais externa: células e gordura, como tijolo e cimento. O tijolo segura a água dentro; o cimento impede que o de fora entre.\n\nQuase todo problema de pele que eu vejo começa com esse cimento danificado.",
        "cenas": [
            {"tipo": "texto", "texto": "O que é a tal “barreira da pele”?", "etiqueta": "o básico", "dur": 2.8},
            {"tipo": "texto", "texto": "Imagina um muro: célula é o tijolo, gordura é o cimento.", "dur": 3.6},
            {"tipo": "texto", "texto": "O muro segura a água dentro e impede o de fora de entrar.", "dur": 3.6},
            {"tipo": "texto", "texto": "Sabonete errado, água quente e esfoliação demais quebram o cimento.", "dur": 3.8},
            {"tipo": "texto", "texto": "Quase todo problema de pele começa aí.", "etiqueta": "a raiz", "dur": 3.2},
        ],
    },
    {
        "id": 20, "pilar": "autocuidado",
        "corpo": "Pele saudável tem poro, tem textura, tem um dia pior antes da menstruação.\n\nO que a gente vê na tela é filtro, luz de anel e edição — e ninguém escreve isso na legenda.\n\nO objetivo não é pele lisa. É pele confortável, hidratada e que não dói.",
        "cenas": [
            {"tipo": "texto", "texto": "Pele boa não é pele lisa.", "etiqueta": "verdade", "dur": 2.6},
            {"tipo": "texto", "texto": "Pele saudável tem poro. Tem textura.", "dur": 2.8},
            {"tipo": "texto", "texto": "Tem um dia pior antes da menstruação.", "dur": 3.0},
            {"tipo": "texto", "texto": "O que você vê na tela é filtro, luz de anel e edição.", "dur": 3.6},
            {"tipo": "texto", "texto": "O objetivo é pele confortável. Não pele de propaganda.", "etiqueta": "o alvo certo", "dur": 3.6},
        ],
    },
    {
        "id": 21, "pilar": "educativo",
        "corpo": "Manhã e noite não pedem a mesma rotina — pedem rotinas com objetivos opostos.\n\nDe manhã a pele se defende: antioxidante e protetor. De noite ela repara: limpeza de verdade e tratamento.\n\nTrocar a ordem desperdiça os dois lados.",
        "cenas": [
            {"tipo": "texto", "texto": "Manhã e noite não pedem a mesma rotina.", "etiqueta": "dois objetivos", "dur": 3.0},
            {"tipo": "texto", "texto": "De manhã a pele se DEFENDE.", "rodape": "manhã", "dur": 2.8},
            {"tipo": "produto", "texto": "Antioxidante e protetor. Só isso já basta.", "produto": "hidratante-antioxidante-timewise.png", "rodape": "manhã", "dur": 3.4},
            {"tipo": "texto", "texto": "De noite ela REPARA: limpeza de verdade e tratamento.", "rodape": "noite", "dur": 3.6},
            {"tipo": "texto", "texto": "Trocar a ordem desperdiça os dois lados.", "etiqueta": "a regra", "dur": 3.2},
        ],
    },
    {
        "id": 22, "pilar": "produto",
        "corpo": "A pele em volta dos olhos é até cinco vezes mais fina que a do rosto e quase não tem glândula.\n\nPor isso ela marca primeiro — e por isso creme de rosto ali costuma ser pesado demais.\n\nQuantidade: um grão de arroz para os dois olhos, batidinha com o dedo anelar, nunca esfregando.",
        "cenas": [
            {"tipo": "texto", "texto": "Por que a área dos olhos marca primeiro", "etiqueta": "olhos", "dur": 3.0},
            {"tipo": "texto", "texto": "A pele ali é até 5x mais fina — e quase não tem glândula.", "dur": 3.6},
            {"tipo": "produto", "texto": "Um grão de arroz para os dois olhos.", "produto": "creme-para-area-dos-olhos-timewise.png", "rodape": "quantidade", "dur": 3.6},
            {"tipo": "texto", "texto": "Batidinha com o dedo anelar. Nunca esfregando.", "dur": 3.2},
            {"tipo": "texto", "texto": "É o passo mais barato de começar e o que mais se nota depois.", "etiqueta": "vale a pena", "dur": 3.6},
        ],
    },
    {
        "id": 23, "pilar": "prova",
        "corpo": "Minha pele também tem semana ruim. Quando isso acontece eu não corro atrás de produto novo — eu tiro coisa da rotina.\n\nVolto para limpeza suave, hidratante e protetor. Três passos, nada de ativo, por uns dez dias.\n\nNa maioria das vezes o problema era excesso, não falta.",
        "cenas": [
            {"tipo": "texto", "texto": "O que eu faço quando a minha pele fica ruim", "etiqueta": "bastidor", "dur": 3.0},
            {"tipo": "retrato", "texto": "Eu não compro nada. Eu TIRO coisa da rotina.", "foto": "ref-10-espelho-meio-corpo.jpg", "foco_y": 0.26, "dur": 3.6},
            {"tipo": "texto", "texto": "Limpeza suave, hidratante e protetor. Só.", "dur": 3.0},
            {"tipo": "texto", "texto": "Nada de ativo, por uns dez dias.", "dur": 2.8},
            {"tipo": "texto", "texto": "Quase sempre o problema era excesso, não falta.", "etiqueta": "a lição", "dur": 3.4},
        ],
    },
    {
        "id": 24, "pilar": "educativo",
        "corpo": "\"Quanto tempo até eu ver resultado?\"\n\nA pele leva cerca de 28 dias para trocar toda a camada de células — e esse ciclo fica mais lento com a idade. Antes disso você sente (maciez, conforto); depois disso você vê.\n\nQuem desiste na segunda semana desiste sempre um pouco antes de funcionar.",
        "cenas": [
            {"tipo": "texto", "texto": "“Quanto tempo até eu ver resultado?”", "etiqueta": "a pergunta", "dur": 2.8},
            {"tipo": "texto", "texto": "A pele troca a camada inteira de células em cerca de 28 dias.", "dur": 3.8},
            {"tipo": "texto", "texto": "Antes disso você SENTE: maciez, conforto, menos repuxo.", "dur": 3.6},
            {"tipo": "texto", "texto": "Depois disso você VÊ: textura, brilho, tom mais uniforme.", "dur": 3.6},
            {"tipo": "texto", "texto": "Quem desiste na 2ª semana desiste pouco antes de funcionar.", "etiqueta": "constância", "dur": 3.8},
        ],
    },
]


def main() -> None:
    caminho = os.path.join(BASE, "reels.json")
    with open(caminho, encoding="utf-8") as f:
        banco = json.load(f)

    existentes = {r["id"] for r in banco["reels"]}
    entrando = [r for r in NOVOS if r["id"] not in existentes]
    banco["reels"].extend(entrando)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)
        f.write("\n")

    rostos = sum(1 for r in banco["reels"]
                 if any(c.get("tipo") == "retrato" for c in r["cenas"]))
    print(f"+{len(entrando)} roteiros — banco com {len(banco['reels'])}, "
          f"{rostos} pedindo rosto.")


if __name__ == "__main__":
    main()
