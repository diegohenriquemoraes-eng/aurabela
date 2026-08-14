# AuraBela — Estratégia de feed

Revisão de 14/08/2026. Substitui a parte visual da `ESTRATEGIA.md` (que continua
valendo para pilares, CTA, SEO e bio).

---

## 1. O problema, com número

O sistema antigo tinha **dois templates, e os dois exigiam foto do rosto da
Marcia**. O banco tem **10 fotos**.

| | Sistema antigo | Sistema novo |
|---|---|---|
| Post estático | 1 foto dela | 0 (só 3 dos 32 conteúdos pedem rosto) |
| Reels | **5 fotos dela** (uma por cena) | 0 ou 1, no máximo |
| Consumo em 2 semanas (28 peças) | **~84 usos** de 10 fotos | **4 usos** |
| Cada foto reaparecia | ~4× por semana | ~1× a cada 3 semanas |

Não era exagero de percepção: com 84 usos em 10 arquivos, **cada foto voltava ao
feed a cada dois dias**. Em um mês o perfil inteiro seria a mesma cara repetida
— e o banco estaria queimado, sem nada para repor.

> Medido de verdade: `python ferramentas/simular_feed.py 14` roda 14 dias de
> feed sem publicar e imprime o consumo. Foi assim que os números acima saíram.

---

## 2. Onde eu discordo em parte do pedido — e por quê

O pedido foi "a maioria foto do produto ou frases de beleza". Metade certa,
metade armadilha:

- **Certo:** o rosto tem de ficar raro. É o único insumo que acaba.
- **Armadilha:** um feed que é *só* packshot da Mary Kay + card de frase é
  exatamente o feed genérico de consultora que existe às centenas. Packshot
  oficial é a mesma imagem que outras 400 mil consultoras publicam — não
  diferencia ninguém, e feed de catálogo espanta seguidor.

O que os perfis grandes de beleza fazem **não é escolher entre rosto, produto ou
frase**. É ter **um sistema visual único aplicado a formatos diferentes** — a
mesma paleta, a mesma tipografia, a mesma assinatura no mesmo lugar, variando o
tipo de peça. É o sistema que faz o perfil parecer marca; o rosto entra como
prova, não como preenchimento.

**A regra que orienta tudo:** rotacionar o ativo **escasso** (o rosto dela — 10
arquivos, não repõe sozinho) e escalar o ativo **renovável** (produto, texto,
ritual, número — infinitos e de custo zero).

---

## 3. Os seis formatos do feed

Todos saem de `formatos.py` e compartilham as primitivas de `arte.py`: mesma
margem (110px), mesma escala tipográfica, mesmo selo no rodapé, mesmo grão de
papel por cima. Mudar um valor em `arte.py` muda o feed inteiro de uma vez.

| Formato | O que é | Serve para | Peso no banco |
|---|---|---|---|
| **frase** | cartão tipográfico, sem foto nenhuma | autocuidado, verdade incômoda, posicionamento | 10 de 32 |
| **mito** | bloco escuro (mito) sobre bloco claro (verdade) | o formato que mais se **compartilha** | 6 de 32 |
| **ritual** | passo a passo numerado | o educativo que se **salva** | 5 de 32 |
| **produto** | packshot oficial sobre fundo de cor | conversão (o pilar produto) | 5 de 32 |
| **dado** | um número enorme + a frase que o explica | autoridade em 1 segundo de scroll | 3 de 32 |
| **retrato** | a foto real dela, sangrando na peça | prova, "sou eu quem testa" | **3 de 32** |

Amostra de cada um: `saida-amostra/formatos/00-grade.jpg`.

**Detalhe técnico que vale ouro no formato produto:** o packshot é composto em
*multiply*, não recortado. O branco do estúdio vira transparente sozinho, a
sombra cinza do próprio packshot vira sombra de verdade sobre a cor, e a tampa
branca do frasco continua inteira — coisa que recorte automático come. Além
disso, a tarja lilás "Melhor avaliado" que a loja embute em 4 produtos é cortada
na origem: ela é da vitrine, não do produto.

---

## 4. O orçamento de rosto (a trava que não cede)

Em `curadoria.py`, e só lá:

```
ORCAMENTO_ROSTO   = 6   # no máximo 1 peça com o rosto dela a cada 6 publicadas
COOLDOWN_FOTO     = 21  # uma foto só volta depois de 21 peças
COOLDOWN_FORMATO  = 3   # nunca o mesmo formato dentro das 3 últimas
COOLDOWN_TOM      = 2   # nem o mesmo fundo dentro das 2 últimas
COOLDOWN_PRODUTO  = 8   # nem o mesmo produto dentro de 8
```

Três consequências desenhadas de propósito:

1. **Reels e estático dividem o mesmo orçamento**, porque dividem a mesma grade
   do perfil. Contar só o estático deixaria o Reels queimar foto por fora.
2. **Se o orçamento estourou, a peça não vira foto.** Um conteúdo `retrato` é
   rebaixado para cartão de frase com o mesmo gancho — entrega a mesma mensagem
   e não gasta o que não se repõe. É o único lugar do sistema em que essa regra
   é lida.
3. **Um Reels usa no máximo uma foto**, na cena em que ela realmente importa —
   nunca nas cinco.

Resultado medido em 12 dias / 24 peças: **4 peças com rosto (1 a cada 6), 4
fotos diferentes, nenhuma repetida.**

---

## 5. A grade — o perfil é lido como mosaico, não como post

Desde 2025 a grade do perfil é **4:5**, não quadrada. O visitante vê 9 peças de
uma vez, e é isso que decide se ele segue.

- **Ritmo claro/escuro:** quatro tons (areia, rosé, creme, café) rotacionados
  com trava contra dois escuros seguidos. Grade só clara parece catálogo; só
  escura parece funeral. Na simulação: areia 8, rosé 6, creme 5, café 5.
- **Capa de Reels com texto centralizado:** a grade mostra só o miolo do 9:16.
  Gancho ancorado no rodapé aparecia **cortado no meio da palavra** no perfil —
  corrigido.
- **Sem gancho repetido:** roteiro de Reels e post estático não podem carregar a
  mesma frase, senão ela aparece duas vezes na mesma tela do perfil.

Mosaico simulado de 12 dias: `saida-amostra/simulacao/00-perfil.jpg`.

---

## 6. O que ainda depende da Marcia — e é o que mais vale

O sistema agora aguenta rodar meses sem foto nova. Mas o que separa o feed dela
do feed de qualquer outra consultora **não é o packshot oficial** — é foto
**dela** com o produto na vida real. Esse é o ativo renovável que só ela produz,
e ela produz com o celular, em dez minutos.

**Lista de fotos para ela tirar (não precisa de rosto na maioria):**

1. Produto na mão dela — só a mão, luz de janela, fundo neutro (5 fotos)
2. Produto na pia do banheiro, na rotina real (5)
3. Textura: creme espalhado nas costas da mão, gota do sérum (5)
4. Produtos juntos sobre toalha/mármore, vista de cima (5)
5. Aplicando no rosto — pode ser só metade do rosto, ou de perfil (5)
6. Retratos novos: luz de janela, fundo limpo, **sem óculos escuros**,
   enquadramentos variados (10–15) — esses vão para o banco de `retrato`

Os itens 1 a 5 **não gastam o banco de rosto** e podem entrar como formato de
produto próprio. É o material com maior conversão do nicho e o mais barato de
produzir. Vale muito mais do que 15 selfies.

---

## 7. Pendências (em ordem de urgência)

1. **Banco de Reels acaba em 12 dias** (26/08/2026). São 12 roteiros para uma
   peça por dia; o de estáticos tem 32. Repor `reels.json` antes disso — o
   workflow abre issue ao esgotar, mas aí já é atraso.
2. **Carrossel** — é o formato de maior salvamento do nicho e o único do sistema
   que ainda não existe. A API aceita (containers filhos com
   `is_carousel_item=true` e depois um container `CAROUSEL`); a arte já está
   pronta, bastaria encadear 5 peças. Fase 2.
3. **Fotos da lista da seção 6.**
4. **Nome do perfil e CEP** — continuam pendentes no app do celular (ver
   `CLAUDE.md`), e o campo Nome é a maior alavanca de descoberta que existe.

---

## 8. Como conferir sem publicar

```bash
python ferramentas/amostra_formatos.py      # um exemplo de cada formato
python ferramentas/simular_feed.py 14       # 14 dias de feed + mosaico + números
python publicar_estatico.py --ensaio        # a peça real de hoje
python publicar_reels.py --ensaio           # o Reels real de hoje
```
