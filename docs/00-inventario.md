# 00 — Inventário dos ativos existentes (Fase 0)

**Data da leitura:** 06/11/2026.
**Método:** clones rasos (`--depth 1`) de `atlaspen`, `argos` e `aletheia`, lidos arquivo a
arquivo; `ctresb/leis` lido pela API do GitHub, sem clone (8,5 GB no servidor); `astraea`
clonado inteiro. O que não foi lido está dito na seção 7.

| Repositório | Tamanho no GitHub | Último *push* | Licença | Commits |
|---|---|---|---|---|
| `luccas-amorim/atlaspen` | 7,8 MB | 04/11/2026 | Apache-2.0 (código) + CC BY 4.0 (dados) | ativo, PR #101 |
| `luccas-amorim/argos` | 176 KB | 04/10/2026 | MIT | 1 commit (*squash* do PR #3) |
| `luccas-amorim/aletheia` | 555 KB | 03/11/2026 | MIT (código) + CC BY 4.0 (catálogo) | rodadas automáticas |
| `ctresb/leis` | **8,5 GB** | 02/11/2026 | MIT (código); textos de lei sem proteção autoral | 323.849+ (uma norma por commit) |
| `luccas-amorim/astraea` | 8 KB | 06/11/2026 | nenhuma ainda | 1 commit (`start.md`, o enunciado desta tarefa) |

---

## 1. AtlasPen

### 1.1 Arquitetura

- **Site:** Astro 7 + React 19 + TypeScript, publicado no GitHub Pages com domínio
  próprio (`atlaspen.com.br`, `base` `/`). Sem servidor nem banco: o site lê JSON
  derivado em `static/data/`.
- **Separação fonte × derivado:** `data/*.json` é a fonte, editável por PR;
  `static/data/*.json` é gerado por `scripts/transform_data.py` e a CI exige que o
  derivado esteja sincronizado. Regra que "mais quebra em silêncio" segundo o próprio
  README.
- **Robôs:** Python 3 só com biblioteca padrão (não há `requirements.txt` nem
  `pyproject.toml`; os testes usam `pytest`). Vivem em `scripts/robos/`, com um
  núcleo (`nucleo/`: baixar, parsear, dispositivo, fração, vigência, revogação,
  histórico) e uma camada de rede única (`fontes/rede.py`, adaptada do ctresb/leis).
- **Motor de atributos** (`src/lib/atributos/`): funções puras em TypeScript que
  recebem cenário e devolvem cabível / condicional / incabível por instituto; a
  simulação roda o mesmo motor sobre cópia em memória.

### 1.2 Formato dos dados

Catorze arquivos em `data/`, todos JSON legíveis, com `_meta` descritivo quando é
objeto. Os que importam para o Astraea:

| Arquivo | Tamanho | O que é |
|---|---|---|
| `crimes.json` | 872 KB | 1.548 registros, um por tipo penal; campos de vocabulário fechado (`acao`, `elemento`, `hediondo`…), pena em meses, campos de condição (`hediondo_condicao`, `acao_condicao`) em vez de lacuna preenchida |
| `fontes.json` | 24 KB | um diploma por entrada: URL do compilado, URN LexML, **sentinela** (string que prova frescor da página), rótulos |
| `conferencia.json` | 332 KB | trilha de auditoria por registro: data, resultado (`conferido`, `divergente`, `sem_moldura_na_lei`, `dispensado`), dispositivo, URL da fonte |
| `historico-legislativo.json` | 800 KB | vida de cada dispositivo (criação, alteração, revogação, datas) |
| `ids-aposentados.json` | 4 KB | ids que já foram URL pública e nunca voltam |
| `avisos.json` | 8 KB | ADI em curso, tese de repercussão geral, com data da consulta |
| `curadoria.json` | 228 KB | estado do Curador (leis antigas apontadas no ctresb/leis e confirmadas no Planalto) |

Formato exemplar de registro (`crimes.json`, id 1): `lei`, `artigo` com grafia canônica,
`crime`, `pena_min`/`pena_max` em meses, `tipo_pena`, `acao`, `hediondo`, `elemento`,
`tentativa`, `violencia`, `grave_ameaca`, `obs`, `hediondo_condicao`.

### 1.3 Robôs e pipelines

Nove robôs determinísticos, sem IA; nenhum escreve no catálogo (abrem issue, PR ou
relatório). Os que têm algo a ensinar ao Astraea estão marcados.

| Robô | O que faz | Ensina ao Astraea? |
|---|---|---|
| Vigia | moldura de cada registro contra o compilado do Planalto | o padrão *sentinela + snapshot `.part` só promovido quando íntegro* |
| Auditor | hediondez, ação penal, nomes contra regras escritas; derivação só vale com lastro no texto | "fundamento verificado ou zera" |
| Sentinela | Seção 1 do DOU da semana, texto integral, triagem em três níveis | triagem em níveis com descarte nomeado |
| Recenseador | lista de leis do ano × o que o watcher viu: defesa contra o falso negativo | o **censo mensal** contra uma lista oficial |
| Arquivista | documento cuja dependência mudou depois da última releitura | vencimento de prosa |
| Cotejador | segunda fonte (Senado, Câmara, ctresb) só pergunta, nunca escreve | "fonte secundária aponta, não escreve" |
| Relator | precedentes STF/STJ no Banco Nacional de Precedentes do CNJ | — (específico) |
| Curador | leis antigas no ctresb/leis confirmadas no Planalto | consumo do ctresb por API, por caminho |
| Proponente | transforma leitura direta em PR, com nota | "máquina propõe, gente aprova" |

Mecanismos transversais reutilizáveis como **ideia**: `excecoes*.json` (achado julgado,
com motivo e data, casado por tipo + alvo), `cobertura-limites.json` (quantos registros
o conferidor aceita não garantir; crescer é regressão), `conferencia.json --carimbar`.

### 1.4 Agendamentos (GitHub Actions, 8 *workflows*)

| Workflow | Gatilho | Função |
|---|---|---|
| `ci.yml` | PR e push em `main` | transform `--estrito --max-contradicoes=0`, derivado sincronizado, typecheck, knip, `verificar`, `equivalencia`, build, rotas |
| `conferidor.yml` | segunda, 08:00 UTC (05:00 Brasília) + manual | jobs paralelos vigia / sentinela / auditor / arquivista / cotejador, artefatos, issue e PR via GitHub App |
| `fontes.yml` | sábado, 02:00 UTC | ensaio: baixa ~70 compilados e descarta; falhou, abre issue `fontes` |
| `deploy.yml` | push em `main` | build Astro + `upload-pages-artifact` + `deploy-pages` |
| `regen-data.yml` | push em `main` tocando `data/` | regenera derivado e comita de volta com token do App |
| `release.yml` | push em `main` | tag + Release a partir das entradas de changelog (só a partir da v1.0.0) |
| `dependabot.yml` | diário, 13:00 UTC | auto-merge de minor/patch quando a CI passa |
| `branches.yml` | segunda, 09:00 UTC | faxina de branches |

Exige um **GitHub App** próprio (`atlaspen-automacao[bot]`) para abrir PR e comitar na
`main`; sem ele, os robôs degradam para artefato.

### 1.5 Dependências

Node ≥ 22.23, Astro, React, `@astrojs/sitemap`, `remark-directive`, `knip`, TypeScript
6; Python 3 só *stdlib* (+ `pytest` em dev); `pdftotext` do poppler para PDF de lei.
`package-lock.json` tem 230 KB.

### 1.6 Convenções (`CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`)

- `CLAUDE.md` tem uma linha: `@AGENTS.md`. Regra nova entra em `AGENTS.md`, que o Codex
  e outros agentes leem pelo nome.
- **Acuidade jurídica é o valor central**: dado errado publicado é pior que ausente;
  nada entra sem conferência contra o compilado oficial; nunca preencher lacuna com
  plausibilidade; campo condicional em vez de campo vazio.
- **C1–C8** impostas pela CI: um registro = um tipo penal; toda entrada declara sanção;
  `id` append-only (é a URL pública; reiniciar exige remapear tudo); um registro por
  dispositivo; nome é dado; hediondez vem de tabela curada; pena em meses; perdão
  judicial é lista curada.
- **Versão:** SemVer com leitura explícita; `0.0.x` até a v1.0.0; *feed* de notas publica
  só alteração de LEI, não correção de dado; "uma sessão = uma release"; `CITATION.cff`
  cita pela data até a v1.0.0.
- `docs/` é exatamente o que vai ao ar; documento interno fica na raiz (`AUDITORIA.md`,
  `TRIAGEM.md`) ou em `.superpowers/`.
- `Closes #N` obrigatório; branch própria; **não dar push nem abrir PR sem o usuário
  pedir**; cuidado com CRLF no Windows.
- **Auditoria por amostragem** (`AUDITORIA.md`): protocolo pré-registrado, semente =
  hash do commit, estratos, censo onde a população é pequena, taxa com intervalo de
  confiança. É a peça que o Astraea precisa adaptar para "revisão por amostragem".
- Dupla licença: Apache-2.0 para código, CC BY 4.0 para dados e textos; `NOTICE`
  lista o que não está sob nenhuma delas.

### 1.7 Escala: o que não sai do Brasil

O *crawler* do AtlasPen é um leitor do **HTML do Planalto**, e só dele: fatia o HTML cru
porque "a árvore do Word malformado desloca as fronteiras de parágrafo", detecta
codificação por BOM → meta → UTF-8 → cp1252 porque o acervo mistura cp1252 e UTF-16,
reconhece `Art . 190` com espaço, sufixos `359-M-B`, texto citado congelado sob artigo
alterador, e lê a moldura de pena em português ("reclusão, de um a três anos") com
`pena_parser.py`. Cada diploma precisa de uma sentinela escrita à mão em `fontes.json`.

Nada disso generaliza para 193 países: cada portal nacional tem outro HTML, outra
codificação, outra língua e outra sintaxe de pena. **Para o Astraea o *crawler* do
Planalto não serve nem como base**; o que serve é a disciplina em volta dele (sentinela,
`.part`, trilha de conferência, exceções com motivo), que o Argos e o Alétheia já
generalizaram.

---

## 2. ctresb/leis (terceiro)

### 2.1 O que é

Legislação brasileira convertida para Markdown a partir de fontes oficiais
(Planalto, Senado, normas.leg.br, SAPL estaduais, DOU, Câmara), com cabeçalho
estruturado e link para a origem. Base inicial de 323.849 normas (1 CF, 29.184
federais, 294.664 estaduais e distritais), **uma por commit**, assinadas por quem as
promulgou e datadas do dia da aprovação. Pastas: `constituicao.md`, `federal/`,
`estaduais/UF/`, `municipais/`, `reguladores/`, `jurisprudencia/`, `tratados/`
(subpastas `bitributacao`, `direitos-humanos`, `oit`), `scripts/`.

### 2.2 Licença (verificada em 06/11/2026)

O arquivo `LICENSE` é a **MIT** (Copyright 2026 João Davi) seguida de uma nota: os
textos das normas são atos oficiais e, pelo art. 8º, I, da Lei 9.610/98, não são objeto
de proteção autoral; a MIT aplica-se ao código em `scripts/`. O GitHub mostra "Other"
porque o texto da licença tem esse parágrafo acrescentado e o detector não o reconhece.
Consumir os dados é livre; adaptar código exige manter o aviso (o AtlasPen já faz isso
em `scripts/robos/fontes/LICENSE-ctresb-leis.txt`).

### 2.3 Pipelines e agendamento

Não há GitHub Actions (`.github/` só tem `FUNDING.yml`). Os ~40+ scripts em
`scripts/` (`baixar_*.py`, `auditar_*.py`, `agregar_*.py`) rodam na máquina do
mantenedor; o `WORKLOG.md` (272 KB) diz que é operado por agentes de IA. O `README`
registra **crise de armazenamento** em 01/11/2026 (133,8 GB locais, campanha de
apoio via Pix com 7% da meta). Os últimos cinco commits são sobre a campanha, não sobre
dados.

### 2.4 Como o AtlasPen o usa

Pela API do GitHub, por caminho (`fontes/ctresb.py`), sem clone: Cotejador observa o
que mudou e Curador tria leis antigas. Regra fixada em 25/10/2026: **nunca é fonte de
dado nem dependência**; se a leitura falha, o relatório diz que não leu.

### 2.5 Para o Astraea

Só interessa ao registro do Brasil: a Lei 2.889/1956 (genocídio) já está no AtlasPen, e
`tratados/direitos-humanos` pode guardar o Decreto 30.822/1952 (promulgação da
Convenção de 1948). Não há equivalente do ctresb para outros países, e o seu modelo
(um repositório de 8,5 GB, um commit por norma, dependente de uma pessoa e de doações)
é exatamente o que o Astraea **não** deve replicar.

---

## 3. Argos

### 3.1 Arquitetura

Pacote Python 3.11+ só com biblioteca padrão (`argos/`, 2.213 linhas, 12 módulos + 4
adaptadores), instalável com `pip install -e .`, CLI `argos rodar | retriar |
validar-lexico`. Quatro peças que o Astraea herda:

1. **Contrato do adaptador** (`contrato.py`): `Fonte` com `id`, `limite_por_minuto`,
   `respeita_robots`, e três funções: `listar(desde) -> Referencia*`,
   `baixar(ref) -> Documento`, `sentinela(doc) -> bool`. `Documento` carrega texto
   normalizado, `hash_texto`, `capturado_em`, cabeçalhos e **destaques** (ementa,
   manchete, assuntos) que levam ao nível 3.
2. **Cliente HTTP educado** (`http.py`): User-Agent do projeto, obedece
   `robots.txt` e o limite declarado, tenta de novo em 429 e 5xx, acusa
   `BloqueadoPorPais` e `BloqueadoPorRobots` como política, não como falha.
3. **Léxico como dado** (`lexico.py` + `exemplos/lexico.schema.json`): `termos[]` com
   `chave`, `formas` (sem acento/caixa, palavra inteira, `…` vale até 60 caracteres),
   `exclusoes`, `categorias`, `peso`; `contexto.exige_qualquer`.
4. **Triagem em níveis** (`triagem.py`): 0 sem termo / só exclusão; 1 termo sem
   contexto; 2 termo + contexto (pede juízo); 3 termo em destaque (aceito). Nível 0 e 1
   saem no relatório completo com o motivo: o filtro é auditável e retriável.

Mais: `captura.py` (`.part` promovido só quando a sentinela passa), `estado.py`
(hashes vistos, última rodada por fonte, **pendentes** que voltam toda rodada),
`saidas/` (JSONL canônico: `aceitos`, `pede-juizo`, `itens`; relatório em dois
tamanhos; `rodada.json` com códigos de saída 0/2/3).

### 3.2 Adaptadores existentes

| Adaptador | Fonte | Serve ao Astraea? |
|---|---|---|
| `djen` | Diário de Justiça Eletrônico Nacional (STJ etc.) | não (Brasil; exige IP brasileiro) |
| `datajud` | API pública do CNJ, sem texto | não (Brasil) |
| `lista` | tabela HTML que muda devagar; id = número + hash da linha; linha alterada volta a ser lida | **sim**: é o adaptador certo para listas de casos da CIJ, situações do TPI, estado de ratificação da UN Treaty Collection |
| `rss` | RSS 2.0 e Atom genérico; texto sempre da página | **sim**: notícias de tribunais e agências |

`exemplos/atlaspen/` gera o léxico a partir de `crimes.json` e mapeia a rodada de volta
aos registros: o padrão "consumidor gera o léxico do próprio catálogo" é o que o
Astraea deve seguir (léxico de genocídio gerado da lista de situações/casos
monitorados, não escrito à mão em código).

### 3.3 Agendamento, estado do projeto

Só `ci.yml` (push e PR; matriz Python 3.11–3.13; ruff, validar-lexico, pytest).
**Não há rodada agendada**: a vigilância real depende de IP brasileiro para DJEN e STJ,
e isso nunca foi resolvido. Um único commit (*squash* de 04/10/2026), versão 0.1.0,
roadmap v0.2 pela metade; o README registra uma expansão a precatórios e planilhas em
estudo. Em outras palavras: **motor pronto e testado, operação parada**.

### 3.4 Convenções

MIT; sem dependência de execução; fixture e teste sem rede por adaptador; não ignora
`robots.txt` nem contorna WAF, CAPTCHA ou bloqueio por país; nenhum modelo de linguagem
na triagem (um nível opt-in com modelo "pode existir, marcado na saída, nunca único
critério"); não cruza fontes para montar perfil de pessoa; o consumidor é lido, nunca
editado.

---

## 4. Alétheia

### 4.1 Arquitetura

Descendente direto do Argos (mesmo contrato, mesmo `http.py` com `redigir()` de
segredos, mesma triagem), reconstruído em 05/10/2026 como v0.2.0: 3.765 linhas, 9
adaptadores, CLI `aletheia rodar | retriar | estimar | sondar | validar-lexico |
validar-config`. O que ele acrescentou ao Argos e interessa ao Astraea:

| Peça | O que faz |
|---|---|
| `fontes/gdelt.py` | GDELT DOC 2.0: notícias do mundo em ~65 línguas, janela móvel de ~90 dias, 250 artigos por consulta, pergunta dia a dia e refatia em 6 h quando o dia enche; texto vem da página do veículo, com `robots.txt` respeitado |
| `fontes/rss.py` | RSS/Atom genérico, com lista de marcas de página de erro servida com HTTP 200 |
| `fontes/wayback.py` + `arquivo.py` | descoberta por CDX (prefixo × ano, com progresso) e **cópia de referência** no Internet Archive por URL exata |
| `fontes/topico.py`, `wikipedia.py`, `openalex.py`, `crossref.py`, `ia.py`, `lista.py` | páginas de tag, links externos de verbetes, produção acadêmica, Internet Archive, CSV curado |
| `estimativa.py` | captura e recaptura entre canais (Chapman, Chao): quanto falta, por estrato |
| `saidas/catalogo.py`, `vistas.py` | catálogo CSV de 14 colunas (id pela URL normalizada, snapshot, hash, nível, chaves, `lexico_versao`) e matriz de observações |
| `config.json` | fontes declaradas em dado, com `estrato`, `fatias_por_rodada`, `limite_por_minuto` |
| `index.html` | página estática que lê `catalogo.csv` e `estimativa.md` do próprio repositório, sem CDN |

### 4.2 Formato dos dados

`catalogo.csv` (14 colunas: `id, url, dominio, estrato, titulo, publicado_em,
capturado_em, snapshot, hash_texto, nivel, identificadores, categorias,
primeira_rodada, lexico_versao`), `vistas.csv` (uma linha por observação de um
documento por um canal numa rodada), `estado/<fonte>.json` (33 arquivos, 292 KB),
`saidas/<rodada>/` (71 rodadas em um mês, 2,9 MB: `aceitos.jsonl`, `pede-juizo.jsonl`,
`itens.jsonl`, dois relatórios, `rodada.json`). **Texto integral não é guardado**
(`guardar_texto: false`): o catálogo aponta, a cópia de referência é a do Wayback.

### 4.3 Agendamento

`rodada.yml`: segunda, 09:17 UTC, `timeout-minutes: 340`, `concurrency` sem
cancelamento, `permissions: contents: write`; **uma fonte por vez com commit e push
depois de cada uma** (se o job estourar o tempo, nada se perde); entradas manuais
`desde` e `fonte`; segredos `OPENALEX_API_KEY` e `CROSSREF_MAILTO`; comita como
`aletheia-bot` com o `GITHUB_TOKEN` padrão (sem App). `ci.yml`: matriz 3.11–3.13,
ruff, validações, pytest.

### 4.4 Estado real em 06/11/2026

- O README diz "catálogo ainda vazio, à espera da primeira varredura" (estado de
  05/10), mas `catalogo.csv` tem **282 linhas** e `vistas.csv` 446, de rodadas de 12/10
  a 19/10: o README está defasado.
- A última rodada (02/11/2026, `wayback:brasildefato`) falhou com `_ssl.c:993: The
  handshake operation timed out` no CDX do Wayback, código 2; a de 03/11 comitou. A
  operação roda, com falhas de rede do Wayback como ruído normal.
- Léxico `carandiru-provisorio` (6 termos), estimativa de cobertura publicada: imprensa
  ≤ 2 % do piso, acadêmico ≤ 60 %. O método funciona; a cobertura é baixa porque os
  canais quase não se sobrepõem.

### 4.5 Convenções

MIT para código e CC BY 4.0 para o catálogo (`LICENSE-CATALOGO.md`); `CITATION.cff`;
`CHANGELOG.md`; Google e redes sociais fora por política (`robots.txt`); `docs/pessoas.md`
com base legal LGPD (art. 7º, IV; art. 4º, II, b), sem coluna de nome, remoção a pedido em 7
dias, registro de decisões; segredos redigidos de todo log. Decisões "da pesquisa, não do
código" listadas em `docs/plano.md`.

---

## 5. Astraea hoje

Um commit (`Create implementation plan for Astraea project`, 06/11/2026) com um único
arquivo, `start.md`, que é o enunciado desta tarefa. Sem licença, sem Pages, sem
Actions, sem `docs/`. O repositório **não está vazio**, ao contrário do que o enunciado
diz; nada nele conflita com o que vem a seguir.

---

## 6. Tabela de reúso

Legenda: **TQ** = reusar tal como está (dependência ou cópia literal com aviso);
**AD** = reusar com adaptação; **DADO** = consumir como dado, sem copiar código;
**NÃO** = não serve ao Astraea.

| Ativo | Origem | Veredito | Por quê |
|---|---|---|---|
| Contrato `Fonte` / `Referencia` / `Documento` | Argos → Alétheia | **TQ** | é o contrato que qualquer fonte nova (CIJ, TPI, IRMCT, GDELT) implementa; as funções 2 e 3 do Astraea são adaptadores deste contrato |
| `http.py` (robots, limite, `redigir`, bloqueio por país) | Alétheia | **TQ** | versão mais completa; substitui o `rede.py` do AtlasPen |
| `captura.py` (`.part` + sentinela), `estado.py` (pendentes), `triagem.py`, `saidas/` JSONL | Alétheia | **TQ** | motor inteiro; o Astraea o instala como pacote (`pip install git+…`) ou o vendoriza com aviso MIT |
| `lexico.schema.json` + `lexico.py` | Argos | **TQ** | um léxico por língua e por função cabe no formato sem mudança |
| Adaptadores `gdelt`, `rss` | Alétheia | **TQ** | GDELT é a espinha da função 2; RSS cobre tribunais e agências |
| Adaptador `lista` | Argos | **AD** | serve a listas de casos (CIJ), situações (TPI) e status de tratados; precisa de *parser* por página |
| `estimativa.py` (captura e recaptura) | Alétheia | **AD** | mede cobertura do noticiário por estrato; precisa de estratos novos (língua, região) |
| `rodada.yml` (uma fonte por vez, commit por fonte, timeout 340) | Alétheia | **AD** | padrão certo para Actions; mudar fontes, segredos e, mais tarde, separar repositório de dados |
| `index.html` estático lendo CSV | Alétheia | **AD** | prova que tela sem servidor funciona; o Astraea tem três telas e precisa de JSON e filtros |
| `deploy.yml` (Pages por artefato) | AtlasPen | **AD** | mesmo padrão, sem Astro na primeira fase |
| `transform_data.py --estrito` (vocabulário fechado, id append-only, contradições = 0) | AtlasPen | **AD** | a ideia: um validador que falha o build; o código é todo específico de tipo penal |
| `conferencia.json` (trilha por registro), `excecoes*.json`, `cobertura-limites.json` | AtlasPen | **AD** | mesma estrutura, chaves outras (país, caso, item de notícia) |
| `AUDITORIA.md` (amostragem pré-registrada) | AtlasPen | **AD** | protocolo de revisão por amostragem com estratos por fonte e nível de confiança |
| Convenções: `id` append-only, fonte × derivado, "aponta, não escreve", `Closes #N`, SemVer explícito, `CITATION.cff`, dupla licença, `CLAUDE.md` → `AGENTS.md` | AtlasPen | **TQ** | herança direta para `CONTRIBUTING.md` e `CLAUDE.md` do Astraea |
| `docs/pessoas.md` (LGPD, remoção a pedido) | Alétheia | **AD** | genocídio envolve vítimas e acusados nomeados; política idêntica, base legal a ampliar (GDPR para fontes europeias) |
| `crimes.json`, `fontes.json`, `historico-legislativo.json` | AtlasPen | **DADO** | preenche o registro do Brasil na função 1 (Lei 2.889/56; art. 1º, Lei 8.072/90); lido por URL pública, nunca copiado |
| `ctresb/leis` (`tratados/`, `federal/`) | terceiro | **DADO** | só para conferência do Brasil, pela API, sem clone (8,5 GB) e sem dependência: se falhar, o relatório diz |
| `catalogo.csv` do Alétheia, saídas do Argos | Alétheia / Argos | **NÃO** | são outro tema (Carandiru) e outro consumidor (AtlasPen) |
| `nucleo/baixar.py`, `parsear.py`, `pena_parser.py`, `dispositivo_canonico.py`, `fontes.json` com sentinelas por diploma | AtlasPen | **NÃO** | leitor do HTML do Planalto e da sintaxe de pena em português; não escala para 193 portais |
| `dou_watcher.py`, Recenseador, Relator, Curador, Cotejador, Proponente | AtlasPen | **NÃO** (ideia sim, código não) | fontes brasileiras; o Proponente abre PR com GitHub App, que é um padrão a copiar mais tarde |
| Adaptadores `djen`, `datajud` | Argos | **NÃO** | tribunais brasileiros, IP brasileiro |
| Motor de atributos, simulação, site Astro + React | AtlasPen | **NÃO** na fase 1 | o Astraea não calcula institutos; Astro pode voltar quando as telas crescerem |
| `wayback.py` por prefixo × ano, `topico.py`, `wikipedia.py` | Alétheia | **NÃO** na fase 1 | são canais de varredura do passado; o Astraea começa pela vigilância do presente (GDELT, RSS) e pode ligá-los depois para o retrospecto de um caso promovido |
| Precatórios e planilhas | Argos | **NÃO** | fora do tema |

---

## 7. O que não foi lido

- O código do site do AtlasPen (`src/`), os planos em `.superpowers/` e os testes em
  detalhe: não afetam o reúso.
- Os scripts do ctresb/leis além da listagem de nomes, e o `WORKLOG.md` (272 KB).
- O corpo dos adaptadores `wayback`, `topico`, `openalex`, `crossref` e `ia` do
  Alétheia: lidos só pela docstring e pelo `config.json`, porque ficam fora da fase 1.
- Nenhuma fonte externa (UN Treaty Collection, CIJ, TPI, GDELT…) foi sondada nesta fase;
  isso é a Fase 1 (`02-fontes.md`) e depende do ok ao esboço.

## 8. Conclusões da Fase 0

1. **O motor existe e é um só.** Argos e Alétheia compartilham contrato, cliente HTTP,
   triagem, estado e saídas; o Alétheia é a versão mais nova e mais completa. As
   funções 2 (notícias) e 3 (tribunais) do Astraea são, em código, **adaptadores e
   configuração** desse motor, não um motor novo. O trabalho novo é escrever adaptadores
   para fontes internacionais e um léxico multilíngue.
2. **A função 1 (leis penais do mundo) não tem *crawler* reutilizável**, e não deve ter:
   o *crawler* do AtlasPen é do Planalto. O mapa mundial é um conjunto pequeno de fatos
   estruturados por país (ratificações, existência de código penal, tipificação do
   genocídio, pena máxima), que vem de **poucas fontes globais**, não de 193 portais
   nacionais raspados. A sondagem de `02-fontes.md` (06/11/2026) reduziu ainda mais a
   lista: só a UN Treaty Collection é automatizável; CICV é consulta manual, SHERLOC
   está vazio para genocídio e Legislationline está fora do ar. O detalhamento por
   país vem depois, por carga humana ordenada por prioridade.
3. **Lacunas do motor para o Astraea:** o léxico casa grafias, não traduz; o contexto
   (`exige_qualquer`) é por léxico, então cada língua precisa do seu; não há modelo de
   linguagem (por política, e isso deve ser mantido na triagem); não há banco de dados;
   as saídas são CSV e JSONL comitados, o que limita o crescimento (ver
   `04-arquitetura.md`).
4. **Riscos já visíveis nos ativos:** o Argos não roda agendado e depende de IP
   brasileiro para as fontes que importam ao AtlasPen (irrelevante para o Astraea, mas
   mostra que "motor pronto" não é "operação pronta"); o Wayback falha por SSL com
   frequência; o GDELT só guarda ~90 dias; o ctresb/leis está em crise de armazenamento
   e depende de doações; os três repositórios do autor são mantidos por uma pessoa.
5. **Atualização de 09/11/2026:** a recomendação abaixo não foi adotada. Pela D2, o
   motor do Astraea nasce de uma **cópia** do Alétheia, traduzida para inglês (D8) e
   livre para divergir; o Alétheia não é dependência (ver `04-arquitetura.md`, "Onde o
   motor vive"). Os vereditos **TQ** da tabela da seção 6 continuam valendo no sentido
   de "cópia literal com aviso". Este inventário é o retrato de 06/11/2026 e cita os
   ativos com os nomes que eles têm nos repositórios de origem.

   **Recomendação que saiu daqui, para o esboço do plano:** o Astraea **não copia** o
   motor; **depende** dele como pacote, apontando para um commit fixo do Alétheia (ou de
   um pacote extraído, `argos-core`, decisão pendente em `07-decisoes-pendentes.md`),
   e contribui de volta os adaptadores genéricos (`lista` com *parser* por página, RSS
   multilíngue). Assim o Carandiru, o AtlasPen e o Astraea melhoram o mesmo motor.
