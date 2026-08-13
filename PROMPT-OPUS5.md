# PROMPT PARA COLAR NO OPUS 5

> Cole o texto abaixo (tudo dentro do bloco) como sua próxima mensagem, já no
> modo Opus 5. Ele é autossuficiente: a pesquisa e as decisões já estão prontas
> no arquivo ESTRATEGIA.md do projeto. O Opus deve construir, não re-pesquisar.

---

Construa o projeto de automação de Instagram da **Marcia (@aurabelastore_on)**,
revenda de skincare Mary Kay. Toda a pesquisa e as decisões estratégicas já estão
feitas em `C:\Users\NOTE\Desktop\Projetos\AuraBela\ESTRATEGIA.md` — **leia esse
arquivo primeiro e siga-o à risca**. Replique o caminho técnico validado do
projeto `C:\Users\NOTE\Desktop\Projetos\posts-vendanaobra` (leia o CLAUDE.md,
publicar.py, legenda.py, gerar_carrossel.py, gerar_story.py e os workflows dele),
mas este é um projeto **100% separado**: outro repositório, outro token, outro
banco de conteúdo, sem nenhum cruzamento com o vendanaobra.

As **12 fotos reais em alta da Marcia** já estão em `AuraBela/fotos/`
(ref-01…ref-12). Use-as. O rosto **real** dela aparece em todo post — nunca gerar
rosto por IA.

## O que construir

1. **`git init`** no projeto AuraBela + commit inicial (regra do Diego: todo
   projeto nasce versionado).

2. **`gerar_estatico.py`** (Pillow): post estático 1080x1350 (4:5) que usa a foto
   real da Marcia como base e aplica arte por cima no estilo dos grandes perfis
   de beleza (paleta nude/rosa/marrom, tipografia fina, gancho grande no topo,
   selo discreto "@aurabelastore_on"). Layout com âncoras fixas para todo post
   sair idêntico (aprenda a técnica no gerar_carrossel.py do vendanaobra —
   tamanho de fonte fixo, posição fixa, contact-sheet mental). Tratamento leve na
   foto (brilho/contraste suave). O Gemini pode gerar fundo/elemento gráfico
   **como opção com fallback total para Pillow** — se o Gemini falhar por
   qualquer motivo, a peça sai igual só com Pillow. **Rosto nunca é IA.**

3. **`gerar_reels.py`** (ffmpeg): Reels vertical 1080x1920, 8–20s, a partir de
   1–3 fotos reais dela com movimento **Ken Burns** (zoom/pan lento), texto
   animado com a dica do dia (gancho nos 3 primeiros segundos), CTA no final e
   uma trilha instrumental livre de direitos (inclua 2–3 faixas royalty-free em
   `audio/`). 100% local, sem API de vídeo — este é o caminho que não pode parar.

4. **`gerar_story.py`**: story 1080x1920 de reforço com a arte do dia emoldurada
   (adapte o do vendanaobra).

5. **`legenda.py`**: ciclo de CTA com memória (7 posições, ver ESTRATEGIA seção 5:
   `seguir → PELE → vitrine → PELE → oferta → vitrine → CONSULTORA`), ciclo de
   pilar de conteúdo com memória (ESTRATEGIA seção 4), e montagem de legenda com
   **SEO** (palavras-chave reais: skincare, pele madura, rotina de skincare, pele
   30+, autocuidado, Mary Kay) + no máximo **5 hashtags**. Comment-to-DM: cada CTA
   pede uma palavra (PELE / EU QUERO / CONSULTORA) e o link vai no Direct; link
   permanente fica na bio. Suporte a **promoção**: campo `promocao` que, quando
   preenchido, entra no slide de oferta e na legenda.

6. **`conteudos.json`**: banco inicial com **pelo menos 30 posts** (gancho, corpo,
   pilar, cta sugerido, foto de referência), português impecável, no tom honesto/
   acolhedor de autoridade em skincare para mulheres 30+. Distribua pelos 5
   pilares. Escreva **legendas virais** de verdade — gancho forte, storytelling,
   valor real, CTA claro. Além disso, um banco menor de **dicas curtas** para os
   Reels (frase-gancho + 2–3 passos). Preveja aviso de esgotamento (issue) quando
   a reserva ficar baixa, como no vendanaobra.

7. **`publicar_estatico.py`** e **`publicar_reels.py`**: mesma espinha do
   publicar.py do vendanaobra (fila = banco menos publicados; sobe imagem/vídeo
   para o repo público; cria container na Graph API; publica; registra;
   story de reforço; commita estado). Reels usa `media_type=REELS` com `video_url`
   (a Graph API baixa o vídeo por URL pública, igual às imagens). Suporte a
   `--ensaio`, `--garantir` e `--id`.

8. **Workflows** em `.github/workflows/`:
   - `reels-diario.yml` — 09h BRT todo dia (com a espera-até-o-horário do
     vendanaobra, porque o cron do Actions atrasa).
   - `estatico-diario.yml` — 19h BRT todo dia.
   - `rede-de-seguranca.yml` — repescagem 2h após cada horário (`--garantir`) e
     **abre issue** se nem a repescagem publicar.

9. **`CLAUDE.md`** do projeto AuraBela documentando tudo (formato, cadência,
   ciclos, armadilhas, token), no capricho do CLAUDE.md do vendanaobra.

## Configuração da conta Meta (token que NÃO expira)

O token do vendanaobra só gerencia a página "Venda na Obra" — **não serve** para
a conta da Marcia. Antes de publicar de verdade, é preciso (passo humano do
Diego, descrito na ESTRATEGIA seção 10): conta profissional + Página do Facebook
vinculada + **token de sistema que não expira** (`expires_at: 0`) + o IG User ID
da Marcia. **Recomende app/token próprios da conta dela** (isolamento total).
Deixe o código lendo o token de uma variável `META_TOKEN_AURABELA` (env ou
arquivo separado) e o IG User ID de uma constante — e **construa tudo em modo
`--ensaio`** (gera as peças sem publicar) para o Diego revisar antes de ligar a
publicação. Não tente publicar de verdade até o Diego confirmar o token e o ID.

## Ordem sugerida

1. Ler ESTRATEGIA.md + os arquivos do vendanaobra.
2. git init + estrutura de pastas.
3. gerar_estatico.py + gerar_reels.py + gerar_story.py → rodar em `--ensaio` e
   me mostrar **prints** das peças (regra do Diego: visual só está pronto com
   print; não confiar em "rodou sem erro").
4. legenda.py + conteudos.json (30+ posts, legendas virais).
5. publicar_*.py + workflows + rede de segurança.
6. CLAUDE.md.
7. Criar o repositório público separado, subir, e deixar pronto para o Diego só
   inserir o token e ligar o agendamento.

## Regras permanentes do Diego (valem aqui também)

- Responder **em português**, trabalhar em silêncio, sem pedir autorização a cada
  passo (permissão total implícita).
- Arte é só considerada pronta **com print conferido** (desktop e, no caso de
  peça vertical, no formato certo).
- Entregas que o Diego pediu (ex.: mockup da bio nova) vão para a **Área de
  Trabalho**; o projeto em si fica em `Projetos\AuraBela`.
- Ao terminar, **alimentar o Cérebro** (Obsidian em `Desktop\Cérebro`): criar/
  atualizar a nota do projeto AuraBela e commitar o cofre.
- Mudança na **bio/perfil** da Marcia espera aprovação com mockup antes de
  aplicar (a proposta de bio está na ESTRATEGIA seção 6).
