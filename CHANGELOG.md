# Changelog

Uma sessão = uma entrada. Datas no fuso de Brasília. Até a v1.0.0 a versão é `0.0.x`
(ver `CONTRIBUTING.md`, "Versão e notas").

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
