# Como contribuir — Astraea

## Visão geral

- **Fonte dos dados:** `data/` (um arquivo por entidade; notícias em JSONL por mês).
- **Dados consumidos pelo site:** `static/data/` — **gerado** por
  `scripts/transform.py`. Não edite à mão.
- **Motor dos robôs:** próprio, em `astraea/engine/`, nascido de uma cópia do
  Alétheia (aviso MIT e `sha` de origem no `NOTICE`); adaptadores em
  `astraea/sources/`.
- **Língua:** dados e código em inglês; documentação em português; telas em `en` e
  `pt-BR` (ver `AGENTS.md`).
- **Plano e decisões:** `docs/00` a `docs/07`. O que mudar de regra muda lá primeiro.

## Glossário

- **Situação** — o contexto (conflito, território, período) em que genocídio é
  alegado, investigado ou julgado. É a entidade que liga as três telas.
- **Status** — o grau da qualificação jurídica alcançado numa situação, com o órgão
  que o produziu: `allegation`, `political_recognition`, `investigation`, `accusation`,
  `provisional_measures`, `merits_decision`, `closed`.
- **Ato** — a unidade da tela de decisões: ordem, sentença, parecer, mandado,
  andamento. Um caso tem muitos atos.
- **Carimbo** — o bloco de proveniência de um campo: `url`, `source`, `read_on`,
  `confidence`, `checked_by`.
- **Promoção** — a passagem de um registro de `surface` para `under_investigation` e
  `detailed`, por gatilho registrado e decisão humana.

## Como os dados são atualizados

1. **Semanalmente**, os *workflows* `news.yml` e `courts.yml` rodam o motor
   sobre as fontes declaradas em `config/`, gravam em `data/` o que passou ao nível 2
   ou 3 e comitam, uma fonte por vez, com o relatório da rodada em `runs/`.
2. **Mensalmente**, `countries.yml` lê as fontes globais da função 1 e abre um **PR**
   com o que mudou em `countries.json`. O PR é a revisão.
3. **O que pede juízo** sai no relatório e, para tribunais, é lido toda semana: o ato
   que muda status entra por commit humano, com `checked_by: human`.
4. **Trimestralmente**, `audit.yml` sorteia a amostra e abre o PR com a planilha;
   a taxa de erro vai para `docs/auditoria.md` e para a página do projeto.

> Em resumo: **a máquina coleta e propõe; gente decide status, promoção e correção.**

## Passos de uma atualização de dado (PR)

1. Edite **apenas** `data/`.
2. Se mexeu em termos (`situations.terms` ou `data/lexicon/fixed/`), refaça o léxico:
   `python scripts/build_lexicon.py --execute`. Depois regenere o derivado:
   `python scripts/transform.py --draft --execute` enquanto durar a carga inicial,
   `--strict --execute` quando não houver mais rascunho (no Windows, abra o
   PowerShell na pasta do projeto; o aviso "a execução de scripts foi desabilitada"
   diz respeito a `.ps1`, não a Python, e pode ser ignorado).
3. Rode a bateria de `AGENTS.md`.
4. Abra o PR dizendo **o que** mudou, **por que** e **qual fonte** sustenta. Mudança de
   status de situação cita o ato (`decisions.id`).

## Convenções do catálogo (impostas pela CI onde marcado)

### C1. Todo campo afirmado tem carimbo ⛔ imposta

`valor` não nulo exige `url`, `source` (existente em `sources.json` e `ativa`),
`read_on`, `confidence` e `checked_by`. Sem isso, `--strict` reprova. A carga inicial
usa `--draft`, e o relatório conta os rascunhos. Campo que não é bloco (`name`,
`un_status`, `un_member_since`) recebe o carimbo por uma linha de
`data/verification.json` que cite o registro e o campo.

### C2. Status sem órgão não é status ⛔ imposta

Cada item de `situations.statuses` tem `code`, `by`, `date`, `url`, `confidence`.
`merits_decision` exige `outcome`. `provisional_measures` e `merits_decision` exigem
`checked_by: human`.

### C3. `id` é append-only ⛔ imposta

Nunca reatribuído. País que deixa de existir ganha `valid_until`; documento que sai
vai para `retired-ids.json`.

### C4. Um ato por registro

A chave de decisão é `tribunal + caso + data + tipo_ato`. Dois atos no mesmo dia são
dois registros. Um caso não é registro.

### C5. Vocabulário fechado ⛔ imposta

Toda enumeração tem lista em `scripts/vocabularies.py`. Valor novo entra por PR que
muda a lista e o `03-modelo-de-dados.md` juntos.

### C6. Texto nosso tem autor; texto de terceiro não existe aqui

`description`, `summary` e `title_translations` têm `author` (`human` ou `model:<id>`), até 600
caracteres. Nenhum campo guarda corpo de notícia ou de decisão.

### C7. Língua original sempre

`language` (ISO 639-1) em todo documento; `languages` em todo ato. Sem língua, não entra.

### C8. Fonte vencida não alimenta rodada ⛔ imposta

`sources.json` guarda `robots_checked_on`; o robô recusa fonte sem verificação nos
últimos 180 dias, e o Arquivista abre issue antes do vencimento.

### C9. Nome de pessoa só como o tribunal escreve

Em `decisions.json`, no nome do caso ou do ato. Em nenhum outro lugar. Pedido de
remoção segue `docs/pessoas.md`.

## Versão e notas

SemVer com a leitura do AtlasPen: `0.0.x` até o lançamento; o `CHANGELOG.md` registra
cada sessão. Mudança de **esquema** (campo novo, enumeração nova) sobe o número do
meio; quebra de contrato dos dados abertos, o primeiro. Mudança de dado não é
versão: é commit com carimbo.

## Licenças

Código sob Apache-2.0; dados, resumos e documentação sob CC BY 4.0. Metadados de
documentos de terceiros são apontados, não redistribuídos; cada fonte de dado
agregado (GDELT, UN Treaty Collection) é citada no `NOTICE` e na página de fontes.

## Desenvolvimento

```bash
pip install -e ".[dev]"            # instala o Astraea (com o motor) e as ferramentas
python scripts/build_lexicon.py            # simulação; --execute grava o léxico
python scripts/transform.py --draft        # --strict quando não houver rascunho
python -m pytest
astraea validate-lexicon data/lexicon/*.json
```

Exige Python 3.11+. Sem dependências de execução: o motor usa só a biblioteca padrão,
como o Alétheia de onde veio.
