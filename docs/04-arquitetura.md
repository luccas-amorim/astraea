# 04 — Arquitetura

## Princípios

1. **Sem servidor, sem banco.** Tudo é arquivo de texto versionado e site estático, como
   no AtlasPen e no Alétheia. O custo fixo é zero e nada precisa ficar ligado.
2. **Um motor, três configurações.** As funções 2 e 3 rodam sobre um motor próprio,
   nascido do Alétheia (contrato de adaptador, cliente HTTP educado, triagem por
   léxico, estado com pendentes, saídas JSONL; ver "Onde o motor vive"). A função 1
   não tem *crawler*: tem um **carregador** por fonte global e um validador.
3. **O robô propõe, a pessoa decide o que muda status.** O robô grava notícia e
   andamento; a mudança de status na taxonomia (medida provisória, mérito) e a
   promoção de um registro exigem commit humano.
4. **Fonte secundária aponta, não escreve.** Wikipedia, Wikidata e agregadores servem
   para achar o que falta e abrir pergunta; nunca preenchem campo.
5. **Toda rodada deixa rastro.** Relatório em dois tamanhos, `run.json` com código
   de saída, estado gravado mesmo quando a fonte falha.

## Visão geral

```mermaid
flowchart LR
  subgraph F1[Função 1: leis penais do mundo]
    UNTC[UN Treaty Collection<br/>capítulos IV.1 e XVIII.10]
    CICV[CICV: implementação nacional]
    UNODC[SHERLOC / Legislationline]
    PM[Pena de morte:<br/>Cornell / Anistia]
    CARG[carregadores/<br/>um por fonte, saída JSON]
    UNTC --> CARG
    CICV --> CARG
    UNODC --> CARG
    PM --> CARG
  end

  subgraph F2[Função 2: notícias]
    GDELT[GDELT DOC 2.0<br/>65 línguas]
    RSS2[RSS de agências<br/>e veículos]
    ESP[fontes especializadas<br/>Justiceinfo, ONU]
  end

  subgraph F3[Função 3: tribunais]
    CIJ[CIJ: casos e press releases]
    TPI[TPI: situações, casos, Court Records]
    IRMCT[IRMCT / ECCC / regionais]
  end

  subgraph MOTOR[Motor próprio, astraea/engine/, nascido do Alétheia]
    AD[adaptadores:<br/>gdelt, rss, listing, icj, icc]
    HTTP[cliente HTTP:<br/>robots, limite, sentinela]
    TRI[triagem por léxico<br/>níveis 0–3]
    EST[estado por fonte<br/>pendentes]
    AD --> HTTP --> TRI --> EST
  end

  GDELT --> AD
  RSS2 --> AD
  ESP --> AD
  CIJ --> AD
  TPI --> AD
  IRMCT --> AD

  subgraph DATA[data/ — a fonte, versionada]
    P[countries.json]
    S[situations.json]
    N[news/YYYY/MM.jsonl]
    D[decisions.json]
    L[lexicon/*.json]
    C[verification.json<br/>exceptions.json]
    I[i18n/en.json<br/>i18n/pt-BR.json]
  end

  CARG --> P
  TRI --> N
  TRI --> D
  S --> L
  L --> TRI

  subgraph SAIDA[Derivado e site]
    T[scripts/transform.py<br/>--strict]
    SD[static/data/*.json]
    SITE[GitHub Pages, en e pt-BR:<br/>início, /countries, /news, /decisions]
    T --> SD --> SITE
  end

  P --> T
  S --> T
  N --> T
  D --> T
  I --> T

  H((pessoa)) -. status da taxonomia,<br/>promoção, amostra .-> S
  H -. PR .-> P
  TRI -. relatório da rodada,<br/>pede-juízo .-> H
```

## Os robôs

| Robô | Função | O que faz | Herança | Agendamento |
|---|---|---|---|---|
| **Tabelião** | 1 | lê o **XML por tratado** da UN Treaty Collection (IV.1 e XVIII.10, verificado em `02-fontes.md`) e grava `genocide_convention` e `rome_statute` de cada país, com data, tipo, reservas e retiradas; acusa país novo, retirada e reserva nova | adaptador `listing` do Argos (tabela que muda devagar; linha alterada volta a ser lida) | mensal |
| **Cartógrafo** | 1 | a sondagem mostrou que **não há base aberta viva** de códigos penais: na fase 1 o Cartógrafo só reconfere, todo mês, se Legislationline, SHERLOC, Library of Congress e WorldLII voltaram a responder, e reabre a fonte em `sources.json` quando sim; `penal_code` e `domestic_genocide` entram por carga humana | Cotejador do AtlasPen ("só pergunta") | mensal |
| **Sentenciador** (nome a decidir, D15) | 1 | lê a classificação de pena de morte no espelho do Cornell e propõe `death_penalty`; o anexo anual da Anistia entra à mão | `listing` | semanal (Cornell atualiza às quartas) |
| **Vigia das notícias** | 2 | `astraea run` com `config/news.json`: GDELT por língua (`sourcelang:` × termos) e por tema (`WB_2509_GENOCIDE`), a 1 requisição por 5 s; ReliefWeb por `appname`; ~15 *feeds* RSS (lista em `02-fontes.md`); lê a página do veículo para triar, **exceto nos domínios com *opt-out* de mineração de texto**, onde tria só pelo *feed* e marca `no_text_by_policy`; grava nível ≥ 2 em `news/`, conta nível 0–1 no relatório | motor inteiro (do Alétheia) + adaptador `reliefweb` novo | semanal (diário na fase de calibração) |
| **Escrivão** | 3 | adaptador `icj` (`listing` sobre página de caso e lista de *press releases*; PDF só como URL), `rss` do TPI (registros e notícias), IRMCT, KSC, RSCSL, Corte Africana, TRIAL e HUDOC, `listing` sobre as páginas de mandato da OHCHR; grava `procedural_step` e `press_release` em `decisions.json`; o que parece ordem ou sentença vai para pede-juízo (`needs-review.jsonl`) | motor + `listing` | semanal |
| **Recenseador** | 2 e 3 | uma vez por mês confronta a lista de casos da CIJ e do TPI com o que o Escrivão viu, e a contagem do GDELT por língua com o que o Vigia gravou: defesa contra o falso negativo | Recenseador do AtlasPen | mensal |
| **Arquivista** | todas | fonte com `robots_checked_on` vencido, léxico sem versão nova há 180 dias, documento de `docs/` cuja dependência mudou | Arquivista do AtlasPen | semanal |
| **Auditor** | todas | sorteia a amostra do trimestre (semente = hash do commit), gera a planilha de conferência, lê a planilha preenchida e publica a taxa | `AUDITORIA.md` do AtlasPen | trimestral |

Nenhum robô escreve em `situations.statuses`, em `promotion` ou em campo com
`checked_by: human`. O validador reprova commit de robô que toque neles.

## Agendamentos (GitHub Actions)

| Workflow | Cron (UTC) | Timeout | Commit | Observações |
|---|---|---|---|---|
| `ci.yml` | push e PR | 15 min | não | `transform --strict`, derivado sincronizado, `pytest`, validação de léxico e config, `ruff` |
| `news.yml` | segunda 06:00 | 340 min | uma fonte por vez, `git pull --rebase` + push depois de cada uma (padrão do Alétheia) | `concurrency: news`, sem cancelar; entradas manuais `since` e `source` |
| `courts.yml` | terça 06:00 | 120 min | idem | separado do de notícias para que a falha de um não cale o outro |
| `countries.yml` | dia 1, 05:00 | 60 min | abre **PR**, nunca comita na `main` | o diff de ratificações é pequeno e legível; o PR é a revisão |
| `sources-check.yml` | sexta 02:00 | 15 min | não; abre issue | ensaio das fontes, como o `fontes.yml` do AtlasPen: na sexta se descobre que a fonte mudou, não na segunda |
| `audit.yml` | manual (trimestral) | 30 min | abre PR com a planilha da amostra | |
| `deploy.yml` | push em `main` tocando `static/`, `site/` ou `data/` | 10 min | — | `upload-pages-artifact` + `deploy-pages`, como no AtlasPen; sem Astro na fase 1 |

Limites verificados em 06/11/2026 (docs.github.com):

- Actions é **gratuito em repositório público** em *runners* padrão e não consome a
  cota de US$ 12/mês do plano Free; artefatos: 500 MB.
- Cada *job* pode rodar até **6 horas**; o *workflow*, 35 dias. O cron pode atrasar
  em hora de pico e o intervalo mínimo é de 5 minutos.
- **Em repositório público, o cron é desligado após 60 dias sem atividade.** Para um
  projeto de uma pessoa isso é risco real: o próprio commit do robô conta como
  atividade, então enquanto a rodada comitar, o cron se mantém; se três rodadas
  seguidas falharem sem comitar, o Arquivista abre issue avisando que o cron vai
  morrer.
- `GITHUB_TOKEN`: 1.000 requisições/hora por repositório; PAT: 5.000. Só importa para o
  Cartógrafo quando ler o ctresb/leis por API.

Os robôs comitam com o `GITHUB_TOKEN` padrão como `astraea-bot`, como no Alétheia.
Abrir PR (o `countries.yml`) exige `permissions: pull-requests: write`; o padrão de
GitHub App do AtlasPen fica para quando houver PR que precise disparar CI (commit de
`GITHUB_TOKEN` não dispara outros *workflows*, de propósito; isso é aceitável para a
rodada e inaceitável para o PR de países, que precisa passar na CI: na fase 1 o PR é
aberto com um PAT de escopo mínimo guardado em *secret*, e a troca pelo App é
melhoria registrada no roteiro).

## Onde o motor vive

**Decidido em 09/11/2026 (D2): motor próprio, nascido de uma cópia do Alétheia.** O
Alétheia é ponto de partida, não dependência. O Astraea copia o que lhe serve, traduz
para inglês e segue sozinho.

### Como nasce (fase 1, primeira sessão)

1. **Cópia literal.** Primeiro commit do motor: os módulos do Alétheia que o Astraea
   usa, tal como estão no `sha` da `main` no dia da cópia (em 09/11/2026, `6168d36`),
   em `astraea/engine/`, com os testes e as *fixtures* deles, o texto da licença MIT em
   `LICENSE-aletheia.txt` e uma linha no `NOTICE` com o repositório e o `sha` de origem.
2. **Prova da cópia.** Os testes copiados passam sem mudança. Se não passarem, o
   problema é do ambiente (Python 3.14, por exemplo) e se resolve antes de traduzir.
3. **Tradução.** Commit separado que só renomeia para inglês (módulos, classes,
   funções, chaves das saídas, esquema do léxico, comandos), com os testes renomeados
   junto e verdes. Daí em diante o motor diverge livremente.

O que se copia: contrato, cliente HTTP (com `redigir()` de segredos), captura com
`.part` e sentinela, estado com pendentes, triagem, léxico e seu esquema, saídas,
validação de configuração, os adaptadores `gdelt`, `rss` e `lista`, o arquivo de
referência no Wayback (`arquivo.py`, para `snapshot`) e a estimativa de cobertura. O
que não se copia agora: `topico`, `wikipedia`, `openalex`, `crossref`, `ia` e a
varredura CDX do `wayback`, que ficam fora da fase 1 e podem vir depois pelo mesmo
caminho (cópia, prova, tradução).

### Nomes

| Alétheia | Astraea |
|---|---|
| `Fonte`, `Referencia`, `Documento` | `Source`, `Reference`, `Document` |
| `listar(desde)`, `baixar(ref)`, `sentinela(doc)` | `list(since)`, `fetch(ref)`, `sentinel(doc)` |
| `destaques`, `hash_texto`, `capturado_em` | `highlights`, `text_hash`, `captured_at` |
| `BloqueadoPorRobots`, `BloqueadoPorPais` | `BlockedByRobots`, `BlockedByCountry` |
| `captura.py`, `estado.py`, `triagem.py`, `lexico.py`, `saidas/`, `estimativa.py`, `arquivo.py` | `capture.py`, `state.py`, `triage.py`, `lexicon.py`, `outputs/`, `estimate.py`, `archive.py` |
| adaptador `lista` | adaptador `listing` |
| `aceitos.jsonl`, `pede-juizo.jsonl`, `itens.jsonl`, `rodada.json` | `accepted.jsonl`, `needs-review.jsonl`, `items.jsonl`, `run.json` |
| `estado/<fonte>.json`, `saidas/<rodada>/` | `state/<source>.json`, `runs/<run>/` |
| `aletheia rodar`, `retriar`, `estimar`, `sondar`, `validar-lexico`, `validar-config` | `astraea run`, `retriage`, `estimate`, `probe`, `validate-lexicon`, `validate-config` |
| léxico: `termos`, `chave`, `formas`, `exclusoes`, `categorias`, `peso`, `contexto.exige_qualquer` | `terms`, `key`, `forms`, `exclusions`, `categories`, `weight`, `context.requires_any` |

### O preço, e como pagá-lo

Uma correção feita no Alétheia não chega aqui sozinha, e uma feita aqui não volta para
lá. É o preço aceito. Para pagá-lo, no começo de cada fase a pessoa (ou o agente) lê o
`git log` do Alétheia desde o `sha` registrado no `NOTICE`, porta à mão o que valer a
pena e registra no `CHANGELOG.md` o que veio e o novo `sha` de referência.

### Opções consideradas

| Opção | Por que não |
|---|---|
| Instalar o Alétheia como dependência fixada por `sha` | o pacote e o código são em português e falam de Carandiru; toda mudança de contrato para servir ao Astraea (`Document.languages`, textos por *locale*) obrigaria a mexer no outro projeto |
| Extrair antes um `argos-core` comum aos três | refatorar três repositórios antes de o Astraea existir; se um motor comum vier a fazer sentido, ele pode nascer do motor do Astraea, já em inglês |
| Reescrever do zero com o Alétheia como referência | de três a cinco sessões a mais (chute), sem ganho que os testes copiados não deem |

## Armazenamento e crescimento

Premissas (verificáveis na primeira semana de rodada e corrigíveis no `06-roteiro.md`):

| Entidade | Tamanho por item | Volume esperado | Por ano |
|---|---|---|---|
| País | ~3 KB | 197, estável | ~600 KB, não cresce |
| Situação | ~2 KB | 30–60 | ~100 KB |
| Decisão | ~1,5 KB | 200–600 atos/ano (CIJ + TPI + IRMCT + regionais) | ~1 MB |
| Notícia nível ≥ 2 | ~700 B (JSONL) | GDELT devolve milhares de artigos/dia com "genocide" em períodos de crise; estimativa de **300–1.500 itens/dia** que passem ao nível 2, com 4–6 línguas | **75–380 MB** |
| Notícia nível 0–1 | só contagem no relatório | — | ~0 |
| Relatórios de rodada (`runs/`) | 50–300 KB por rodada | 52–104 rodadas | 5–30 MB |
| Estado (`state/`) | hashes vistos | cresce com os itens | 10–40 MB |

Projeção acumulada (cenário médio, 800 itens/dia de nível ≥ 2):

| Horizonte | `data/news/` | repositório (árvore) | histórico git (estimado 2–3×) |
|---|---|---|---|
| 1 ano | ~200 MB | ~250 MB | ~600 MB |
| 3 anos | ~600 MB | ~700 MB | ~1,8 GB |
| 5 anos | ~1 GB | ~1,2 GB | ~3 GB |

Contra os limites do GitHub (verificados em 06/11/2026): repositório recomendado
**abaixo de 1 GB**, fortemente recomendado abaixo de 5 GB; arquivo acima de 100 MiB
bloqueado (por isso JSONL **por mês**, nunca um arquivo só); fonte do Pages
recomendada abaixo de 1 GB; **site publicado no máximo 1 GB**; 100 GB/mês de banda.

Conclusões:

1. **O repositório único se sustenta por 1 a 2 anos** se (a) só nível ≥ 2 for gravado,
   (b) as notícias forem particionadas por mês, (c) o site derivado levar só os últimos
   90 dias de notícias mais índices agregados, e (d) `runs/` for podado a 12 meses.
2. **No terceiro ano a arquitetura estática continua servindo, mas o repositório único
   não**: o histórico git passa de 1 GB, o clone fica lento e cada PR de código carrega
   commits de robô. O gatilho de separação é objetivo: **árvore acima de 500 MB ou
   mais de um commit de robô por dia**. Nesse ponto nasce `astraea-dados`
   (só `data/`, `state/`, `runs/`, CC BY 4.0) e o `astraea` passa a lê-lo na CI
   como submódulo ou por *download* de release.
3. **A arquitetura estática deixa de servir** só se a tela de notícias precisar de
   busca por texto sobre o acervo inteiro (hoje a busca é por mês e situação, sobre
   índices pequenos) ou se o volume de nível ≥ 2 passar de ~3.000/dia. Aí a resposta é
   um índice pré-calculado (ex.: *sqlite* servido como arquivo estático e lido com
   *range requests*) antes de qualquer servidor. O plano não prevê servidor em nenhum
   horizonte.
4. **Releases trimestrais** com DOI no Zenodo (como o Alétheia planeja) são o arquivo
   de longo prazo: o repositório pode podar o que a release já guarda.

## As telas

Fase 1: HTML estático com JavaScript sem *framework*, lendo `static/data/*.json`, no
padrão do `index.html` do Alétheia, uma página por tela. Sem CDN e sem Node: as
páginas saem de modelos em `site/` por `scripts/build_site.py` (só biblioteca padrão),
uma cópia por *locale* e uma ficha por país e por situação, porque o GitHub Pages não
reescreve rotas. Astro entra quando as telas pedirem componentes compartilhados
(fase 3 do roteiro), e o AtlasPen já tem a configuração a copiar.

**Duas línguas desde o primeiro dia.** Toda rota existe em `/en/…` e em `/pt-br/…`,
com o mesmo caminho depois do prefixo (`/en/countries/BRA`, `/pt-br/countries/BRA`): o
caminho é identificador e não se traduz; o que muda é o texto. A raiz `/` é uma página
curta nas duas línguas que leva à versão do navegador. Cada página tem o seletor de
língua e as marcas `hreflang`. Texto nosso que não tem versão no *locale* aparece na
versão que existe, marcado com a língua ("disponível só em português"). As rotas da
tabela abaixo são escritas sem o prefixo.

| Tela | Rota | O que mostra | Dados |
|---|---|---|---|
| Início | `/en/`, `/pt-br/` | o que é o Astraea, três contadores (países com ratificação conferida, notícias nos últimos 30 dias, atos de tribunal no ano), as situações com status mais alto no último trimestre, "como citar" | `quality.json`, `situations.json` |
| Leis penais do mundo | `/countries`, `/countries/<ISO>` | tabela com filtros (ratificou a Convenção? tipifica genocídio? pena de morte?), completude por campo, e a ficha do país com proveniência campo a campo; o mapa coroplético é SVG estático gerado no *build*, sem biblioteca | `countries.json` |
| Notícias | `/news` | últimos 90 dias, filtros por situação, língua, veículo, nível; gráfico de volume por semana e por língua; cada item com título original, língua, veículo, data, *link* e, se houver, tradução e resumo marcados | `news-recent.json`, `news-index.json` |
| Decisões | `/decisions`, `/situations/<id>` | linha do tempo por situação com o status da taxonomia e o órgão; tabela de atos por tribunal; ficha da situação com os países, os status e os atos | `decisions.json`, `situations.json` |
| Projeto | `/about/*` | metodologia, fontes (com confiança e termos), robôs, dados abertos, pessoas, como citar | `docs/` |

Dados abertos: `static/data/*.json` sob CC BY 4.0, com `CITATION.cff` e o dicionário
de campos em `docs/dados-abertos.md`, como no AtlasPen.

## Multilinguismo

- **Coleta**: o GDELT traduz 65 línguas para inglês na indexação e aceita busca em
  inglês sobre todas; o adaptador consulta por língua (`sourcelang:`) para que a
  contagem por língua seja real, e grava `language` do original. O UN News tem *feed* em
  10 línguas; BBC, DW, France 24, Al Jazeera, Anadolu e HRW têm *feeds* por língua.
- **Classificação**: um léxico por língua, no formato do Argos. Na fase 1: inglês,
  francês, espanhol, português e árabe (os idiomas das fontes oficiais mais o da
  situação com maior volume). Línguas sem léxico entram pelo GDELT com a busca em
  inglês e ficam no nível 1 (`no_context`), contadas e não gravadas, até ganharem
  léxico: o relatório diz quantas por língua, e é isso que decide a próxima língua.
- **Tradução**: nenhuma na triagem. O título original é o que se publica. Tradução
  de título, quando houver, vai para `title_translations`, marcada com `author`, e é
  opcional (D4 pendente: humana, modelo de linguagem com custo estimado em
  `05-viabilidade-e-riscos.md`, ou nenhuma).
- **Telas e dados abertos**: chaves em inglês, nunca traduzidas; rótulos em
  `data/i18n/<locale>.json`; textos nossos como texto localizado; telas em `en` e
  `pt-BR` desde a fase 1 (ver "As telas" e `03-modelo-de-dados.md`, "Várias línguas").
  Os demais *locales* entram pela fase multilíngue do `06-roteiro.md`.
- **Registro**: `language` em todo documento; `languages` em decisão (CIJ e TPI publicam
  em inglês e francês; Corte IDH em espanhol; ECCC em khmer, inglês e francês).

## Promoção: do monitoramento ao detalhamento

O gatilho é **objetivo e registrado**; a decisão é humana.

| Gatilho (qualquer um) | Quem detecta | O que acontece |
|---|---|---|
| Ato de tribunal com `taxonomy_status` ≥ `provisional_measures` numa situação | Escrivão, em pede-juízo | a pessoa confirma o ato, grava o status e marca `promotion.level = under_investigation` |
| Volume de notícias de nível 3 de uma situação acima de 3× a mediana das 12 semanas anteriores | Vigia, no relatório | issue com rótulo `promotion-candidate` |
| País sem `domestic_genocide` conferido que apareça como `territory` ou `respondent` de situação com status ≥ `investigation` | transformador, em `quality.json` | issue: o registro superficial virou prioridade de conferência |
| Pedido explícito da pesquisa | pessoa | issue |

Níveis de `promotion`:

1. `surface`: o registro como o robô o produziu.
2. `under_investigation`: há dono e prazo (a issue); os campos vazios do país e os atos da
   situação são conferidos à mão; o resumo próprio é escrito; `checked_by: human`.
3. `detailed`: o registro ganhou um **dossiê**, que vive em **repositório-filho**
   (`astraea-<situation>`, modelo do Alétheia: léxico próprio, varredura do passado
   com Wayback, estimativa de cobertura, catálogo próprio) ou, quando for lei de um
   país, no padrão do AtlasPen (o Brasil já tem o seu). O Astraea guarda só `onde` e
   os campos de superfície; o dossiê é citado pela URL. Isso mantém o Astraea leve e
   deixa cada dossiê com o ritmo, a licença e o léxico que a pesquisa pedir.

Regra de ouro: **a promoção nunca reescreve o registro superficial**; acrescenta. O
que o robô achou continua lá, com o carimbo original, e o que a pessoa conferiu entra
com o carimbo dela.

## Segurança e segredos

Só chaves gratuitas e opcionais (OpenAlex, Crossref, se os dossiês as usarem), em
*secrets* do repositório; o cliente HTTP redige qualquer `api_key=` de log e relatório,
como no Alétheia. Nenhum segredo entra em `data/`, em `runs/` ou em `state/`.
Dependabot semanal para Actions, como no AtlasPen; sem dependências Python de
execução, não há o que atualizar fora disso.
