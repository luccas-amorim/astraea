# 02 — Fontes

**Verificação: 06/11/2026.** Cada fonte foi sondada nesta data: página de entrada,
`robots.txt`, termos de uso, existência de RSS ou API, e, quando relevante, resposta
a um cliente HTTP identificado (`User-Agent` do projeto). "Não lido" quer dizer que
a sondagem falhou e diz por quê; não quer dizer que a fonte seja inviável. A política
do motor (herdada do Argos) vale para a leitura dos resultados: **o que o `robots.txt`
proíbe não se lê; WAF, CAPTCHA e bloqueio por país não se contornam; termos que
proíbem robôs excluem a fonte.**

Confiança: **A** oficial/intergovernamental, **B** acadêmica/ONG com método público,
**C** imprensa/comunitária/secundária.

Os nomes de campo e de adaptador citados aqui foram atualizados em 09/11/2026 para o
vocabulário em inglês do `03-modelo-de-dados.md` (D8); o resultado das sondagens não
mudou.

> **Aviso sobre o ambiente da sondagem.** A verificação foi feita de uma rede corporativa
> com inspeção TLS (IP de saída 130.41.92.237). Alguns bloqueios (Cloudflare na Library
> of Congress, bloqueio de IP no WorldLII, certificado "vencido" em
> deathpenaltyworldwide.org) podem ser do ambiente, não da fonte. A primeira sessão com a
> sua máquina e com um *runner* do GitHub Actions deve **repetir** as linhas marcadas
> "bloqueado" antes de descartá-las.
>
> Em 10/11/2026, da máquina do dono, o certificado de deathpenaltyworldwide.org continua
> vencido (expirou em 21/12/2025): é da fonte, não do ambiente (1.5).

## Função 1: leis penais do mundo

### 1.1 Resumo

| Fonte | Conf. | O que entrega para os campos | Licença / termos | `robots.txt` | API / massa | Línguas | Atualização | Veredito |
|---|---|---|---|---|---|---|---|---|
| **UN Treaty Collection** (treaties.un.org), capítulos IV.1 (Convenção de 1948) e XVIII.10 (Estatuto de Roma) | A | assinatura; ratificação/adesão/sucessão com data e tipo; declarações, reservas, objeções, retiradas, notas; "STATUS AS AT 06-11-2026": 41 signatários e **154 partes** na Convenção; 137 signatários e **125 partes** no Estatuto, com seção de retiradas (art. 127) | termos gerais da ONU: uso pessoal não comercial, sem redistribuir nem derivar sem permissão; página própria de termos da UNTC → "Page not found" | `User-agent: *`, `Crawl-delay: 2`, **sem `Disallow`** | **XML por tratado, verificado**: `/doc/Publication/MTDSG/Volume%20I/Chapter%20IV/IV-1.en.xml` e `/Volume%20II/Chapter%20XVIII/XVIII-10.en.xml` (HTTP 200; `encoding="ISO-8859-1"`, servido como `text/html`, sem `Last-Modified`); estrutura `Treaty/Header/ExternalData/Status`, `Participants/Table/Row/Entry`, `Declarations`, `Objections`, `EndNotes`; nomes com `<superscript>` de nota a limpar; PDF ao lado | EN, FR | diária | **A fonte da função 1.** Entra por `listing` sobre o XML, mensal; a sentinela é o bloco `Status` do XML conferido contra as linhas (correção de 10/11/2026, adiante) |
| **CICV — IHL Databases / National Practice** | A | legislação e jurisprudência nacional de implementação do DIH, com filtros por instrumento, tipo, tópico e Estado (fontes secundárias falam em 195 países) | termos gerais do CICV: cópia com indicação de fonte, sem modificação, sem uso comercial; `legal-notice` do subdomínio → 404 | tudo permitido | nenhuma; **SPA** ("You need to enable JavaScript") | 7 línguas de interface | não observada | **Consulta manual** por país durante a carga; o filtro "genocídio" **não foi confirmado nem negado** (o componente não expôs as opções) |
| **UNODC SHERLOC — Database of Legislation** | A | legislação por país (~190 + Santa Sé e Palestina com asterisco; **sem Kosovo nem Taiwan**); a taxonomia tem "Genocide (underlying acts)" e "Genocide (contextual elements)", **mas as buscas testadas devolvem 0 leis** | termos da ONU (uso pessoal, não comercial) | 404 | nenhuma; SPA; `WebFetch` 403, navegador funciona | 6 oficiais | não declarada | **Fora** por ora: taxonomia existe, conteúdo de genocídio vazio; reconferir a cada semestre |
| **Legislationline** (OSCE/ODIHR) | A | **em reconstrução**: redireciona para `odihr.osce.org/odihr/legal-opinions-and-comments/`; a coleção de códigos penais (`/documents/section/criminal-codes`) → 404; "The new platform will be available in the coming months" | não encontrados | Drupal padrão | nenhuma | EN | — | **Indisponível em 06/11/2026**; o Arquivista reconfere mensalmente; cópias antigas de códigos existem em ecoi.net (pista) |
| **Law Library of Congress — Global Legal Monitor** | A | não lido | não lido | **não lido**: Cloudflare "verificação de segurança" em todas as rotas, inclusive `/robots.txt` | API JSON `?fo=json` documentada no espelho GitHub (`libraryofcongress.github.io`), sem autenticação; limite "20 req/min" só por busca, não lido na fonte | EN | — | **Bloqueado no ambiente**; repetir de outra rede; se abrir, é fonte de notícias jurídicas por país (função 1 e 2) |
| **WorldLII / CommonLII / AustLII** | B | não lido | AustLII copyright → 403 | Cloudflare `Content-Signal: ai-train=no`; `Allow: /`; **~40 robôs de IA com `Disallow: /`** (ClaudeBot, GPTBot, CCBot…) | não | — | — | **Bloqueado** ("Sorry, you have been blocked" para o IP); repetir de outra rede; o `robots.txt` permite *crawler* genérico |
| **BAILII** | B | só Reino Unido e Irlanda | cópia gratuita com crédito; **proíbe "external indexing … by web robots" e "bulk downloading"**; bloqueia domínios | `Disallow` das coleções; GPTBot vetado | não | EN | — | **Não** |
| **Cornell LII /world** | B | diretório de *links* por região; sem dado por país | CC BY-NC-SA 2.5 | Drupal, `Crawl-delay: 10` | não | EN | sem data | irrelevante (só *links*) |
| **Prevent Genocide International** | C | **nada: domínio estacionado** (`/lander`, página de *parking*); último *snapshot* no Wayback em 06/11/2024 | — | do estacionador | não | — | morto | **Fora**; a lista histórica de legislação doméstica só via Wayback, como semente |
| **Cornell Center on the Death Penalty Worldwide** | B | status por país em 4 categorias, execuções, perfis; "We update global execution figures each Wednesday"; base "being redesigned" | sem termos; "© 2026 Cornell" | não lido (lido em 10/11: permite tudo, 1.5) | não; HTML (em 10/11: a base do mapa responde JSON, 1.5) | EN, FR | semanal | **Sim, por `listing`** no espelho `dpw.lawschool.cornell.edu` (o domínio principal apresentou certificado vencido via proxy corporativo; em 10/11, vencido de qualquer rede, 1.5) |
| **Anistia Internacional — Death Sentences and Executions** | B | relatório anual em PDF (abril), 13 línguas, com anexo por país; a página web só traz agregados ("113 abolicionistas") | **CC BY-NC-ND 4.0** (`/about-us/permissions/`) | proíbe `/*/search/`; alguns robôs vetados; `crawl-delay: 5` para CCBot | não; PDF | 13 | anual | **Sim, carga anual à mão** do anexo; a licença ND impede derivar o PDF, não impede registrar o status com citação |
| **Constitute Project** | B | constituições (cláusulas sobre pena de morte), não códigos penais; XML de países e tópicos | **sem CC**: "commercial use is expressly prohibited"; "used solely for providing information to users of this site" | **proíbe `/*.xml$`, `/*.json`, `/*?*key=*`**: os próprios endpoints de dados | API com chave (doc em Google Doc) | EN, AR, ES | — | **Não** (robots veda os dados) |
| **ICC — Assembly of States Parties** | A | lista de Estados-partes por grupo regional, sem datas | `terms-use` → "Browser Validation Page" | Drupal padrão | não | EN, FR | — | **Fraco**; o XML XVIII.10 da UNTC é superior; Gcore bloqueou navegador e `WebFetch`, `curl` passou |
| **Wikidata** | C | P1891 "signatory", P6193 "ratified by" existem, **mas os itens da Convenção (Q865344) e do Estatuto (Q838958) têm 0 declarações**; 70 itens `P31 = código penal`; nenhuma propriedade de pena de morte | **CC0** | Wikimedia: exige `User-Agent`, respeitar 429 e `maxlag` | SPARQL, API, *dumps* | multilíngue | contínua | **Semente quase vazia** para estes campos; serve para nomes, ISO e *links* de código penal |
| **Wikipedia (EN)** | C | "List of parties to the Genocide Convention" (tabela Estado/assinatura/depósito/método; "As of September 2026, 154 states"; seção **"Municipal laws"** com dispositivos internos por país); "Capital punishment by country" (status, última execução, ano de abolição, categorias da Anistia "as of 2025") | CC BY-SA 4.0 + GFDL; proíbe uso automatizado abusivo | Wikimedia padrão | API, *dumps* | EN (+) | contínua | **Semente, nunca fonte**: a seção "Municipal laws" é o índice de partida para `domestic_genocide`, a conferir fonte a fonte |
| **GlobaLex** (NYU) | B | guias narrativos de pesquisa por país; "Last Updated: January/February 2026" | © NYU | **veta robôs de IA** (ClaudeBot, Anthropic-AI, GPTBot…) | não | EN | — | guia para leitura humana na promoção; não se raspa |
| **Foreign Law Guide** (Brill) | B | ~190 jurisdições, **assinatura paga** (fontes secundárias) | não lido | não lido (CloudFront 403/202) | não | — | — | **Não** |
| **EUR-Lex / N-Lex** | A | só direito da UE; N-Lex é portal para as 27 bases nacionais e lista sites oficiais de 17 países fora da UE | EUR-Lex: reutilização livre (Decisão 2011/833/UE), metadados CC0; N-Lex: "consult the copyright notice of the database concerned" | EUR-Lex: não lido (202); N-Lex: inexistente | EUR-Lex: *webservice*/SPARQL | 24 | diária | **N-Lex como catálogo de `official_url`** para 27 + 17 países; não se raspa |
| **Conselho da Europa (CODICES etc.)** | A | nenhuma base de códigos penais nacionais localizada | não lido | `coe.int` → 403 | — | — | — | **Fora** (403, 404, 502, certificado inválido) |
| **International Crimes Database** (Asser), **TRIAL (UJAR/UJIM)** | B | casos e verbetes; **sem seção de legislação** | ICD: "All Rights Reserved", citar e notificar; TRIAL: reprodução além da lei exige autorização | ICD 404; TRIAL `Crawl-delay: 10` | não; PDFs | EN, FR, ES | ICD irregular; UJAR anual | função 3, não 1 |
| **ICC Legal Tools Database** | A | 441.314 documentos; coleção "National Criminal Jurisdictions" com 20.914 itens (leis, decisões, comunicados, misturados), PURLs estáveis `/doc/<id>/` | não comercial; citar PURL; "All rights reserved" | `ai-train=no`; `Allow: /`; robôs de IA vetados | não documentada; SPA | EN | diária | **consulta manual** durante a promoção; não se raspa |

Pistas não verificadas: tabelas do Sexto Comitê da AGNU sobre jurisdição universal
(`static.un.org/en/ga/sixth/80/universal_jurisdiction/scope_table.pdf`) listam
dispositivos nacionais por crime; a base NILD (Nottingham, 2006–2014) só em fontes
históricas.

### 1.2 O que isso decide

1. **A função 1 não é um *crawler*; é um conjunto de dados curado com uma fonte
   automatizada.** O único dado por país que se lê por robô com estabilidade é o XML da
   UN Treaty Collection: assinatura, vinculação, tipo, reservas, objeções e retiradas
   das duas convenções, para 154 e 125 partes. Isso preenche `genocide_convention` e
   `rome_statute` de todos os 197 registros no primeiro mês, com confiança A.
2. **`penal_code` e `domestic_genocide` não têm base aberta viva em 06/11/2026.**
   Prevent Genocide morreu; Legislationline está fora do ar; SHERLOC tem a taxonomia e
   não tem o conteúdo; o CICV exige navegação manual; Legal Tools mistura tudo e veta
   robôs; os LIIs bloqueiam. Esses dois campos entram **à mão, país a país**, a partir
   de dois índices de partida (a seção "Municipal laws" da Wikipedia e o N-Lex para a
   `official_url`) e conferidos na fonte oficial ou, na falta dela, numa fonte B com
   `confidence: B`. O ritmo realista é de **10 a 20 países por sessão de trabalho**;
   os 197 levam de 10 a 20 sessões, e o roteiro ordena pelos países com situação
   monitorada.
3. **Pena de morte** entra pelo espelho do Cornell (`listing`, semanal, 4 categorias) e
   pelo anexo anual da Anistia (carga à mão, CC BY-NC-ND: registra-se o status com
   citação, não se redistribui o PDF).
4. **Pena máxima** não tem fonte global: é lida do código penal de cada país na mesma
   sessão de carga de `penal_code`, e fica `unknown` até lá.
5. **A questão transversal 1 ganha um dado**: SHERLOC não lista Kosovo nem Taiwan e
   marca Santa Sé e Palestina com asterisco; a UNTC lista a Palestina e a Santa Sé como
   partes. O esquema com `un_status` acomoda os quatro sem forçar nenhuma fonte.
6. **Três fontes pedem repetição de outra rede** antes de serem descartadas: Library
   of Congress (API JSON documentada e sem chave, se o Cloudflare for do ambiente),
   WorldLII (o `robots.txt` permite *crawler* genérico) e o domínio principal do
   Cornell.

### 1.3 O que a sondagem não conseguiu

Library of Congress (desafio em todas as rotas); WorldLII/CommonLII/AustLII (IP
bloqueado); ICC ASP (contagem e datas); certificado de `deathpenaltyworldwide.org`;
Foreign Law Guide; Conselho da Europa; `robots.txt` do EUR-Lex; *snapshot* do
Wayback da Prevent Genocide; filtro "genocídio" no CICV; anexo por país do relatório
da Anistia (PDF não extraído no ambiente); organização por país da coleção do Legal
Tools; `Last-Modified` do XML da UNTC. Nenhuma fonte foi percorrida país a país:
verificou-se existência, estrutura, termos e acesso.

### 1.4 O que a leitura de 10/11/2026 corrigiu (fase 2, sessão 1)

- **"STATUS AS AT" não é sentinela.** A linha está na página HTML do tratado
  (`/Pages/ViewDetails.aspx`), não no XML, e marca a hora em que a página foi gerada: lida
  em 10/11/2026, dizia "STATUS AS AT : 10-11-2026 10:15:36 EDT" nos dois tratados. O XML
  traz o bloco `Status` (`Signatories`, `Parties`); a sentinela do adaptador é ele,
  conferido contra as linhas da tabela (as datas entre colchetes, de quem se retirou, não
  contam). Em 10/11/2026: 41 signatários e 154 partes na Convenção; 137 e 125 no
  Estatuto, os mesmos números de 06/11.
- **As 125 partes do Estatuto incluem as Ilhas Cook**, que não estão entre os 197 da D1.
  Entre os 197, são 124.
- **A nota de retiradas do Estatuto é uma tabela** dentro da nota 2 do XML, com data de
  notificação, data de efeito (ou "(Withdrawn)", quando a retirada foi revogada) e a
  notificação do depositário. Em 10/11/2026: Burundi e Filipinas saíram; Níger, Burkina
  Faso, Mali, Venezuela, Chade e Nauru notificaram em 2026, com efeito em 2027; África do
  Sul, Gâmbia e Hungria revogaram.
- O `robots.txt` foi relido pelo cliente do motor (`Crawl-delay: 2`, sem `Disallow`) e
  continua sem `Last-Modified` no XML.

### 1.5 O que a leitura de 10/11/2026 corrigiu (fase 2, sessão 2: pena de morte)

Leituras feitas da máquina do dono pelo cliente HTTP do motor, com o `User-Agent` do
Astraea e o `robots.txt` obedecido; os sha256 estão no `CHANGELOG.md`.

- **O domínio principal tem certificado vencido de qualquer rede.** O de
  `deathpenaltyworldwide.org` (GoDaddy) expirou em 21/12/2025; `www.` derruba a
  conexão. Não se contorna (regra 7): o Astraea lê o espelho.
- **O espelho `dpw.lawschool.cornell.edu`** tem certificado válido (Let's Encrypt, até
  19/12/2026) e `robots.txt` que permite tudo (`User-Agent: *`, `Disallow:` vazio;
  `Last-Modified` 30/10/2026). **Não há página de termos de uso** no espelho nem na
  base: só "© 2026 Cornell Center on the Death Penalty Worldwide" no rodapé. O Astraea
  grava só a categoria de cada país, com a fonte citada, sem texto.
- **A tabela não está no HTML.** A legenda do mapa da página inicial pede a uma base em
  outro servidor, `cornell-dpw.herokuapp.com`, uma lista por categoria:
  `/api/countries/by-law-status/1?lawStatus=<categoria>` (`1` é inglês; `2`, francês),
  que devolve uma lista JSON de `{displayName, isoCode}` (ISO alfa-2 ou `null`). O
  `robots.txt` desse servidor responde 404, o que pela convenção não veda nada. As quatro
  categorias são `Abolitionist`, `Abolitionist For Ordinary Crimes`, `Abolitionist de
  facto` e `Retentionist`. **A página não dá contagem por categoria**: a sentinela é a
  forma das quatro listas (todas vieram, nenhuma vazia, nenhum nome em duas).
- **Em 10/11/2026: 95 + 6 + 45 + 35 = 181 nomes.** Seis estão fora dos 197 (cinco
  territórios e o Chipre do Norte); 22 dos 197 não estão em nenhuma lista (Andorra,
  Burkina Faso, Burundi, Cabo Verde, Congo, Guatemala, Ilhas Marshall, Kiribati,
  Liechtenstein, Malta, Maurício, Micronésia, Mônaco, Nauru, Palau, Samoa, San Marino,
  Santa Sé, São Tomé e Príncipe, Seicheles, Suriname, Tuvalu).
- **A própria base define só duas categorias**, na pergunta "Retentionist or Abolitionist
  De Facto" do perfil de país: retencionista é quem executou nos últimos dez anos;
  abolicionista *de facto*, quem não executa há pelo menos dez. As outras duas não têm
  definição publicada. A correspondência com as categorias da Anistia, e por que o *de
  facto* não é gravado, está no `03-modelo-de-dados.md` ("Como a pena de morte é
  preenchida").
- **A página se contradiz.** O mapa da página inicial é colorido por um *plugin* (um
  dicionário alfa-2 → cor no próprio HTML), e diverge da lista da base em sete países que
  a base classifica: Cazaquistão e Israel (base: crimes comuns; mapa: abolicionista e
  retencionista), Guiné Equatorial e Coreia do Norte (base: retencionista; mapa: crimes
  comuns e *de facto*), Papua-Nova Guiné, Zâmbia (base: *de facto*; mapa: abolicionista) e
  Coreia do Sul (base: *de facto*; mapa: retencionista). O mapa ainda pinta cinco países
  que a base não lista (Burkina Faso, Burundi, Congo, Guatemala, Suriname) e tem erro
  visível nos rótulos das duas Coreias. **O robô lê a base** (decisão do dono,
  10/11/2026); os quatro que ficam carimbados apesar da divergência (Cazaquistão,
  Israel, Guiné Equatorial, Coreia do Norte) são os primeiros a conferir no anexo da
  Anistia.
- A configuração da página declara `currentYear = '2020'` e o rodapé injetado diz "©
  2025 Cornell University"; com o aviso de que a base está sendo refeita, são sinais de
  que a classificação pode estar atrasada em alguns países. A confiança fica B, e a
  carga anual da Anistia é a conferência.

### 1.6 O que a carga humana de 10/11/2026 encontrou (fase 2, sessão 4: lei penal)

Leituras dos portais oficiais dos 24 países da carga humana, da máquina do dono, pelo
cliente do motor (o `robots.txt` obedecido), salvo o Planalto; sha256 no `CHANGELOG.md`.
A seção "Municipal laws" da Wikipedia serviu só de índice de partida (regra 4).

| País | Portal | O que aconteceu | Resultado |
|---|---|---|---|
| Brasil | `planalto.gov.br` | **derruba toda conexão do cliente do motor e do `curl`** (o próprio `robots.txt`); no navegador, as páginas e um `robots.txt` 404 | lido à mão no navegador embutido (`planalto`), mais o AtlasPen (`atlaspen`) |
| Brasil | `atlaspen.com.br` | `robots.txt` com `Disallow: /` para todos | lido no repositório do próprio projeto, nunca no site |
| Alemanha | `gesetze-im-internet.de` | lê | rascunho (`gesetze-im-internet`) |
| Argentina | `servicios.infoleg.gob.ar` | lê; `robots.txt` 404 | rascunho (`infoleg`) |
| Bangladesh | `bdlaws.minlaw.gov.bd` | lê; páginas em UTF-16 | rascunho (`bdlaws`) |
| África do Sul | `justice.gov.za` (PDF da lei) | lê; o endereço em `gov.za` deu 404 | rascunho (`justice-gov-za`); país sem código penal |
| Rússia | `kremlin.ru/acts/bank` | lê, texto consolidado em 54 páginas; `pravo.gov.ru` não respondeu | rascunho (`kremlin-acts`) |
| França | `legifrance.gouv.fr` | `robots.txt` veda as páginas dos códigos | vazio com `reason` |
| China | `flk.npc.gov.cn` | `robots.txt` veda; `npc.gov.cn` lê, mas o texto do Código não foi localizado | vazio |
| Iraque | `iraqld.hjc.iq` | `robots.txt` veda | vazio |
| Israel | `main.knesset.gov.il` | HTTP 247 sem conteúdo (desafio de robô) | vazio; não se contorna |
| Camboja | `moj.gov.kh` | página "Request Rejected" (WAF) | vazio |
| Bélgica | `ejustice.just.fgov.be` | derruba a conexão | vazio |
| Países Baixos | `wetten.overheid.nl` | certificado autoassinado na cadeia, da rede do dono | vazio |
| Gâmbia | `moj.gov.gm` | certificado que não se verifica | vazio |
| Sérvia | `pravno-informacioni-sistem.rs` | aplicação JavaScript, sem texto | vazio |
| Ucrânia, Mianmar, Bósnia | `zakon.rada.gov.ua`, `mlis.gov.mm`, `mpr.gov.ba` | não responderam | vazio |
| Síria | `parliament.gov.sy` | não resolve no DNS | vazio |
| Sudão, Etiópia, Ruanda, Tanzânia | `moj.gov.sd`, `hopr.gov.et`, `minijust.gov.rw`, `parliament.go.tz` | respondem, mas a lei não foi alcançada nesta sessão | vazio, a continuar |
| Palestina | — | nenhum portal oficial localizado; o Muqtafi (Birzeit, acadêmico) não respondeu | vazio |

- **O Planalto e o robô.** O AtlasPen já registrava que o Planalto serve página de
  bloqueio a robôs. O Astraea **não o lê por robô**; a leitura desta sessão foi feita no
  navegador embutido do aplicativo, sem desafio a vencer (nenhum CAPTCHA, `robots.txt`
  404), com o sha256 de cada resposta calculado no próprio navegador. É a leitura de
  pessoa que a carga humana pressupõe, e é **escolha a revisar pelo dono** (`CHANGELOG.md`).
- **Fonte por portal.** Cada portal oficial lido é uma entrada própria em `sources.json`
  (uma por canal, como as demais), com `robots_checked_on` da leitura; cinco novas, além
  de `planalto` e `atlaspen`.
- **Certificados que não se verificam** (Países Baixos, Gâmbia) podem ser do caminho de
  rede do dono, não do site (a sondagem de 06/11 já tinha visto um *proxy* corporativo).
  Repetir de outra rede antes de concluir; nunca desligar a verificação. **Resolvido em
  11/11 (1.7): nos dois casos o defeito era do site ou do Windows, não da rede.**

### 1.7 O que a segunda tentativa de 11/11/2026 encontrou (fase 2, sessão 5)

Os 18 vazios da 1.6, de novo, da máquina do dono, pelo cliente do motor, com o
`robots.txt` obedecido e a verificação de certificado ligada; sha256 no `CHANGELOG.md`.

| País | Portal tentado | O que aconteceu | Resultado |
|---|---|---|---|
| Sudão | `moj.gov.sd/sudanlaws` | é um leitor de *e-book* (Kotobee); os capítulos são páginas estáticas em `/sudanlaws/epub/EPUB/xhtml/`, que o próprio leitor carrega; `robots.txt` 404; livro de 01/08/2017 | rascunho (`moj-sd`) |
| Ruanda | `minijust.gov.rw/official-gazette` | o Diário Oficial em PDF, trilíngue; a Lei 68/2018 está no número especial de 27/09/2018 | rascunho (`minijust-rw`) |
| Bósnia | `sudbih.gov.ba` (Tribunal da BiH) | o Ministério (`mpr.gov.ba`) continua sem responder; o Tribunal republica o Diário Oficial (o Código de 2003 e as alterações até 61/04) | rascunho (`sudbih`) |
| Gâmbia | `moj.gov.gm` | o certificado `*.gov.gm` não cobre `www.moj.gov.gm`, e o servidor não envia o intermediário; lido em `moj.gov.gm` com o intermediário RapidSSL do endereço AIA do próprio certificado, verificado contra as raízes da Mozilla | `penal_code` em rascunho (`moj-gm`); o crime não está na lei lida |
| Países Baixos | `wetten.overheid.nl` | o certificado se verifica contra as raízes da Mozilla (faltava a raiz certSIGN no repositório do Windows que o Python consulta); o `robots.txt` **veda agentes de IA pelo nome** (`ClaudeBot`, `anthropic-ai`, `ChatGPT-User` e outros) | vazio: espera a leitura do dono |
| Bélgica | `ejustice.just.fgov.be` | agora responde; o `robots.txt` veda os caminhos das leis (`/eli/`, `/loi/`, `/wet/`, `/cgi_loi/`) | vazio |
| França | `legifrance.gouv.fr` | o próprio `robots.txt` responde 403 (o motor lê como "veda tudo") | vazio |
| Etiópia | `justice.gov.et` | o Ministério publica o Código Penal (Proclamação 414) só em PDF amárico, com camada de texto em codificação de fonte antiga, que não se extrai; `fsc.gov.et` 503; `hopr.gov.et` sem índice de leis | vazio |
| Tanzânia | `parliament.go.tz`, `nalis.sheria.go.tz`, `tanzlii.org` | o Parlamento só publica as leis aprovadas; o NaLIS não tem leis; o TanzLII (do Judiciário) desafia o cliente (Cloudflare) e declara `ai-input=no` | vazio |
| Sérvia | `pravno-informacioni-sistem.rs` | aplicação JavaScript, também no endereço ELI que o `robots.txt` permite; o texto vem de APIs listadas num arquivo de configuração em base64, não chamadas | vazio; escolha do dono |
| Síria | `moj.gov.sy` | responde, mas não publica o Código Penal; o Parlamento continua sem DNS | vazio |
| Iraque | `parliament.iq`, `moj.gov.iq` | o `robots.txt` do Parlamento veda tudo; o Ministério não responde | vazio |
| Camboja | `moj.gov.kh` | derruba a conexão (em 10/11, "Request Rejected") | vazio |
| Israel | `main.knesset.gov.il` | o mesmo HTTP 247, que só roda um desafio JavaScript | vazio; não se contorna |
| Ucrânia | `zakon.rada.gov.ua`, `data.rada.gov.ua`, `rada.gov.ua` | nenhum responde | vazio |
| Mianmar | `mlis.gov.mm`, `pyidaungsu.hluttaw.mm` | o primeiro não responde (https nem http); o Parlamento é aplicação JavaScript | vazio |
| China | `npc.gov.cn` | sem mudança | vazio |
| Palestina | `www.moj.pna.ps` | HTTP 400 "URL with hostname … is not allowed", que não vem do site; o Muqtafi segue sem responder | vazio |

- **Robô de IA vetado pelo nome é veto à sessão.** O `User-Agent` do Astraea passa no
  `robots.txt` holandês, mas quem lê na carga humana é um modelo de linguagem, e o
  arquivo veda pelo nome os agentes de IA, inclusive os que buscam a pedido de usuário
  (`ChatGPT-User`, `MistralAI-User`). O mesmo vale para `Content-Signal: ai-input=no`
  (TanzLII). A sessão não lê; o país espera a leitura do dono. Conferido nos portais já
  lidos (Gesetze im Internet, InfoLEG, bdlaws, kremlin.ru, justice.gov.za, e os quatro de
  hoje): nenhum veda agente de IA pelo nome.
- **Cadeia incompleta se completa, não se ignora.** Na Gâmbia, o intermediário veio do
  endereço AIA que o próprio certificado declara e foi verificado contra as raízes da
  Mozilla (`openssl verify`) antes de entrar; no holandês, bastaram as raízes da Mozilla.
  A verificação de nome e de cadeia ficou ligada nos dois. O cliente do motor não muda:
  as duas leituras usaram um transporte com outro arquivo de raízes, fora do repositório.
  É escolha a revisar pelo dono (`CHANGELOG.md`).
- **Lei lida sem o crime não é `no`.** A lei penal nova da Gâmbia não traz o crime; `no`
  afirmaria que nenhuma lei do país o traz, o que a leitura de uma lei não sustenta. O
  `domestic_genocide` fica vazio com `reason`.

### 1.8 O que a terceira volta de 11/11/2026 encontrou (fase 2, sessão 6)

Os 14 vazios da 1.7, da máquina do dono, pelo cliente do motor, com o `robots.txt`
obedecido (e lido à procura de agentes de IA vetados pelo nome) e a verificação de
certificado ligada, com as raízes da Mozilla; sha256 no `CHANGELOG.md`. Ucrânia, Mianmar
e Camboja foram tentados de novo; nos outros, a sessão procurou gazeta, parlamento ou
tribunal que ainda não tivesse sido tentado. A busca na web serviu só de índice
(regra 4); cópias da WIPO, da ILO, de universidades e de editoras não entram.

| País | Portal novo ou tentado de novo | O que aconteceu | Resultado |
|---|---|---|---|
| Países Baixos | `zoek.officielebekendmakingen.nl` (Staatsblad) | o `robots.txt` do Diário Oficial **não veda agentes de IA** (só o *AhrefsBot*) e veda as páginas de resultado de busca; a Wet internationale misdrijven está no Stb. 2003, 270, como promulgada | `domestic_genocide` e `max_penalty` em rascunho (`officielebekendmakingen`); `penal_code` vazio, porque o Código consolidado só está no `wetten.overheid.nl` |
| Bélgica | `lachambre.be` (documentos parlamentares) | lê (`Crawl-delay: 5`); o novo Código Penal (leis de 29/02/2024, Livros I e II, em vigor desde 08/04/2026) está no texto aprovado em plenário e submetido à sanção; a lei de 16/03/2026 (DOC 56 1160) muda vários artigos, mas não o 36 nem o 82 | os três blocos em rascunho (`lachambre`) |
| China | `npc.gov.cn` (por http; o https falha no *handshake*) | o `robots.txt` só veda o *YisouSpider*; a página da Lei Penal é só um invólucro que aponta para a tradução inglesa "só para referência"; o Boletim do Supremo Tribunal Popular (`gongbao.court.gov.cn`) responde com um WAF (302, `CWAP-waf`); o Boletim do Comitê Permanente da APN de 2021 traz a Lei consolidada até a Emenda XI, num PDF de uns 20 MB que o servidor cortou duas vezes, perto dos 14 MB | vazio |
| Ucrânia | `zakon.rada.gov.ua`, `minjust.gov.ua`, `supreme.court.gov.ua`, `ovu.com.ua`, `golos.com.ua` | a Rada continua sem responder; o Ministério só aponta para a Rada; o Supremo lista as leis que alteram o Código, não o texto; `ovu.com.ua` virou site de notícias; o `robots.txt` do `golos.com.ua` veda `ClaudeBot` pelo nome | vazio |
| Mianmar | `mlis.gov.mm`, `unionsupremecourt.gov.mm` | o MLIS continua sem responder; o Supremo publica doze leis (o Código de Processo Penal entre elas), não o Código Penal | vazio |
| Camboja | `moj.gov.kh`, `senate.gov.kh`, `eccc.gov.kh` | o Ministério responde "Request Rejected" (WAF), até ao `robots.txt`; o Senado derruba a conexão; a ECCC só publica a sua própria lei, limitada aos crimes de 1975 a 1979 | vazio; não se contorna |
| França | `echanges.dila.gouv.fr/OPENDATA/LEGI/` | a DILA publica a base LEGI (a do Légifrance) em dados abertos, `robots.txt` 404, mas só como um arquivo de 1,2 GB e incrementos diários | vazio; o *download* é escolha do dono |
| Sérvia | `parlament.gov.rs`, `mpravde.gov.rs`, `slglasnik.com` | a Assembleia publica os projetos (*predlozi zakona*), não a lei aprovada; o Ministério fecha a conexão TLS; o certificado da editora do Diário não se verificou (a cadeia pelo AIA não foi tentada) | vazio; as APIs continuam escolha do dono |
| Israel | `fs.knesset.gov.il`, `gov.il` | o servidor de arquivos do Knesset também passou a responder com o desafio HTTP 247; o `robots.txt` do `gov.il` responde 403 | vazio |
| Iraque | `hjc.iq`, `moj.gov.iq` | o `robots.txt` do Conselho Judiciário responde 403; o Ministério não responde | vazio |
| Palestina | `plc.ps`, `courts.gov.ps`, `dft.gov.ps` | o Conselho Legislativo é página de hospedagem suspensa; os tribunais não respondem; `dft.gov.ps` não resolve | vazio |
| Etiópia | `hopr.gov.et`, `fsc.gov.et` | sem índice de leis; o Supremo responde 503 | vazio |
| Síria | `pministry.gov.sy` | não responde | vazio |
| Tanzânia | `judiciary.go.tz`, `agctz.go.tz` | nada novo | vazio |

Nos já lidos, a conferência das alterações (item 2 do pedido da sessão):

- **Bósnia.** A Procuradoria da BiH (`tuzilastvobih.gov.ba`) publica uma consolidação
  "não oficial" até o SG 47/23. O art. 171 não mudou (continua sem "como tal"); o
  *dugotrajni zatvor* passou para o art. 42b, de 21 a 45 anos. O teto do bloco (45 anos)
  continua; o bloco não mudou.
- **Ruanda.** A Lei 69/2019 (no portal do Ministério) deu nova redação ao art. 92:
  perpétua que não se atenua, e o art. 54 quando o autor era criança. O bloco (`life`)
  continua. A alteração de dezembro de 2023, que a imprensa noticia, não está nas pastas de
  novembro e dezembro de 2023 do Diário no portal.
- **Sudão.** O portal só tem o livro de 2017; nenhuma alteração posterior foi achada nele.
- **Gâmbia.** A Assembleia Nacional registra o projeto como "Assented" (terceira leitura em
  28/03/2025); não dá a data de entrada em vigor.

- **Portal sem veto, do mesmo governo que veda.** O `robots.txt` do Diário Oficial
  holandês não veda agentes de IA; o da base consolidada (`wetten.overheid.nl`), mantida
  pelo mesmo órgão (KOOP), veda. A sessão leu o Diário e não a base. A regra do `AGENTS.md`
  é por portal; ler o Diário é **escolha a revisar pelo dono** (`CHANGELOG.md`).
- **Texto aprovado pelo parlamento, não o publicado.** Na Bélgica, a lei como publicada no
  *Moniteur belge* está no `ejustice.just.fgov.be`, que veda os caminhos das leis. O texto
  lido é o que a Câmara aprovou e submeteu à sanção, idêntico, segundo a própria Câmara, ao
  da segunda leitura; as erratas do *Moniteur* não foram lidas. Escolha a revisar.

### 1.9 O que a quarta volta de 11/11/2026 encontrou (fase 2, sessão 7)

Da máquina do dono, pelo cliente do motor, com o `robots.txt` obedecido (e lido à procura
de agentes de IA vetados pelo nome) e a verificação de certificado ligada, com as raízes
da Mozilla; sha256 no `CHANGELOG.md`. Não havia resposta do dono às escolhas a revisar
nem aprovação para baixar a LEGI; a França não foi tentada.

| País | Portal | O que aconteceu | Resultado |
|---|---|---|---|
| China | `npc.gov.cn` (Boletim do Comitê Permanente, número especial de 2021) | o PDF (19.937.723 bytes) veio inteiro em onze pedidos de 2 MB por `Range`, cada um pelo cliente do motor; um deles voltou cortado e o seguinte retomou do último byte recebido. A Lei Penal está no texto de 2020, emendada até a Emenda XI (26/12/2020), e não traz o crime de genocídio | `penal_code` em rascunho (`npc-gazette`); `domestic_genocide` vazio com `reason`, como na Gâmbia |
| Ucrânia | `zakon.rada.gov.ua` | não respondeu (uma tentativa) | vazio |
| Mianmar | `mlis.gov.mm` | não respondeu (uma tentativa) | vazio |
| Camboja | `moj.gov.kh` | "Request Rejected" (WAF), também no `robots.txt` | vazio; não se contorna |
| Etiópia | `ethiopar.net` (domínio antigo do Parlamento, apontado pelo NATLEX) | domínio estacionado | vazio |

Os outros vazios (Israel, Iraque, Palestina, Síria, Sérvia, Tanzânia, o `penal_code`
holandês) não tiveram fonte oficial nova: a busca na web, só como índice (regra 4), deu
cópias da WIPO, do NATLEX, de ONGs e de editoras, que não entram.

Nos já lidos, só o que a fonte oficial diz:

- **Ruanda.** As pastas do Diário Oficial no portal do Ministério, de março a dezembro de
  2023 e de março a dezembro de 2024 (não há pastas de janeiro e fevereiro), não têm, pelo
  nome dos arquivos, nenhuma lei que altere a Lei 68/2018. A alteração de dezembro de 2023
  continua sem fonte oficial.
- **Sudão.** O índice do livro de leis tem o mesmo sha256 da sessão 5: nenhuma alteração
  posterior a 2017 no portal.
- **Gâmbia.** A ficha da Assembleia continua "Assented", sem data de entrada em vigor. O
  site do Ministério não foi lido de novo: a cadeia pelo AIA é escolha que espera o dono.

- **Pedido por partes não contorna nada.** O servidor chinês cortou o arquivo inteiro
  perto dos 14 MB nas duas tentativas da sessão 6. O cabeçalho `Range` é HTTP comum, e o
  servidor respondeu 206 a cada parte; cada parte passou pelo `robots.txt` e pelo limite do
  cliente. É escolha a revisar pelo dono (`CHANGELOG.md`).

## Função 2: notícias

### 2.1 Resumo

| Fonte | Conf. | Entrega | Licença / termos | `robots.txt` | API e limites | Línguas | Janela | Custo | Veredito |
|---|---|---|---|---|---|---|---|---|---|
| **GDELT DOC 2.0 API** | B (índice) | lista de artigos (URL, título, data, domínio, língua, país da fonte) em JSON/CSV/RSS; nunca texto | "unlimited and unrestricted use … without fee"; **citação obrigatória** ao GDELT (`about.html#termsofuse`) | `api.gdeltproject.org/robots.txt` → 404; `www.gdeltproject.org` só proíbe `/data/` | sem chave; **1 requisição a cada 5 s por IP** (mensagem literal do servidor: "Please limit requests to one every 5 seconds… All high-traffic users should switch to our ngrams dataset"); `maxrecords` até 250; operadores `sourcelang:`, `sourcecountry:`, `theme:`, `domain:` dentro de `query`; modo `timelinevol` dá a contagem por dia | 65 línguas traduzidas, busca em inglês | docs dizem "3 meses", mas a consulta com `startdatetime=20190101` **devolveu artigo de 04/01/2019**: cobre desde 2017 | grátis | **Espinha da função 2 no MVP**, com o adaptador do Alétheia (que já consulta dia a dia e refatia em 6 h) e `rate_limit_per_minute: 12` (= 5 s) |
| **GDELT GKG 2.1** (arquivos de 15 min) | B | CSV zipado a cada 15 min: URL, data, temas (`V2THEMES`), tom, locais, pessoas; sem texto; arquivo inglês ~5 MB/1.191 linhas, tradução ~12 MB/3.027 linhas | idem | `data.gdeltproject.org/robots.txt` → 404 | download HTTP direto, sem chave; `lastupdate.txt` e `lastupdate-translation.txt` (este apontou para arquivo ainda não publicado → 404 transitório) | inglês + "translation" (47 línguas-fonte vistas num arquivo) | desde 02/2015 | grátis; **~1,5 GB/dia** de download (192 arquivos) | **Fase 2**, se o Recenseador mostrar truncamento da DOC API: sem teto de 250 e com os temas já marcados |
| **Temas GKG** | — | `LOOKUP-GKGTHEMES.TXT` (59.315 temas): **`WB_2509_GENOCIDE`** (2,29 M ocorrências), `WB_2508_ETHNIC_CLEANSING` (438 k), `WB_2510_WAR_CRIMES`, `WB_2513_CRIMES_AGAINST_HUMANITY`, `SELF_IDENTIFIED_ATROCITY`, família `CRISISLEX_*`; não há tema "GENOCIDE" puro | — | — | — | — | — | — | usar `theme:WB_2509_GENOCIDE` na DOC API como segundo canal, ao lado da busca por termo |
| **GDELT no BigQuery** | B | SQL sobre GKG e eventos completos | dados abertos; BigQuery sob termos Google Cloud | — | conta Google Cloud; *sandbox* sem cartão: 1 TiB de consulta/mês; acima, US$ 6,25/TiB; **uma varredura do GKG inteiro custa vários TiB** | idem | desde 2015 | grátis até 1 TiB/mês | **Fora** do fluxo (conta Google, custo imprevisível); útil para pesquisa pontual |
| **GDELT Web NGrams / TOC** | B | TOC por minuto (id, data, língua, título, URL) + 4-gramas; sem texto | idem | — | sem chave; arquivo por minuto | multilíngue | "temporário" segundo o blog (30/06/2026) | grátis | **Não** (status temporário) |
| **Media Cloud** | B | `story_list` por cliente Python: URL, título, data, língua, fonte; sem texto ("can't be released because of copyright") | termos de 16/05/2023: plataforma não dá permissão sobre conteúdo de terceiros; saídas podem ser redistribuídas; atribuição recomendada; "best fitted to academic, nonprofit, and journalistic research" | `www` vazio; `search` é SPA | chave gratuita (cadastro); **4.000 req/semana**; alguns endpoints 2 req/min | ~19 línguas de busca; 200 M+ *stories* | por fonte, desde o início da coleta do RSS dela | grátis (acadêmico) | **Fase 2**: segundo canal independente para a estimativa de cobertura (como o Alétheia faz com Crossref × OpenAlex); não testado ao vivo (exige conta) |
| **Europe Media Monitor / NewsBrief** | A | historicamente *clusters* de manchetes com RSS por categoria; **o site novo (`media-monitor.europa.eu`) é SPA** e os endpoints RSS antigos devolvem HTML ou 403 | CC BY 4.0 para conteúdo da UE; manchetes são de terceiros | `emm.newsbrief.eu` → 403; `media-monitor.europa.eu` → 500: **não lidos** | nenhuma API documentada encontrada | "300.000 artigos/dia em até 70 línguas" (data.europa.eu) | não documentada | grátis | **Incerto**; inspecionar em navegador na primeira sessão; se houver RSS no domínio novo, entra |
| **ReliefWeb API v2** | A | JSON: título, URL, origem, datas, língua, fonte (tipo), formato, país, tema | "Anyone may use the ReliefWeb API"; respeitar direitos das fontes; termos da ONU | `api.reliefweb.int`: `Disallow: /` (bloqueia *crawlers* da API; o uso é por `appname`) | **`appname` pré-aprovado obrigatório** (formulário; sem ele, 403); 1.000 itens/chamada; **10.000 chamadas/dia** | multilíngue; cobertura humanitária global (ONU, ONGs, mídia parceira) | desde 1996; via API desde 2011 | grátis | **Sim, fase 1**: pedir o `appname` na primeira semana; é o canal das comissões de inquérito e dos comunicados de ONG |
| **UN News RSS** | A | RSS com 30 itens por *feed* | termos da ONU (uso pessoal não comercial, sem redistribuir) | só bloqueia `/core`, `/search`, `/user`; **sem crawl-delay** | sem API | **10 línguas verificadas** (`/feed/subscribe/{en,fr,es,ru,zh,ar,pt,sw,hi,ur}/news/all/rss.xml`); fr/ru/pt/sw vêm gzip sem cabeçalho | só os 30 últimos | grátis | **Sim, fase 1** (o adaptador `rss` do Alétheia precisa tratar gzip sem `Content-Encoding`) |
| **Reuters** | A | **sem RSS público** (`/tools/rss` → 401) | cabeçalho do `robots.txt`: coleta automatizada "prohibited unless you have prior written consent" | `User-agent: *` → `Disallow: /` | nenhuma | — | — | licenciamento pago | **Inviável** |
| **AP** | A | *feeds* → 403 | ToS → 403 (não lido) | `Disallow: /*.rss`, `/api/v2/feed/`; veta CCBot, GPTBot, ClaudeBot | nenhuma | — | — | licença AP | **Inviável** |
| **AFP** | A | `/en/rss` → 403 | não lido | não lido (403) | nenhuma | — | — | pago | **Inviável** |
| **BBC** | A | RSS por serviço: world (27), arabic (24), mundo (34), russian (39), persian (33), swahili (45), hindi (35) | termos §15: pode-se usar o *feed* com crédito; "you're not allowed to pluck metadata from our content or RSS *feeds*" para outros fins; uso comercial exige permissão | `feeds.bbci.co.uk` só caminhos legados; `www.bbc.com` sem bloqueio geral | — | ~40 línguas do World Service | só recentes | grátis (não comercial) | **Sim, com a leitura estrita do §15**: listar pelo *feed* e ler a página; guardar só título, URL, data (que é o uso de *feed*) |
| **Al Jazeera** | A | RSS en (25) e ar (25) | cl. 6: proíbe autorizar "text or data mining, or web *scraping*"; uso pessoal não comercial | `User-agent: *` só bloqueia `/api`, `/search`; **veta anthropic-ai, ClaudeBot, GPTBot, CCBot** | — | en, ar | recentes | grátis | **Só metadados do feed** (sem ler a página: a cláusula de TDM veta); nível máximo 2 |
| **Deutsche Welle** | A | RSS en (120), ar (45), es (21), ru (75); fa/fr/sw com 0 itens | página oficial de RSS → 404; sem cláusula de *scraping* lida | `rss.dw.com` livre; `www.dw.com` veta anthropic-ai, CCBot | — | ~30 línguas | recentes | grátis | **Sim** |
| **France 24** | A | RSS en, es, ar (22–24); fr | "All rights reserved"; licenciamento via francemm.com | `User-agent: *` tudo permitido; **veta Claude-Code, ClaudeBot, anthropic-ai, ChatGPT-User** | — | en, fr, es, ar | recentes | grátis | **Sim** |
| **EFE** | A | *feeds* → **HTTP 500** | aviso legal: **reserva expressa de TDM** (art. 67.3 RDL 24/2021) | permite | — | es | — | — | **Fora** (sem *feed* e com opt-out) |
| **Agência Brasil** | A | RSS internacional (10 itens) | reprodução autorizada com fonte, sem fim comercial | **`Crawl-delay: 10`** | — | pt (há en/es) | recentes | grátis | **Sim** |
| **Xinhua** | A (estatal) | RSS en (20) | "All rights reserved" | `english.news.cn` → 404 | — | en (+) | recentes | grátis | sim, marcado como estatal |
| **Anadolu** | A (estatal) | RSS en, ar, fr, ru (30 cada) | termos → "Content not found" | `Allow: /`, `Disallow: /api/` | — | 13 línguas | recentes | grátis | sim, marcado como estatal |
| **TASS** | A (estatal) | RSS en (100) | cl. 4.5 **proíbe** inclusão "into… RSS *feeds*, creation of interactive databases"; 5.3.3 proíbe programas automáticos | `Disallow: /search` | — | en, ru | recentes | grátis | **Fora** (termos hostis a base de dados) |
| **The Guardian** | A | RSS world (45); **API** Open Platform | ToS proíbe *scraper* sem autorização; API: 500 req/dia e **"must not keep any OP Content for longer than 24 hours"** | permite seções e RSS | API Developer grátis, não comercial | en | API desde 1999 | grátis | **RSS sim; API não** (retenção de 24 h é incompatível com arquivo) |
| **Le Monde** | A | RSS une (16), international (20) | CGU atrás de desafio anti-robô (não lida) | permite seções; bloqueia `/ws`, `/api`, `/recherche` | — | fr, en | recentes | grátis | sim, *feeds*; termos a reler em navegador |
| **El País** | A | RSS MRSS (88) e portada (21) | aviso legal: **reserva expressa de TDM** (art. 67.3 RDL 24/2021) | veta ClaudeBot, Claude-User, CCBot; `feeds.elpais.com/robots.txt` → 403 | — | es | recentes | grátis | **Só metadados do feed**, sem ler a página |
| **JusticeInfo.net** | B | RSS en, fr (10 cada) | textos republicáveis com fonte, sem uso comercial (exceto despachos AFP) | só `/*?s=*` | — | fr, en (+ es, uk, ru, ar parciais) | recentes | grátis | **Sim, fase 1**: especializado em justiça transicional |
| **Genocide Watch** | C | RSS Wix (20): *reposts* e alertas | sem termos | `Allow: /` | — | en | recentes | grátis | sim, confiança C |
| **Early Warning Project** (USHMM) | B | avaliação anual de risco; dados em GitHub (licença não verificada) | não localizada | só `/cms`, `/login` | sem *feed* | en | anual | grátis | **apontar**, não coletar (o Astraea não é alerta precoce) |
| **UN Office on Genocide Prevention** | A | — | termos da ONU | `un.org`: `Crawl-delay: 10` | — | — | — | — | **não verificado**: a URL entra em *loop* de redirecionamento 302 |
| **Human Rights Watch** | B | RSS en, ar, fr, es (20 cada) | publicações sob Creative Commons (crédito, não comercial, sem derivados); *linkar* é livre | permite | — | 9 línguas | recentes | grátis | **Sim** |
| **Anistia Internacional** | B | RSS en, fr, es, ar (12 cada) | proíbe "automated tools, *scraping*, data-mining… unless we have allowed this or the law permits it" | **`Crawl-Delay: 5`** | — | 7+ línguas | recentes | grátis | **Só metadados do feed** (a cláusula não escreve que o *feed* é permitido) |
| **Crisis Group / CrisisWatch** | B | RSS geral (10); CrisisWatch RSS → 403 | sem cláusula explícita de *scraping* | Drupal padrão | — | en (+) | mensal | grátis | sim, *feed* geral |
| **Minority Rights Group** | B | *feed* → **403** (Cloudflare) | não lidos | veta ClaudeBot, CCBot, GPTBot, anthropic-ai | — | en | — | — | **não verificado**; repetir de outra rede |
| **ACLED** | B | eventos de conflito (não notícias) | EULA: licença não comercial; **proíbe reproduzir, redistribuir ou derivar**; proíbe uso como "training data, embeddings, or knowledge-base input"; "Scraping and crawling the Site is prohibited" | Drupal padrão | conta + OAuth; API só a partir do nível Research | global | desde 1997 | grátis para pesquisa | **Fora** (incompatível com projeto aberto) |
| **Common Crawl CC-NEWS** | B | WARC completos com HTML integral | respeitar direitos de terceiros; proíbe coletar dados pessoais | `data.commoncrawl.org`: `Disallow: /` (é um balde de dados) | sem conta; *rate limiting* desde 2023 | multilíngue (~50% dos domínios perdidos por bloqueio ao CCBot) | desde 08/2016 | **~395 GB/mês** a baixar e processar (369 WARCs × 1,07 GB em 10/2026) | **Inviável sem servidor** |
| **Google News RSS** | — | RSS de busca (100 itens) responde | ToS proíbe acesso automatizado contra o `robots.txt` | **`Disallow: /`** com `Allow` só para `/`, `/home`, `/topics/`, `/publications/`, `/stories/`, `/swg/`, `/about`: **`/rss/` não está permitido** | — | todas | dias | grátis | **Vetado por `robots.txt`** (política do Alétheia, mantida) |
| **Bing News API** | — | — | — | — | **aposentada em 11/08/2025** | — | — | — | inexistente |
| **NewsAPI.org** | — | JSON | Developer: só desenvolvimento e teste; termos: "may not publicly release or disclose any data"; proíbe "competing news database" | `Disallow: /v1/, /v2/` | 100 req/dia grátis, atraso 24 h; Business US$ 449/mês | ~14 | 1 mês / 5 anos | US$ 0–1.749/mês | **Fora** (cláusulas impedem publicar) |
| **GNews** | — | JSON | Free "non-commercial"; termos → 404 | `Disallow: /api` | 100 req/dia, 10 artigos/req, atraso 12 h; Essential € 49,99/mês | ~22 | 30 dias / desde 2020 | € 0–249,99/mês | **Fora** |
| **Event Registry / NewsAPI.ai** | B | JSON de artigos e eventos | Free: não pode servir a projeto "that produces commercial or institutional value"; §6 proíbe redistribuir os dados "as such"; permite exibir manchete, trecho e *link* | bloqueia `/article`, `/event`, `/api` | Free 2.000 *tokens*; 5K US$ 90/mês | 50+ línguas, 150 k fontes | desde 2014 | US$ 0–90+/mês | **Fora no MVP**; única API comercial cujos termos permitiriam a tela (manchete + *link*), ao custo de US$ 90/mês |
| **Wikinews** | C | — | CC BY 4.0 | Wikimedia | API | 31 edições | — | — | **Fechado**: todas as edições em modo somente leitura desde 04/05/2026 |
| **Wikipedia Portal:Current events** | C | HTML do portal com itens datados e *links* para fontes, via API `action=parse` | CC BY-SA 4.0 | Wikimedia; `User-Agent` com contato obrigatório; `maxlag` | API grátis | por língua | histórico completo | grátis | **Semente** semanal: itens com "genocide" viram candidatos a situação |

### 2.2 O que isso decide

1. **O GDELT continua sendo a espinha, mas com duas correções ao plano original.**
   (a) O servidor pede **5 segundos entre requisições**: o adaptador do Alétheia já
   respeita isso (`rate_limit_per_minute: 12`), e a rodada semanal com 5 línguas × 7 dias ×
   até 4 fatias de 6 h fica em ~140 requisições, 12 minutos. (b) A janela **não é de
   90 dias**: a consulta a 2019 funcionou, então o retroativo de notícias desde 2017 é
   possível para uma situação promovida, com paciência (o `effective_since` do adaptador
   precisa parar de cortar em 90 dias quando a resposta provar que há dado).
2. **Dois canais no GDELT, não um**: a busca por termo em cada língua (`sourcelang:`) e
   a busca por tema `WB_2509_GENOCIDE`. O **modo `timelinevol`** dá a contagem diária
   por consulta e é a **defesa contra o falso negativo**: o Recenseador compara a
   contagem com o que foi gravado e acusa truncamento no teto de 250. Se truncar com
   frequência, o GKG de 15 minutos (sem teto, com temas) entra na fase 2, ao custo de
   ~1,5 GB/dia de download no *runner*.
3. **A triagem lê o texto da página do veículo**, como no Alétheia, e é aí que entram
   três regras novas: respeitar o bloco `User-agent: *` de cada veículo (os vetos a
   `ClaudeBot`/`anthropic-ai` não se aplicam ao `User-Agent` próprio do Astraea, mas
   o Astraea também não se faz passar por navegador); **respeitar o *opt-out* expresso
   de mineração de texto** (El País, EFE, Al Jazeera cl. 6, Anistia): nesses domínios o
   robô não baixa a página, tria só pelo título e pela descrição do *feed*, e o item
   fica no nível máximo 2 com `reason: "no_text_by_policy"`; e honrar
   `Crawl-delay` (10 s em `un.org` e na Agência Brasil, 5 s na Anistia).
4. **RSS na fase 1**: UN News (10 línguas), BBC World Service (várias línguas, dentro do
   §15), DW, France 24, Agência Brasil, Guardian, Le Monde, JusticeInfo, HRW, Crisis
   Group, Genocide Watch; Xinhua e Anadolu marcados como estatais em `sources.json`.
   Fora por termos: Reuters, AP, AFP, TASS, Google News, Guardian API, ACLED, NewsAPI,
   GNews. Fora por custo: Common Crawl, BigQuery.
5. **ReliefWeb entra na fase 1** depois do pedido de `appname` (formulário; grátis):
   é o canal dos relatórios de comissões de inquérito e comunicados humanitários que
   usam a palavra, com metadados limpos e sem *scraping*.
6. **Media Cloud na fase 2** como segundo canal independente, para que a estimativa de
   cobertura por captura e recaptura (herdada do Alétheia) tenha dois canais
   comparáveis por língua.
7. **EMM e Minority Rights** pedem nova sondagem em navegador e de outra rede.

### 2.3 O que a sondagem não conseguiu

EMM/NewsBrief (SPA, robots 500); termos de Reuters (401), AP (403), AFP (403), Le
Monde (desafio JS), Anadolu (404), GNews (404), ReliefWeb (página só com JS),
`feeds.elpais.com/robots.txt` (403), `tass.ru` (desafio); DW sem página oficial de
RSS; GDELT DOC API sob limitação durante o teste (só 1 de 7 chamadas devolveu dados:
`sourcelang:arabic`, `theme:` e `maxrecords` não confirmados ao vivo); codebook GKG
2.1 em PDF não legível; `lastupdate-translation.txt` apontando para arquivo ainda
inexistente; UN Office on Genocide Prevention em *loop* 302; Early Warning Project
sem página de *downloads*; Genocide Watch `/alerts` e CrisisWatch RSS; Media Cloud
API ao vivo (exige conta).

## Função 3: decisões de tribunais internacionais

### 3.1 Resumo

| Fonte | Conf. | Canal verificado | Formato | `robots.txt` | Termos | Línguas | Freq. | Bloqueio | Veredito |
|---|---|---|---|---|---|---|---|---|---|
| **CIJ** (icj-cij.org) | A | lista HTML de *press releases* e página de caso com abas (ordens, julgamentos); **sem RSS** (`/rss.xml` 404); lista de e-mail | HTML + PDF com padrão estável `/sites/default/files/case-related/{n}/{n}-AAAAMMDD-{tipo}-NN-00-{en\|fr}.pdf` | Drupal padrão; sem `crawl-delay`; nada contra robôs | `/disclaimer`: não reproduzir para fins comerciais; "consultation or use … constitutes full acceptance" | EN, FR | irregular; PRs numerados por ano (2026/28 em 04/11) | **PDFs devolvem 403 `cf-mitigated: challenge`** a cliente não-navegador; o HTML responde 200 | **Sim, por `listing`**: listar atos, datas, números de PR e URLs das páginas; o PDF fica como URL, nunca baixado pelo robô |
| **TPI** (icc-cpi.int) | A | **RSS verificados**: `/rss/news/all` e `/rss/records/all` (registro, situação, caso, órgão, data) | HTML (+PDF em `/sites/default/files/CourtRecords/`) | Drupal padrão | `/disclaimer`: uso pessoal não comercial, sem redistribuir; reprodução sem permissão escrita salvo o permitido | EN, FR (+ outras nos registros) | diária | `WebFetch` recebeu 403 em tudo; cliente `curl` identificado recebeu 200 (nginx): bloqueio seletivo por UA/IP de ferramentas | **Sim, por `rss`**: o melhor canal do levantamento |
| **ICC Legal Tools Database** (legal-tools.org) | A | SPA React; URLs `/doc/{id}/`; *backend* JSON em `/api/` não documentado | HTML/PDF | **bloqueia ~40 robôs de IA**, inclusive `ClaudeBot` e `anthropic-ai`; `Content-Signal: ai-train=no`; `crawl-delay: 10` | `/footer/terms-of-use` só por clique "Agree"; **não lido** | EN | contínua | Cloudflare | **Não** na fase 1: API sem documentação, termos não lidos, robôs de IA vetados |
| **IRMCT** (irmct.org) | A | **RSS verificado** `/en/rss.xml` (notícias); UCR (`ucr.irmct.org`) exige **registro e login**; CLD sem API | HTML/PDF | Drupal, `Crawl-delay: 10` | uso pessoal não comercial; reprodução com fonte; UCR "reserves the right to deny … access" | EN, FR, BCS, RW | baixa (mensal) | UCR fechado a anônimos | **RSS do site**; UCR fora (sem conta e sem termos para automação) |
| **TPII** (icty.org), **TPIR** (unictr.irmct.org) | A | listas estáticas de casos; sem RSS | HTML/PDF | Drupal, `Crawl-delay: 10` / `Disallow` de `/search` | iguais ao IRMCT | EN, FR, BCS, RW | estático (fechados em 2017 e 2015) | nenhum | **Carga única à mão** dos casos de genocídio; sem monitor |
| **ECCC** (eccc.gov.kh) | A | sem lista datada; arquivo judicial Next.js (232 mil docs, login "My Session"), sem API visível | HTML/PDF | permite tudo; `archive.` → HTTP 500 | nenhum encontrado | EN, KM, FR | residual desde 01/2023 | nenhum | **Carga única** + verificação esporádica |
| **RSCSL** (rscsl.org) | A | **RSS verificado** `/feed/` (WordPress) | HTML/PDF | permite tudo | só "© All Rights Reserved" | EN | 3–4 itens/ano | nenhum | RSS; sem genocídio no mandato, só para completude |
| **Kosovo Specialist Chambers** (scp-ks.org) | A | **RSS verificados** `/en/news/rss` e `/en/blogs/30/feed`; repositório com filtros, sem API | HTML/PDF | Drupal padrão | `/en/legal-notice`: cópia livre para uso privado, informação e educação, com fonte | EN, SQ, SR | semanal | nenhum | RSS; **não julga genocídio** (fora do MVP) |
| **STL** (encerrado) | — | `stl-tsl.org` **não resolve DNS**; acervo migrou para Stanford Virtual Tribunals | — | não lido (timeout) | Stanford: "publicly available online for free" | EN, FR, AR | nada novo | — | nada a monitorar |
| **Corte IDH** (corteidh.or.cr) | A | comunicados em PDF `/docs/comunicados/cp_NN_AAAA.pdf`; buscador de jurisprudência é aplicação **vLex** sem API pública; RSS não localizado | PDF/HTML | content signals `ai-train=no`; `Allow: /` | **não lidos**: domínio inteiro atrás de Cloudflare `challenge` para qualquer cliente não-navegador | ES (parte EN/PT) | alta | **Cloudflare challenge** em todas as páginas | **Inviável por robô na fase 1**; entra por `listing` curada à mão quando houver ato sobre genocídio |
| **CIDH** (oas.org/es/cidh) | A | lista HTML de comunicados; sem RSS; lista de e-mail | HTML | `Crawl-delay: 3`; proíbe `/decisions/`, `/documents/` | não lidos | ES, EN, PT, FR | quase diária | nenhum | *scraping* leve da lista; baixo rendimento para genocídio |
| **TEDH / HUDOC** | A | **endpoint JSON do próprio site** `hudoc.echr.coe.int/app/query/results?query=…&select=itemid,docname,kpdate,ecli,appno…` (devolve `resultcount` e `results[]`); **RSS verificado** de *press releases*; *feeds* por país e câmara em echr.coe.int/rss-feeds | JSON/HTML/PDF/DOCX | `hudoc`: **não existe** (devolve o HTML do app); `echr.coe.int`: proíbe `/search` | `copyright-and-disclaimer`: reprodução para uso privado, informação e educação, com "© ECHR-CEDH"; comercial com permissão; **nada sobre acesso automatizado** | EN, FR | diária | Cloudflare na frente, serviu 200 | **RSS sim; JSON com parcimônia** (não documentado; consulta testada `genocide` em câmara/grande câmara: 393 resultados) |
| **Corte Africana** (african-court.org, ajudata) | A | **RSS verificado** `/afchpr/feed/`; AJUDATA lista `/decisions`, `/pending`, sumários; sem API; "Follow cases" com CAPTCHA | HTML/PDF | 404 nos dois hosts (não lido) | só "© All Rights Reserved" | EN, FR, AR, PT | 4 sessões/ano | `/wpafc/` → 500 | RSS + *scraping* leve do AJUDATA |
| **Comissão Africana** (achpr.au.int) | A | URLs datadas de *press releases*, decisões e resoluções; `/en/rss.xml` existe mas **mistura 2026 com 2018–2020** | HTML/PDF | content signals `ai-train=no`; comentário de 26/08/2026: um *crawler* enumerando buscas derrubou o banco → `/search` proibido | "Site Terms" → 404 | EN, FR, AR, SW, PT | semanal | Cloudflare (serviu 200) | *scraping* leve das listas, **nunca `/search`**; fonte sensível a automação |
| **TRIAL International** | B | **RSS verificado** `/feed/`; UJAR 2026 em PDF (abril/2026; 86 casos em 20 países) | HTML/PDF | `Crawl-delay: 10` | "Legal Content" não lido | EN, FR | semanal; UJAR anual | nenhum | RSS; UJAR como `listing` anual de jurisdição universal |
| **International Crimes Database** (Asser) | B | `/Cases/ByName`, `/Crimes/Genocide`, `/Case/{id}` (~3.331); sem RSS; ainda atualizado (03/11/2026) | HTML | permite tudo | "© 2013 … All Rights Reserved"; "as is" | EN | irregular | nenhum | *scraping* leve para carga histórica; não monitorar |
| **Open Society Justice Initiative** | B | `/litigation` com filtros; sem RSS; poucas datas | HTML | Drupal padrão | termos → 404 | EN | irregular | Cloudflare (200) | baixo valor; fora |
| **OHCHR / CDH** (ohchr.org) | A | páginas de mandato das comissões de inquérito (`/en/hr-bodies/hrc/co-is`: 15 mandatos) listam relatórios e PRs; `/en/rss.xml` é *feed* genérico; `/en/latest` → 403 | HTML/PDF | Drupal padrão | termos gerais da ONU: uso pessoal não comercial, sem obra derivada sem permissão | EN + AR/FR/ES/RU/ZH | 3 sessões/ano + PRs semanais | Cloudflare `challenge` em partes | *scraping* leve das páginas de mandato (funcionaram); IIMM (`iimm.un.org`) sem RSS |
| **UN Digital Library** | A | busca Invenio devolve **MARCXML**; registros `/record/{id}` | MARCXML/HTML | `Crawl-Delay: 5`; **`Disallow: /search`, `/rss`** | termos da ONU | 6 oficiais | contínua | `/record/` → 202 vazio (challenge JS) | **Não**: a saída existe, mas `/search` é proibido; só por *sitemap* |
| **ODS** (documents.un.org) | A | SPA; `/api/symbol/access` | PDF | **`Disallow: /doc`, `/access`, `/api`** | termos da ONU | 6 oficiais | contínua | só com JS | **Não por política**; `docs.un.org/{lang}/{símbolo}` como URL canônica de metadado |
| **WorldCourts.com** | C | índices por tribunal e ano; **CIJ e TPI param em 2020** | HTML/PDF | `ai-train=no`; `Crawl-delay: 20` | `/terms.htm` cl. 11f **proíbe "data mining, robots or similar"**; cl. 20–21 multa de C$ 10.000 por arquivo | EN | parado | — | **Não** (termos e desatualização) |
| **Oxford Reports on Int. Law** | B | assinatura (Oxford Law Pro) | HTML | proíbe `/search`, `/rest/`; `Crawl-delay: 5` | não lidos (CloudFront challenge) | EN | — | CloudFront | **Não** (pago e bloqueado) |

### 3.2 O que isso decide

1. **O TPI entra por RSS no primeiro dia.** O *feed* de registros judiciais traz
   número do registro, situação, caso e órgão emissor: é exatamente a granularidade
   "um ato por registro" do modelo de dados. O bloqueio ao `WebFetch` e não ao
   `curl` identificado mostra que a identificação do projeto no `User-Agent` importa
   (e que uma política de UA pode mudar: o Arquivista vigia).
2. **A CIJ entra por `listing`**: a página de cada caso pendente (178, 182, 192, 202) e
   a lista de *press releases* são HTML lido sem bloqueio; o PDF do ato fica como URL
   e **não é baixado** (Cloudflare o veta a robôs). Como o Astraea guarda só
   metadados, a restrição não custa nada; o `text_hash` de ato da CIJ fica `null`
   com `reason: "pdf_blocked_to_robots"`.
3. **IRMCT, RSCSL, KSC, Corte Africana e TRIAL entram por RSS** com custo quase zero;
   só IRMCT e Corte Africana têm genocídio no mandato.
4. **A Corte IDH é inviável por robô** (Cloudflare para tudo, buscador terceirizado à
   vLex). Entra por `listing` curada à mão. A alternativa que não se faz: navegador
   automatizado para passar no *challenge*.
5. **A jurisprudência histórica (TPII, TPIR, ECCC) é carga única**, feita à mão a
   partir das listas estáticas de casos, nas situações iniciais.
6. **HUDOC tem um JSON útil e sem termos para ele.** Usar o RSS oficial; o JSON só
   para carga histórica, com limite baixo e identificação, e registrar a decisão.
7. **Legal Tools, UN Digital Library, ODS, WorldCourts e ORIL ficam fora**, cada um
   por motivo de política (robôs vetados, `Disallow`, termos, pagamento), não por
   dificuldade técnica.
8. **As comissões de inquérito da ONU são fonte de `investigation` e `allegation`**, não
   de decisão: entram no Escrivão como páginas de mandato (`listing`), e a URL canônica
   do documento é `docs.un.org/{lang}/{símbolo}`.

### 3.3 Estado dos casos de genocídio em 06/11/2026 (para a carga inicial)

Tudo abaixo vem da página oficial citada, salvo onde marcado "imprensa".

| Caso | Estado | Fonte |
|---|---|---|
| **CIJ 178 — Gâmbia v. Mianmar** (11 intervenientes) | audiências de mérito 12–29/01/2026; **sentença de mérito marcada para 19/11/2026** (PR 2026/27, 03/11/2026) | https://www.icj-cij.org/case/178 |
| **CIJ 192 — África do Sul v. Israel** | contra-memorial de Israel em 12/03/2026 com objeções à jurisdição; Ordem de 21/05/2026: réplica até 22/11/2027, tréplica até 22/05/2029; intervenções em 2026 (Paraguai, Países Baixos, Islândia, Namíbia, EUA, Hungria, Fiji); Colômbia retirou a declaração (PR 2026/24, 22/09/2026) | https://www.icj-cij.org/case/192 |
| **CIJ 182 — Ucrânia v. Rússia** | Ordem de 05/12/2025 admitiu as reconvenções russas; réplica da Ucrânia até 07/12/2026, tréplica até 07/12/2027 | https://www.icj-cij.org/case/182 |
| **CIJ 202 — RDC v. Ruanda** | petição de 26/06/2026 (PR 2026/17); Ordem de 04/08/2026 fixou prazos (PDF bloqueado; prazos não lidos). Segundo Opinio Juris (07/09/2026), invoca o art. IX da Convenção de 1948 (Ruanda retirou a reserva em 2008) alegando genocídio contra hutus refugiados e nyindu: **não confirmado na página da CIJ** | https://www.icj-cij.org/case/202 ; https://opiniojuris.org/2026/09/07/a-new-genocide-convention-case-in-the-icj-drc-v-rwanda-version-3-0/ |
| **CIJ 197 — Sudão v. EAU** | Ordem de 05/05/2025: medidas provisórias rejeitadas (14–2) e **caso removido da lista** (9–7) por falta manifesta de jurisdição (reserva dos EAU ao art. IX) | https://www.icj-cij.org/case/197 |
| **CIJ 193 — Nicarágua v. Alemanha** | audiências sobre objeções preliminares 07–10/09/2026; decisão pendente; o título não fala em genocídio (a imprensa trata como cumplicidade em Gaza) | https://www.icj-cij.org/case/193 |
| **TPI — Darfur** | Al Bashir, único acusado de genocídio no TPI, foragido (dois mandados não executados); Abd-Al-Rahman condenado em 06/10/2025 por 27 crimes contra a humanidade e de guerra (sem genocídio), 20 anos em 09/12/2025, **apelações pendentes**; Banda encerrado em 23/07/2026 | https://www.icc-cpi.int/darfur |
| **ONU — COI sobre o TPO** | 16/09/2025: "Israel has committed genocide in the Gaza Strip"; A/HRC/62/CRP.2 (23/06/2026) e A/81/430 (26/10/2026) reafirmam | https://www.ohchr.org/en/hr-bodies/hrc/co-israel/index |
| **ONU — FFM Sudão** | A/HRC/61/77 (19/02/2026) "hallmarks of genocide in El Fasher"; A/HRC/62/CRP.4 (08/07/2026); A/HRC/63/23 (03/09/2026); A/HRC/65/CRP.1 (28/10/2026) | https://www.ohchr.org/en/hr-bodies/hrc/ffm-sudan/index |
| **ONU — COI Síria, Etiópia** | sem achado de genocídio localizado em 2026; ICHREE (Etiópia) encerrada em 2023 | idem `co-is` |
| **Jurisdição universal** (imprensa, **não verificado em fonte judicial**) | Argentina: mandados por genocídio contra 25 autoridades de Mianmar (13/02/2025); Países Baixos: perpétua a ruandês (28/08/2026); Alemanha: condenação por genocídio iazidi | UJAR 2026 (TRIAL) como fonte de carga |

### 3.4 O que a sondagem não conseguiu

- Texto completo dos termos do TPI e do Legal Tools; relatório do Procurador ao CSNU de
  07/2026 (PDF 403 ao `WebFetch`).
- Corte IDH: nada lido além do `robots.txt`.
- Termos do HUDOC/JSON; `robots.txt` de `ucr.irmct.org`, `archive.eccc.gov.kh`,
  `african-court.org`, `ajudata`, `hudoc` (inexistentes ou com erro).
- OHCHR: lista geral de *press releases* e página própria de termos (404).
- PDFs da CIJ: todos atrás de *challenge*; o PR 2026/17 e a Ordem de 04/08/2026 não
  foram lidos.
- Não sondados: `press.un.org`, Eurojust/Genocide Network, tribunais nacionais.

## Decisões transversais que saem das três sondagens

1. **Identificação própria.** O robô usa `User-Agent: Astraea/<versão>
   (+https://github.com/luccas-amorim/astraea; contato)` e obedece ao bloco
   `User-agent: *`. Vetos nominais a robôs de IA (ClaudeBot, GPTBot, CCBot) **não** o
   alcançam, e ele **não** se apresenta como navegador. O TPI mostrou que isso importa:
   bloqueou o `WebFetch` e serviu o `curl` identificado.
2. **`Content-Signal: ai-train=no`** aparece em vários hosts (Legal Tools, LIIs, Corte
   IDH, Comissão Africana, WorldCourts). O Astraea não treina modelo com nada; o sinal
   fica registrado em `sources.json` e a política de modelo de linguagem (D4 em
   `07-decisoes-pendentes.md`) exclui esses domínios de qualquer rascunho automático.
3. **PDF bloqueado não é dado perdido.** Como só se guardam metadados, o ato da CIJ
   entra com URL, data e número, `text_hash: null` e motivo.
4. **Três fontes-chave exigem gesto humano único:** `appname` do ReliefWeb
   (formulário), chave do Media Cloud (cadastro), e nenhuma outra. Não há chave paga
   no MVP.
5. **Reconferência periódica é parte do sistema:** Legislationline (em
   reconstrução), SHERLOC (taxonomia vazia), EMM (site novo), Library of Congress e
   WorldLII (bloqueio talvez do ambiente) ganham `state: suspended` em `sources.json` com
   data de reconferência, e o Arquivista as reabre.

<!-- Verificação concluída em 06/11/2026 com as três sondagens. -->
