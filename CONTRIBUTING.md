# Como contribuir — Astraea

## Visão geral

- **Fonte dos dados:** `data/` (um arquivo por entidade; notícias em JSONL por mês).
- **Dados consumidos pelo site:** `static/data/` — **gerado** por
  `scripts/transformar.py`. Não edite à mão.
- **Motor dos robôs:** o pacote do Alétheia, fixado por `sha` em `pyproject.toml`;
  adaptadores próprios em `astraea/fontes/`.
- **Plano e decisões:** `docs/00` a `docs/07`. O que mudar de regra muda lá primeiro.

## Glossário

- **Situação** — o contexto (conflito, território, período) em que genocídio é
  alegado, investigado ou julgado. É a entidade que liga as três telas.
- **Status** — o grau da qualificação jurídica alcançado numa situação, com o órgão
  que o produziu: `alegacao`, `reconhecimento_politico`, `investigacao`, `acusacao`,
  `medida_provisoria`, `decisao_merito`, `encerrado`.
- **Ato** — a unidade da tela de decisões: ordem, sentença, parecer, mandado,
  andamento. Um caso tem muitos atos.
- **Carimbo** — o bloco de proveniência de um campo: `url`, `fonte`, `lido_em`,
  `confianca`, `conferido_por`.
- **Promoção** — a passagem de um registro de `superficial` para `em_investigacao` e
  `detalhado`, por gatilho registrado e decisão humana.

## Como os dados são atualizados

1. **Semanalmente**, os *workflows* `noticias.yml` e `tribunais.yml` rodam o motor
   sobre as fontes declaradas em `config/`, gravam em `data/` o que passou ao nível 2
   ou 3 e comitam, uma fonte por vez, com o relatório da rodada em `saidas/`.
2. **Mensalmente**, `paises.yml` lê as fontes globais da função 1 e abre um **PR**
   com o que mudou em `paises.json`. O PR é a revisão.
3. **O que pede juízo** sai no relatório e, para tribunais, é lido toda semana: o ato
   que muda status entra por commit humano, com `conferido_por: humano`.
4. **Trimestralmente**, `auditoria.yml` sorteia a amostra e abre o PR com a planilha;
   a taxa de erro vai para `docs/auditoria.md` e para a página do projeto.

> Em resumo: **a máquina coleta e propõe; gente decide status, promoção e correção.**

## Passos de uma atualização de dado (PR)

1. Edite **apenas** `data/`.
2. Regenere o derivado: `python scripts/transformar.py --estrito` (no Windows, abra o
   PowerShell na pasta do projeto; o aviso "a execução de scripts foi desabilitada"
   diz respeito a `.ps1`, não a Python, e pode ser ignorado).
3. Rode a bateria de `AGENTS.md`.
4. Abra o PR dizendo **o que** mudou, **por que** e **qual fonte** sustenta. Mudança de
   status de situação cita o ato (`decisoes.id`).

## Convenções do catálogo (impostas pela CI onde marcado)

### C1. Todo campo afirmado tem carimbo ⛔ imposta

`valor` não nulo exige `url`, `fonte` (existente em `fontes.json` e `ativa`),
`lido_em`, `confianca` e `conferido_por`. Sem isso, `--estrito` reprova. A carga inicial
usa `--rascunho`, e o relatório conta os rascunhos.

### C2. Status sem órgão não é status ⛔ imposta

Cada item de `situacoes.status` tem `codigo`, `por`, `data`, `url`, `confianca`.
`decisao_merito` exige `resultado`. `medida_provisoria` e `decisao_merito` exigem
`conferido_por: humano`.

### C3. `id` é append-only ⛔ imposta

Nunca reatribuído. País que deixa de existir ganha `vigencia_ate`; documento que sai
vai para `ids-aposentados.json`.

### C4. Um ato por registro

A chave de decisão é `tribunal + caso + data + tipo_ato`. Dois atos no mesmo dia são
dois registros. Um caso não é registro.

### C5. Vocabulário fechado ⛔ imposta

Toda enumeração tem lista em `scripts/vocabularios.py`. Valor novo entra por PR que
muda a lista e o `03-modelo-de-dados.md` juntos.

### C6. Texto nosso tem autor; texto de terceiro não existe aqui

`descricao`, `resumo` e `titulo_pt` têm `autor` (`humano` ou `modelo:<id>`), até 600
caracteres. Nenhum campo guarda corpo de notícia ou de decisão.

### C7. Língua original sempre

`lingua` (ISO 639-1) em todo documento; `linguas` em todo ato. Sem língua, não entra.

### C8. Fonte vencida não alimenta rodada ⛔ imposta

`fontes.json` guarda `robots_verificado_em`; o robô recusa fonte sem verificação nos
últimos 180 dias, e o Arquivista abre issue antes do vencimento.

### C9. Nome de pessoa só como o tribunal escreve

Em `decisoes.json`, no nome do caso ou do ato. Em nenhum outro lugar. Pedido de
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
pip install -e ".[dev]"            # instala o motor do Alétheia fixado e as ferramentas
python scripts/transformar.py --estrito
python -m pytest
aletheia validar-lexico data/lexico/pt.json
```

Exige Python 3.11+. Sem dependências de execução além do motor.
