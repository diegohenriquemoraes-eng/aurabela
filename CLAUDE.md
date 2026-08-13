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
| `gerar_estatico.py` | Pillow → post 1080x1350 sobre a foto real dela |
| `gerar_reels.py` | ffmpeg → Reels 1080x1920 com Ken Burns |
| `gerar_story.py` | Story 1080x1920 com a arte emoldurada |
| `legenda.py` | Ciclos de CTA e de pilar (com memória) + legenda com SEO |
| `publicador.py` | Peças comuns: API, git, fila, estado |
| `publicar_estatico.py` / `publicar_reels.py` | Os dois publicadores |
| `renovar_token.py` | Renova o token de 60 dias (roda todo mês) |
| `conteudos.json` | Banco de 32 posts estáticos |
| `reels.json` | Banco de 12 roteiros de Reels |
| `publicados.json` / `estado_ciclo.json` | O que saiu + memória dos ciclos |
| `fotos/` | **Fotos reais em alta** da Marcia (ref-01 … ref-12) |

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

Então: **estático** = Pillow sobre a foto real; **Reels** = ffmpeg (Ken Burns)
sobre as fotos reais. Tudo local, custo zero, sem cota. IA só entraria como
enfeite opcional com fallback total para Pillow — nunca no rosto.

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
CICLO_CTA    seguir → PELE → vitrine → PELE → oferta → vitrine → seguir
CICLO_PILAR  educativo → prova → produto → autocuidado → educativo → produto → prova
```

Girando separados, a combinação varia sozinha e o feed nunca fica repetitivo.
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
  roupa clara sumia.
- **Texto ancorado de baixo para cima** no template `capa`: gancho longo
  invadia o rodapé quando a âncora era pelo topo.
- **Repositório público** é obrigatório: a API baixa a mídia por URL https
  pública (`raw.githubusercontent.com`) e não aceita upload de arquivo local —
  mesma razão do vendanaobra.
- **Vídeo demora mais que imagem** para a API processar: `esperar()` tem 60
  tentativas (~4 min).
- **Reels sem faixa de áudio** pode ser recusado: `gerar_reels` embute silêncio
  quando não há trilha em `audio/`.

## Rodar na mão

```bash
python publicar_estatico.py --ensaio    # gera a arte e mostra a legenda
python publicar_reels.py --ensaio       # monta o mp4 e mostra a legenda
python publicar_estatico.py --id 7      # conteúdo específico
python renovar_token.py --checar        # confere se o token está vivo
```

## Conteúdo

Escopo: skincare, cuidados com a pele, autocuidado e beleza para mulheres 30+.
Tom honesto e acolhedor — **autoridade sem promessa milagrosa** ("testo antes de
indicar" é o posicionamento). Português revisado à mão; o banco não é gerado na
hora.

Quando o banco ficar com ≤8 conteúdos (ou ≤4 roteiros), o publicador avisa no
log e o workflow abre issue ao esgotar.
