# Changelog

Uma sessão = uma entrada. Datas no fuso de Brasília. Até a v1.0.0 a versão é `0.0.x`
(ver `CONTRIBUTING.md`, "Versão e notas").

## 2026-11-10 — Fase 2, sessão 1: Tabelião (tratados pela UN Treaty Collection)

Branch `fase2/tabeliao`. Não havia resposta às "Escolhas a revisar" das sessões 3 e 4;
elas continuam abertas, nas entradas daquelas sessões.

**Dado novo: `genocide_convention` e `rome_statute` nos 197 registros.** 195 com os dois
blocos carimbados (`source: untc`, confiança A, `checked_by: robot`, `read_on:
2026-11-10`); Taiwan e Kosovo com os dois vazios e `reason`. Contagens, iguais às do
bloco `Status` do depositário e às de 06/11/2026 no `02-fontes.md`:

| | Partes | Signatários sem vínculo | Retirados | Não participam | Vazios |
|---|---|---|---|---|---|
| Convenção sobre o Genocídio (IV-1) | **154** | 1 (República Dominicana) | — | 40 | 2 |
| Estatuto de Roma (XVIII-10) | **124** + Ilhas Cook = **125** | 29 | 2 (Burundi, Filipinas) | 40 | 2 |

A UNTC conta 41 signatários na Convenção e 137 no Estatuto (quem assinou, vinculado ou
não; os colchetes de quem se retirou não contam). Seis países notificaram a retirada do
Estatuto em 2026, com efeito em 2027, e continuam `party` com as duas datas: Níger,
Burkina Faso, Mali, Venezuela, Chade e Nauru. A Hungria notificou em 2025 e revogou em
29/05/2026.

**Leituras desta sessão**, todas pelo cliente HTTP do motor, com o `User-Agent` do
Astraea e o `robots.txt` obedecido:

- `https://treaties.un.org/doc/Publication/MTDSG/Volume%20I/Chapter%20IV/IV-1.en.xml`:
  HTTP 200, 78.616 bytes, `text/html`, sem `Last-Modified`, sha256
  `e2d65ee6723990e38be51bf431494e0986966d291b63a688b00ebcde3fc43d8d`.
- `https://treaties.un.org/doc/Publication/MTDSG/Volume%20II/Chapter%20XVIII/XVIII-10.en.xml`:
  HTTP 200, 119.352 bytes, `text/html`, sem `Last-Modified`, sha256
  `54071add75dd8a6d564f4c95d47ec6d18fe540fed7f99e5ba1257e0dd81d99fa`.
- `robots.txt` do `treaties.un.org`: `Crawl-delay: 2`, sem `Disallow`; o cliente esperou
  os 2 segundos entre as requisições.
- As duas páginas HTML dos tratados
  (`/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=IV-1&chapter=4&clang=_en`, sha256
  `19be9275898ce6cd6d7b38d352b3f3c99db297332d6de34cf0448ad4695dba54`, e
  `mtdsg_no=XVIII-10&chapter=18`, sha256
  `b857c8226bbfd6a7aa58f35f1e3ccc6451180ff3d7c09e150fc7d89e3b70a362`), lidas uma vez só
  para achar a linha "STATUS AS AT": as duas diziam "10-11-2026 10:15:36 EDT".
- `https://unstats.un.org/unsd/methodology/m49/overview/` (tabela M49): HTTP 200,
  1.721.575 bytes, sha256 `b9048114f6e7f2abda83bf03d4263c9d7cd1bd7230e3d0461025ee7839a7a1fb`;
  o `robots.txt` só veda `/wiki/`. Também abri esse `robots.txt` uma vez com o `curl`,
  fora do motor, só para lê-lo.

**Correções ao plano:**

- **A sentinela não é "STATUS AS AT".** Essa linha não está no XML; está na página HTML
  e marca a hora em que a página foi gerada. A sentinela é o bloco `Status` do XML
  (signatários e partes) conferido contra as linhas: a leitura só vale quando as linhas
  contam o mesmo. Registrado no `02-fontes.md` (1.4, nova) e no `sources.json` (`untc`).
- **As *fixtures* não são o XML inteiro.** O XML traz o texto integral das declarações,
  reservas, objeções e notas do depositário, e a regra 2 ("nunca texto integral de
  terceiros") e os termos da ONU impedem pô-lo no repositório. **Divergi do que você
  pediu:** as *fixtures* em `tests/fixtures/untc/` são os arquivos baixados, byte a byte,
  com cada parágrafo de prosa trocado por um marcador que diz a que artigos ele se
  refere. A tabela, as contagens, as datas e a tabela de retiradas ficam intactas. O
  `scripts/trim_untc_fixtures.py` as gera e se recusa a gravar se o adaptador ler a
  *fixture* de modo diferente do original; com os arquivos acima, as duas leituras são
  idênticas. sha256 das *fixtures*: `IV-1.en.xml`
  `cf92b55e7d874a6f885fa99c44c2a132b601bf0e80929dac4dba34cd8fef7501`, `XVIII-10.en.xml`
  `4171037da17689267be311ebf1ea8141a9f02017b33791b175d41c035db4ff6c`.
- O 06 falava em *fixture* com o XML de 06/11/2026; o de 06/11 não foi guardado, e as
  *fixtures* são de 10/11.

**Código:**

- `astraea/sources/listing.py` (novo): o adaptador `listing`. Lê a tabela inteira numa
  requisição, confere a sentinela e devolve uma referência por linha, com `id` = chave +
  resumo da linha: **linha que muda volta a ser lida**, a que não muda não. O formato
  `untc_treaty` decodifica pela declaração do XML (ISO-8859-1 lido como cp1252, como o
  resto do motor, sem perder byte), ignora o `text/html` do cabeçalho, limpa os
  `<superscript>` dos nomes, lê os códigos de ação do próprio cabeçalho da tabela
  (`Accession(a), Succession(d), Ratification`), as declarações e reservas, as objeções e
  a tabela de retiradas. Data em formato desconhecido, código de ação fora do cabeçalho,
  nome repetido, declaração ou objeção de quem não está na tabela, linha riscada sem
  retirada e contagem que não fecha **interrompem a leitura**: nada é adivinhado.
  Registrado em `astraea/sources/__init__.py` (tipo `listing`).
- `scripts/load_treaties.py` (novo): a carga. Lê os dois XML pela rede (ou de uma pasta,
  com `--xml-dir` e `--read-on`), casa os nomes, monta os blocos, mostra o sha256 de cada
  resposta e o que mudaria; `--execute` grava. Nunca apaga; não toca bloco com
  `checked_by: human`; bloco com os mesmos valores fica como estava, com o `read_on`
  antigo, para que a leitura mensal sem novidade dê diff vazio.
- `scripts/trim_untc_fixtures.py` (novo): as *fixtures*, como descrito acima.
- `scripts/transform.py`: data de tratado tem de ser completa (`check 0`).
- Testes: `tests/test_listing.py` (20: as duas *fixtures*, a referência por linha, linha
  alterada, `robots.txt`, sentinela, arquivo truncado, página de erro, formatos
  desconhecidos, decodificação, *superscript*, datas, artigos),
  `tests/test_load_treaties.py` (14: a carga a partir das *fixtures* devolve exatamente o
  `countries.json` do repositório; nome sem mapa, bloco de pessoa, leitura sem novidade,
  simulação, leitura que falha; contagens e valores conhecidos) e dois no
  `tests/test_transform.py` (data de tratado, `participation`).

**Dados e vocabulário** (C5: `scripts/vocabularies.py`, `data/i18n/` e o `03` juntos):

- `data/untc-names.json` (novo): os 30 nomes da UNTC que não são, letra por letra, o
  `name.en` de `countries.json`, cada um com o alfa-3 e a forma do nome na tabela M49.
  Os outros 153 casam letra por letra, e todos os que a M49 tem concordam com ela. Cinco
  formas da M49 foram escritas à mão: "Bahamas (The)" → "Bahamas", "Czech Republic" →
  "Czechia", "Côte d'Ivoire" → "Côte d’Ivoire" (apóstrofo curvo), "St. Kitts and Nevis" e
  "St. Vincent and the Grenadines" → "Saint …". As Ilhas Cook estão com `id: null` e
  `reason`. A Palestina é "State of Palestine" → `PSE`; a Santa Sé não aparece em nenhum
  dos dois tratados; Taiwan e Kosovo estão em `absent`, com a razão de ficarem vazios.
- `sources.json`: fonte nova `unsd-m49` (89 fontes); `untc` com a sentinela corrigida e
  `robots_checked_on: 2026-11-10`. O `NOTICE` ganhou as duas.
- Campos novos: `genocide_convention.participation`, `.reservations_article_ix`,
  `.objections`; `rome_statute.participation`, `.consent_type` (com `acceptance` e
  `approval`, que o Estatuto tem), `.withdrawal_notified`, `.objections`. `withdrawal`
  passou a ser, explicitamente, a data em que a retirada produz efeito. 7 campos e 18
  valores rotulados nas duas línguas. O porquê de cada um está no `03`, parágrafo novo
  "Como o Tabelião preenche os tratados".

**Bateria:** 274 testes passam; `ruff check` e `ruff format --check` limpos;
`astraea validate-lexicon data/lexicon/*.json` valida os cinco; `python
scripts/transform.py --draft --check` passa; `python scripts/build_site.py` simula as
duas páginas. **`--strict` reprova, de propósito, só pelos mesmos 9 status em rascunho**
(travas 3 e 6); nenhum campo de tratado está em rascunho. `config/` ainda não existe.
`countries.complete` continua 0: faltam os blocos de lei penal e de pena.

**O que as mensagens novas dizem** (saem em inglês):

- `IV-1: 78616 bytes, sha256 …; Status: 41 signatories, 154 parties; the rows agree`: a
  leitura passou na sentinela; o sha256 é o que vai para o CHANGELOG.
- `new: BRA.genocide_convention = party` e `changed: HUN.rome_statute: participation:
  'withdrawn' -> 'party'`: o que a carga mudaria, campo a campo. Num mês sem novidade,
  não aparece nenhuma das duas.
- `left alone (checked by a person): BRA.rome_statute`: bloco que você carimbou; o robô
  não o toca.
- `FAIL IV-1: 'Fooland' is not a name of countries.json nor of data/untc-names.json;
  check it in the M49 table and add it by hand` e `nothing was written`: país novo na
  tabela, ou nome mudado. Confira o nome na M49, acrescente a linha em
  `data/untc-names.json` e rode de novo.
- `FAIL the Status block says 41 signatories and 154 parties; the rows count …`: o
  arquivo veio incompleto ou mudou de forma; nada foi gravado.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **`url` é o endereço do XML lido**, não a página `ViewDetails` do exemplo do `03`, que é
  mais legível para gente. Se preferir a página, a troca é uma linha do *script*.
- **Taiwan e Kosovo vazios com `reason`**, e não `none`. Se preferir `none` carimbado, é
  apagar a lista `absent` de `data/untc-names.json` e rodar a carga.
- **`reservations` não separa declaração de reserva**, e `reservations_article_ix` só diz
  que o texto cita o art. IX. A Argentina, por exemplo, tem `yes` por uma reserva ao art.
  IX limitada aos territórios do art. XII.
- **Retirada revogada some do bloco** (África do Sul, Gâmbia, Hungria). Se quiser o
  rastro, cabe um campo `withdrawal_rescinded`.
- **Signatário que anunciou não querer ser parte** (Estados Unidos, Israel, Rússia,
  Sudão, nas notas do depositário) fica `signatory`, como a tabela o mostra.
- **`read_on` só muda quando o valor muda.** O PR mensal fica limpo, mas o carimbo diz
  quando o valor foi lido pela primeira vez, não a última leitura. Se quiser as duas
  coisas, a leitura mensal pode gravar uma linha `confirmed` em `verification.json`
  (decisão da fase 2, item 3).

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver a carga sem gravar nada** (lê os dois XML da UNTC pela internet; leva alguns
   segundos por causa do `Crawl-delay`):

   ```powershell
   python scripts\load_treaties.py
   ```

   Deve terminar com `up to date: data/countries.json`. Se a ONU tiver mudado alguma
   linha desde 10/11, aparecem linhas `changed:` e `would write: data/countries.json`;
   nada foi gravado, e `--execute` grava.
2. **Rodar a bateria:**

   ```powershell
   python scripts\transform.py --draft --check
   python -m pytest
   ```

   O primeiro termina com `static/data is up to date`; o segundo, com `274 passed`.
3. **Ver um país:** abra `data\countries.json` no editor e procure `"BRA"`. Os dois blocos
   novos estão depois de `un_member_since`.
4. **Enviar ao GitHub.** O merge na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

## 2026-11-10 — Fase 1, sessão 4: site mínimo, CI, deploy e política de robô

Branch `fase1/site`. Fecha a fase 1. Não havia resposta às "Escolhas a revisar" da
sessão 3; elas continuam abertas, na entrada daquela sessão.

**Site** (`docs/04-arquitetura.md`, "As telas", parágrafo novo "Como a página é gerada"):

- `scripts/build_site.py` gera a página inicial em `/en/` e `/pt-br/` e uma raiz curta
  que leva à língua do navegador (com os dois *links* para quem lê sem JavaScript). A
  página mostra o que é o Astraea; o contador "197 countries, 0 checked" / "197 países,
  0 conferidos" (`countries.total` e `countries.complete` de `quality.json`); as dez
  situações com o rótulo do status mais alto no *locale*, *link* para a página oficial
  lida e a marca "rascunho: ainda não conferido por uma pessoa", ou "sem status
  registrado"; quantos campos estão em rascunho; como citar (montado do
  `CITATION.cff`); os *links* dos dados abertos. Datas pelos `formats` dos rótulos, com a
  mesma função do `transform.py`. Seletor de língua e marcas `hreflang`.
- Textos da interface em `site/i18n/en.json` e `site/i18n/pt-BR.json`; modelos em
  `site/templates/`; uma folha de estilo em `site/assets/`, sem *framework* nem fonte
  externa.
- **Saída em `_site/`**, fora do git (`.gitignore`); o 04 não dizia o diretório.
  Simulação por padrão, `--execute` grava, nunca apaga.
- **Divergência do 04, registrada lá:** a página é montada no *build*, em Python, e não
  lida por JavaScript no navegador. Funciona sem JavaScript, e o teste confere o contador
  no HTML.
- Regra 1 na tela: um teste confere, nas duas línguas, que a palavra só aparece nos
  textos de interface como nome do crime ("crime of genocide", "crime de genocídio") e
  nunca na lista de situações nem nos contadores.

**Workflows** (`.github/workflows/`):

- `ci.yml`, em todo *push* e PR: `transform.py --draft`, `--draft --check`, `pytest`,
  `astraea validate-lexicon data/lexicon/*.json`, `build_site.py` em simulação, `ruff
  check` e `ruff format --check`. O `--strict` roda como passo informativo: mostra a
  contagem de rascunhos no resumo da execução e só reprova se falhar por outra causa. O
  `AGENTS.md` diz quando ele volta a ser a régua. `validate-config` está comentado até
  `config/` existir. Python 3.14, o mesmo da sua máquina.
- `deploy.yml`, em *push* na `main` que toque `static/`, `site/` ou `data/`, e também à
  mão: confere o derivado, gera `_site/` no *runner* e publica com
  `upload-pages-artifact` e `deploy-pages`. Não faz commit. **Acrescentei** aos caminhos
  `scripts/build_site.py`, `CITATION.cff` e o próprio *workflow*, porque uma mudança no
  gerador ou na citação também muda a página publicada.
- Versões das *actions* conferidas nas páginas de *releases* em 10/11/2026:
  `checkout@v7`, `setup-python@v7`, `configure-pages@v6`, `upload-pages-artifact@v5`,
  `deploy-pages@v5`. **Os workflows não foram executados**: sem *push*, só deu para
  conferir os comandos localmente, um por um, inclusive o *script* do passo informativo.

**Política de robô no motor** (item 5 do roteiro). **Divergência em relação ao
Alétheia**, cujo cliente só lia o `robots.txt` para `Disallow` e baixava toda página:

- `astraea/engine/http.py`: o cliente guarda o `Crawl-delay` de cada host entre duas
  requisições a ele, contando a leitura do `robots.txt`; vale o maior entre esse intervalo
  e o limite por minuto da fonte. O `User-Agent` próprio não mudou.
- `astraea/engine/policy.py` (novo): lê de `data/sources.json` os domínios das fontes com
  `no_text_by_policy` (o host cobre os subdomínios: `elpais.com` cobre
  `feeds.elpais.com`). Neles a rodada não baixa a página: monta o documento com o título
  e a descrição da listagem, e a triagem para no nível 2 com `reason:
  "no_text_by_policy"` (níveis 0 e 1 mantêm o motivo). Vale para todo adaptador, não só
  para o RSS: um artigo da Al Jazeera achado pelo GDELT também não é baixado.
- `Document.policy` é campo novo; o adaptador `rss` guarda a descrição do item
  (`description` no RSS, `summary` no Atom); a configuração de rodada ganha a chave
  `registry` (o caminho de `data/sources.json`), cobrada por `validate-config` e por
  `astraea run`.
- `sources.json` já marcava `no_text_by_policy` nos quatro domínios que o 02 lista (El
  País, EFE, Al Jazeera, Anistia); um teste passa a conferir isso.

**Dado novo: carimbo do `un_status` dos quatro não membros.** A página
https://www.un.org/en/about-us/non-member-states foi lida em 10/11/2026 pelo cliente do
motor, com o `robots.txt` obedecido e o `Crawl-delay: 10` do `un.org` respeitado (sha256
da resposta `a2f57eccfc47cbfa94aa116973cb6c9032bd8e260f5c4318960e29e35692ea4c`). Fonte
nova `un-non-member-states` em `sources.json` (88 fontes) e duas linhas novas em
`verification.json`, ambas `checked_by: robot`:

- Santa Sé (`VAT`) e Palestina (`PSE`) como observadores, confiança A: a página as
  lista.
- Kosovo (`XKX`) e Taiwan (`TWN`) como não membros, confiança B: o carimbo vem da
  ausência nesta lista e na de membros lida em 09/11/2026, que juntas são o rol inteiro
  de Estados da ONU. Nenhuma página da ONU os nomeia.

O `NOTICE` ganhou a página nova. Com isso, **os rascunhos caem de 13 campos em 9
registros para 9 campos em 5 registros**: só os nove status das situações, que esperam o
seu carimbo (regra 3). `countries.complete` continua 0, porque os campos de lei penal e
de tratado ainda não existem.

**Bateria:** 238 testes passam (17 do site, 11 da política de robô); `ruff check` e
`ruff format --check` limpos; `astraea validate-lexicon data/lexicon/*.json` valida os
cinco; `python scripts/transform.py --draft --check` passa; `python
scripts/build_site.py --execute` gera as duas páginas. **`--strict` reprova, de
propósito, só pelos 9 status em rascunho** (travas 3 e 6).

**O que as mensagens novas dizem** (saem em inglês):

- `would write (new): _site/en/index.html`: simulação do `build_site.py`, que diz o que
  gravaria; `left alone (...)`: arquivo em `_site/` que o *script* não gera e não apaga.
- `site: 10 files, home page in /en/, /pt-br/; base URL https://...`: resumo; o endereço
  serve às marcas `hreflang`.
- Na CI, `strict (informative): 9 fields in draft, in 5 records`: aviso azul, não erro.
- `"registry" is required (data/sources.json)`: configuração de rodada sem o caminho das
  fontes; o robô se recusa a rodar sem saber quais domínios não pode ler.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **Kosovo e Taiwan com confiança B por ausência.** Se preferir que ausência não
  carimbe, basta apagar a última linha de `verification.json` e rodar
  `python scripts\transform.py --draft --execute`: os dois voltam a ser rascunho.
- **O título da citação** está em português nas duas páginas, porque é o do
  `CITATION.cff`.
- **Nenhum nome de robô** aparece na página (o "Sentenciador" é provisório, D15).
- O texto "o que é o Astraea" é meu e é texto de interface, não campo de dado: leia
  antes da primeira publicação.
- A CI usa só o Python 3.14. O `pyproject.toml` promete 3.11+, mas nada roda no 3.11;
  se quiser a promessa conferida, uma matriz com as duas versões dobra o tempo da CI.

**Para você (Windows), no PowerShell, dentro da pasta do projeto:**

1. **Enviar ao GitHub.** O merge na `main` local já foi feito; falta o *push*, que é seu:

   ```powershell
   git push origin main
   ```

   Na primeira vez pode abrir uma janela do *Git Credential Manager* pedindo para entrar
   no GitHub pelo navegador; é esperado. Se aparecer `rejected ... (fetch first)`, a
   `main` mudou no GitHub (por exemplo, por um envio de arquivo pela interface do site):
   rode `git pull --rebase` e repita o *push*.
2. **Ligar o Pages.** No site do GitHub, no repositório: **Settings → Pages → Build and
   deployment → Source: GitHub Actions**. Sem isso o *deploy* falha no passo
   `configure-pages` com um erro como `Get Pages site failed` ou `Not Found`: não é
   defeito do código. Depois de mudar, vá em **Actions → Deploy → Run workflow → Run
   workflow** para publicar sem novo *push*.
3. **Ver a CI.** Aba **Actions** do repositório. Cada *push* cria uma execução de **CI**
   (e, quando toca o site ou os dados, uma de **Deploy**). Bolinha verde: passou;
   vermelha: falhou (clique nela e depois no passo com ✗ para ver a mensagem). O passo
   "Validate (strict, informative while drafts remain)" fica verde e deixa um aviso azul
   com a contagem de rascunhos; o quadro **Summary** da execução repete a contagem. Aviso
   amarelo sobre versão de *Node.js* de alguma *action* é do GitHub, não do projeto, e não
   derruba nada.
4. **Ver o site.** Quando o *Deploy* ficar verde, o endereço aparece no quadro dele
   (`github-pages`): deve ser https://luccas-amorim.github.io/astraea/, que leva a
   `/en/` ou `/pt-br/`.
5. **Ver a página antes do *push*** (opcional):

   ```powershell
   python scripts\build_site.py --execute
   python -m http.server 8000 --directory _site
   ```

   Abra http://localhost:8000/ no navegador e feche o servidor com Ctrl+C no PowerShell.
   O Windows pode perguntar, numa janela do "Firewall do Windows Defender", se o Python
   pode usar a rede: "Cancelar" basta, porque o endereço é local.

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
