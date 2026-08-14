# AuraBela — @aurabelastore_on

Automação de conteúdo do Instagram da **Marcia Lima** (revenda de skincare
Mary Kay). Projeto **totalmente separado** do `posts-vendanaobra`: outro app,
outro token, outro repositório, outro banco. Mesmo caminho técnico validado —
nenhuma interferência entre os dois.

| Item | Valor |
|---|---|
| Conta | `@aurabelastore_on` · IG User ID `17841461553382411` |
| App do Facebook | `4100345400259383` ("aurabela") |
| App do Instagram | `1069671342251434` ("aurabela-IG") |
| Perfil pessoal dela | `@marciaolivelima` (fonte de fotos) |
| Vitrine (link da bio) | `loja.marykay.com.br/minha-vitrine?slug=aurabela` |

## Calendário

| Hora BRT | Peça | Publicador |
|---|---|---|
| **09h** | **Reels** (dica de skincare, rosto em movimento) | `publicar_reels.py` |
| **19h** | **Post estático** 4:5 | `publicar_estatico.py` |
| Após o estático | Story de reforço | `gerar_story.py` |

Todo dia, inclusive fim de semana — beleza tem consumo alto no fim de semana,
diferente de conteúdo B2B. Manhã pega a rotina de skincare; noite pega o scroll
do sofá.

## Arquivos

| Arquivo | Papel |
|---|---|
| `config.py` | IDs da conta/app e leitura do token (nada de segredo no repo) |
| `tipografia.py` | Playfair Display + Montserrat (variáveis) e a paleta |
| `arte.py` | Primitivas visuais: tons, fundo com grão, tracking, selo, ajuste de corpo |
| `formatos.py` | Os 6 formatos de peça única 1080x1350 (ver ESTRATEGIA-FEED.md) |
| `carrossel.py` | Slides do carrossel (capa, passo, nota, fecho) — o formato que mais salva |
| `curadoria.py` | **Quem entra hoje, em que formato e em que tom** — e o orçamento de rosto |
| `foto.py` | Tratamento das fotos reais dela (letterbox, luz, recorte com foco) |
| `gerar_reels.py` | ffmpeg → Reels 1080x1920; cenas de texto, produto ou retrato |
| `gerar_story.py` | Story 1080x1920 com a arte emoldurada |
| `legenda.py` | Ciclos de CTA e de pilar (com memória) + legenda com SEO |
| `publicador.py` | Peças comuns: API, git, fila, estado |
| `publicar_estatico.py` / `publicar_reels.py` | Os dois publicadores (o das 19h alterna carrossel e imagem única) |
| `renovar_token.py` | Renova o token de 60 dias (roda todo mês) |
| `conteudos.json` | Banco de 32 posts (formato por post; 11 têm `slides` e viram carrossel) |
| `reels.json` | Banco de 24 roteiros de Reels (cenas com tipo) |
| `produtos.json` + `produtos/` | 48 packshots de skincare Mary Kay (catálogo VTEX da loja) |
| `publicados.json` / `estado_ciclo.json` | O que saiu + memória dos ciclos |
| `fotos/` | **Fotos reais em alta** da Marcia (ref-01 … ref-12) — recurso ESCASSO |
| `ferramentas/baixar_produtos.py` | Rebaixa o catálogo (local, não roda no Actions) |
| `ferramentas/simular_feed.py` | Simula N dias e monta o mosaico do perfil, sem publicar |
| `ferramentas/amostra_formatos.py` | Um exemplo de cada formato |
| `ferramentas/conferir_bancos.py` | **Portão antes do commit**: capas repetidas entre bancos, campos, referências |
| `ferramentas/repor_reels.py` / `injetar_slides.py` | Acrescentam ao banco sem reescrevê-lo |

## As duas decisões de arquitetura que sustentam o projeto

### 1. O rosto é REAL, nunca gerado por IA

O pedido original era gerar as imagens e os vídeos com IA (Gemini/Veo). A
decisão foi **não usar IA no caminho crítico**, por dois motivos:

- **Não pode parar.** Os tiers gratuitos de vídeo (Veo ~50 créditos/dia, Kling
  ~66/dia) têm limite diário, exigem login manual e mudam de política. É
  exatamente o tipo de dependência que morre em silêncio — como o blog do
  vendanaobra, que ficou 6 dias fora por chave inválida.
- **Rosto sintético destrói confiança.** Em skincare, o rosto *é* a prova. Um
  rosto "quase ela" cai no vale da estranheza justo onde a credibilidade mora.

Então: nada de IA no caminho crítico. Tudo local, custo zero, sem cota. IA só
entraria como enfeite opcional com fallback total para Pillow — nunca no rosto.

**Corolário descoberto em 14/08/2026, e é uma regra tão forte quanto a primeira:
se o rosto é real, ele é FINITO.** São 10 fotos. O sistema original gastava foto
dela em 100% das peças (1 por estático, **5 por Reels**) — 84 usos a cada duas
semanas, cada foto voltando ao feed a cada dois dias. Isso queimava o banco e
poluía a grade com a mesma cara.

A correção está em `curadoria.py` + `formatos.py`: **1 peça com rosto a cada 6
publicadas**, cooldown de 21 peças por foto, e cinco formatos que não dependem
dela (frase, produto, ritual, mito, dado). Se o orçamento estourou, a peça é
rebaixada para cartão de frase — nunca gasta foto. Detalhes e números em
**`ESTRATEGIA-FEED.md`**; mexer em formato ou em peso de banco passa por lá.

### 2. API do Instagram com Instagram Login (e não a Graph API clássica)

A conta da Marcia **não tem Página do Facebook** — só o perfil pessoal dela
(conferido na Central de Contas em 12/08/2026). A Graph API clássica exige
Página; esta não exige.

O preço é o token durar **60 dias** em vez de nunca expirar. Resolvido pelo
`renovar_token.py` + `token-renovar.yml`, que renovam **todo mês** (30 dias de
folga: se uma renovação falhar, a próxima ainda pega o token vivo).

## Ciclos: o que o post PEDE e o que ele ENTREGA

Duas rotações independentes, as duas com memória em `estado_ciclo.json`, as duas
avançando pela **posição** (nunca pelo nome — nomes repetem no ciclo e
`list.index()` acharia sempre a 1ª ocorrência, prendendo a rotação num
sub-loop; é a armadilha que o vendanaobra já pagou).

```
CICLO_CTA    (7)  seguir → PELE → vitrine → PELE → oferta → PELE → vitrine
CICLO_PILAR  (5)  educativo → prova → produto → autocuidado → educativo
```

**Os tamanhos são coprimos (7 e 5) de propósito.** Com o mesmo tamanho os dois
girariam juntos e a combinação CTA+pilar se repetiria idêntica a cada 7 posts —
feed previsível. Assim ela só volta a se repetir depois de 14.

**Os CTAs de venda nunca caem em posições seguidas** — sempre há um `PELE` ou
`seguir` entre `vitrine` e `oferta`, inclusive na volta do ciclo (posição 6 → 0).
Educação e captura abrem espaço; a oferta fecha. Reordenar sem checar isso
transforma o perfil em vitrine. Peso resultante em 35 posts: PELE 15, vitrine 10,
seguir 5, oferta 5.

O estado só é gravado **quando o post publica de fato** — um dia que falhe não
adianta o ciclo nem repete.

## Foco: VENDER PRODUTO (decidido pelo Diego em 12/08/2026)

O perfil é loja, **não recrutamento**. O CTA "consultora" e o pilar
"renda-extra" saíram dos ciclos: perfil com dois focos (comprar *e* virar
consultora) converte pior nos dois, porque a pessoa não entende se aquilo é
uma vitrine ou uma oportunidade de negócio. Para reativar, basta recolocar as
duas entradas — o resto do código aguenta.

## Conversão

No Instagram o link **só é clicável no Direct e na bio**, nunca na legenda do
feed. Então:

- CTA de conversão pede uma **palavra no comentário** (comment-to-DM): `PELE`
  (monta o ritual — captura e segmenta), `EU QUERO` (oferta).
- O link permanente da vitrine fica **na bio**.
- Promoção: preencher o campo `promocao` em `estado_ciclo.json` — ela entra
  automaticamente na legenda, **antes** do CTA (a oferta precisa aparecer
  enquanto a pessoa ainda está lendo).

## SEO e hashtags

Em 2026 palavra-chave na legenda pesa mais que hashtag, e o Instagram só conta
~5 hashtags com eficácia. `HASHTAGS` em `legenda.py` tem 5 por pilar. As
palavras-chave reais (skincare, pele madura, rotina de skincare, pele 30+,
autocuidado) vão no corpo do texto.

## Bio

No ar desde 12/08/2026 (aprovada pelo Diego):

```
✨ Sua pele 30+ merece cuidado simples e de verdade
🧴 Testo tudo antes de indicar — sem milagre
💬 Dúvida? Chama no Direct
🛍️ Vitrine oficial 👇
```

Duas correções que o Diego fez na proposta original, as duas certas: **"comenta
PELE" não vai em bio** (não há onde comentar — é CTA de post), e **renda extra
não entra** (divide a mensagem de um perfil de venda).

**Pendente (só existe no app do celular, não na web):**
- Trocar o **Nome** para `Marcia · Skincare para pele 30+` — o campo Nome é
  indexado na busca do Instagram, é a maior alavanca de descoberta.
- Apagar o **CEP** que aparece abaixo da bio (vem do endereço comercial da
  conta profissional).

## Armadilhas já pagas

- **Console do Windows em cp1252** estoura ao imprimir emoji das legendas. O
  `publicador.py` reconfigura `stdout`/`stderr` para UTF-8 na importação. Não
  afeta o que vai para a API (sempre UTF-8) — afetava só o `--ensaio` e o log.
- **Fotos com barras pretas**: algumas fotos vieram do Instagram com letterbox.
  `_cortar_barras()` varre as bordas e corta antes de compor.
- **Contraste sobre foto clara**: véu duplo no Reels (forte na base para o
  texto, leve no topo para o selo) e etiqueta em creme, não rosa — rosa sobre
  roupa clara sumia. No formato `retrato` o véu precisa estar **cheio já em 68%
  da altura**, não só no rodapé: rampa lenta deixava o gancho sumir na blusa.
- **Packshot: multiply, nunca recorte.** Recorte por flood fill come a tampa
  branca do frasco (branco encostando em branco) e deixa a sombra do estúdio
  como retângulo fantasma. Compor em multiply resolve os dois — mas exige fundo
  **claro** e exige normalizar o fundo do packshot para 255 (a Mary Kay serve em
  cinza 241, que em multiply vira um retângulo visível).
- **Tarja "Melhor avaliado"** vem embutida no packshot de 4 produtos. É da
  vitrine, não do produto — `_tirar_selo()` corta na origem.
- **Capa de Reels com texto centralizado**: a grade do perfil (4:5 desde 2025)
  mostra só o miolo do 9:16; gancho no rodapé aparecia cortado no meio da
  palavra no perfil.
- **Texto ancorado de baixo para cima** no `retrato`: gancho longo invadia o
  rodapé quando a âncora era pelo topo.
- **Medir para caber, não estimar por nº de caracteres** (`arte.caber`): escala
  fixa por contagem estoura com palavra longa. E `evitar_orfao=True` onde o
  texto é centrado, senão sobra uma palavra sozinha na última linha.
- **Cada banco certo sozinho, errado entre si.** O mesmo gancho em
  `conteudos.json` e em `reels.json` vira duas peças iguais lado a lado na grade
  do perfil. Só apareceu no mosaico da simulação — por isso existe
  `ferramentas/conferir_bancos.py`, que barra capas acima de 72% de semelhança.
- **A cena de rosto do Reels tem de ser a CAPA.** No meio do vídeo ela debita o
  orçamento de rosto e não aparece na grade: gasta o recurso escasso sem mostrar.
- **Carrossel: todo filho tem de chegar a FINISHED** antes de entrar no
  container pai. Publicar com um filho ainda baixando devolve erro 100 de
  validação, que é genérico e não diz qual item falhou.
- **Um bloco de texto centrado por cálculo fica alto demais** (`altura()` conta o
  entrelinha da última linha, que não é tinta). O centro óptico dos slides ficou
  em 0,51 da altura, não 0,46.
- **Repositório público** é obrigatório: a API baixa a mídia por URL https
  pública (`raw.githubusercontent.com`) e não aceita upload de arquivo local —
  mesma razão do vendanaobra.
- **Vídeo demora mais que imagem** para a API processar: `esperar()` tem 60
  tentativas (~4 min).
- **Reels sem faixa de áudio** pode ser recusado: `gerar_reels` embute silêncio
  quando não há trilha em `audio/`.
- **Segredo nunca interpolado no `run` de um workflow.** `${{ steps.x.outputs.token }}`
  dentro de `run:` faz o Actions montar o comando e **imprimir no log** — e o
  repositório é público. Outputs de step não são mascarados automaticamente (só
  secrets são). Passe por `env:` e mascare na origem com `::add-mask::`.
  Aconteceu em 13/08: o token do Instagram vazou no log. O que resolveu não foi
  apagar o log — foi **revogar o app no Instagram e reautorizar**, porque renovar
  não invalida o token anterior.
- **O pipe do PowerShell (`|`) acrescenta CRLF** ao gravar um secret, e o runner
  responde `Bad credentials`. Grave em arquivo sem BOM e use
  `cmd /c "gh secret set X --repo Y < arquivo"`.
- **`raw.githubusercontent.com` serve `.mp4` como `application/octet-stream`**
  (a imagem sai como `image/jpeg`, correta). A API costuma aceitar assim, mas
  **isso ainda não foi validado com um post real** — é o único ponto do fluxo
  que não deu para testar sem token. Se o container do Reels falhar com erro de
  vídeo inválido, o plano B é hospedar o mp4 num asset de GitHub Release (que
  sai como `video/mp4`) e apontar `REPO_RAW` do vídeo para lá. O post estático
  não corre esse risco.

## Rodar na mão

```bash
python publicar_estatico.py --ensaio    # gera a arte e mostra a legenda
python publicar_reels.py --ensaio       # monta o mp4 e mostra a legenda
python publicar_estatico.py --id 7      # conteúdo específico
python renovar_token.py --checar        # confere se o token está vivo

python ferramentas/conferir_bancos.py   # PORTÃO: capas repetidas, campos, referências
python ferramentas/simular_feed.py 15   # 15 dias de feed + mosaico, sem publicar
python ferramentas/amostra_formatos.py  # um exemplo de cada formato
python ferramentas/baixar_produtos.py   # rebaixa o catálogo Mary Kay (só local)

python publicar_estatico.py --ensaio --unico       # força imagem única
python publicar_estatico.py --ensaio --carrossel   # força carrossel
```

## Conteúdo

Escopo: skincare, cuidados com a pele, autocuidado e beleza para mulheres 30+.
Tom honesto e acolhedor — **autoridade sem promessa milagrosa** ("testo antes de
indicar" é o posicionamento). Português revisado à mão; o banco não é gerado na
hora.

Quando o banco ficar com ≤8 conteúdos (ou ≤4 roteiros), o publicador avisa no
log e o workflow abre issue ao esgotar.

**Fôlego dos bancos:** 24 roteiros de Reels (~3 semanas, 1/dia), 11 carrosséis
(~3 semanas, dia sim dia não) e 21 posts de imagem única (~6 semanas). Os dois
primeiros acabam por volta de **05/09/2026** — repor antes com
`ferramentas/repor_reels.py` e `ferramentas/injetar_slides.py`.
