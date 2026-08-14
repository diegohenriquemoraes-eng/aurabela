# -*- coding: utf-8 -*-
"""Injeta os roteiros de carrossel (`slides`) em conteudos.json.

Existe como script, e nao como edicao manual do JSON, porque o banco e grande e
o resto dos campos (gancho, corpo, pilar, formato) tem de ficar intacto. Rodar
de novo apenas sobrescreve os `slides` dos ids listados aqui.

Formato de cada slide: {tipo, titulo, texto?}
  capa  — gancho grande + linha de apoio (o `texto`)
  passo — numerado automaticamente, na ordem em que aparece
  nota  — miolo sem numero (virada de raciocinio, aviso, contexto)
  cta   — fecho escuro com o pedido de acao

Sete a nove slides e o ponto doce: tempo de tela suficiente para o algoritmo ler
valor, sem derrubar a taxa de conclusao. A API para em 10.
"""
from __future__ import annotations

import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SLIDES = {
    # ---------------------------------------------------------------- rituais
    1: [
        {"tipo": "capa", "titulo": "A ordem certa do seu skincare",
         "texto": "Quase todo mundo erra o passo 3."},
        {"tipo": "passo", "titulo": "Limpar",
         "texto": "Tira a oleosidade e a poluição do dia. Sem isso, nada do que vem depois entra."},
        {"tipo": "passo", "titulo": "Tônico",
         "texto": "Devolve o equilíbrio da pele e prepara para absorver o que vem a seguir."},
        {"tipo": "passo", "titulo": "Sérum",
         "texto": "É aqui que mora o ativo. É também o passo que mais gente pula."},
        {"tipo": "passo", "titulo": "Hidratante",
         "texto": "Sela tudo o que veio antes e segura a água dentro da pele."},
        {"tipo": "passo", "titulo": "Protetor solar",
         "texto": "De manhã, sempre, mesmo em casa. À noite ele sai e entra o tratamento."},
        {"tipo": "nota", "titulo": "A regra por trás de tudo isso",
         "etiqueta": "o porquê",
         "texto": "Do mais líquido para o mais denso. Se você inverte, o creme pesado vira barreira e o que vem depois não atravessa."},
        {"tipo": "cta", "titulo": "Salva pra não errar a ordem.",
         "texto": "E me conta no Direct quais desses cinco você já tem — eu monto a sua rotina com o que está na sua gaveta."},
    ],
    10: [
        {"tipo": "capa", "titulo": "Antes de comprar creme caro, responde isso",
         "texto": "Três perguntas. Se falhar em uma, o creme não vai resolver."},
        {"tipo": "passo", "titulo": "Você lava o rosto com produto de rosto?",
         "texto": "Sabonete de corpo é alcalino demais: arranca a barreira e a pele responde com mais óleo."},
        {"tipo": "passo", "titulo": "Você usa protetor todo dia?",
         "texto": "Inclusive em casa. Sem isso, qualquer tratamento vira enxugar gelo."},
        {"tipo": "passo", "titulo": "Você usa o que já tem até acabar?",
         "texto": "Rotina trocada toda semana não dá tempo de a pele responder a nada."},
        {"tipo": "nota", "titulo": "Já vi isso muitas vezes",
         "texto": "Gente comprando sérum de alto valor e lavando o rosto com sabonete de corpo. É tênis de corrida para correr na areia fofa."},
        {"tipo": "nota", "titulo": "Arruma a base primeiro",
         "texto": "Aí o produto bom aparece — e você gasta menos para ter mais resultado."},
        {"tipo": "cta", "titulo": "Salva antes da próxima compra.",
         "texto": "Se quiser, me chama no Direct com as suas três respostas. Eu te digo por onde começar."},
    ],
    16: [
        {"tipo": "capa", "titulo": "A noite é quando a pele trabalha",
         "texto": "De dia ela se defende. De noite ela repara."},
        {"tipo": "passo", "titulo": "Tirar tudo",
         "texto": "Maquiagem, protetor e poluição. Água micelar no algodão resolve em trinta segundos."},
        {"tipo": "passo", "titulo": "Limpar de verdade",
         "texto": "Com produto de rosto. A limpeza da noite é a mais importante do dia inteiro."},
        {"tipo": "passo", "titulo": "Tratar",
         "texto": "Sérum ou creme de tratamento. É agora que o ativo é melhor aproveitado."},
        {"tipo": "passo", "titulo": "Selar",
         "texto": "Hidratante por cima, para nada evaporar enquanto você dorme."},
        {"tipo": "nota", "titulo": "O que você ganha com isso",
         "etiqueta": "o porquê",
         "texto": "É à noite que a pele renova célula, repara o dano do dia e produz colágeno. Com o poro entupido, ela faz isso pela metade."},
        {"tipo": "cta", "titulo": "Cinco minutos. Todo dia.",
         "texto": "Salva pra lembrar hoje à noite — e me conta amanhã se a pele acordou diferente."},
    ],
    18: [
        {"tipo": "capa", "titulo": "Por que a mancha volta sempre no mesmo lugar",
         "texto": "Mancha tem memória. É isso que quase ninguém te conta."},
        {"tipo": "nota", "titulo": "O que está acontecendo",
         "texto": "A célula que produziu pigmento demais uma vez faz de novo com muito menos estímulo. Ela aprendeu o caminho."},
        {"tipo": "passo", "titulo": "Clarear",
         "texto": "Trata o que já está lá. É por onde todo mundo começa — e onde quase todo mundo para."},
        {"tipo": "passo", "titulo": "Renovar",
         "texto": "Acelera a troca de células. Constância vale muito mais do que produto forte."},
        {"tipo": "passo", "titulo": "Proteger",
         "texto": "Sem isso o sol devolve tudo. Proteção não é o último passo do tratamento: é o que sustenta ele."},
        {"tipo": "nota", "titulo": "O erro clássico",
         "texto": "Clarear sem proteger é enxugar gelo. Você tira no inverno e o verão devolve inteirinho."},
        {"tipo": "cta", "titulo": "Salva pra consultar no verão.",
         "texto": "E se a sua mancha já voltou mais de uma vez, me chama: provavelmente falta o passo 3."},
    ],
    29: [
        {"tipo": "capa", "titulo": "Começando do zero? Compra nessa ordem",
         "texto": "A ordem de compra não é a ordem de uso — e é aqui que quase todo mundo erra."},
        {"tipo": "passo", "titulo": "Protetor solar",
         "texto": "O que mais devolve resultado. É o único que impede o dano em vez de tentar consertar depois."},
        {"tipo": "passo", "titulo": "Limpeza de rosto",
         "texto": "O que para de estragar. Produto de rosto, não sabonete de corpo."},
        {"tipo": "passo", "titulo": "Hidratante",
         "texto": "O que recupera a barreira e faz a pele parar de repuxar."},
        {"tipo": "passo", "titulo": "Só então o sérum",
         "texto": "Antes disso ele trabalha numa pele que continua sendo agredida todo dia."},
        {"tipo": "nota", "titulo": "Um item por mês",
         "texto": "Em quatro meses você tem uma rotina completa sem sentir no bolso — e usa cada um até acabar."},
        {"tipo": "cta", "titulo": "Salva e começa pelo primeiro.",
         "texto": "Me chama que eu te digo qual versão de cada um combina com a sua pele."},
    ],
    # ------------------------------------------------------------------ mitos
    3: [
        {"tipo": "capa", "titulo": "Sabonete de corpo no rosto",
         "texto": "O erro mais comum que eu vejo — e o mais barato de corrigir."},
        {"tipo": "nota", "titulo": "O que a gente acha", "etiqueta": "mito",
         "texto": "“É tudo pele, então serve.”"},
        {"tipo": "nota", "titulo": "O que é de verdade", "etiqueta": "verdade",
         "texto": "A pele do rosto é mais fina e tem outro pH. Sabonete de corpo é alcalino demais para ela."},
        {"tipo": "nota", "titulo": "O que acontece",
         "texto": "Ele arranca a barreira junto com a sujeira. A pele resseca, se assusta e produz mais óleo para compensar."},
        {"tipo": "nota", "titulo": "Como saber que é o seu caso",
         "texto": "Pele que repuxa depois do banho e fica oleosa duas horas depois. Sim, dá as duas coisas ao mesmo tempo."},
        {"tipo": "nota", "titulo": "O que fazer",
         "texto": "Um gel ou espuma de limpeza facial. É o item mais barato da rotina e o que mais muda o resultado."},
        {"tipo": "cta", "titulo": "Compartilha com quem lava o rosto no banho.",
         "texto": "É a correção que dá resultado mais rápido — e não custa quase nada."},
    ],
    6: [
        {"tipo": "capa", "titulo": "“Fico em casa o dia todo, não preciso de protetor”",
         "texto": "Era o que eu também achava."},
        {"tipo": "nota", "titulo": "UVA atravessa vidro", "etiqueta": "verdade",
         "texto": "Você não sente, não queima, não fica vermelha. E ela vai marcando."},
        {"tipo": "nota", "titulo": "O caso que ficou famoso",
         "texto": "Um caminhoneiro passou 28 anos com o lado esquerdo do rosto na janela. Os dois lados tinham a mesma idade. Não pareciam."},
        {"tipo": "nota", "titulo": "Onde você toma sol sem perceber",
         "texto": "Janela do escritório, vidro do carro, varanda, os dez minutos do portão até o mercado."},
        {"tipo": "nota", "titulo": "O que fazer",
         "texto": "Protetor de manhã, todo dia. Rosto, pescoço e mãos — as mãos entregam a idade antes do rosto."},
        {"tipo": "nota", "titulo": "Por que vale tanto",
         "texto": "80% do envelhecimento da pele vem do sol, não da idade. É a única parte que está no seu controle."},
        {"tipo": "cta", "titulo": "Salva e passa amanhã de manhã.",
         "texto": "Se não souber qual textura combina com a sua pele, me chama no Direct."},
    ],
    12: [
        {"tipo": "capa", "titulo": "“Minha pele é oleosa, não uso hidratante”",
         "texto": "É o conselho que mais estraga pele boa."},
        {"tipo": "nota", "titulo": "O que quase ninguém separa", "etiqueta": "o começo do erro",
         "texto": "Óleo e água são coisas diferentes. Dá para ter muito óleo e nenhuma água ao mesmo tempo."},
        {"tipo": "nota", "titulo": "O que a pele faz",
         "texto": "Sem água, ela entende que está em risco e produz o dobro de óleo para se proteger."},
        {"tipo": "nota", "titulo": "O ciclo que se fecha",
         "texto": "Você lava para tirar o óleo. Ela produz mais. Você lava de novo. E assim vai, por anos."},
        {"tipo": "nota", "titulo": "Como quebrar",
         "texto": "Hidratante em gel, textura leve, sem óleo. Todo dia, de manhã e à noite."},
        {"tipo": "nota", "titulo": "O que esperar",
         "texto": "Em duas ou três semanas a oleosidade cai. Não some — regula, que é o que você quer."},
        {"tipo": "cta", "titulo": "Manda pra amiga de pele oleosa.",
         "texto": "Ela provavelmente está lavando o rosto três vezes por dia achando que ajuda."},
    ],
    22: [
        {"tipo": "capa", "titulo": "O pescoço entrega a idade que o rosto esconde",
         "texto": "Você cuida do rosto há anos — e aí vê uma foto de perfil."},
        {"tipo": "nota", "titulo": "Por que ele envelhece primeiro", "etiqueta": "verdade",
         "texto": "A pele do pescoço e do colo é mais fina e tem menos glândula. Tem menos suporte para se manter firme."},
        {"tipo": "nota", "titulo": "E ainda leva mais sol",
         "texto": "Decote, dirigindo, andando na rua. Quase ninguém passa protetor ali."},
        {"tipo": "nota", "titulo": "A regra fácil",
         "texto": "O que sobrar na mão depois do rosto, você espalha no pescoço e no colo. Custa zero e muda tudo."},
        {"tipo": "nota", "titulo": "Sempre de baixo para cima",
         "texto": "Acompanhando o sentido em que a pele se sustenta, nunca puxando para baixo."},
        {"tipo": "cta", "titulo": "Salva e faz hoje à noite.",
         "texto": "É a mudança de hábito com melhor custo-benefício da rotina inteira: zero real."},
    ],
    26: [
        {"tipo": "capa", "titulo": "Esfoliar todo dia não deixa a pele mais lisa",
         "texto": "Deixa mais sensível. E, de novo, mais oleosa."},
        {"tipo": "nota", "titulo": "O que a esfoliação é", "etiqueta": "verdade",
         "texto": "Um acelerador de renovação. Não é borracha de apagar — não adianta esfregar mais."},
        {"tipo": "nota", "titulo": "O que acontece no excesso",
         "texto": "A barreira vai embora. A pele fica vermelha, sensível e produz mais óleo para se defender."},
        {"tipo": "nota", "titulo": "A frequência certa",
         "texto": "Uma a duas vezes por semana serve para a maioria das peles. Pele sensível: uma, e olhe lá."},
        {"tipo": "nota", "titulo": "Como saber que passou do ponto",
         "texto": "Se arde ao passar o hidratante depois, você exagerou. Dá uma semana de folga para a barreira voltar."},
        {"tipo": "cta", "titulo": "Salva antes do próximo esfoliante.",
         "texto": "E se a sua pele anda ardendo sem motivo, me chama — quase sempre é isso."},
    ],
    31: [
        {"tipo": "capa", "titulo": "Beber água não hidrata a sua pele",
         "texto": "Pelo menos não do jeito que te contaram."},
        {"tipo": "nota", "titulo": "Como a água chega lá", "etiqueta": "verdade",
         "texto": "Ela vem por dentro, sobe até a pele e evapora pela superfície o dia inteiro."},
        {"tipo": "nota", "titulo": "O que segura essa água",
         "texto": "A barreira da pele. Se ela está danificada, a água sai de qualquer jeito — beba o que beber."},
        {"tipo": "nota", "titulo": "O que danifica a barreira",
         "texto": "Sabonete errado, esfoliação demais, sol sem proteção e banho muito quente."},
        {"tipo": "nota", "titulo": "O que fazer",
         "texto": "Bebe água E hidrata. Um não substitui o outro: o hidratante é a tampa do copo."},
        {"tipo": "cta", "titulo": "Salva pra lembrar dos dois.",
         "texto": "Se a sua pele repuxa mesmo bebendo dois litros por dia, o problema é a barreira. Me chama."},
    ],
}


def main() -> None:
    caminho = os.path.join(BASE, "conteudos.json")
    with open(caminho, encoding="utf-8") as f:
        banco = json.load(f)

    por_id = {p["id"]: p for p in banco["posts"]}
    faltando = [i for i in SLIDES if i not in por_id]
    if faltando:
        sys.exit(f"ids inexistentes em conteudos.json: {faltando}")

    for i, slides in SLIDES.items():
        por_id[i]["slides"] = slides

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"{len(SLIDES)} carrosseis injetados "
          f"({sum(len(s) for s in SLIDES.values())} slides).")


if __name__ == "__main__":
    main()
