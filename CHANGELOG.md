# Changelog

Uma sessão = uma entrada. Datas no fuso de Brasília. Até a v1.0.0 a versão é `0.0.x`
(ver `CONTRIBUTING.md`, "Versão e notas").

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
