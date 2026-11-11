# 06 — Roteiro

Unidade de esforço: a **sessão**, um bloco de 2 a 4 horas de trabalho com um agente de
código, do começo ao fim, com `CHANGELOG.md` e bateria verde (como no AtlasPen, "uma
sessão = uma release"). As estimativas são em sessões e em semanas de calendário com
duas sessões por semana; ambas são chutes declarados, a corrigir ao fim de cada fase.

## O menor Astraea útil (MVP)

O MVP é o que está **pronto ao fim da fase 4**:

- **Leis penais do mundo:** 197 registros com `genocide_convention` e `rome_statute`
  preenchidos pelo robô e carimbados; `death_penalty` proposto pelo robô e confirmado;
  `penal_code` e `domestic_genocide` preenchidos à mão só para os países das dez
  situações iniciais (~25 países); os demais vazios com motivo e contados na tela.
- **Decisões:** todos os atos da CIJ e do TPI sobre genocídio desde 01/01/2019, mais a
  carga histórica das dez situações, com status na taxonomia e URL oficial; RSS de TPI,
  IRMCT, KSC, RSCSL, Corte Africana, TRIAL, HUDOC e páginas de mandato da OHCHR rodando
  toda semana.
- **Notícias:** GDELT (termo + tema, 5 línguas), ReliefWeb e ~15 *feeds* rodando toda
  semana há quatro semanas sem intervenção; nível 3 na tela; contagem por língua e por
  nível publicada; taxa de falso positivo da primeira amostra publicada.
- **Site:** página inicial e três telas estáticas em `en` e `pt-BR`, dados abertos em
  `static/data/` com rótulos nas duas línguas, `CITATION.cff`, página de fontes com
  confiança e termos.
- **Um registro promovido de ponta a ponta** (Gâmbia v. Mianmar é o candidato natural:
  sentença de mérito marcada para 19/11/2026).

O que o MVP **não** tem: os 197 países com código penal conferido; léxicos além das
cinco línguas; telas e rótulos além de `en` e `pt-BR`; Media Cloud e GKG; mapa; Astro;
dossiê-filho; motor comum a outros projetos.

## Fases

### Fase 0 — Plano (feita em 06/11/2026)

`docs/00` a `docs/07`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`. **Pronto quando:**
você respondeu às decisões de `07-decisoes-pendentes.md` que afetam a fase 1 (D1, D2,
D3, D7, D8) e o plano foi ajustado. **Feito em 09/11/2026**: D1, D3 e D7 aceitas como
recomendadas; D2 virou motor próprio a partir do Alétheia; D8 virou dados e código em
inglês, com telas em `en` e `pt-BR`.

### Fase 1 — Esqueleto (4 sessões, ~2 semanas)

1. **Motor** (1 sessão): cópia literal dos módulos do Alétheia em `astraea/engine/`,
   testes copiados verdes, depois a tradução para inglês em commit separado, com
   testes verdes de novo (passo a passo em `04-arquitetura.md`, "Onde o motor vive").
   **Feito em 09/11/2026**: 105 testes verdes no Python 3.14, `ruff` limpo, comando
   `astraea` instalado; `pyproject.toml`, `NOTICE` e `LICENSE-aletheia.txt` já
   existem (sobra do item 2: `LICENSE`, `LICENSE-CC-BY-4.0`, `CITATION.cff`, `MITO.md`).
2. Licenças (`LICENSE` Apache-2.0, `LICENSE-CC-BY-4.0`, `LICENSE-aletheia.txt` MIT,
   `NOTICE` com o `sha` de origem do motor), `CITATION.cff`, `CHANGELOG.md`, `MITO.md`,
   `.gitignore`, `pyproject.toml` sem dependências de execução e com `pytest`/`ruff`
   em dev. **Feito em 09/11/2026** (sessão 2), com `LICENSE-unicode.txt` a mais, pelo
   CLDR.
3. `data/` com `countries.json` (197 registros só com `id`, `name` em `en` e `pt-BR` e
   `un_status`, lidos de uma lista ISO em domínio público e conferidos contra a lista
   de membros da ONU), `situations.json` (as dez de D6, com `terms` em cinco línguas),
   `sources.json` (todas as fontes de `02-fontes.md` com `state`), `lexicon/` gerado,
   `retired-ids.json`, `i18n/en.json` e `i18n/pt-BR.json` com o rótulo de cada campo e
   de cada valor. **Feito em 09/11/2026** (sessão 2), menos `situations.json` e
   `lexicon/`, que ficam para a sessão 3: `countries.json` com 197 registros (códigos e
   nomes do Unicode CLDR 49, conferidos contra a lista da ONU), `sources.json` com 87
   entradas, `retired-ids.json` vazio, rótulos nas duas línguas e
   `scripts/vocabularies.py` como lista única dos vocabulários. **Completado em
   10/11/2026** (sessão 3): `situations.json` com as dez situações (nove status em
   cinco delas, todos à espera do carimbo de pessoa; cinco ainda sem status),
   `verification.json`, os termos fixos em `lexicon/fixed/` e o léxico gerado nas
   cinco línguas (o árabe em rascunho, sem falante).
4. `scripts/transform.py --strict | --draft` com as onze travas de
   `03-modelo-de-dados.md`; `scripts/build_lexicon.py`; `scripts/build_site.py`;
   `ci.yml`; `deploy.yml` com uma página inicial mínima em `/en/` e `/pt-br/` lendo
   `quality.json`. **Feito em 10/11/2026** (sessão 3): `transform.py`,
   `build_lexicon.py` e `static/data/` gerado. **Completado em 10/11/2026** (sessão 4):
   `build_site.py` (página inicial em `/en/` e `/pt-br/`, saída em `_site/`), `ci.yml`
   e `deploy.yml`. Enquanto houver rascunho, a CI valida com `--draft` e compara o
   derivado com `--draft --check`; `--strict` roda como passo informativo e volta a ser
   a régua quando os status tiverem carimbo de pessoa (regra no `AGENTS.md`).
5. Política de robô em código: `User-Agent` próprio, `Crawl-delay`, lista de domínios
   com `no_text_by_policy`. **Feito em 10/11/2026** (sessão 4): o cliente HTTP guarda o
   `Crawl-delay` de cada host; a rodada lê de `data/sources.json` os domínios com
   `no_text_by_policy` e, neles, tria só pelo título e pela descrição da listagem, com
   nível máximo 2 (`astraea/engine/policy.py`).

**Pronto quando:** `ci.yml` verde; o site publica a página inicial nas duas línguas
com "197 países, 0 conferidos" / "197 countries, 0 checked"; `transform --strict`
reprova um registro de exemplo sem carimbo e `--draft` o aceita; a trava 11 reprova
um valor sem rótulo em `pt-BR`.

### Fase 2 — Função 1 automática (3 sessões, ~2 semanas)

1. **Tabelião:** adaptador `listing` sobre o XML da UNTC (IV.1 e XVIII.10): decodificar
   ISO-8859-1, limpar `<superscript>`, mapear nome → ISO (tabela de exceções à mão),
   extrair assinatura, vinculação, tipo, reservas, objeções, retiradas; sentinela =
   "STATUS AS AT". Fixture com o XML de 06/11/2026. Grava com `checked_by: robot`.
   **Feito em 10/11/2026** (fase 2, sessão 1), com duas correções: a sentinela é o bloco
   `Status` do XML (o "STATUS AS AT" é da página HTML e só marca a hora de geração), e as
   *fixtures* são os XML de 10/11/2026 sem a prosa do depositário (regra 2).
2. **Pena de morte:** adaptador `listing` sobre o espelho do Cornell; carga do anexo da
   Anistia 2024 à mão (status por país, com citação).
   **Feito em 10/11/2026** (fase 2, sessão 2), a parte do robô: formato
   `cornell_dpw_status` e `scripts/load_death_penalty.py`, com 130 países carimbados e 67
   vazios com `reason`. Duas correções: a tabela não está no HTML do espelho, e sim numa
   base em outro servidor, que a legenda do mapa consulta (`02-fontes.md`, 1.5); e só três
   das quatro categorias do Cornell correspondem às da Anistia, então os 45 países *de
   facto* esperam o anexo (`03-modelo-de-dados.md`). A carga do anexo da Anistia é do
   dono, à mão; o caminho está no `03` e **ainda não foi feita**.
3. `countries.yml` mensal abrindo PR; tela `/countries` com tabela, filtros, completude e
   ficha com proveniência.
   **Feito em 10/11/2026** (fase 2, sessão 3), com três escolhas registradas no `04`: o
   Cornell entra no mesmo *workflow* mensal, e não num semanal próprio; os filtros são
   CSS, sem JavaScript; o mapa coroplético fica fora até a D13. **Rodou no GitHub em
   10/11/2026**: o PR #1 ("sem novidade", commit vazio do robô) foi aceito pelo dono.
4. Carga humana dos ~25 países das situações iniciais: `penal_code`,
   `domestic_genocide`, `max_penalty`, começando pelo Brasil (lido do AtlasPen).
   **Começada em 10/11/2026** (fase 2, sessão 4). Lista aprovada pelo dono, 24 países, nesta
   ordem: Brasil; os 8 da prioridade do `quality.json` (Mianmar, Palestina, Israel,
   Ucrânia, Rússia, Sudão, Bósnia, Sérvia); os outros 7 com elo em `situations.json`
   (Gâmbia, África do Sul, Etiópia, China, Iraque, Ruanda, Camboja); e 8 de foro ou base
   de jurisdição, sem elo (Alemanha, França, Bélgica, Países Baixos, Argentina,
   Bangladesh, Tanzânia, Síria). Brasil, Alemanha, Argentina, Bangladesh e Rússia têm os
   três blocos em rascunho, e a África do Sul dois; os outros 18 estão vazios com `reason`
   (`02-fontes.md`, 1.6). O carimbo é do dono, por `scripts/stamp.py`.
   **Continuada em 11/11/2026** (fase 2, sessão 5): segunda tentativa nos 18 vazios. Sudão,
   Ruanda e Bósnia ganharam os três blocos em rascunho, e a Gâmbia o `penal_code` (a lei
   lida não tem o crime); a Alemanha ganhou o `enacted_year`. Os 14 restantes têm o motivo
   de 11/11 (`02-fontes.md`, 1.7); dois deles, Países Baixos e Bélgica, esperam a leitura
   do dono, porque o `robots.txt` veda a leitura por modelo ou por robô. O que falta são
   portais que não respondem, que vedam robôs ou que desafiam o cliente: a próxima sessão
   só avança com outra rede, com leitura do dono ou com fonte oficial nova.
   **Terceira volta em 11/11/2026** (fase 2, sessão 6): fonte oficial nova para os 14
   vazios. A Bélgica ganhou os três blocos em rascunho (o novo Código Penal, pelo texto que
   a Câmara aprovou), e os Países Baixos o `domestic_genocide` e o `max_penalty` (a Wet
   internationale misdrijven, pelo Diário Oficial, que não veda agentes de IA). Os outros
   têm o motivo renovado (`02-fontes.md`, 1.8). Nos já lidos, a sessão conferiu as
   alterações posteriores: nenhum valor mudou.
   **Quarta volta em 11/11/2026** (fase 2, sessão 7): a China ganhou o `penal_code` em
   rascunho (a Lei Penal no Boletim do Comitê Permanente da APN, texto de 2020), sem o crime
   de genocídio (`domestic_genocide` vazio com `reason`, como na Gâmbia). Ucrânia, Mianmar e
   Camboja, mais uma tentativa, sem leitura; a França espera a decisão do dono sobre a LEGI.
   Nos já lidos, nenhuma fonte oficial nova sobre Ruanda, Sudão ou Gâmbia
   (`02-fontes.md`, 1.9).
   **Quinta volta em 11/11/2026** (fase 2, sessão 8): sem resposta do dono às escolhas,
   nem carimbo, nem leitura holandesa, nem sim à LEGI. Na China, a Emenda XII (29/12/2023)
   foi lida no Boletim da APN e não traz o crime; os Boletins seguintes não trazem emenda
   nova. Sérvia, Iraque e Tanzânia tiveram portal oficial novo, sem leitura; os outros
   vazios, nenhum (`02-fontes.md`, 1.10). Continuam treze países com leitura e onze vazios.

**Pronto quando:** 197 registros com tratados carimbados; o PR mensal roda e mostra
diff vazio ou legível; a ficha do Brasil está completa e conferida; a primeira
reconferência de Legislationline e SHERLOC está agendada no Arquivista.
**Em 11/11/2026** (fase 2, sessão 8) a reconferência ficou com o Cartógrafo, como o `04`
já previa, e não com o Arquivista: `scripts/recheck_sources.py`, mensal, dentro do
`countries.yml` (a primeira vez no dia 1 de dezembro, se a `main` com ele estiver no
GitHub até lá), para Legislationline, SHERLOC,
Library of Congress e WorldLII. O que falta do "Pronto quando" é do dono: o carimbo da
ficha do Brasil.

### Fase 3 — Função 3 (4 sessões, ~3 semanas)

1. Adaptador `rss` do motor (vindo do Alétheia) configurado para TPI (registros e notícias), IRMCT,
   KSC, RSCSL, Corte Africana, TRIAL, HUDOC (*press releases*); filtro por léxico de
   situação; tratamento de gzip sem cabeçalho.
2. Adaptador `icj`: `listing` sobre a página de cada caso pendente e sobre a lista de
   *press releases*; o PDF fica como URL com `text_hash: null` e motivo.
3. Adaptador `ohchr`: `listing` sobre as páginas de mandato das comissões de inquérito.
4. Carga histórica à mão: atos de 2019–2026 da CIJ (178, 182, 192, 193, 197, 202) e
   do TPI (Darfur); sentenças de mérito históricas das dez situações (TPIR Akayesu,
   TPII Krstić, CIJ Bósnia e Croácia, ECCC caso 002/02); Corte IDH e CIDH por `listing`
   curada quando houver ato pertinente.
5. `courts.yml` semanal; tela `/decisions` e `/situations/<id>` com a linha do tempo e
   o rótulo com órgão.

**Pronto quando:** a rodada semanal roda três semanas seguidas; a sentença da CIJ de
19/11/2026 (Gâmbia v. Mianmar) entra pelo fluxo (pede-juízo → status `merits_decision`
com `outcome` → tela) e serve de prova da promoção; nenhum status sem órgão passa no
validador.

### Fase 4 — Função 2 (4 sessões + 4 semanas de calibração)

1. `config/news.json`: GDELT por língua (`sourcelang:` × termos do léxico) e por
   tema (`WB_2509_GENOCIDE`), com `rate_limit_per_minute: 12`; *feeds* da lista da fase 1 de
   `02-fontes.md`; ReliefWeb (depois do `appname`).
2. Adaptador `reliefweb`; ajuste do adaptador GDELT para não cortar em 90 dias quando a
   resposta tiver dado; `timelinevol` no Recenseador.
3. Léxicos en, fr, es, pt, ar com `contexto` jurídico por língua, revisados por falante
   quando houver.
4. `news.yml` **diário durante 4 semanas**, lendo o relatório a cada 2–3 dias e
   ajustando exclusões; depois semanal.
5. Tela `/news` (90 dias, filtros, gráfico por língua e semana).

**Pronto quando:** quatro semanas seguidas sem intervenção; a amostra de 60 itens
(20 de nível 3, 20 de nível 2, 20 de nível 1) foi lida e a taxa de falso positivo do
nível 3 está abaixo de 20% (limiar inicial, declarado) e a de falso negativo do nível 1
está registrada; o Recenseador não acusa truncamento em mais de 10% dos dias-língua.

### Fase 5 — Fechamento do MVP (2 sessões)

1. Página inicial com contadores e situações; `/about` com metodologia, fontes,
   robôs, dados abertos, pessoas, como citar.
2. `AUDITORIA.md` do Astraea (protocolo pré-registrado, adaptado do AtlasPen: estratos
   por fonte e nível, semente = hash do commit), `audit.yml`, primeira amostra.
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
| 10 | primeiro dossiê-filho (`astraea-<situation>`, modelo Alétheia com Wayback) | registro em `detailed` |
| 11 | motor comum extraído do motor do Astraea, se outro projeto (Argos, Alétheia) quiser adotá-lo | pedido de um segundo consumidor |
| 12 | separação `astraea-dados` | árvore > 500 MB ou > 1 commit de robô/dia |
| 13 | Astro no site; mapa (D13) | telas pedindo componentes compartilhados |
| 14 | **várias línguas**: telas, rótulos e dicionário de dados abertos em espanhol, francês e árabe (com leitura da direita para a esquerda), depois chinês e russo, completando as seis oficiais da ONU mais o português | fim da fase 5; é a primeira depois do MVP, junto com a 6 |

**Fase 14 em detalhe.** Um *locale* novo entra de uma vez, por sessão própria, e só vai
ao ar quando estiver completo: `data/i18n/<locale>.json` com todos os campos e valores
(a trava 11 passa a valer para ele), `site/i18n/<locale>.json` com a interface inteira,
o nome de cada país e de cada situação, e o dicionário de dados abertos gerado. Os
textos nossos (descrições e resumos) não precisam estar completos: a tela mostra a
versão que existe, marcada com a língua, e `quality.json` conta o que falta. Quem
traduz é uma pessoa, ou um modelo de linguagem com revisão humana, conforme a D4. A
ordem pode mudar por decisão registrada, por exemplo se um leitor de uma língua se
oferecer para revisar. Estimativa: 1 sessão por *locale* para rótulos e interface,
mais a revisão por falante.

## Esforço total até o MVP

| Fase | Sessões | Semanas | Leitura humana acumulada |
|---|---|---|---|
| 1 | 4 | 2 | — |
| 2 | 3 | 2 | ~25 países |
| 3 | 4 | 3 | ~60 atos históricos |
| 4 | 4 (+ calibração) | 6 | 60 itens de amostra |
| 5 | 2 | 1 | 1 auditoria |
| **Total** | **17** | **~14 semanas** | |

A sessão a mais da fase 1 é a importação do motor. As duas línguas da tela não têm
sessão própria: cada tela nasce com os seus rótulos em `en` e `pt-BR`, e isso pesa um
pouco em cada sessão das fases 2 a 5 (chute: 10 a 15% a mais).

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

Isso instala o próprio Astraea, com o motor que já vem dentro dele, e baixa as
ferramentas de teste (`pytest`, `ruff`). Demora um minuto.

### Rodar a bateria (toda sessão)

```powershell
python scripts\transform.py --draft
python -m pytest
```

Durante a carga inicial o modo é `--draft`: ele aceita o campo ainda sem carimbo e
diz quantos são ("9 fields in draft, in 5 records"). `python scripts\transform.py
--strict` mostra a lista do que falta carimbar e termina com "strict: FAILED"; isso
é esperado até os status das situações serem conferidos por você.

Os *scripts* do projeto **nunca apagam** e, quando alteram arquivo, rodam em
simulação por padrão: `python scripts\transform.py --draft` mostra o que faria;
`python scripts\transform.py --draft --execute` grava. O mesmo vale para
`python scripts\build_lexicon.py`, que refaz o léxico depois de uma mudança nos
termos. Os comandos e as opções são em inglês
(`--strict`, `--draft`, `--execute`); as mensagens que eles mostram também, e o
`CHANGELOG.md` de cada sessão explica em português o que cada uma quer dizer. A CI roda sempre com `--execute`
num diretório temporário e compara.

### Configurar o GitHub (uma vez, na interface do site)

1. **Settings → Pages → Build and deployment → Source:** *GitHub Actions*.
2. **Settings → Actions → General → Workflow permissions:** *Read and write
   permissions*, e marque *Allow GitHub Actions to create and approve pull requests*
   (o `countries.yml` abre PR).
3. **Settings → Secrets and variables → Actions:** nenhum segredo na fase 1. Na fase
   4, `RELIEFWEB_APPNAME` (o nome aprovado no formulário do ReliefWeb) e, se usar,
   `MEDIACLOUD_API_KEY`. O cliente HTTP redige os dois de qualquer log.
4. **Actions → *Notícias* → Run workflow** para a primeira rodada à mão, com `source`
   preenchida (uma fonte pequena primeiro, como no `docs/operacao.md` do Alétheia).

### O que você NÃO precisa fazer

Instalar Node, Astro ou qualquer banco; ter servidor; pagar por API; rodar nada na
sua máquina depois da fase 1 (o GitHub Actions roda tudo). O *push* para o GitHub
continua sendo decisão sua, pedida explicitamente em cada sessão.
