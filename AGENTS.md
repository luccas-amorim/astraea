# Instruções para agentes de IA — Astraea

Observatório de superfície sobre o crime de genocídio e a lei penal do mundo: três
telas (leis penais por país, notícias, decisões de tribunais internacionais), site
estático no GitHub Pages, dados abertos em JSON. **O valor central é a proveniência**:
todo dado diz de onde veio, quando foi lido e com que confiança. Um dado sem fonte é
pior que um dado ausente.

Este arquivo é lido pelo Codex e demais agentes pelo nome; o Claude Code o lê via
`CLAUDE.md`, que só o importa. Regra nova entra **aqui**. O plano do projeto está em
`docs/00` a `docs/07`; o que ainda não foi decidido está em
`docs/07-decisoes-pendentes.md`, e **decisão pendente não se decide em código**.

## Estado do projeto

Em 11/11/2026 o repositório tem o plano, o motor (`astraea/engine/`, `astraea/sources/`,
`astraea/cli.py`), as licenças, os dados da fase 1, o Tabelião e a pena de morte:
`data/countries.json` (197 registros com `id`, `name`, `un_status`, `un_member_since`,
`situations`, os blocos `genocide_convention` e `rome_statute`, carimbados pelo robô ou
vazios com `reason` em Taiwan e Kosovo, e `death_penalty`, carimbado pelo robô a partir
do Cornell em 130 países e vazio com `reason` em 67; e, nos 24 países da carga humana,
`penal_code`, `domestic_genocide` e `max_penalty`, em rascunho à espera do carimbo do dono
ou vazios com `reason`), `data/situations.json` (as dez da D6; nove status, todos sem carimbo de
pessoa), `data/sources.json` (105 fontes), `data/untc-names.json` e
`data/cornell-names.json` (nome da UNTC e do Cornell → alfa-3, um arquivo por fonte),
`data/verification.json` (a trilha que carimba os campos escalares),
`data/lexicon/` (termos fixos em `fixed/` e o léxico gerado em cinco línguas; o árabe é
rascunho), `data/retired-ids.json` e `data/i18n/`. `scripts/vocabularies.py` é a lista
única dos vocabulários fechados e das chaves de rótulo; `scripts/build_lexicon.py` gera o
léxico; `scripts/transform.py` valida com as onze travas e gera `static/data/`;
`scripts/build_site.py` gera, em `/en/` e `/pt-br/`, a página inicial, a tela
`/countries/` (completude por campo e a tabela dos 197 com filtros em CSS, sem
JavaScript) e as 197 fichas `/countries/<ISO>/` com o carimbo de cada campo (modelos e
textos em `site/`, saída em `_site/`, fora do git). `.github/workflows/ci.yml` roda a
bateria em todo *push* e PR; `deploy.yml` publica no GitHub Pages; `countries.yml`, no
dia 1 de cada mês, roda as duas cargas por `scripts/countries_monthly.py` e abre PR da
branch `robot/countries` (ou issue, se uma carga falhar); nunca comita na `main`. O motor honra o `Crawl-delay` por
host e não baixa página de domínio com `no_text_by_policy` (`astraea/engine/policy.py`).
O adaptador `listing` (`astraea/sources/listing.py`) lê tabela que muda devagar; os
formatos são o XML por tratado da UNTC, que `scripts/load_treaties.py` grava em
`countries.json`, e as quatro listas de pena de morte do Cornell, que
`scripts/load_death_penalty.py` grava em `death_penalty` (os dois em simulação por
padrão). `scripts/stamp.py` lista os blocos prontos para carimbo e grava `checked_by:
human` só no que o dono indicar. O Cartógrafo (`scripts/recheck_sources.py`, dentro do
`countries.yml`) pergunta todo mês se Legislationline, SHERLOC, Library of Congress e
WorldLII voltaram a responder e reabre a fonte em `sources.json` quando sim (o SHERLOC só é
reconferido). 390 testes. A fase 1 e os itens 1 a 3 da fase 2 estão
feitos (o anexo da Anistia espera a carga à mão do dono; o `countries.yml` rodou no GitHub
em 10/11/2026); o item 4, a carga humana dos 24 países, começou na sessão 4 da fase 2 e
seguiu nas sessões 5 a 9 (quinze países com leitura, nove vazios com `reason` de 11/11/2026;
`02-fontes.md`, 1.7 a 1.11); o que falta depende de outra rede, da leitura do dono ou de
fonte oficial nova. Antes de escrever código, leia o `00-inventario.md` e o
`04-arquitetura.md` ("Onde o motor vive"): o motor é **próprio**,
nascido de uma cópia do Alétheia (`luccas-amorim/aletheia`) com o aviso MIT e o `sha` de
origem no `NOTICE`, traduzido para inglês e livre para divergir. O Alétheia não é
dependência; correção que valha a pena trazer de lá é portada à mão e registrada no
`CHANGELOG.md`.

## Regras que não se negociam

1. **O sistema nunca afirma genocídio.** Registra quem afirmou, em que grau, com URL e
   data, na taxonomia de `docs/03-modelo-de-dados.md`. Tela, resumo, commit e issue
   dizem "alegado por X", "medida provisória da CIJ", nunca "genocídio" solto.
2. **Nunca texto integral de terceiros.** Metadados, *link*, data, fonte, língua e
   resumo próprio. `excerpt` só em relatório de rodada, até 320 caracteres.
3. **Robô não muda status nem promove.** `situations.statuses`, `promotion` e qualquer
   campo com `checked_by: human` só mudam por commit de pessoa. O validador
   reprova o contrário.
4. **Fonte secundária aponta, não escreve.** Wikipedia, Wikidata, agregadores e
   modelos de linguagem geram perguntas e rascunhos marcados; nunca preenchem campo
   de país nem decidem triagem.
5. **`id` é append-only.** País é ISO 3166-1 alfa-3 (`XKX` para Kosovo); situação é
   *slug*; documento é `hash` da URL normalizada. Nunca reatribuído; o que sai vai para
   `data/retired-ids.json`.
6. **Fonte × derivado.** `data/` é editável; `static/data/` é gerado por
   `scripts/transform.py` e a CI exige sincronia. Nunca edite o derivado. A exceção
   dentro de `data/` é `data/lexicon/<lang>.json`, gerado por
   `scripts/build_lexicon.py`: edita-se `data/lexicon/fixed/<lang>.json` e
   `situations.terms`, e o validador reprova o léxico que não bate com eles.
7. **Robots, limites e bloqueios são política.** O cliente HTTP obedece `robots.txt`
   e o limite declarado por fonte; WAF, CAPTCHA e bloqueio por país não se contornam.
   Google e APIs comerciais de notícias ficam fora.
8. **Pessoas.** Nome de pessoa só em `decisions.json`, como o tribunal o escreve.
   Política de remoção em `docs/pessoas.md`.
9. **Nada entra sem carimbo.** Campo afirmado tem `url`, `source`, `read_on`,
   `confidence` e `checked_by`. `--draft` só na carga inicial, e o relatório de
   qualidade conta o que ainda está em rascunho.

## Como trabalhar neste repositório

- **Antes de concluir**, rode a bateria (quando ela existir; até lá, o que houver):

  ```
  python scripts/transform.py --strict
  python scripts/transform.py --draft --check
  python -m pytest
  astraea validate-lexicon data/lexicon/*.json
  python scripts/build_site.py
  astraea validate-config config/*.json
  ruff check . && ruff format --check .
  ```

  Enquanto durar a carga inicial, `--strict` **reprova de propósito** e só pelos
  rascunhos (travas 3 e 6: campo sem carimbo, status de tribunal sem `checked_by:
  human`); qualquer outra trava na saída dele é erro seu. `--draft --check` tem de
  passar: valida relaxando só essas duas e confere que `static/data/` está em dia. Se
  não estiver, `python scripts/transform.py --draft --execute`; se o léxico estiver
  velho, `python scripts/build_lexicon.py --execute` antes. Rascunho não se "resolve"
  preenchendo `checked_by`: quem carimba como `human` é a pessoa (regra 3).

- **Carga humana (lei penal).** A sessão lê e prepara o bloco com `url`, `source`,
  `read_on` e `confidence`, e deixa `checked_by: null`; quem carimba é o dono, com
  `scripts/stamp.py`. Modelo de linguagem não escreve `note` nem decide o valor que a
  fonte não dá: o que fica em dúvida vai para a lista "o que conferir" do `CHANGELOG.md`.
  Portal que veda robôs, desafia o cliente ou não responde deixa o bloco vazio com
  `reason`; não se contorna (regra 7). A única leitura fora do cliente do motor foi a do
  Planalto, no navegador embutido, e está registrada como escolha a revisar
  (`02-fontes.md`, 1.6). Portal cujo `robots.txt` veda agentes de IA pelo nome
  (`ClaudeBot`, `anthropic-ai`, `ChatGPT-User`…) ou declara `Content-Signal:
  ai-input=no` não é lido por sessão que é modelo, mesmo que o `User-Agent` do Astraea
  passe: fica para a leitura do dono. Certificado com cadeia incompleta se completa pelo
  endereço AIA do próprio certificado, verificado contra as raízes da Mozilla; a
  verificação nunca se desliga (`02-fontes.md`, 1.7).
- **Quando o `--strict` volta a ser a régua da CI.** Hoje o `ci.yml` roda
  `--draft` e `--draft --check` como travas e o `--strict` como passo informativo (mostra
  a contagem de rascunhos e só reprova por outra causa). No dia em que
  `static/data/quality.json` tiver `drafts.fields` igual a zero (os nove status com
  carimbo `human` da pessoa), o mesmo commit troca, no `ci.yml`, `--draft` por
  `--strict` nos dois passos de trava e apaga o passo informativo; o `deploy.yml` passa
  a conferir com `--strict --check`. Rascunho novo depois disso entra por PR que já
  passe no `--strict`, ou com a volta do passo informativo registrada no
  `CHANGELOG.md`.
- **Configuração de rodada** (`config/*.json`, quando existir) leva `"registry":
  "../data/sources.json"`: é dali que a rodada lê os domínios com `no_text_by_policy`, e
  `astraea run` recusa configuração sem ela.

- **Línguas.** Dados e código em **inglês**: nomes de arquivo, chaves, valores de
  vocabulário fechado, *ids*, *slugs*, comandos, opções, nomes de módulo e de
  *workflow*. Chave publicada não se traduz nem se renomeia depois. Documentação
  (`docs/`, este arquivo, `CHANGELOG.md`), commits e issues continuam em português, e
  os nomes dos robôs (Tabelião, Escrivão…) também, como nomes próprios. As telas
  nascem em `en` e `pt-BR`; o que se traduz são rótulos e textos nossos, nunca as
  chaves (`03-modelo-de-dados.md`, "Várias línguas").
- **Uma sessão = uma entrada no `CHANGELOG.md`**, com data e o que mudou de dado, de
  fonte ou de regra. Correção de dado antigo entra como correção; alteração de status
  de situação entra com o ato que a sustentou.
- **Issue que o robô abre, a pessoa fecha** com `Closes #N` no PR ou no commit.
- **Teste não fixa o valor do dia.** O PR mensal do robô muda `countries.json`; teste que
  compare o repositório com uma *fixture* tem de aceitar bloco lido depois (`read_on`
  mais novo) ou carimbado por pessoa, como fazem `test_load_treaties.py` e
  `test_load_death_penalty.py`. Do contrário, o primeiro mês com novidade reprova a CI.
- **Decisão nova vai para `docs/`** (o documento afetado) e, se for regra, para cá.
  Não escreva regra em comentário de código.
- **Para o dono do projeto**, que não programa no dia a dia e usa Windows: todo passo
  que ele precise executar vem explícito, com os avisos que o PowerShell vai mostrar;
  todo *script* que altere arquivo roda em modo simulação por padrão (`--execute`
  para valer) e nunca apaga; quando uma escolha sua divergir do que ele pediu, diga e
  diga por quê; em prosa, termo estrangeiro em itálico.
- **Trabalhe em branch própria** quando houver código; commits pequenos que expliquem
  o porquê. **Não faça `git push` nem abra PR sem o usuário pedir.**
- Editar `.md` com Python ou `sed` no Windows introduz CRLF; grave bytes ou confira o
  fim de linha (lição do AtlasPen). O `.gitattributes` grava texto com LF e as
  *fixtures* byte a byte (`-text`); não mude isso.
- Todo `open`, `read_text` e `write_text` de texto leva `encoding="utf-8"`, inclusive
  nos testes: no Windows o padrão é cp1252, e foi o que derrubou dois testes do motor
  copiado (lição da sessão de 09/11/2026).
- Ambiente: `python -m venv .venv`, `pip install -e ".[dev]"`; a bateria roda com o
  Python e o `ruff` de dentro do `.venv`.

## O que não entra, e onde entra

- Texto de notícia ou de decisão: não entra. Entra o *link* e, se houver, o
  `snapshot` do Internet Archive.
- Alegação de imprensa como status: não entra. Entra como notícia ligada à situação.
- Previsão, pontuação de risco, ranking de países: não entra. O Astraea aponta para o
  Early Warning Project e para o Genocide Watch.
- Campo de país preenchido "por analogia" com país vizinho ou com a mesma tradição
  jurídica: não entra. Fica vazio com `reason`.
- Léxico em código: não entra. Léxico é dado, um arquivo por língua, gerado de
  `situations.json` mais os termos fixos.
