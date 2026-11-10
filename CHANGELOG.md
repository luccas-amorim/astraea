# Changelog

Uma sessão = uma entrada. Datas no fuso de Brasília. Até a v1.0.0 a versão é `0.0.x`
(ver `CONTRIBUTING.md`, "Versão e notas").

## 2026-11-10 — Fase 1, sessão 3: situações, léxico e validador

Branch `fase1/validador`. O motor (`astraea/engine/`, `astraea/sources/`) não mudou;
`astraea/cli.py` mudou num ponto (ver "Código").

**Dados novos** (todos em `data/`):

- `situations.json` — as dez situações da D6, seguida como recomendada: `rohingya-myanmar`,
  `gaza-2023`, `ukraine-2022`, `darfur`, `tigray-ethiopia`, `uyghurs-xinjiang`,
  `yazidis-sinjar`, `rwanda-1994`, `srebrenica-1995`, `cambodia-1975`. Cada uma com
  `name` (`en`, `pt-BR`), `countries` com papel, `period`, `terms` nas cinco línguas da D5
  e `promotion` em `surface`. Nenhuma `description` (depende da D4) e nenhum nome de
  pessoa (regra 8).
- **Status: nove, em cinco situações, todos com `checked_by: null`** (o carimbo `human` é
  seu, regra 3). Entrou só o que a seção 3.3 do `02-fontes.md` ou a página oficial
  sustenta:

  | Situação | Status | Órgão (`by`) | Data | De onde |
  |---|---|---|---|---|
  | `rohingya-myanmar` | `accusation` | The Gambia, application instituting proceedings (ICJ) | 2019-11-11 | icj-cij.org/case/178 |
  | `rohingya-myanmar` | `provisional_measures` | International Court of Justice | 2020-01-23 | icj-cij.org/case/178 |
  | `gaza-2023` | `accusation` | South Africa, application instituting proceedings (ICJ) | 2023-12-29 | icj-cij.org/case/192 |
  | `gaza-2023` | `provisional_measures` | International Court of Justice | 2024-01-26 | icj-cij.org/case/192 |
  | `gaza-2023` | `investigation` | Independent International Commission of Inquiry on the Occupied Palestinian Territory, including East Jerusalem, and Israel (UN) | 2025-09-16 | seção 3.3 do `02-fontes.md` (a página da OHCHR devolveu 403) |
  | `ukraine-2022` | `provisional_measures` | International Court of Justice | 2022-03-16 | icj-cij.org/case/182 |
  | `darfur` | `investigation` | International Criminal Court | 2005-06 | icc-cpi.int/darfur |
  | `darfur` | `accusation` | International Criminal Court, warrant of arrest | 2010-07-12 | icc-cpi.int/darfur |
  | `srebrenica-1995` | `merits_decision` (`partial`) | International Court of Justice | 2007-02-26 | icj-cij.org/case/91 |

  Páginas lidas em 10/11/2026: as quatro da CIJ pela ferramenta de leitura de páginas do
  agente; a do TPI pelo cliente HTTP do motor, com o `User-Agent` do Astraea e o
  `robots.txt` obedecido (sha256 da resposta
  `3c74cb769e684edb200671b5b9c297e981426083de79b545008691ca066ce45c`). Responderam com
  bloqueio e **não foram contornadas** (regra 7): `ohchr.org` (403, desafio da
  Cloudflare, nas páginas da missão sobre Mianmar e da comissão sobre o território
  palestino ocupado), `unictr.irmct.org` (403) e `eccc.gov.kh/en/cases` (500).
- **Cinco situações sem status**, de propósito: `tigray-ethiopia` e `uyghurs-xinjiang`
  (a 3.3 não registra ato; a comissão da ONU sobre a Etiópia fechou em 2023 sem achado
  localizado), `yazidis-sinjar` (a 3.3 só tem imprensa não verificada), `rwanda-1994`
  (a página do TPIR bloqueou) e `cambodia-1975` (a página inicial da ECCC afirma a
  condenação, mas sem data, e a de casos deu erro). As sentenças históricas (TPIR, TPII,
  ECCC) são a carga à mão da fase 3.
- `countries.json` — os 197 registros ganham `situations` (lista vazia onde não há elo).
  Quinze países têm elo: BIH, CHN, ETH, GMB, IRQ, ISR, KHM, MMR, PSE, RUS, RWA, SDN,
  SRB, UKR, ZAF.
- `verification.json` — a trilha que carimba os campos escalares, com as duas leituras
  da sessão 2: os 197 nomes (CLDR, confiança B) e `un_status` e `un_member_since` dos
  193 membros (lista da ONU, confiança A), ambas `checked_by: robot`, lidas em
  09/11/2026.
- `lexicon/fixed/<lang>.json` — os termos fixos de en, fr, es, pt e ar, mantidos à mão:
  doze termos com as mesmas chaves nas cinco línguas e a lista de marcadores jurídicos
  de cada uma. `lexicon/<lang>.json` — o léxico gerado (22 termos por língua; 80 formas
  em inglês, 93 em francês, 101 em espanhol, 105 em português, 133 em árabe).
- `i18n/` — 117 campos e 126 valores rotulados nas duas línguas (entraram as categorias
  do léxico, os campos da trilha e os campos derivados) e os padrões de data de cada
  *locale*.

**O árabe é rascunho.** Foi escrito sem falante e não foi revisto por um: grafias
(الروهينغا / الروهينجا), partículas prefixadas listadas à mão e a escolha de "حرب
الإبادة" como forma de `genocide` pedem revisão. A marca `DRAFT` está na `description`
de `lexicon/fixed/ar.json` e de `lexicon/ar.json`.

**Derivado novo:** `static/data/` (`countries.json`, `situations.json`,
`i18n/en.json`, `i18n/pt-BR.json`, `quality.json`), gerado por
`python scripts/transform.py --draft --execute`.

**Código:**

- `scripts/transform.py` — as onze travas do `03-modelo-de-dados.md`, lendo os
  vocabulários de `scripts/vocabularies.py`; gera `static/data/`. Simulação por padrão,
  `--execute` grava, nunca apaga, `--check` acusa derivado desatualizado, `--draft`
  relaxa só as travas 3 e 6.
- `scripts/build_lexicon.py` — gera `data/lexicon/<lang>.json` dos termos fixos e de
  `situations.terms`. Simulação por padrão, `--execute` grava.
- `scripts/vocabularies.py` — categorias do léxico, campos da trilha e derivados,
  línguas com léxico, ordem da taxonomia, o carimbo.
- `astraea/cli.py` — `astraea validate-lexicon` aceita vários arquivos e expande o
  asterisco por conta própria, porque o PowerShell entrega `data/lexicon/*.json` sem
  expandir e a bateria pede exatamente isso.
- Testes: `tests/test_transform.py` (cada trava, os dois modos, os derivados, os dados
  reais) e `tests/test_build_lexicon.py` (o gerador e o que os termos casam em cada
  língua).

**Decisões tomadas nesta sessão**, todas registradas no `03-modelo-de-dados.md` e
reversíveis por você:

- **Carimbo de `un_status` e `un_member_since`:** uma linha de `verification.json`
  (seções "Carimbo dos campos escalares" e "Trilha de conferência"). A leitura da
  sessão 2 entrou como `checked_by: robot`; para isso a definição de `robot` passou a
  incluir o *script* de carga com o `hash` da resposta registrado, além do adaptador com
  sentinela. Se preferir que só adaptador conte, basta pôr `checked_by: null` nas duas
  linhas: os 197 países viram rascunho.
- **Data parcial** (`2005-06`, `2003`) em status e período, para gravar "June 2005"
  como a fonte dá.
- **`closed` abaixo de todos** no cálculo do status mais alto; entre iguais, o mais
  antigo; o rótulo de `merits_decision` leva o resultado.
- **Onde vivem os termos fixos**, a versão do léxico com resumo do conteúdo e as cinco
  categorias.
- A trava 3 cobra os cinco itens do carimbo (o `03` listava quatro; a C1 do
  `CONTRIBUTING.md`, cinco).

**Bateria:** 210 testes passam; `ruff check` e `ruff format --check` limpos;
`astraea validate-lexicon data/lexicon/*.json` valida os cinco;
`python scripts/transform.py --draft --check` passa. **`python scripts/transform.py
--strict` reprova, de propósito, só por rascunho: 13 campos em 9 registros** (os nove
status, quatro deles também pela trava 6, e o `un_status` de Palestina, Santa Sé, Kosovo
e Taiwan, que a página de membros lida não cobre). `config/` ainda não existe.

**O que as mensagens dizem** (elas saem em inglês):

- `draft check 3 (stamp): situations[gaza-2023].statuses[1]: asserted without stamp:
  missing checked_by` — o status afirma algo e ninguém carimbou; em `--draft` é só
  aviso.
- `FAIL check 6 (status recorded by a person): ...` — medida provisória ou decisão de
  mérito sem `checked_by: human`.
- `strict: only drafts stand in the way` — só há rascunhos entre os dados e o modo
  estrito; `draft: passed. ... 13 fields in draft` — passou, contando-os.
- `would write (changed): static/data/quality.json` — simulação: diz o que gravaria;
  `left alone (...)` — arquivo que o *script* não gera e não apaga.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **Os `id` das situações ficam para sempre** depois de publicados (regra 5); ainda dá
  para trocar antes do `git push`. Segui o `03` (`rohingya-myanmar`, `gaza-2023`,
  `darfur`, `srebrenica-1995`) e o padrão grupo-lugar ou lugar-ano nos demais; a D6 fala
  em "Srebrenica/Bósnia" e "Camboja (ECCC)", e eu usei `srebrenica-1995` e
  `cambodia-1975`.
- **Comissão de inquérito: `investigation` ou `allegation`?** A comissão da ONU afirmou,
  em 16/09/2025, o que a 3.3 transcreve; gravei como `investigation` (órgão com mandato),
  seguindo o exemplo do `03`, e não como `allegation`.
- **Ucrânia:** só a medida provisória de 16/03/2022. A petição da Ucrânia pede que a
  Corte declare que ela *não* cometeu genocídio, e gravá-la como `accusation` diria o
  contrário; as reconvenções russas admitidas em 05/12/2025 ficaram fora porque não li
  o seu conteúdo na página.
- **Darfur:** ficaram fora a ordem da CIJ de 05/05/2025 (Sudão v. EAU) e o relatório da
  missão da ONU sobre El Fasher, porque a D6 trata "Sudão 2023–" como situação omitida;
  se você os quiser em `darfur`, ou numa situação nova, a 3.3 já os sustenta. A data do
  mandado (12/07/2010) vem da página do TPI; que é esse o mandado com a imputação de
  genocídio vem do exemplo do `03`, a conferir no próprio ato.
- **Srebrenica:** `outcome: partial` sem nota. A regra 3 da taxonomia pede a nota (a
  Corte reconheceu o genocídio e não a responsabilidade pela autoria), mas nota é texto
  nosso com `author`, que depende da D4.
- **Períodos** não têm fonte no modelo: são meus, quase todos com `approximate: true`.
- **Papéis:** só `territory`, `applicant`, `respondent` e, no Camboja, `forum`. Não usei
  `party`.
- **Termos de situação:** grupo, lugar específico e nome do caso, nunca o nome do país;
  Ucrânia só com formas amarradas a "genocídio". "Gaza" e "Darfur" entram sozinhos e vão
  trazer volume: a tela de notícias (fase 4) deve exigir categoria além de `situation`.
- O *locale* `pt-BR` mostra o órgão em inglês ("medidas provisórias — International
  Court of Justice, 26/01/2024"), porque `by` é texto de terceiro e não se traduz. O
  `03` ilustra com "CIJ"; se quiser a sigla, ela teria de vir de um rótulo, não de `by`.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

```powershell
python scripts\transform.py --draft
python scripts\transform.py --strict
python -m pytest
```

O primeiro termina com `draft: passed`; o segundo lista os 13 rascunhos e termina com
`strict: FAILED`, que é o esperado. Nenhum dos dois grava nada sem `--execute`. Para
carimbar um status depois de ler a página: em `data/situations.json`, troque
`"checked_by": null` por `"checked_by": "human"`, rode
`python scripts\transform.py --draft --execute` e faça o commit você mesmo.

## 2026-11-09 — Fase 1, sessão 2: licenças e primeiros dados

Branch `fase1/dados`. Nenhuma linha do motor mudou.

**Licenças:** `LICENSE` (Apache-2.0, texto baixado de apache.org) e `LICENSE-CC-BY-4.0`
(texto de creativecommons.org), ambos sem alteração; `LICENSE-unicode.txt` (aviso do
CLDR, que a Licença Unicode v3 exige junto dos dados); `CITATION.cff` com autoria pessoal
(D14, como recomendado); `MITO.md` (Arato, Ovídio, Virgílio). O `NOTICE` ganhou as duas
fontes de dados de terceiros desta sessão.

**Dados novos** (todos em `data/`):

- `countries.json` — os 197 registros da D1, só com `id`, `name` (`en`, `pt-BR`),
  `un_status` e `un_member_since`. Nenhum campo de lei penal ou de tratado: ficam
  **ausentes** até a fase 2. De onde veio cada coisa:
  - **códigos alfa-3**: Unicode CLDR 49.0.0, `cldr-core/supplemental/codeMappings.json`
    (sha256 `e046ac4c…46c7`), pela tag `49.0.0` do repositório `unicode-org/cldr-json`;
  - **nomes**: o mesmo CLDR, `cldr-localenames-full/main/en/territories.json`
    (`1326fb3b…bf04`) e `main/pt/territories.json` (`89604c7c…9ee8`; o `pt` do CLDR é o
    português do Brasil), na forma padrão de cada um;
  - **membros e data de admissão**: https://www.un.org/en/about-us/member-states, lida
    em 09/11/2026 (sha256 da página `7447a452…6067`), depois de ler o `robots.txt`
    (`Crawl-delay: 10`, página permitida). Os 193 cartões da página foram casados com o
    CLDR pelo código alfa-2 da bandeira de cada cartão, e os 193 nomes conferidos um a
    um: as diferenças são só de forma ("Bolivia (Plurinational State of)" × "Bolivia").
    `un_member_since` é a data de admissão tal como a ONU a publica (Alemanha 1973,
    Sérvia 2000, Rússia 1945).
  - **Exceções**, ambas no `NOTICE`: Kosovo é `XKX` (D1), não o `XKK` do CLDR; a
    Palestina usa a forma `alt-short` do CLDR ("Palestine", "Palestina"), porque a forma
    padrão, "Palestinian Territories", nomeia um território, e o registro da D1 é o
    Estado observador.
- `sources.json` — 87 entradas: todas as fontes do `02-fontes.md` (85, uma por canal) e
  as duas desta sessão (`cldr`, `un-member-states`). 46 `active`, 10 `suspended`,
  31 `discarded`, cada uma com `reason`. Ficaram sem `robots_checked_on` 16 fontes,
  porque o 02 não registra a leitura do `robots.txt` delas: `loc-glm`,
  `prevent-genocide`, `cornell-dpw`, `foreign-law-guide`, `eur-lex`, `coe`,
  `gdelt-bigquery`, `gdelt-ngrams`, `emm`, `afp`, `guardian-api`, `el-pais`,
  `bing-news`, `stl`, `hudoc`, `afchpr`. O robô recusa essas fontes até a reconferência.
  A leitura dos campos (uma entrada por canal, `api`, `reason`, 404 como lido) está no
  `03-modelo-de-dados.md`, seção "Fontes".
- `retired-ids.json` — lista vazia.
- `i18n/en.json` e `i18n/pt-BR.json` — 108 campos e 110 valores rotulados nas duas
  línguas. A convenção da chave está no `03`, seção "Várias línguas".

**Código:** `scripts/vocabularies.py`, lista única dos vocabulários fechados, das chaves de
campo e dos *locales* (a C5 do `CONTRIBUTING.md` já apontava para ele); o `transform.py`
da sessão 3 deve ler dele. `tests/test_data.py`: os 197 *ids* (únicos, alfa-3, conjunto
exato da D1), `un_status` e data por grupo, campos permitidos, `retired-ids.json`, forma
das fontes e cobertura dos rótulos nas duas línguas.

**Bateria:** 115 testes passam; `ruff check` e `ruff format --check` limpos.
`transform.py`, `data/lexicon/` e `config/` ainda não existem, então `validate-lexicon` e
`validate-config` não têm o que validar.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- Nomes do CLDR que soam a menu: "Congo - Kinshasa" (`COD`, nas duas línguas), "Congo -
  Brazzaville" (`COG`, em inglês), "Myanmar (Burma)", "St. Kitts & Nevis". O CLDR tem
  variantes (`alt-variant`, `alt-short`) para vários deles; usei só a da Palestina.
- `VAT` aparece como "Vatican City" / "Cidade do Vaticano", o nome do CLDR. O observador
  na ONU é a Santa Sé, e o CLDR não tem esse nome.
- `icc-asp` ficou `discarded`: o 02 a chama de "fraca" e superada pelo XML da UNTC.
- `reason` em `sources.json` ficou em inglês, sem versão por *locale*; traduzir depende
  da D4 (autoria por modelo).

## 2026-11-09 — Fase 1, sessão 1: o motor (versão 0.0.1)

Primeiro código do Astraea. Nenhum dado, fonte ou *workflow* ainda.

**Motor** (`docs/04-arquitetura.md`, "Onde o motor vive"): copiado do Alétheia no commit
`6168d36` e traduzido para inglês, em quatro commits que se leem sozinhos: cópia byte a
byte, prova (testes verdes), recorte dos canais fora da fase 1, tradução. Ficaram o
contrato, o cliente HTTP educado, a captura com sentinela, o estado com pendentes, a
triagem em níveis, o léxico, a rodada, as saídas, o catálogo, as observações, a
estimativa de cobertura, a cópia de referência no Wayback e os adaptadores `rss`,
`gdelt` e `curated_list`. Comando `astraea` com `run`, `retriage`, `estimate`,
`validate-lexicon` e `validate-config`.

**Bateria:** 105 testes passam no Python 3.14 (Windows); `ruff check` e
`ruff format --check` limpos. `transform.py` ainda não existe.

**Correções ao plano:**

- O adaptador `lista` do Alétheia lê um CSV feito à mão; não é o leitor de tabela que o
  inventário supunha (esse é do Argos). Virou `curated_list`. O leitor de página e de
  XML, `listing`, é escrito na fase 2 (`04-arquitetura.md`, `06-roteiro.md`).
- Os testes do Alétheia falhavam no Windows por dois motivos de ambiente, não de
  versão do Python: fim de linha das *fixtures* (resolvido por `.gitattributes`) e
  leitura sem `encoding` (os testes agora leem em UTF-8). Regra nova no `AGENTS.md`.

**Arquivos novos:** `pyproject.toml`, `.gitattributes`, `.gitignore`, `NOTICE`,
`LICENSE-aletheia.txt` (MIT do Alétheia), `schemas/lexicon.schema.json`.

**Para você (Windows), quando quiser rodar os testes:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest
```

O segundo comando pode dar o aviso "a execução de scripts foi desabilitada neste
sistema"; a solução está no `docs/06-roteiro.md`, "Criar o ambiente Python".

## 2026-11-09 — Decisões D1, D2, D3, D7 e D8; plano ajustado

Sessão só de plano: nenhum código, dado ou *workflow*.

**Decisões** (`docs/07-decisoes-pendentes.md`):

- D1 (197 países, Kosovo `XKX`), D3 (repositório único com gatilho de separação) e D7
  (Apache-2.0 + CC BY 4.0): aceitas como recomendadas.
- D2: **motor próprio** nascido de uma cópia do Alétheia (aviso MIT e `sha` de origem
  no `NOTICE`), traduzido para inglês e livre para divergir. O Alétheia não é
  dependência.
- D8: **dados e código em inglês** (arquivos, chaves, valores, *ids*, comandos);
  documentação, commits, issues e nomes dos robôs em português; telas em `en` e
  `pt-BR` desde a fase 1. Chave publicada não muda mais.

**Regras** (`AGENTS.md`): nova regra de línguas; o estado do projeto descreve o motor
próprio; a bateria passa a chamar `scripts/transform.py --strict` e
`astraea validate-lexicon` / `validate-config`.

**Plano:**

- `03-modelo-de-dados.md` reescrito com o vocabulário em inglês; nova seção "Várias
  línguas" (rótulos em `data/i18n/<locale>.json`, textos nossos por *locale*, cada
  versão com `author`); trava 11 (valor sem rótulo nos *locales* ativos reprova); os
  *slugs* de situação passam a ser em inglês (`rohingya-myanmar`).
- `04-arquitetura.md`: "Onde o motor vive" reescrito (cópia, prova, tradução; tabela
  de nomes Alétheia → Astraea; o preço da divergência); rotas com prefixo `/en/` e
  `/pt-br/`; páginas geradas por `scripts/build_site.py`.
- `06-roteiro.md`: fase 1 com 4 sessões (a primeira importa o motor); MVP com 17
  sessões; nova fase 14, várias línguas (es, fr, ar, depois zh e ru).
- `05-viabilidade-e-riscos.md`: R15 reescrito para o motor próprio; R18 novo (telas
  em duas línguas desencontradas).
- `00`, `01`, `02` e `CONTRIBUTING.md`: nomes atualizados e notas de atualização; o
  inventário continua citando os ativos de origem pelos nomes que eles têm lá.
