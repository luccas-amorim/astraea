# 06 — Roteiro

Unidade de esforço: a **sessão**, um bloco de 2 a 4 horas de trabalho com um agente de
código, do começo ao fim, com `CHANGELOG.md` e bateria verde (como no AtlasPen, "uma
sessão = uma release"). As estimativas são em sessões e em semanas de calendário com
duas sessões por semana; ambas são chutes declarados, a corrigir ao fim de cada fase.

## O menor Astraea útil (MVP)

O MVP é o que está **pronto ao fim da fase 4**:

- **Leis penais do mundo:** 197 registros com `convencao_1948` e `estatuto_roma`
  preenchidos pelo robô e carimbados; `pena_de_morte` proposto pelo robô e confirmado;
  `codigo_penal` e `genocidio_interno` preenchidos à mão só para os países das dez
  situações iniciais (~25 países); os demais vazios com motivo e contados na tela.
- **Decisões:** todos os atos da CIJ e do TPI sobre genocídio desde 01/01/2019, mais a
  carga histórica das dez situações, com status na taxonomia e URL oficial; RSS de TPI,
  IRMCT, KSC, RSCSL, Corte Africana, TRIAL, HUDOC e páginas de mandato da OHCHR rodando
  toda semana.
- **Notícias:** GDELT (termo + tema, 5 línguas), ReliefWeb e ~15 *feeds* rodando toda
  semana há quatro semanas sem intervenção; nível 3 na tela; contagem por língua e por
  nível publicada; taxa de falso positivo da primeira amostra publicada.
- **Site:** página inicial e três telas estáticas, dados abertos em `static/data/`,
  `CITATION.cff`, página de fontes com confiança e termos.
- **Um registro promovido de ponta a ponta** (Gâmbia v. Mianmar é o candidato natural:
  sentença de mérito marcada para 19/11/2026).

O que o MVP **não** tem: os 197 países com código penal conferido; léxicos além das
cinco línguas; Media Cloud e GKG; mapa; Astro; dossiê-filho; `argos-core`.

## Fases

### Fase 0 — Plano (feita em 06/11/2026)

`docs/00` a `docs/07`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`. **Pronto quando:**
você respondeu às decisões de `07-decisoes-pendentes.md` que afetam a fase 1 (D1, D2,
D3, D7, D8) e o plano foi ajustado.

### Fase 1 — Esqueleto (3 sessões, ~2 semanas)

1. Licenças (`LICENSE` Apache-2.0, `LICENSE-CC-BY-4.0`, `NOTICE`), `CITATION.cff`,
   `CHANGELOG.md`, `MITO.md`, `.gitignore`, `pyproject.toml` com o Alétheia fixado por
   `sha` e `pytest`/`ruff` em dev.
2. `data/` com `paises.json` (197 registros só com `id`, nomes e `estatuto_onu`, lidos
   de uma lista ISO em domínio público e conferidos contra a lista de membros da ONU),
   `situacoes.json` (as dez de D6, com `termos` em cinco línguas), `fontes.json` (todas
   as fontes de `02-fontes.md` com `estado`), `lexico/` gerado, `ids-aposentados.json`.
3. `scripts/transformar.py --estrito | --rascunho` com as dez travas de
   `03-modelo-de-dados.md`; `scripts/gerar_lexico.py`; `ci.yml`; `deploy.yml` com uma
   página inicial mínima lendo `qualidade.json`.
4. Política de robô em código: `User-Agent` próprio, `Crawl-delay`, lista de domínios
   com `sem_texto_por_politica`.

**Pronto quando:** `ci.yml` verde; o site publica a página inicial com "197 países, 0
conferidos"; `transformar --estrito` reprova um registro de exemplo sem carimbo e
`--rascunho` o aceita.

### Fase 2 — Função 1 automática (3 sessões, ~2 semanas)

1. **Tabelião:** adaptador `lista` sobre o XML da UNTC (IV.1 e XVIII.10): decodificar
   ISO-8859-1, limpar `<superscript>`, mapear nome → ISO (tabela de exceções à mão),
   extrair assinatura, vinculação, tipo, reservas, objeções, retiradas; sentinela =
   "STATUS AS AT". Fixture com o XML de 06/11/2026. Grava com `conferido_por: robo`.
2. **Pena de morte:** adaptador `lista` sobre o espelho do Cornell; carga do anexo da
   Anistia 2024 à mão (status por país, com citação).
3. `paises.yml` mensal abrindo PR; tela `/paises` com tabela, filtros, completude e
   ficha com proveniência.
4. Carga humana dos ~25 países das situações iniciais: `codigo_penal`,
   `genocidio_interno`, `pena_maxima`, começando pelo Brasil (lido do AtlasPen).

**Pronto quando:** 197 registros com tratados carimbados; o PR mensal roda e mostra
diff vazio ou legível; a ficha do Brasil está completa e conferida; a primeira
reconferência de Legislationline e SHERLOC está agendada no Arquivista.

### Fase 3 — Função 3 (4 sessões, ~3 semanas)

1. Adaptador `rss` do Alétheia configurado para TPI (registros e notícias), IRMCT,
   KSC, RSCSL, Corte Africana, TRIAL, HUDOC (*press releases*); filtro por léxico de
   situação; tratamento de gzip sem cabeçalho.
2. Adaptador `cij`: `lista` sobre a página de cada caso pendente e sobre a lista de
   *press releases*; o PDF fica como URL com `hash_texto: null` e motivo.
3. Adaptador `ohchr`: `lista` sobre as páginas de mandato das comissões de inquérito.
4. Carga histórica à mão: atos de 2019–2026 da CIJ (178, 182, 192, 193, 197, 202) e
   do TPI (Darfur); sentenças de mérito históricas das dez situações (TPIR Akayesu,
   TPII Krstić, CIJ Bósnia e Croácia, ECCC caso 002/02); Corte IDH e CIDH por `lista`
   curada quando houver ato pertinente.
5. `tribunais.yml` semanal; tela `/decisoes` e `/situacoes/<id>` com a linha do tempo e
   o rótulo com órgão.

**Pronto quando:** a rodada semanal roda três semanas seguidas; a sentença da CIJ de
19/11/2026 (Gâmbia v. Mianmar) entra pelo fluxo (pede-juízo → status `decisao_merito`
com `resultado` → tela) e serve de prova da promoção; nenhum status sem órgão passa no
validador.

### Fase 4 — Função 2 (4 sessões + 4 semanas de calibração)

1. `config/noticias.json`: GDELT por língua (`sourcelang:` × termos do léxico) e por
   tema (`WB_2509_GENOCIDE`), com `limite_por_minuto: 12`; *feeds* da lista da fase 1 de
   `02-fontes.md`; ReliefWeb (depois do `appname`).
2. Adaptador `reliefweb`; ajuste do adaptador GDELT para não cortar em 90 dias quando a
   resposta tiver dado; `timelinevol` no Recenseador.
3. Léxicos en, fr, es, pt, ar com `contexto` jurídico por língua, revisados por falante
   quando houver.
4. `noticias.yml` **diário durante 4 semanas**, lendo o relatório a cada 2–3 dias e
   ajustando exclusões; depois semanal.
5. Tela `/noticias` (90 dias, filtros, gráfico por língua e semana).

**Pronto quando:** quatro semanas seguidas sem intervenção; a amostra de 60 itens
(20 de nível 3, 20 de nível 2, 20 de nível 1) foi lida e a taxa de falso positivo do
nível 3 está abaixo de 20% (limiar inicial, declarado) e a de falso negativo do nível 1
está registrada; o Recenseador não acusa truncamento em mais de 10% dos dias-língua.

### Fase 5 — Fechamento do MVP (2 sessões)

1. Página inicial com contadores e situações; `/projeto` com metodologia, fontes,
   robôs, dados abertos, pessoas, como citar.
2. `AUDITORIA.md` do Astraea (protocolo pré-registrado, adaptado do AtlasPen: estratos
   por fonte e nível, semente = hash do commit), `auditoria.yml`, primeira amostra.
3. Versão `0.1.0`, release no GitHub e DOI no Zenodo.

**Pronto quando:** os quatro critérios de sucesso de `01-visao-e-escopo.md` estão
cumpridos e a taxa da primeira auditoria está publicada.

### Fases seguintes (sem prazo; uma por vez, por decisão registrada)

| Fase | O que | Gatilho |
|---|---|---|
| 6 | carga humana dos países restantes, 10–20 por sessão, na ordem: partes na Convenção com reserva ao art. IX → partes no Estatuto → demais | sempre; é o trabalho de fundo |
| 7 | Media Cloud como 2.º canal e estimativa de cobertura por língua | fim da fase 4 |
| 8 | GKG de 15 min | Recenseador acusando truncamento |
| 9 | léxicos nas línguas das situações (birmanês, tigrínia, amárico, uigur, ucraniano, russo) | contagem de nível 1 por língua |
| 10 | primeiro dossiê-filho (`astraea-<situacao>`, modelo Alétheia com Wayback) | registro em `detalhado` |
| 11 | `argos-core` extraído; Argos, Alétheia e Astraea dependem dele | 3.º adaptador genérico provado |
| 12 | separação `astraea-dados` | árvore > 500 MB ou > 1 commit de robô/dia |
| 13 | Astro no site; mapa (D13) | telas pedindo componentes compartilhados |

## Esforço total até o MVP

| Fase | Sessões | Semanas | Leitura humana acumulada |
|---|---|---|---|
| 1 | 3 | 2 | — |
| 2 | 3 | 2 | ~25 países |
| 3 | 4 | 3 | ~60 atos históricos |
| 4 | 4 (+ calibração) | 6 | 60 itens de amostra |
| 5 | 2 | 1 | 1 auditoria |
| **Total** | **16** | **~14 semanas** | |

Com duas sessões por semana, o MVP sai em pouco mais de três meses; com uma, em seis.
Depois do MVP, o regime é de 2 a 4 horas por semana (nível 2 de tribunais, amostra de
notícias, PR mensal de países) mais as sessões de carga de países que você quiser.

## O que você precisa fazer, passo a passo (Windows)

Tudo abaixo é para a **fase 1**; as fases seguintes trazem o seu próprio passo a
passo no `CHANGELOG.md` da sessão. Nenhum passo apaga nada.

### Preparar a máquina (uma vez)

1. **Instalar o Git for Windows** (https://git-scm.com/download/win). No instalador,
   aceite os padrões. O Windows pode mostrar "Deseja permitir que este aplicativo faça
   alterações no seu dispositivo?": é o instalador pedindo permissão de administrador;
   responda **Sim**.
2. **Instalar o Python 3.12** (https://www.python.org/downloads/windows/). Na primeira
   tela do instalador, **marque "Add python.exe to PATH"** antes de clicar em
   *Install Now*. Sem isso o PowerShell não acha o `python`.
3. **Abrir o PowerShell**: menu Iniciar → digite `PowerShell` → *Windows PowerShell*.
   Não precisa ser "como administrador".
4. Conferir:

   ```powershell
   git --version
   python --version
   ```

   Se o segundo responder "python não é reconhecido", feche e reabra o PowerShell
   (o PATH só vale em janela nova). Se ainda assim falhar, reinstale marcando o PATH.

### Clonar o repositório (uma vez)

```powershell
cd $HOME\Documents
git clone https://github.com/luccas-amorim/astraea.git
cd astraea
```

O Git pode abrir uma janela "Connect to GitHub" pedindo *login*: é o *Git Credential
Manager*; entre com a sua conta. Nada é enviado ao GitHub até você dar `git push`.

### Criar o ambiente Python (uma vez)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Aviso esperado:** "a execução de scripts foi desabilitada neste sistema" (erro
`PSSecurityException`). É a política padrão do PowerShell, que bloqueia qualquer
*script* `.ps1`, inclusive o de ativação. Para liberar **só para o seu usuário**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Responda `S` (Sim). Depois repita `.venv\Scripts\Activate.ps1`. O *prompt* passa a
começar com `(.venv)`. Esse comando libera *scripts* locais e assinados; não desliga
nenhuma proteção do Windows além dessa política de *scripts* do PowerShell.

```powershell
pip install -e ".[dev]"
```

Isso baixa o motor do Alétheia (do GitHub, no `sha` fixado) e as ferramentas de
teste. Demora um minuto.

### Rodar a bateria (toda sessão)

```powershell
python scripts\transformar.py --estrito
python -m pytest
```

Os *scripts* do projeto **nunca apagam** e, quando alteram arquivo, rodam em
simulação por padrão: `python scripts\transformar.py` mostra o que faria;
`python scripts\transformar.py --executar` grava. A CI roda sempre com `--executar`
num diretório temporário e compara.

### Configurar o GitHub (uma vez, na interface do site)

1. **Settings → Pages → Build and deployment → Source:** *GitHub Actions*.
2. **Settings → Actions → General → Workflow permissions:** *Read and write
   permissions*, e marque *Allow GitHub Actions to create and approve pull requests*
   (o `paises.yml` abre PR).
3. **Settings → Secrets and variables → Actions:** nenhum segredo na fase 1. Na fase
   4, `RELIEFWEB_APPNAME` (o nome aprovado no formulário do ReliefWeb) e, se usar,
   `MEDIACLOUD_API_KEY`. O cliente HTTP redige os dois de qualquer log.
4. **Actions → *Notícias* → Run workflow** para a primeira rodada à mão, com `fonte`
   preenchida (uma fonte pequena primeiro, como no `docs/operacao.md` do Alétheia).

### O que você NÃO precisa fazer

Instalar Node, Astro ou qualquer banco; ter servidor; pagar por API; rodar nada na
sua máquina depois da fase 1 (o GitHub Actions roda tudo). O *push* para o GitHub
continua sendo decisão sua, pedida explicitamente em cada sessão.
