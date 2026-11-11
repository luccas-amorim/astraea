# Changelog

Uma sessão = uma entrada. Datas no fuso de Brasília. Até a v1.0.0 a versão é `0.0.x`
(ver `CONTRIBUTING.md`, "Versão e notas").

## 2026-11-11 — Fase 2, sessão 9: a Sérvia pela Procuradoria, Israel pelo Knesset e o *endpoint* do SHERLOC

Branch `fase2/carga-humana-6`, a partir da `main`. **Não havia resposta às "Escolhas a
revisar"** das sessões 4 a 8, nem bloco carimbado (nenhum `checked_by: human` em
`countries.json`, `situations.json` ou `verification.json`), nem leitura sua do *Wetboek
van Strafrecht*, nem aprovação para baixar a LEGI: o commit próprio das respostas não
existiu, a França não foi tentada e o `penal_code` holandês continua vazio.

**O `countries.yml` com o Cartógrafo ainda não rodou**, e não por *push*, *token* ou
falha: o *cron* é `0 5 1 * *` (dia 1, 05:00 UTC) e hoje é 11/11. A `main` com o Cartógrafo
já está no GitHub (`origin/main` em `84fc107`; CI e Deploy desse *push* estavam na fila
quando a sessão olhou). A primeira execução é a de **01/12/2026**; se quiser antes, é o
botão "Run workflow" do *workflow* Countries (ele aceita `workflow_dispatch`). O
*workflow* não foi tocado. De passagem: o CI do PR #1 do robô (10/11) aparece como falho,
mas **sem nenhum *job*** ("workflow file issue"), e o CI do *merge* na `main` passou; vale
olhar no PR de dezembro se o *check* vem vermelho do mesmo jeito.

**O que mudou no dado.** Os blocos lidos são rascunho, com `checked_by: null`, até o seu
carimbo. Nenhuma `note` (D4 pendente).

| País | `penal_code` | `domestic_genocide` | `max_penalty` | Fonte |
|---|---|---|---|---|
| Sérvia | Krivični zakonik (SG 85/2005) | art. 370 | perpétua | `tuzilastvorz` (B) |
| Israel | חוק העונשין, התשל"ז-1977 | vazio, motivo novo (a lei de 1950 existe e está em vigor; o texto não foi lido) | ausente | `knesset-odata` |
| Iraque, Etiópia, Tanzânia | motivo renovado | idem | ausente | — |
| os outros 19 | sem mudança | sem mudança | sem mudança | — |

Agora são **quinze países com leitura** e **nove vazios** (Camboja, Etiópia, França,
Iraque, Mianmar, Palestina, Síria, Tanzânia, Ucrânia; `02-fontes.md`, 1.11).

**Fontes novas em `sources.json`** (105, eram 103), `function: 1`, `active`,
`robots_checked_on: 2026-11-11`: `tuzilastvorz`, a página de leis da Procuradoria para
Crimes de Guerra da Sérvia, confiança **B**; `knesset-odata`, o serviço de dados abertos do
Knesset, confiança A.

**Leituras desta sessão.** Pelo cliente HTTP do motor, com o `User-Agent` do Astraea, o
`robots.txt` obedecido (e lido à procura de agentes de IA vetados pelo nome; nenhum dos
lidos hoje os veta) e a verificação de certificado ligada, com as raízes da Mozilla
(tamanho em bytes, sha256):

- Sérvia, Procuradoria (`tuzilastvorz.org.rs`): o `robots.txt` 1.706,
  `2a787f20489a257692bad5f16ae5ceb28876cd38d8d9cde9c84a2d3835e30bab`; a página inicial
  81.319, `b69c2d5516521a3d527d6ca72dc899348442980260f13dfd2fc921f93e6e1855`; a página
  "Закони" 45.317, `a933df0429309328a75977a6f5ff66450aed212dce649dd03e541af52fd7a4d1`; o
  Código Penal (`/public/files/pages/2024-10/KRIVIČNI ZAKONIK.pdf`) 870.154,
  `d785a9125e3fa4477d5d60e2df14195d60037cabc12ccf679354145c8f6d79ef`.
- Sérvia, Assembleia: o `robots.txt` 649,
  `5815f6e53c8dba8572276fd9cbc35e022d4b98931b83e90f806b9f5018d38625`; a lei de 2026
  (`/upload/archive/files/lat/pdf/zakoni/14_saziv/2043-26-lat..pdf`) 53.898,
  `56e7a4d8eb1054c9d007484606256eed48b469d692b2ee90ba2c1b817a475e30`.
- Israel, Knesset (`knesset.gov.il/Odata/ParliamentInfo.svc`, `robots.txt` 404): o
  documento do serviço 3.662,
  `406c30cb3ad80c55952eccba30b0c0436b1d07cc914a63496d0b38696371f6ba`; a Lei Penal,
  `KNS_IsraelLaw(2000479)`, 628,
  `31759526e83f4a0e4b2ba3e4b53fdafdb0249572862f11f858258bce8d447d00`; a lei de 1950,
  `KNS_IsraelLaw(2000108)`, 747,
  `7c49c4a40d658291efa58d23bce6bcf35fb54abf23ceb05eb8f986ac87819f82`; os documentos da lei
  de 1950 (`KNS_DocumentIsraelLaw`, nenhum) 111,
  `e92538597cdfb4c97cd21dce0daff9fe3d864bfbf6ab3d222b4c5b4f3dc64538`; as duas buscas por
  nome que acharam os dois registros, 750 e 631 bytes.
- Tanzânia, Ministério (`sheria.go.tz`, `robots.txt` 404): a página inicial 154.235,
  `f953c7b9a462f7a30c965d1df61189f8dc54ff6d7b32412378e45bddd49d17cc`; as publicações
  53.063, `437ff4dab5257d011b969c72424c4628b3f2669bccbe0012cae44ff294136dbf`.
- Sem resposta: `moj.gov.iq` (terceira vez), `fsc.gov.et` (HTTP 503, terceira vez),
  `rjt.gov.rs` (conexão recusada), `lab.pna.ps` (tempo esgotado). Os dois primeiros não se
  tentam mais.
- SHERLOC (`robots.txt` 404): a página da base 520.471,
  `676ef76607d3124ea4040057d364f501d6fa07599a008b2b2b92aa1a7612b791` (a mesma da sessão 8);
  a página da busca 246.138,
  `659e47485a5ea2492baf9a99de7831bafa81444cb8d03535b1ea732744333fa8`; os *scripts*
  `waxs-ng.js` 32.111, `e7c5056f024b1df004f783e3336c31b5c26d8a4ddcbd495cd392d669626ac024`, e
  `legislation-db-controller.js` 25.591,
  `4e23b28b6ffb9d137539313584a33b8d4e9f57af80c7848bab1847a9a36ad655`; o `data.json` sem
  filtro 1.656.730, `67b82beb4cd0db509ae102c8a1cfb8bb1fc4c6eb9631b30057834c9dd43c8870`; com
  o filtro do elemento de intenção 9.144,
  `d03d3906a6749ded86d28910768642540bc606f1e3d797b1bc5234ed9c513001`; com o ato "Killing
  members of the group" 8.964,
  `90cd25df2a9fa4cf5bc64e6dbb1c411e30287224a3925d615ccd7ba40ddf94df`; com o tipo "Sexual
  and gender-based crimes…" 8.973,
  `d45923320a75f0c2c3afafa1919f906954d9ca761748b2925eb9a8a7e707d0cf`.

**O que conferir, país a país.**

- **Sérvia** (abra
  https://www.tuzilastvorz.org.rs/public/files/pages/2024-10/KRIVI%C4%8CNI%20ZAKONIK.pdf):
  - `penal_code`: "Krivični zakonik (Službeni glasnik RS br. 85/2005)", `enacted_year:
    2005` (o *ukaz* de promulgação diz que a Assembleia o aprovou em 29/09/2005),
    `language: sr`, `consolidated_on: null` (o PDF lista os números do Diário até o
    35/2019 e não data a compilação).
  - `domestic_genocide`: art. 370, `year: 2005`, `follows: yes`: "nacionalnu, etničku,
    rasnu ili versku grupu kao takvu", os cinco atos. Dois pontos para o seu juízo: o
    terceiro ato diz "životne uslove koji dovode do potpunog ili delimičnog istrebljenja"
    (condições que *levam* ao extermínio, não "calculadas para"), e o artigo pune quem
    *ordena* e quem *executa*. Se achar que isso não é o art. II, troque para `unknown`
    antes de carimbar.
  - `max_penalty: life`: "kazniće se zatvorom najmanje pet godina ili doživotnim
    zatvorom"; a perpétua (art. 44a) entrou com a alteração 35/2019.
  - **O texto não é oficial**: sem diacríticos (o PDF escreve "kaznie", "odreeno") e com as
    marcas "Tekst pre izmene" de base comercial; **a alteração 94/2024 não está nele** e
    não foi lida. A lei de 2026 (na pasta `zakoni` da Assembleia) muda só os arts. 55a e
    348 a 348g, e não o 370 nem o 44a; o número do Diário dela (63/2026) só aparece em
    fonte secundária. Por isso a confiança B (adiante, "Escolhas").
- **Israel** (abra
  https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_IsraelLaw(2000479)?$format=json):
  - `penal_code`: "חוק העונשין, התשל"ז-1977", `enacted_year: 1977` (publicada em
    04/08/1977, em vigor desde 02/04/1978), `language: he`, `consolidated_on: null` (a
    "LatestPublicationDate", 30/06/2026, é a da última alteração publicada, não a de uma
    compilação). O registro dá título e datas, não o texto.
  - `domestic_genocide`: vazio. O registro `KNS_IsraelLaw(2000108)` dá "חוק בדבר מניעתו
    וענישתו של הפשע השמדת עם, התש"י-1950", publicada em 07/04/1950, sem publicação
    posterior, "תקף" (em vigor); não dá o artigo, a definição nem a pena, e o Knesset não
    lista documento dela. Se quiser que o bloco entre pelo título (`criminalized`,
    `provision: null`, `follows: unknown`), diga.
- **Iraque, Etiópia, Tanzânia**: nada a conferir no valor; os motivos dizem o que foi
  tentado.

**SHERLOC: o *endpoint* e a proposta para o Cartógrafo (nada gravado).** A busca da
página chama
`GET https://sherloc.unodc.org/cld/v3/sherloc/legdb/data.json?lng=en&criteria=<JSON>`; a
resposta tem `found` (o total de entradas), `results` e `facetFields`. **Conta, sim, as
leis por crime**, mas o genocídio não é tipo de crime ali: é subtaxonomia dos crimes
sexuais e de gênero ligados a conflito, com dois campos. Hoje os três filtros deram
`found: 0`, e a base inteira, 14.392. A proposta, se você aprovar:

- trocar a sonda do SHERLOC no `PROBES` pela pergunta ao `data.json` com o filtro
  `legislation.crimeTypes.sgbc-crsvCrimeType.genocideContextualElements.element_s` =
  "Intent to destroy, in whole or in part, a national, ethnical, racial or religious
  group, as such" (o elemento que toda lei de genocídio marcada teria);
- "responde" passa a ser JSON 2xx com a chave `found`; o relatório diz o número
  ("SHERLOC: 0 laws tagged with the genocide intent element");
- `reopens=False` continua: com `found > 0`, o PR mensal diz quantas e você decide se
  reabre (a alternativa é reabrir sozinho quando `found > 0`; não recomendo, porque uma
  contagem não diz de que países nem se a marcação está certa);
- um campo novo no `Probe` (`count`, a chave a contar) e dois testes com respostas
  gravadas: a desta sessão (0) e um caso sintético com 3.

Não mudei o `PROBES`: o pedido manda parar e perguntar.

**Código:** nenhum *script* novo no repositório. O leitor da sessão (o `Client` do motor
com um transporte que aponta as raízes da Mozilla do Git for Windows) e o *script* que
gravou os blocos ficaram na pasta temporária da sessão.

**Bateria:**

- 390 testes passam; `ruff check` e `ruff format --check` limpos.
- `astraea validate-lexicon data/lexicon/*.json` valida os cinco léxicos.
- `python scripts/transform.py --draft --check` passa.
- `python scripts/build_site.py` simula 406 arquivos.
- **`--strict` reprova, de propósito, só pelos rascunhos: 46 campos em 20 registros**
  (eram 42 em 18; 50 achados: 46 da trava 3 e 4 da trava 6). São os 9 status das
  situações e 37 blocos de lei penal que esperam o seu carimbo.
- `config/` ainda não existe.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **A Sérvia por consolidação não oficial em site oficial**, com confiança B. Se preferir
  esperar o texto oficial (o Sistema de Informação Jurídica, por API, é outra escolha
  sua), eu esvazio os três blocos.
- **Israel só pelo registro do Knesset**: o `penal_code` por metadados oficiais; o
  genocídio, não pelo título.
- **A sonda de conteúdo do SHERLOC** (acima).
- As escolhas das sessões 4 a 8 continuam abertas: o SHERLOC fora da reabertura
  automática, a *fixture* sintética do Cartógrafo, o Boletim chinês por `Range`, o
  `enacted_year: 1979` da China, o Diário holandês sem veto, a Bélgica pelo texto da
  Câmara e o `year: 2024`, o veto a agentes de IA, as cadeias pelo AIA (Gâmbia e Sérvia),
  as APIs da Sérvia, os `follows_convention_definition: unknown` (Sudão, Bósnia), o título
  inglês de Ruanda, o `consolidated_on: null` (Alemanha, Rússia), a busca na web como
  índice e o *download* da LEGI.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver o que espera o seu carimbo** (não grava nada):

   ```powershell
   python scripts\stamp.py
   ```

   Deve começar com `37 blocks ready to be stamped`. Se alguma letra hebraica, árabe ou
   chinesa vier trocada por `?`, é só a janela do PowerShell.
2. **Conferir e carimbar**, por país, primeiro em simulação e depois com `--execute` no
   fim:

   ```powershell
   python scripts\stamp.py --field SRB --by "Luccas de Amorim" --read-on 2026-11-12
   ```

   Troque `SRB` por `ISR.penal_code` ou pelos países das sessões anteriores. Se um valor
   estiver errado, **não carimbe**: diga na próxima sessão.
3. **Responder às escolhas**, numa linha cada (a do SHERLOC é "sim" ou "não" à sonda). A
   França só avança com o seu sim à LEGI (1,2 GB), e os Países Baixos com a sua leitura do
   *Wetboek van Strafrecht* no `wetten.overheid.nl` (endereço, título, ano e a data
   "geldend van … t/m …").
4. **Enviar ao GitHub.** O *merge* na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

## 2026-11-11 — Fase 2, sessão 8: a Emenda XII chinesa, sobras da carga humana e o Cartógrafo

Branch `fase2/carga-humana-5`, a partir da `main`. **Não havia resposta às "Escolhas a
revisar"** das sessões 4 a 7, nem bloco carimbado (nenhum `checked_by: human` em
`countries.json` nem em `situations.json`), nem leitura sua do *Wetboek van Strafrecht*,
nem aprovação para baixar a LEGI: o commit próprio das respostas não existiu, a França não
foi tentada e o `penal_code` holandês continua vazio. As escolhas continuam abertas
(adiante, "Escolhas a revisar").

**O que mudou no dado.** Só motivos (`reason`) de blocos vazios; nenhum valor lido mudou,
nenhum bloco novo. Nenhuma `note` (D4 pendente); todo bloco lido continua com
`checked_by: null`.

| País | `penal_code` | `domestic_genocide` | `max_penalty` | O que mudou |
|---|---|---|---|---|
| China | sem mudança | vazio, motivo renovado | ausente | a Emenda XII foi lida, e os Boletins seguintes |
| Sérvia | vazio, motivo renovado | idem | ausente | `slglasnik.com` |
| Iraque | vazio, motivo renovado | idem | ausente | `iraqfsc.iq` |
| Tanzânia | vazio, motivo renovado | idem | ausente | `lrct.go.tz`, `oag.go.tz`, `nps.go.tz` |
| os outros 20 | sem mudança | sem mudança | sem mudança | — |

Continuam **treze países com leitura** e **onze vazios** (`02-fontes.md`, 1.10). Nenhuma
fonte nova em `sources.json` (103): `slglasnik.com` não entrou, porque não serviu de fonte
de nenhum valor.

**Leituras desta sessão.** Pelo cliente HTTP do motor, com o `User-Agent` do Astraea, o
`robots.txt` obedecido (e lido à procura de agentes de IA vetados pelo nome) e a
verificação de certificado ligada, com as raízes da Mozilla (tamanho em bytes, sha256):

- China, `npc.gov.cn` por http (o `robots.txt` não veda agentes de IA): a página inicial
  87.258, `f8c9c414f99abc3ecabe16a5768bb79a532c6fdf8fb850ed06b6e28f91bbf12f` (a mesma da
  sessão 6); o índice dos Boletins (`/wxzlhgb/`) 28.800,
  `2f77bab02dc2a356e141f372c4684bcc4de8cb8980d712f09f3933a4388619d9`; e os Boletins
  inteiros, cada um num pedido só:
  - 2023, nº 7 (`/wxzlhgb/c27214/gb2023/202401/P020240119638254850042.pdf`) 11.674.391, `b618b0adff1517242b1601219fa580133099dc8d1654e1fda05d31f4c123492a`;
  - 2024, nº 1 (a Emenda XII) (`/wxzlhgb/c27214/gb2024/202402/P020240202330064224451.pdf`) 7.282.049, `d0da712ffcf356fe0c1477043fe1e459a8a695e5cbd8928abb437275f056d574`;
  - 2024, nº 2 (`/wxzlhgb/c27214/gb2024/202404/P020240416569776251733.pdf`) 7.805.735, `795c819b4acf181126a5cc5afa9da5c0787ee495fa6db6ae81fe86ee6d6ae223`;
  - 2024, nº 3 (`/wxzlhgb/c27214/gb2024/202406/P020240627409249429110.pdf`) 6.347.402, `4de1426faa6aa99c6c46756ef3ccb7ccd7bbc3ce0fbc75567e8b553c59f5410b`;
  - 2024, nº 4 (`/npc/c2/c30834/202412/P020241223578514715967.pdf`) 6.196.458, `a81c91dfd704a302fc04c77639f96cc6de4a8bb0f6fa2c241a13b12203b9503d`;
  - 2024, nº 5 (`/wxzlhgb/c27214/gb2024/202410/P020241009528032576966.pdf`) 11.985.567, `37710ed379cd2d96c047b47b8762ce778a51664ea9f082b639bc4d18f9efcf62`;
  - 2024, nº 6 (`/npc/c2/c30834/202411/P020241129590892653506.pdf`) 7.316.473, `bd9ef5034a77823622f38316189488694b187b1577513369ece658f5541652fd`;
  - 2025, nº 1 (`/npc/c2/c30834/202501/P020250121307945950324.pdf`) 6.795.719, `eac6dda3419b5296f10785b85a0ec340148ba2cad668f2c642c73a94c5e901e3`;
  - 2025, nº 2 (`/npc/c2/c30834/202504/P020250407512079913904.pdf`) 7.392.466, `56a1672a962477fae64123fc15a7590f3f10bf4b280355e173fa459df1c7303a`;
  - 2025, nº 3 (`/npc/c2/c30834/202505/P020250527348067244443.pdf`) 13.169.780, `f5f5c56f59d8781f7dfd17312406f7691db033576ef6b38ef94bd3c4d140a6e7`;
  - 2025, nº 4 (`/npc/c2/c30834/202508/P020250813598641030534.pdf`) 13.126.708, `c6b24218e474fb68ebcc81503d859b9dee74a76f28a373f4878708bc3acd3d71`;
  - 2025, nº 5 (`/npc/c2/c30834/202510/P020251015315268637401.pdf`) 13.701.325, `98728e8dede0d85ef1774546ead90af246ca1b392bf1ca72b9d939f181da26bb`;
  - 2025, nº 6 (`/npc/c2/c30834/202512/P020251211552547072359.pdf`) 15.268.182, `f6f708efed63788ade9dd2a6df38089c8de7670b99e347099a08e0e8a6175888`;
  - 2026, nº 1 (`/npc/c2/c30834/202602/P020260211598705782373.pdf`) 13.560.312, `2c83b993c415300accca8143ba3743f1413255af79a57d5cf4160f6eb1076007`;
  - 2026, nº 2 (`/npc/c2/c30834/202604/P020260417341841579800.pdf`) 32.710.416, `d3db3844f43dbb0f8881b5187eaa6be0c23c0fd74d4b0c48d48582e28417debf`;
  - 2026, número especial do Código Ambiental (`/npc/c2/c30834/202604/P020260417343768024693.pdf`) 12.145.520, `8cc5278f615371c0ab490de442e307a33664bd2ec409e001622ee6c24c5369a4`;
  - 2026, nº 3 (`/npc/c2/c30834/202605/P020260526519256899719.pdf`) 12.442.987, `14ab2b119b2473100aeee6254eef61582de27ffde7eb58fb448c2408a0bb88d7`;
  - 2026, nº 4 (`/npc/c2/c30834/202608/P020260804592193326881.pdf`) 12.576.314, `66c3819890620afebbebe6f3de7d5c45ba01ce558af846de07732e5e6d813e7b`;
  - 2026, nº 5 (`/npc/c2/c30834/202610/P020261009423157467813.pdf`) 2.631.877, `08ffada735f281eb10972746d01bae9e63a6f1e675ab8629faf093bddfac7b7d`.
- Sérvia: `slglasnik.com` 157.180,
  `30a7c5df8fc381d1d6237748c6e11c77f30a572b06e4b22941065a2690223267`, e a página do Diário
  (`/sluzbena-glasila/sluzbeni-glasnik`) 151.610,
  `55d5d2f64536b368c637115f2f46e477ebf184e430f88a6db4c85d4a5a4e10c8`. O intermediário
  "Sectigo Public Server Authentication CA DV R36" veio do endereço AIA do certificado do
  site (`crt.sectigo.com`, baixado com `curl`, 1.616 bytes em DER, conferido com `openssl verify` contra as
  raízes da Mozilla), sha256
  `8c54c334b66ba4e426772af4a3f9136c19a1aec729fdb28c535c07a5a4ef22e0`.
- Tanzânia: `lrct.go.tz` 75.933,
  `3f5dcec770d1d280d04ec0d95325ae30ec4e80cdaa27857db3e79c1d504a760f`; `oag.go.tz` 121.300,
  `60247e45b601b4459cf8394cecf56ddb3209c8219c86eefdefe01c6df9501557`; `nps.go.tz` 86.380,
  `a7a8dabba35e52fa0407b9b85096882e3c13a17b9a9bb5cda62c42587c518158`.
- Iraque: o `robots.txt` do `iraqfsc.iq` veda tudo; nada além dele foi pedido.
- Mianmar e Camboja: `oag.gov.mm`, `national-assembly.org.kh` e `pmo.gov.kh` não resolvem
  no DNS. Os dois primeiros já constavam como sem DNS: foram tentados de novo por descuido.
- As quatro bases do Cartógrafo: o `robots.txt` do WorldLII 2.676,
  `3073d1e371afb3271c7666148766fedc5145f7d8440f7114062db79b7bd58add` (veda `ClaudeBot`,
  `Claude-Web`, `anthropic-ai`, `GPTBot` e outros pelo nome: a página não foi aberta); a
  página da base do SHERLOC 520.471,
  `676ef76607d3124ea4040057d364f501d6fa07599a008b2b2b92aa1a7612b791`; o Legislationline
  (404 depois de redirecionar para a ODIHR) e a Library of Congress (o próprio
  `robots.txt` bloqueado) não deram página.

**O que conferir, país a país.**

- **China** (abra
  http://www.npc.gov.cn/wxzlhgb/c27214/gb2024/202402/P020240202330064224451.pdf, p. 91 e
  92 do Boletim, na numeração impressa):
  - A Emenda XII ("中华人民共和国刑法修正案（十二）"), aprovada em 29/12/2023 pelo Comitê
    Permanente (Ordem Presidencial nº 18), **em vigor desde 01/03/2024**. Tem oito itens:
    muda os arts. 165, 166 e 169 (gestores de empresas, com um parágrafo novo para as
    empresas privadas) e 387, 390, 391 e 393 (suborno); o item 8 é a vigência. **Não traz
    o crime de genocídio**, nem mexe em artigo que o tocasse.
  - O `penal_code` não mudou: título, `enacted_year: 1979`, `language: zh` e
    `consolidated_on: null` valem igual. O `url` continua o Boletim de 2021, com o texto de
    2020; o texto vigente é esse mais a Emenda XII, e o bloco não afirma consolidação.
  - O `reason` do `domestic_genocide` passou a dizer que a Emenda XII foi lida e que os
    Boletins de 2024 nº 2 a 2026 nº 5 não trazem emenda posterior. Os números de 2025 nº 1 e 2026 nº 1 e 2 citam a Lei Penal só nos relatórios sobre os projetos de deputados ("关于修改刑法的议案"), que não são lei. A busca foi pelo texto extraído dos PDFs (`pdftotext`), por "刑法修正案（十三）", "（十四）" e "修改《中华人民共和国刑法》的决定"; se quiser conferir, o índice de cada ano está em http://www.npc.gov.cn/wxzlhgb/.
- **Sérvia, Iraque, Tanzânia**: nada a conferir no valor; os motivos dizem o que foi
  tentado.

**Código: o Cartógrafo.** Sem decisão sua pendente: ele **cabe no `countries.yml`**, porque
o que muda (`data/sources.json`) também muda o `static/data/quality.json`, o derivado do PR
de países; um *workflow* próprio abriria PRs em conflito, o mesmo motivo que pôs o Cornell
no mensal (`04-arquitetura.md`, "O Cartógrafo, como ficou").

- `scripts/recheck_sources.py`: pergunta uma página de cada base (Legislationline, SHERLOC,
  Library of Congress, WorldLII), pelo cliente do motor; reabre a fonte (`state: active`,
  `robots_checked_on` do dia, `reason` novo) quando ela responde no mesmo *host*, com a marca
  da página e sem desafio; o SHERLOC só é reconferido; fonte descartada fica como está, e
  ativa nunca é suspensa pelo robô. Simulação por padrão, `--execute` para valer, `--only`
  para perguntar a uma só, `--responses` para ler as respostas gravadas (testes).
- `scripts/countries_monthly.py` o roda depois das duas cargas; o PR leva
  `data/sources.json` quando muda; o Cartógrafo sozinho não abre PR quando as duas cargas
  falham, a menos que tenha reaberto uma fonte; falha dele abre issue com explicação
  própria. `countries.yml`: o `git add` inclui `data/sources.json`.
- `astraea/engine/http.py`: `Client.robots()`, o `robots.txt` lido, para a conta dos
  agentes de IA.
- Testes: `tests/test_recheck_sources.py` (14), três novos em
  `tests/test_countries_monthly.py`, um em `tests/test_http.py`. A *fixture*
  (`tests/fixtures/cartographer/responses.json`) é **sintética**: a sessão é modelo, e o
  WorldLII veda agentes de IA. Os testes leem o `sources.json` do repositório com as quatro
  fontes postas de volta em `suspended`, para não fixar o valor do dia.
- Em simulação, de verdade, nas três que não vedam agentes de IA: as três seguem fora
  (Legislationline 404 pela ODIHR; SHERLOC responde, mas não é reaberto; Library of
  Congress bloqueia o `robots.txt`); nada a gravar. A primeira execução de verdade, com o
  WorldLII, é a do `countries.yml` no dia 1 de dezembro, se a `main` estiver no GitHub.

**Bateria:**

- 390 testes passam (eram 372); `ruff check` e `ruff format --check` limpos.
- `astraea validate-lexicon data/lexicon/*.json` valida os cinco léxicos.
- `python scripts/transform.py --draft --check` passa.
- `python scripts/build_site.py` simula 406 arquivos.
- **`--strict` reprova, de propósito, só pelos rascunhos: 42 campos em 18 registros**,
  como na sessão 7 (46 achados: 42 da trava 3 e 4 da trava 6). São os 9 status das
  situações e 33 blocos de lei penal que esperam o seu carimbo.
- `config/` ainda não existe.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **O SHERLOC fora da reabertura automática.** O pedido diz "reabre quando volta a
  responder"; o SHERLOC nunca deixou de responder no navegador, e foi suspenso pelo
  conteúdo. Se preferir que ele reabra quando responder 200, é uma linha (`reopens`).
- **A *fixture* sintética**, e não gravada, pelo veto do WorldLII a agentes de IA.
- **A cadeia da Sérvia pelo AIA**, como na Gâmbia, agora regra do `AGENTS.md`.
- As escolhas das sessões 4 a 7 continuam abertas: o Boletim chinês por partes
  (`Range`), o `enacted_year: 1979` da China, o Diário holandês sem veto, a Bélgica pelo
  texto da Câmara e o `year: 2024`, o veto a agentes de IA, a cadeia da Gâmbia, as APIs da
  Sérvia, os `follows_convention_definition: unknown` (Sudão, Bósnia), o título inglês de
  Ruanda, o `consolidated_on: null` (Alemanha, Rússia), a busca na web como índice e o
  *download* da LEGI.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver o que espera o seu carimbo** (não grava nada):

   ```powershell
   python scripts\stamp.py
   ```

   Deve começar com `33 blocks ready to be stamped`, como na sessão 7. Se algum acento,
   letra árabe ou chinesa vier trocado por `?`, é só a janela do PowerShell.
2. **Conferir e carimbar**, como nas sessões anteriores, por país, primeiro em simulação e
   depois com `--execute` no fim:

   ```powershell
   python scripts\stamp.py --field BRA --by "Luccas de Amorim" --read-on 2026-11-12
   ```

   A ficha do Brasil carimbada é o que falta do "Pronto quando" da fase 2.
3. **Ver o Cartógrafo em simulação** (pergunta às quatro bases e não grava nada):

   ```powershell
   python scripts\recheck_sources.py
   ```

   Deve terminar com `4 sources asked, 0 reopened` e `up to date: data/sources.json`. O
   WorldLII pode demorar uns minutos se não responder: o cliente tenta três vezes.
4. **Responder às escolhas**, na próxima sessão, numa linha cada. A França só avança com o
   seu sim à LEGI (1,2 GB), e os Países Baixos com a sua leitura do *Wetboek van
   Strafrecht* no `wetten.overheid.nl` (endereço, título, ano e a data "geldend van … t/m
   …").
5. **Enviar ao GitHub.** O *merge* na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

## 2026-11-11 — Fase 2, sessão 7: quarta volta da carga humana (a China pelo Boletim da APN)

Branch `fase2/carga-humana-4`, a partir da `main`. **Não havia resposta às "Escolhas a
revisar"** das sessões 4 a 6, nem bloco carimbado (nenhum `checked_by: human` em
`countries.json`), nem leitura sua do *Wetboek van Strafrecht*, nem aprovação para baixar a
LEGI: o passo de aplicá-las ficou vazio, não houve o commit próprio que o pedido previa, e
a França não foi tentada. As escolhas continuam abertas: o Diário holandês sem veto, a
Bélgica pelo texto da Câmara, o veto a agentes de IA, a cadeia da Gâmbia, as APIs da
Sérvia, os `follows_convention_definition: unknown`, o `consolidated_on` e o *download* da
LEGI (nas entradas daquelas sessões).

**O que mudou no dado.** O bloco lido é rascunho, com `checked_by: null`, até o seu
carimbo. Nenhuma `note` (D4 pendente).

| País | `penal_code` | `domestic_genocide` | `max_penalty` | Fonte |
|---|---|---|---|---|
| China | 中华人民共和国刑法 (texto de 2020) | vazio com `reason` (o crime não está na lei) | ausente | `npc-gazette` |
| Ucrânia, Mianmar, Camboja | motivo renovado (três tentativas no dia) | idem | ausente | — |
| Etiópia | motivo renovado (`ethiopar.net` estacionado) | idem | ausente | — |
| os outros 7 vazios | sem mudança | sem mudança | ausente | — |
| os 12 já lidos | sem mudança | sem mudança | sem mudança | — |

Agora são **treze países com leitura** (os doze da sessão 6, mais a China, só com o
`penal_code`) e **onze vazios**. O motivo de cada um está no `reason` do bloco e nas
tabelas do `02-fontes.md`, 1.7 a 1.9.

**Fonte nova em `sources.json`** (103 fontes, eram 102): `npc-gazette`, o Boletim do Comitê
Permanente da Assembleia Popular Nacional, `function: 1`, `A`, `active`,
`robots_checked_on: 2026-11-11`.

**Leituras desta sessão.** Todas pelo cliente HTTP do motor, com o `User-Agent` do Astraea,
o `robots.txt` obedecido (e lido à procura de agentes de IA vetados pelo nome; nenhum dos
lidos hoje os veta) e a verificação de certificado ligada, com as raízes da Mozilla
(tamanho em bytes, sha256):

- China: o `robots.txt` do `npc.gov.cn` (por http) 40,
  `fcccf55444d06a90bbe0d38e34f5bb200ed0e7a193f1c1f126415143ea4e8189`; o Boletim de 2021
  (`npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf`, `Last-Modified`
  24/03/2023) **inteiro**, 19.937.723,
  `2252a75f5549dbd9f902f74c9b9943adfde33729f600c62f3e8c24ea204a5456`. Veio em onze pedidos
  de 2 MB com o cabeçalho `Range`; o servidor respondeu 206 a cada um, e o tamanho total
  que ele declarou bate com o arquivo montado.
- Camboja: o `robots.txt` e a página inicial do `moj.gov.kh` são a mesma página "Request
  Rejected" (266 bytes cada); não se contorna.
- Ucrânia (`zakon.rada.gov.ua`) e Mianmar (`mlis.gov.mm`): uma tentativa cada, sem
  resposta (tempo esgotado na conexão).
- Etiópia: `ethiopar.net` 2.963,
  `9dc2900bcff3911cb126966f933197811756c5bb42be63155aeaf0b786ae7123`, página de domínio
  estacionado.
- Ruanda: a página do Diário Oficial 28.746,
  `312b3e2c99b6e444a6167e33c8751559e1da4efb42dec196545f376c626fd705`; a pasta de 2024 29.437,
  `fe785883f297eeb69f4f2ec21bb2b00e30062cbccfc91712d120d4f7bad4ac19`; e as vinte pastas de
  mês de 2023 e 2024 (março a dezembro de cada ano).
- Sudão: o índice do livro de leis, 36.988,
  `52dccbcfe581206715265f22c03b6de3f76cf1854af1207cbed58efa008f7bf0`, o mesmo da sessão 5.
- Gâmbia: a ficha do projeto na Assembleia (`assembly.gm/bills/362`), 130.396 bytes, como na
  sessão 6; o sha256 muda a cada leitura (a página tem partes dinâmicas), e o texto sobre a
  tramitação é o mesmo.
- As demais sondagens (as pastas de mês de Ruanda, uma por uma, e a busca na web, só como
  índice) ficaram na máquina da sessão e não entram no repositório.

**O que conferir, país a país.** Abra cada endereço no seu navegador.

- **China** (abra
  http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf; o texto de
  2020 vai da p. 1 à 116 do Boletim, e o de 1997, sem as emendas, começa na p. 117):
  - `penal_code`: título "中华人民共和国刑法", `language: zh`. `enacted_year: 1979`: o
    cabeçalho diz "1979年7月1日第五届全国人民代表大会第二次会议通过", e logo depois
    "1997年3月14日第八届全国人民代表大会第五次会议修订". Gravei 1979, o ano da aprovação,
    como na Alemanha (1871); se preferir 1997, o da revisão geral, diga.
    `consolidated_on: null`: o Boletim chama o texto de "2020年修正文本" e o dá como emendado
    até a Emenda XI, aprovada em 26/12/2020; é a data de uma alteração, não da compilação
    (o critério da Alemanha e da Rússia). O número saiu em 15/03/2021. **Alterações
    posteriores à Emenda XI não foram procuradas**: confira se houve alguma (lembro de uma
    Emenda XII, de dezembro de 2023, mas não li fonte dela).
  - `domestic_genocide`: vazio com `reason`. No texto de 2020 não há "灭绝种族" nem
    "种族灭绝", nem outro tipo com os grupos e os atos do art. II da Convenção. `no`
    afirmaria que nenhuma lei chinesa traz o crime, e a leitura de uma lei não sustenta isso
    (`03-modelo-de-dados.md`, como na Gâmbia).
  - `official_url` e `url` são o endereço `http://`: o `https://` do `npc.gov.cn` falha no
    *handshake* (sessão 6).
- **Ruanda**: a alteração de dezembro de 2023 continua sem fonte oficial. Pelo nome dos
  arquivos, nenhuma lei que mude a Lei 68/2018 está nas pastas do Diário de março a
  dezembro de 2023 e de 2024; **não há pastas de janeiro e fevereiro** no portal, e o
  número que a traria pode estar lá. O bloco (`life`, art. 92 na redação da Lei 69/2019)
  continua.
- **Sudão**: nada novo no portal; a Lei 12 de 2020 continua por conferir.
- **Gâmbia**: a Assembleia continua sem a data de entrada em vigor.

**Código:** nenhum *script* novo no repositório. O leitor da sessão (o `Client` do motor,
com um transporte que aponta as raízes da Mozilla do Git for Windows, guarda a parte
recebida de uma resposta cortada e pede o resto por `Range`) ficou na pasta temporária da
sessão.

**Bateria:**

- 372 testes passam; `ruff check` e `ruff format --check` limpos.
- `astraea validate-lexicon data/lexicon/*.json` valida os cinco léxicos.
- `python scripts/transform.py --draft --check` passa.
- `python scripts/build_site.py` simula 406 arquivos.
- **`--strict` reprova, de propósito, só pelos rascunhos: 42 campos em 18 registros**
  (eram 41 em 17). São os 9 status das situações e 33 blocos de lei penal que esperam o
  seu carimbo (travas 3 e 6).
- `config/` ainda não existe.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **O Boletim chinês por partes** (`Range`), depois de o servidor cortar o arquivo inteiro
  duas vezes. Não é desafio a vencer nem bloqueio: cada parte passou pelo `robots.txt` e
  pelo limite do cliente. Se achar que é contornar, eu esvazio o bloco.
- **`enacted_year: 1979`** na China, e não 1997.
- **A busca na web como índice** para achar fonte oficial nova: só apontou cópias da WIPO,
  do NATLEX, de ONGs e de editoras, que não entraram; o único portal oficial que ela
  sugeriu (`ethiopar.net`) está estacionado.
- As escolhas das sessões 4 a 6 continuam abertas, e a LEGI espera o seu sim.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver o que espera o seu carimbo** (não grava nada):

   ```powershell
   python scripts\stamp.py
   ```

   Deve começar com `33 blocks ready to be stamped`. Se algum acento, letra árabe ou
   chinesa vier trocado por `?`, é só a janela do PowerShell: o arquivo está certo.
2. **Conferir e carimbar**, como nas sessões anteriores: a lista "o que conferir", acima;
   depois, por país, primeiro em simulação e depois com `--execute` no fim:

   ```powershell
   python scripts\stamp.py --field CHN.penal_code --by "Luccas de Amorim" --read-on 2026-11-12
   ```

   Troque `CHN.penal_code` pelos países das sessões anteriores, e a data pelo dia da sua
   leitura. Se um valor estiver errado, **não carimbe**: diga na próxima sessão.
3. **Regenerar o derivado e comitar**, como o *script* mostra ao terminar:

   ```powershell
   python scripts\transform.py --draft --execute
   ```

   ```powershell
   git add data\countries.json static\data
   ```

   ```powershell
   git commit -m "Carimba CHN (conferido por Luccas de Amorim em 2026-11-12)"
   ```

   O `git add` pode mostrar o aviso "LF will be replaced by CRLF". É só aviso.
4. **Responder às escolhas**, na próxima sessão, numa linha cada: as desta entrada e as das
   sessões 4 a 6. A França só avança com o seu sim à LEGI (1,2 GB), e os Países Baixos, com
   a sua leitura do *Wetboek van Strafrecht* no `wetten.overheid.nl` (endereço, título, ano
   e a data "geldend van … t/m …").
5. **Enviar ao GitHub.** O *merge* na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

## 2026-11-11 — Fase 2, sessão 6: terceira volta da carga humana (fonte oficial nova)

Branch `fase2/carga-humana-3`, a partir da `main`. **Não havia resposta às "Escolhas a
revisar"** das sessões 4 e 5, nem bloco carimbado, nem leitura sua dos Países Baixos ou da
Bélgica depois do *merge* da sessão 5: o passo de aplicá-las ficou vazio, e as escolhas
continuam abertas (o veto a agentes de IA, a cadeia da Gâmbia, as APIs da Sérvia, os
`follows_convention_definition: unknown` e o `consolidated_on`, nas entradas daquelas
sessões). Por isso não houve o commit próprio que o pedido previa.

**O que mudou no dado.** Os blocos lidos são rascunho, com `checked_by: null`, até o seu
carimbo. Nenhuma `note` (D4 pendente).

| País | `penal_code` | `domestic_genocide` | `max_penalty` | Fonte |
|---|---|---|---|---|
| Bélgica | Code pénal (leis de 29/02/2024) | art. 82 (Livro II) | perpétua | `lachambre` |
| Países Baixos | vazio, motivo novo | Wet internationale misdrijven, art. 3 | perpétua | `officielebekendmakingen` |
| os outros 12 vazios | motivo renovado | motivo renovado | ausente | — |
| os 10 já lidos | sem mudança | sem mudança | sem mudança | — |

Agora são **doze países com leitura** (os dez da sessão 5, mais Bélgica e Países Baixos;
este, sem o `penal_code`) e **doze vazios**. O motivo de cada um está no `reason` do bloco e
na tabela nova do `02-fontes.md`, 1.8.

**Fontes novas em `sources.json`** (102 fontes, eram 100), `function: 1`, `A`, `active`,
`robots_checked_on: 2026-11-11`:

- `officielebekendmakingen`: o Diário Oficial dos Países Baixos (Staatsblad);
- `lachambre`: os documentos parlamentares da Câmara belga.

**Leituras desta sessão.** Todas pelo cliente HTTP do motor, com o `User-Agent` do Astraea,
o `robots.txt` obedecido e a verificação de certificado ligada, com as raízes da Mozilla
(tamanho em bytes, sha256):

- Países Baixos: o `robots.txt` do Diário 196,
  `614ef8ef354c576b6047d8da327a0fbee8d97504c6d598c5bee4cbe00af23006`; o Stb. 2003, 270
  (`zoek.officielebekendmakingen.nl/stb-2003-270.html`) 70.248,
  `a035a513263e45f0ef0ac85429f3421210fa71687215a3741aae1b5fa6d13ab4`.
- Bélgica, Câmara:
  - fichas dos dossiês 55K3374 (Livro I) 71.079,
    `bc38e7c55ae176c723a85d3ddddd1a7ddfe3f537aab15a6f344e0a00ea615b84`; 55K3518 (Livro II)
    73.289, `4b2e4d2d2c64258f939647d52ef8c287fe81b446f9914226de4c5f2ca190e897`; 56K1160 (a
    lei de 2026) 61.001, `8f2b2db4bb4f9709ca10359318bd30d4215c094254ff6216ede0d16cdbb22d6d`;
  - Livro I, texto da segunda leitura (`55K3374010.pdf`) 737.058,
    `890f1f006fc629030b91b33ac1974eff670d526c847f8655e03bee25c899dc1b`, e o do plenário
    (`55K3374012.pdf`, "identique") 78.966,
    `082d36eff370cea1ff6317717b475465882fb75e3d7f2a7b7fe37e7e3a4e6c0c`;
  - Livro II, segunda leitura (`55K3518011.pdf`) 2.855.429,
    `af7fce545f537ab8ddbb3977af685c886acf3a9ad2cae0ca1b553d67f674127b`, e plenário
    (`55K3518013.pdf`, "identique") 77.544,
    `56b127631f716645ba475b187b0e1b837fa5a2a2c63c6b162efc3c13d6bf6c83`;
  - lei de 16/03/2026, segunda leitura (`56K1160010.pdf`) 386.413,
    `cd461d17189cd52781dd135eb7836223638695f8f6b7569bcf50700718a1deb7`, e plenário
    (`56K1160011.pdf`, "identique") 75.399,
    `d4b6142ca6b4d64ea4ed3d13f591c5aba3afc80980e62c57217c2520bfba50fb`.
- Bósnia, consolidação da Procuradoria (`tuzilastvobih.gov.ba/…/Krivicni_zakon_BiH_-_konsolidacija_2023_47_23.pdf`)
  1.170.343, `48534d08870d980df3e236ed5a3249944885db1f5af9bc5a14df4f00db660464`.
- Ruanda, Lei 69/2019 (`minijust.gov.rw/…/Offences_and_penalties_in_general_2019.pdf`)
  5.417.261, `6593f81d44906735e970c62acb176255b861bceea44585292ab9fe3c9d9f3772`; as pastas
  de 2023 do Diário: o ano 29.026,
  `82516bb9fff035b92ded0f613c55a25f17aa67f27cf230f14025377819997934`; novembro 26.402,
  `08879c4b90d7d3eec0fcd71654e11ee1267acced58a26eef4091ee864616c8ff`; dezembro 28.893,
  `ac2310fa606d074a336772ebdad8a25411a30fc31a50885463bd83de8f7c58e8`.
- Gâmbia, a ficha do projeto na Assembleia (`assembly.gm/bills/362`) 130.396,
  `b8ff696b713980086a3e588edd9ea7f6d5bc22fd3b6137da6803ea8910a1c88d`.
- Mianmar, as duas páginas de leis do Supremo (`unionsupremecourt.gov.mm/laws`) 46.445,
  `4b066e861d0a8eac34e3def0c73626e003f18c8b0956253ad80503650c183376`, e 46.285,
  `4839e6d8ce82e6f8b75ba242ae19adfb246f5db7399623357e4098e6ee09cbab`.
- Ucrânia, a página de legislação do Supremo 2.476.820,
  `105a61c55363d4884616b3200aaf65cfdf142b674f80bb43bcf524e8af7821ec`.
- França, a lista da LEGI na DILA 1.322,
  `3cd65fe8296f4e32f545cc1ff76d7455421b8f02a7760dbea1a997582574d41f`.
- China: a página inicial do NPC por http 87.258,
  `f8c9c414f99abc3ecabe16a5768bb79a532c6fdf8fb850ed06b6e28f91bbf12f`, e a página da Lei Penal
  (só um invólucro) 4.458,
  `332b749936fb2e90473740a198a7e1857a7bc544b004f608a76ec797bdc2bc09`. O Boletim de 2021
  (`npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf`, uns 20 MB) veio
  cortado nas duas tentativas (14.075.754 e 14.661.834 bytes); sem arquivo inteiro, não há
  leitura. Fica para a próxima sessão tentar de novo, talvez noutro horário.
- As demais sondagens (páginas iniciais, `robots.txt`, o "Request Rejected" do Camboja, a
  ECCC, os portais que não responderam) ficaram na máquina da sessão e não entram no
  repositório.

**O que conferir, país a país.** Abra cada endereço no seu navegador.

- **Bélgica** (abra https://www.lachambre.be/FLWB/PDF/55/3518/55K3518011.pdf, p. 9 e 10, e
  https://www.lachambre.be/FLWB/PDF/55/3374/55K3374010.pdf, art. 36):
  - `penal_code`: "Code pénal (lois du 29 février 2024 introduisant le livre Ier et le livre
    II du Code pénal)", `enacted_year: 2024`, `language: fr`, `consolidated_on: null`. A
    ficha da Câmara dá as duas leis como de 29/02/2024, publicadas no *Moniteur* de
    08/04/2024 (nº 075). **Entrada em vigor**: o art. 119 do Livro II diz "deux ans après
    le jour de sa publication"; a lei de 16/03/2026 (*Moniteur* de 25/03/2026) fixa 08/04/2026
    para os seus arts. 1 a 124. O `official_url` é o texto da Câmara, não o *Moniteur*
    (adiante, "Escolhas").
  - `domestic_genocide`: art. 82, `year: 2024`, `follows: yes`: "un groupe national,
    ethnique, racial ou religieux comme tel", os cinco atos (1º a 5º), "en temps de paix ou
    en temps de guerre", com remissão expressa à Convenção de 1948.
  - `max_penalty: life`: art. 82, "puni d'une peine de niveau 8"; art. 36 do Livro I, "La
    peine de niveau 8 est constituée de l'emprisonnement à perpétuité" (ou tratamento
    privativo de liberdade de 18 a 20 anos). A lei de 2026 não muda os arts. 36 e 82, e
    revoga só os arts. 3 a 35 e 3 a 118 das duas leis (as alterações a outras leis), não o
    art. 2, que é o Código. **As erratas do *Moniteur*** (28/05/2025 e 19/09/2025 no Livro I;
    03/09/2025 no Livro II) **não foram lidas**.
- **Países Baixos** (abra https://zoek.officielebekendmakingen.nl/stb-2003-270.html):
  - `domestic_genocide`: "Wet van 19 juni 2003, houdende regels met betrekking tot ernstige
    schendingen van het internationaal humanitair recht (Wet internationale misdrijven)",
    `artikel 3`, `year: 2003`, `follows: yes`: "een nationale, etnische of godsdienstige
    groep, dan wel een groep behorend tot een bepaald ras", "als zodanig", os cinco atos
    (a–e). O art. 22 deixa a entrada em vigor para decreto real, que não foi lido.
  - `max_penalty: life`: "levenslange gevangenisstraf of tijdelijke van ten hoogste dertig
    jaren of geldboete van de zesde categorie".
  - **O texto lido é o de 2003.** O `robots.txt` do Diário veda as páginas de resultado de
    busca; alterações posteriores da lei não foram procuradas. A página aponta para a
    versão consolidada no `wetten.overheid.nl`, que esta sessão não lê.
  - `penal_code`: vazio. Se você ler o *Wetboek van Strafrecht* no `wetten.overheid.nl`
    (adiante, "Para você"), eu preparo o bloco.
- **Bósnia** (a conferência que a sessão 5 deixou): na consolidação da Procuradoria até o
  SG 47/23, marcada "PREČIŠĆENI, NEZVANIČNI TEKST", o art. 171 é o mesmo de 2003, e o
  *dugotrajni zatvor* está no art. 42b, "u trajanju od 21 do 45 godina" (era o art. 42(2),
  de 20 a 45). O valor do bloco (45 anos) continua; o bloco não mudou. Na sessão 5, eu
  citei o art. 42(2): ao carimbar, a referência atual é o 42b.
- **Ruanda**: a Lei 69/2019, de 08/11/2019 (Diário especial de 29/11/2019), deu nova
  redação ao art. 92: "life imprisonment that cannot be mitigated by any circumstances",
  e, se o autor era criança, o art. 54. O bloco (`life`) continua. **A alteração de
  dezembro de 2023**, que a imprensa ruandesa noticia, não foi achada nas pastas de
  novembro e dezembro de 2023 do Diário; confira se ela mexe nos arts. 91 e 92.
- **Sudão**: o portal só tem o livro de 2017; a Lei 12 de 2020, que fontes secundárias
  citam, não está nele. Confira se ela mexe nos arts. 27 e 187.
- **Gâmbia**: a Assembleia registra o *Criminal Offences Bill* como "Assented", com a
  terceira leitura em 28/03/2025; a linha "Assented" tem a data de 16/07/2026, que parece
  ser a da atualização da página. A data de entrada em vigor continua sem fonte.

**Código:** nenhum *script* novo no repositório. O leitor da sessão (o `Client` do motor,
com um transporte que aponta as raízes da Mozilla do Git for Windows, e um aviso quando o
`robots.txt` nomeia agentes de IA) ficou na pasta temporária da sessão.

**Bateria:**

- 372 testes passam; `ruff check` e `ruff format --check` limpos.
- `astraea validate-lexicon data/lexicon/*.json` valida os cinco léxicos.
- `python scripts/transform.py --draft --check` passa.
- `python scripts/build_site.py` simula 406 arquivos.
- **`--strict` reprova, de propósito, só pelos rascunhos: 41 campos em 17 registros**
  (eram 36 em 15). São os 9 status das situações e 32 blocos de lei penal que esperam o
  seu carimbo (travas 3 e 6).
- `config/` ainda não existe.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **Ler o Diário Oficial holandês**, cujo `robots.txt` não veda agentes de IA, quando o
  outro portal do mesmo órgão (`wetten.overheid.nl`) veda. A regra do `AGENTS.md` é por
  portal. Se você entender que o veto vale para o governo inteiro, eu esvazio os dois blocos
  dos Países Baixos.
- **Bélgica pelo texto aprovado na Câmara**, e não pelo *Moniteur belge* (que veda os
  caminhos das leis): mesmo texto, segundo a Câmara, mas sem as erratas.
- **`year: 2024` na Bélgica**: o ano do novo Código, embora o genocídio estivesse no art.
  136bis do código antigo desde 2003.
- **A consolidação "não oficial" da Procuradoria da BiH** serviu só para conferir; o bloco
  continua apontando o texto de 2003, no Tribunal.
- **A França pela LEGI** (1,2 GB): se quiser, eu baixo o arquivo inteiro na próxima sessão,
  pelo cliente do motor, e leio só o Code pénal e o art. 211-1.
- As escolhas das sessões 4 e 5 continuam abertas.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver o que espera o seu carimbo** (não grava nada):

   ```powershell
   python scripts\stamp.py
   ```

   Deve começar com `32 blocks ready to be stamped`. Se algum acento ou letra
   árabe vier trocado por `?`, é só a janela do PowerShell: o arquivo está certo.
2. **Conferir e carimbar**, como nas sessões 4 e 5: a lista "o que conferir", acima; depois,
   por país, primeiro em simulação e depois com `--execute` no fim:

   ```powershell
   python scripts\stamp.py --field BEL --by "Luccas de Amorim" --read-on 2026-11-12
   ```

   Troque `BEL` por `NLD`, ou pelos países das sessões anteriores, e a data pelo dia da sua
   leitura. Se um valor estiver errado, **não carimbe**: diga na próxima sessão.
3. **Regenerar o derivado e comitar**, como o *script* mostra ao terminar:

   ```powershell
   python scripts\transform.py --draft --execute
   ```

   ```powershell
   git add data\countries.json static\data
   ```

   ```powershell
   git commit -m "Carimba BEL (conferido por Luccas de Amorim em 2026-11-12)"
   ```

   O `git add` pode mostrar o aviso "LF will be replaced by CRLF". É só aviso.
4. **O Código Penal holandês, se quiser ler você.** No navegador, abra
   https://wetten.overheid.nl e procure "Wetboek van Strafrecht". Anote o endereço, o
   título, o ano e a data da versão consolidada ("geldend van … t/m …"), e me passe na
   próxima sessão. Diga também se a Wet internationale misdrijven, na mesma base, tem
   alguma alteração no art. 3.
5. **Enviar ao GitHub.** O *merge* na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

## 2026-11-11 — Fase 2, sessão 5: segunda tentativa nos 18 vazios da carga humana

Branch `fase2/carga-humana-2`, a partir da `main` (que você já tinha enviado ao GitHub).
Não havia resposta às "Escolhas a revisar" das sessões anteriores nem bloco carimbado
depois do *merge* da sessão 4: o passo de aplicá-las ficou vazio, e as escolhas continuam
abertas nas entradas daquelas sessões.

**O que mudou no dado.** Os blocos lidos são rascunho, com `checked_by: null`, até o seu
carimbo. Nenhuma `note` (D4 pendente).

| País | `penal_code` | `domestic_genocide` | `max_penalty` | Fonte |
|---|---|---|---|---|
| Sudão | القانون الجنائي لسنة 1991 | art. 187 (Lei 15/2009) | morte | `moj-sd` |
| Ruanda | Law N°68/2018 | art. 91 | perpétua | `minijust-rw` |
| Bósnia e Herzegovina | Krivični zakon BiH (SG 3/03) | član 171. | 45 anos | `sudbih` |
| Gâmbia | Criminal Offences Act 2025 | vazio com `reason` (o crime não está na lei) | ausente | `moj-gm` |
| Alemanha | `enacted_year: 1871` (era `null`) | — | — | `gesetze-im-internet` |
| os outros 14 | vazio, motivo de 11/11 | vazio, motivo de 11/11 | ausente | — |

Agora são **dez países com leitura** (Brasil, Alemanha, Argentina, Bangladesh, Rússia,
África do Sul, Sudão, Ruanda, Bósnia, Gâmbia) e **catorze vazios**. O motivo de cada um
está no `reason` do bloco e na tabela nova do `02-fontes.md`, 1.7:

- veda a leitura por modelo ou por robô: Países Baixos (veda agentes de IA pelo nome),
  Bélgica, França, Iraque, China;
- desafia o cliente: Israel, Tanzânia (TanzLII);
- não responde: Ucrânia, Mianmar, Camboja;
- só JavaScript: Sérvia;
- texto que não se extrai: Etiópia (PDF amárico com fonte antiga);
- responde, mas não publica o código: Síria;
- sem portal oficial alcançado: Palestina.

**Os dois casos de certificado** (item 2 do pedido) **não eram da sua rede:**

- **Países Baixos.** A cadeia é válida (Logius → certSIGN Web CA G2 → certSIGN ROOT CA
  G2). O `openssl` a verifica com as raízes da Mozilla; o Python não, porque a raiz
  certSIGN não estava no repositório do Windows que ele consulta. Com as raízes da Mozilla
  e a verificação ligada, o portal respondeu. **Mas o `robots.txt` veda pelo nome os
  agentes de IA**: `ClaudeBot`, `Claude-Web`, `anthropic-ai`, `ChatGPT-User`,
  `MistralAI-User`, `rag-kennisbank` e outros. Quem lê na carga humana é um modelo; não li
  nenhuma lei holandesa. O país espera a sua leitura (adiante, "Para você").
- **Gâmbia.** O certificado do site é `*.gov.gm`, que não cobre `www.moj.gov.gm` (dois
  níveis), e o servidor não envia o intermediário RapidSSL. Baixei o intermediário do
  endereço que o próprio certificado declara (AIA, `cacerts.rapidssl.com`), conferi com
  `openssl verify` que ele sobe até a raiz DigiCert Global Root G2 da Mozilla e li
  `moj.gov.gm`, sem `www`, com a verificação de nome e de cadeia ligada.
- O cliente do motor não mudou: as duas leituras usaram, num *script* fora do
  repositório, o mesmo `Client` com um transporte que aponta outro arquivo de raízes.

**Fontes novas em `sources.json`** (100 fontes, eram 96). Todas `function: 1`, `A`,
`active`, `robots_checked_on: 2026-11-11`:

- `moj-sd`: Ministério da Justiça do Sudão, leis em *e-book*;
- `minijust-rw`: Diário Oficial de Ruanda;
- `sudbih`: Tribunal da Bósnia e Herzegovina, lista de leis penais;
- `moj-gm`: Ministério da Justiça da Gâmbia.

**Leituras desta sessão.** Todas pelo cliente HTTP do motor, com o `User-Agent` do Astraea
e o `robots.txt` obedecido (tamanho em bytes, sha256):

- Sudão, `moj.gov.sd/sudanlaws/epub/EPUB/xhtml/s53c19.html` (o Código Penal) 230.553,
  `ae0541b579d8322aec3db2a66e307f1d22d2d91f7539b4afd149db2e13ad53ba`; o índice do livro,
  `…/xhtml/contents.html` 36.988,
  `52dccbcfe581206715265f22c03b6de3f76cf1854af1207cbed58efa008f7bf0`.
- Ruanda, Diário Oficial especial de 27/09/2018 (`…/Special_of_27.09.2018.pdf`)
  2.307.767, `ea590264dac93a2ed21e5a4a070290c74783e654178c15db0d3fe669b9686ad9`.
- Bósnia, `sudbih.gov.ba/Content/Read/krivicno-pravo` 109.140,
  `9369a8eedcf9baaec42e9620b90ef5df77f7e587352e00ff18344ca97d18992d`; o Código, SG 3/03
  (`/Content/Open/3335…`) 690.363,
  `5d161c5b1a66fb22b3bbb18e7aa4b7d44214713fea1232399be8b905436d4de1`.
- Gâmbia, *Criminal Offences Act 2025* (PDF) 745.821,
  `e74b0064b7f5d63cf1c2e09748c940135e6afc87e24b34738e2c845f709125c8`.
- Alemanha, `gesetze-im-internet.de/stgb/BJNR001270871.html` 1.100.667,
  `e07660f5893a8f0e8036e29a38fdd8cbc8fc8ca6002b1ceb26a6c46a4e51f818`.
- Etiópia, o PDF amárico (`justice.gov.et/…/414-Criminal-Code-New-Amharic.pdf`)
  1.486.760, `b97ed7b148f3d7fe2c85556628fcdde46d9b497f47abb8cb0a108d29b12d9a26`: baixado,
  mas sem texto legível; não sustenta nenhum valor.
- Países Baixos, só o `robots.txt` 5.918,
  `523a97e74fd63d9a0b104882ade1a44e3732b5e35e14d1ae4825b5efe548d9a1`.
- As demais sondagens (páginas iniciais, `robots.txt`, buscas nos sites, a configuração da
  aplicação sérvia) ficaram na máquina da sessão e não entram no repositório.

**O que conferir, país a país.** Abra cada endereço no seu navegador.

- **Sudão** (abra https://moj.gov.sd/sudanlaws/epub/EPUB/xhtml/s53c19.html; o leitor em
  https://moj.gov.sd/sudanlaws/ mostra o mesmo livro):
  - `penal_code`: título "القانون الجنائي لسنة 1991", `enacted_year: 1991`, `language: ar`.
    `consolidated_on: null`: o livro tem `Last-Modified` de 01/08/2017 e não data a
    versão; a lei de alteração mais recente que as notas citam é a 21 de 2015 (nota 22).
    **Alteração posterior a 2017 não está neste texto**: confira se os arts. 27 e 187
    mudaram.
  - `domestic_genocide`: `provision: المادة 187`, `year: 2009`. O Título 18 entrou pela Lei
    15 de 2009 (nota 23). `follows: unknown`: o artigo tem os quatro grupos, "بصفتها تلك"
    (*as such*) e os cinco atos, mas **acrescenta um elemento de contexto**, "في سياق سلوك
    منهجي واسع موجه ضد تلك الجماعة" (no contexto de conduta sistemática e ampla dirigida
    contra o grupo), que a Convenção não exige. Pode ser `narrower`; a decisão é sua.
  - `max_penalty: death`: "يعاقب بالإعدام أو بالسجن المؤبد أو بأي عقوبة أقل" (morte,
    perpétua ou pena menor). O Sudão é retencionista; a trava 10 não pede nota.
- **Ruanda** (abra https://www.minijust.gov.rw/official-gazette, pasta de 2018, número
  especial de 27/09/2018):
  - `penal_code`: o Diário é trilíngue; gravei o título da coluna inglesa, "Law N°68/2018
    of 30/08/2018 determining offences and penalties in general", com `language: en`. Se
    preferir o kinyarwanda ("Itegeko N°68/2018 ryo ku wa 30/08/2018 riteganya ibyaha
    n'ibihano muri rusange", `rw`), diga. `enacted_year: 2018`. Alterações posteriores
    da lei não foram procuradas.
  - `domestic_genocide`: art. 91, `year: 2018`, `follows: yes` (grupo "national, ethnic,
    racial or religious … as such", os cinco atos, "in time of peace or in time of war").
    O art. 93 pune conspiração, planejamento, incitação, tentativa e cumplicidade.
  - `max_penalty: life`: art. 92, "life imprisonment that cannot be mitigated by any
    circumstances".
- **Bósnia e Herzegovina** (abra https://www.sudbih.gov.ba/Content/Read/krivicno-pravo e o
  primeiro PDF, "Krivični zakon BiH - Službeni glasnik BiH br. 3/03"):
  - `penal_code`: `enacted_year: 2003` (imposto pela Decisão 101/03 do Alto Representante;
    em vigor em 01/03/2003), `language: bs`. **O texto lido é o original de 2003.** A
    página do Tribunal lista as alterações só até o SG 61/04; as posteriores não estão
    ali, e os arts. 42 e 171 podem ter mudado. A extração do PDF perde os diacríticos; o
    título vem da lista do Tribunal.
  - `domestic_genocide`: `član 171.`, `follows: unknown`. Tem os quatro grupos e os cinco
    atos, mas **não tem o "como tal"** (*as such*) da Convenção.
  - `max_penalty: years, 45`: o art. 171 comina "kaznom zatvora najmanje deset godina ili
    kaznom dugotrajnog zatvora", e o art. 42(2) põe o *dugotrajni zatvor* entre 20 e 45
    anos.
- **Gâmbia** (abra https://moj.gov.gm/ e procure "Criminal Offences Act 2025"):
  - `penal_code`: "Criminal Offences Act 2025", `enacted_year: 2025`. O site a chama de
    "Assent Copy … Passed 28th March 2025", mas o PDF deixa em branco a data de sanção
    ("[ ]") e não diz quando entra em vigor; a s. 344 revoga o *Criminal Code*, Cap.
    10.01. **Confirme que a lei está em vigor**; se não estiver, o código vigente é o Cap.
    10.01, e o bloco muda.
  - `domestic_genocide`: vazio com `reason`. A lei não traz o crime, e `no` afirmaria que
    nenhuma lei gambiana o traz (`03-modelo-de-dados.md`).
- **Alemanha**: `enacted_year: 1871`, do "Ausfertigungsdatum: 15.05.1871" no cabeçalho da
  página completa do StGB; o `url` do bloco passou a ser essa página, com `read_on:
  2026-11-11`. `consolidated_on` continua `null`: a página diz "zuletzt geändert durch
  Art. 1 G v. 20.3.2026", que é a data de uma alteração. Se quiser `2026-03-20` ali (e o
  mesmo critério na Rússia, "в редакции" de 04/08/2026), diga.

**Código:**

- `tests/test_data.py`: `robots_checked_on` é uma data completa a partir de 06/11/2026, e
  não mais uma lista dos dias já lidos (que toda leitura nova quebrava; "teste não fixa o
  valor do dia").
- Nenhum *script* novo no repositório. O leitor auxiliar (o `Client` do motor, mais o
  transporte com outro arquivo de raízes) ficou na pasta temporária da sessão.

**Bateria:**

- 372 testes passam; `ruff check` e `ruff format --check` limpos.
- `astraea validate-lexicon data/lexicon/*.json` valida os cinco léxicos.
- `python scripts/transform.py --draft --check` passa.
- `python scripts/build_site.py` simula 406 arquivos.
- **`--strict` reprova, de propósito, só pelos rascunhos: 36 campos em 15 registros**
  (eram 26 em 11). São os 9 status das situações e 27 blocos de lei penal que esperam o
  seu carimbo (travas 3 e 6).
- `config/` ainda não existe.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **Veto a agentes de IA vale para a sessão.** Li o `robots.txt` holandês como veto a esta
  sessão, embora o `User-Agent` do Astraea passe; o mesmo para o `ai-input=no` do TanzLII.
  Virou regra no `AGENTS.md` e no `03`. Se discordar, diga.
- **Os dois certificados**: raízes da Mozilla e intermediário pelo AIA, com a verificação
  ligada. A alternativa é deixar a Gâmbia vazia até o site corrigir a cadeia.
- **O Sudão foi lido nos arquivos do leitor de *e-book***, como o navegador os carrega, e
  não na tela do leitor. É o mesmo critério da base do Cornell (a página pede a lista a
  outro endereço, e o robô lê o endereço).
- **A Sérvia não foi lida pelas APIs** que a aplicação lista num arquivo em base64. Se
  achar que é o mesmo caso do Sudão e do Cornell, eu as chamo na próxima sessão.
- **`follows_convention_definition: unknown`** no Sudão (elemento de contexto a mais) e na
  Bósnia (sem "como tal").
- **Título de Ruanda em inglês.**
- **`penal_code` da Gâmbia** com a data de sanção em branco no PDF.
- **`consolidated_on: null`** quando a fonte dá só a data da última alteração (Alemanha,
  Rússia).
- As escolhas das sessões anteriores continuam abertas.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver o que espera o seu carimbo** (não grava nada):

   ```powershell
   python scripts\stamp.py
   ```

   Deve começar com `27 blocks ready to be stamped`. Se algum acento ou letra árabe vier
   trocado por `?`, é só a janela do PowerShell: o arquivo está certo.
2. **Conferir e carimbar** como na sessão 4: a lista "o que conferir", acima; depois, por
   país, primeiro em simulação e depois com `--execute` no fim:

   ```powershell
   python scripts\stamp.py --field RWA --by "Luccas de Amorim" --read-on 2026-11-12
   ```

   Troque `RWA` por `SDN`, `BIH`, `GMB.penal_code` ou `DEU.penal_code`, e a data pelo dia
   da sua leitura. Se um valor estiver errado, **não carimbe**: diga na próxima sessão.
3. **Regenerar o derivado e comitar**, como o *script* mostra ao terminar:

   ```powershell
   python scripts\transform.py --draft --execute
   ```

   ```powershell
   git add data\countries.json static\data
   ```

   ```powershell
   git commit -m "Carimba RWA (conferido por Luccas de Amorim em 2026-11-12)"
   ```

   O `git add` pode mostrar o aviso "LF will be replaced by CRLF". É só aviso.
4. **Países Baixos e Bélgica, se quiser ler você.** Os dois vedam esta sessão (o holandês,
   por veto a IA; o belga, por veto a robôs). No navegador, abra
   https://wetten.overheid.nl e procure "Wet internationale misdrijven" (o
   artigo do genocídio) e "Wetboek van Strafrecht"; na Bélgica, https://www.ejustice.just.fgov.be e o
   Código Penal. Anote, para cada lei, o endereço, o título, o artigo, o ano e a pena
   máxima, e me passe na próxima sessão: eu preparo os blocos com o que você leu, e você
   carimba.
5. **Enviar ao GitHub.** O *merge* na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

## 2026-11-10 — Fase 2, sessão 4: carga humana da lei penal (Brasil primeiro) e `scripts/stamp.py`

Branch `fase2/carga-humana`. Não havia resposta às "Escolhas a revisar" das sessões 3 e 4
da fase 1 nem das sessões 1 a 3 da fase 2; elas continuam abertas, nas entradas daquelas
sessões. O `countries.yml` rodou no GitHub nesta data: o PR #1 ("sem novidade", commit
vazio do robô, com os mesmos seis sha256 da sessão 3) foi aceito por você.

**A lista, aprovada por você** (24 países, nesta ordem; `06-roteiro.md`, fase 2, item 4):
Brasil; os 8 da prioridade do `quality.json` (Mianmar, Palestina, Israel, Ucrânia, Rússia,
Sudão, Bósnia e Herzegovina, Sérvia); os outros 7 com elo em `situations.json` (Gâmbia,
África do Sul, Etiópia, China, Iraque, Ruanda, Camboja); e 8 de foro ou base de
jurisdição, que **não ganharam elo** em `situations.json` (Alemanha, França, Bélgica,
Países Baixos, Argentina, Bangladesh, Tanzânia, Síria).

**Dado novo.** Todos os blocos foram lidos por esta sessão, que é um modelo de linguagem:
são rascunho, com `checked_by: null`, até o seu carimbo. Nenhuma `note`, porque a D4 está
pendente.

| País | `penal_code` | `domestic_genocide` | `max_penalty` | Fonte |
|---|---|---|---|---|
| Brasil | Código Penal (DL 2.848/1940) | Lei 2.889/1956, art. 1º | 40 anos | `planalto` |
| Alemanha | Strafgesetzbuch | VStGB, § 6 (2002) | perpétua | `gesetze-im-internet` |
| Argentina | Código Penal (Ley 11.179, 1921) | Ley 26.200, art. 8º (2007) | perpétua | `infoleg` |
| Bangladesh | Penal Code, 1860 | ICT Act 1973, s. 3(2)(c) | morte | `bdlaws` |
| Rússia | УК РФ (1996) | ст. 357 | morte | `kremlin-acts` |
| África do Sul | vazio com `reason` (sem código) | Act 27 of 2002, s. 4(1) e Schedule 1 | perpétua | `justice-gov-za` |
| os outros 18 | vazio com `reason` | vazio com `reason` | ausente | — |

O motivo de cada um dos 18 está no `reason` do bloco e na tabela do `02-fontes.md`, 1.6:

- portal que veda robôs: França, China, Iraque;
- portal que desafia o cliente: Israel, Camboja;
- portal que derruba a conexão ou não responde: Bélgica, Ucrânia, Mianmar, Bósnia;
- certificado que não se verifica: Países Baixos, Gâmbia;
- texto só por JavaScript: Sérvia;
- endereço que não resolve no DNS: Síria;
- portal que responde, mas a lei não foi alcançada nesta sessão: Sudão, Etiópia,
  Ruanda, Tanzânia;
- nenhum portal oficial localizado: Palestina.

**Nada foi preenchido por analogia.** A seção "Municipal laws" da Wikipedia só serviu
de índice (regra 4).

**Fontes novas em `sources.json`** (96 fontes, eram 89). Todas são `function: 1` e
`active`, com `robots_checked_on: 2026-11-10`:

- `planalto` (A) e `atlaspen` (B);
- `gesetze-im-internet`, `infoleg`, `bdlaws`, `justice-gov-za` e `kremlin-acts` (A).

O `reason` de cada uma diz como foi lida.

**Leituras desta sessão.** Todas pelo cliente HTTP do motor, com o `User-Agent` do Astraea
e o `robots.txt` obedecido (tamanho em bytes, sha256):

- `gesetze-im-internet.de/stgb/` 110.504, `b31c355407e9bd1738b27b1f02bcd929e4e8e7b27b450463b1e2ca23944d5b1b`;
  `/stgb/__38.html` 3.589, `f35dd1e71a2cd41b405a1dee541cb3fcc1eaaf09a79fb091fa4f7ee32ffca88c`;
  `/vstgb/` 9.311, `293a2f7e301c32898b11d197b741d1de44d175d6b1e2db0ce41179167ea2a43d`;
  `/vstgb/__6.html` 4.742, `d6f13b7d1ab5258c0f957511ed70c963dea9309d90675503bcce07b7e3d0c3fb`.
- InfoLEG: Código Penal (`…/16546/texact.htm`) 334.120,
  `52575de7c849442282f2a8ff00a7464adb2a20a0c7d84d3f74ce50215bdfaa28`; Ley 26.200
  (`…/123921/norma.htm`) 30.979, `9c697e6a6273894e4aa13d7e72ab3222131ba881d54af33431362b65b9902e59`.
- bdlaws: Penal Code (`act-11.html`) 883.512,
  `ff0a0b22b9594e8f22743556a2f078d850b2534e8578609009f15e306bfc1156`; ICT Act
  (`act-435.html`) 105.276, `4cffab3741d31c5f11042f1b554c379e3cc73758af60814f1d9f4fecef3ba1dc`;
  s. 3 (`section-12479.html`) 68.382, `12495e6f502e7be1a07acf100720f7b84185c6cc1944269a9c6d135696e320b7`;
  s. 20 (`section-12496.html`) 50.830, `a1f45e283c099edc91b4facc1589abfafc21f6537f92dc4d1d21b51342f5d082`.
- justice.gov.za: Act 27 of 2002 (PDF) 330.356,
  `91b5dfd0273a33f2684cc5537980d2db94f992f5644efeb8700ab939644c87cd`.
- kremlin.ru: УК РФ (`/acts/bank/9555`) 64.833,
  `493c2868d8019a93b830296f4eeca335bd92ceec9926483b04867dbafdf44689`; página 54 (ст. 357)
  62.428, `da21f8c10d65239eba2216186fb7319c66e09a3683e3565809746c2172474588`.
- As sondagens que deram motivo de vazio ficaram registradas na máquina da sessão e não
  entram no repositório: as páginas iniciais de `npc.gov.cn`, `minijust.gov.rw`,
  `moj.gov.sd`, `hopr.gov.et` e `parliament.go.tz`, a resposta 247 do Knesset, o "Request
  Rejected" de `moj.gov.kh` e a página JavaScript do sistema sérvio. O mesmo vale para a
  página da Wikipedia (748.000 bytes,
  `56b45951c7750c421fc29e2f56f2ea4adaabaf0bb076d44a98ea2599405933e8`).

**O Planalto e o AtlasPen, as duas exceções:**

- **O Planalto derruba toda conexão do cliente do motor e do `curl`**, inclusive a do
  `robots.txt`. No navegador, as páginas abrem e o `robots.txt` responde 404. Li as
  quatro leis no **navegador embutido do aplicativo**, sem desafio a vencer, e calculei
  ali o sha256 de cada resposta:
  - Código Penal compilado: 683.589 bytes, `Last-Modified` 09/10/2026,
    `3265a4fd6148a14e6705999f774c3c9dbe0b24fcfc8fe7b61fc201037486975a`;
  - Lei 2.889: 8.736 bytes, `94d07eeb2b781a8a001053b267d52a75188d0d1d507e0435793efb682cf45e9d`;
  - Lei 8.072: 50.432 bytes, `c7d90b50295fb937e7f8af0020c3a7a792f2e25634f0b780b88fd466ce1d14b8`;
  - Lei 13.964: 219.503 bytes, `1ac60916f16f037f60148905eff630cc5ab7e11f6af26b684e55ca4360bd22b0`.

  **Divergência do que o `AGENTS.md` pede ao robô, e por quê:** você pediu a leitura do
  Planalto, e a carga humana é leitura de pessoa; o robô do Astraea continua sem ler o
  Planalto. É a primeira escolha a revisar, adiante.
- **O AtlasPen veda todos os robôs** (`robots.txt`: `User-agent: *`, `Disallow: /`).
  Não li o site. Li `data/crimes.json` no seu repositório local
  (`luccas-amorim/atlaspen`, commit `4258a18`, 914.957 bytes, sha256
  `9cd852db6b184ff1c28d1c95f091d29db2fd1248bd0725366545a41c569ccdca`): os registros 551 a
  557 e 1462 a 1476 são os da Lei 2.889. O `alternative_url` do Brasil aponta para o
  arquivo publicado, `https://atlaspen.com.br/data/crimes.json`, como no exemplo do `03`.

**Brasil: o que conferir, campo a campo, e onde.** Abra cada endereço no seu navegador.

- `penal_code` (abra https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm):
  - `exists: yes`, `enacted_year: 1940` e `language: pt`.
  - `title`: "Código Penal (Decreto-Lei nº 2.848, de 7 de dezembro de 1940)", como no
    cabeçalho da página.
  - `consolidated_on: 2026-10-09`: **o Planalto não data a compilação**. O valor é o
    `Last-Modified` da página. A alteração mais recente que a página cita é a Lei 15.425,
    de 2026 (art. 282). Se preferir `null`, diga.
  - `official_url`: a própria página; `alternative_url`: o AtlasPen.
- `domestic_genocide` (abra https://www.planalto.gov.br/ccivil_03/leis/l2889.htm):
  - `status: criminalized`, `provision: art. 1º`, `year: 1956`.
  - `instrument`: "Lei nº 2.889, de 1º de outubro de 1956".
  - `follows_convention_definition: yes`. O art. 1º traz os quatro grupos (nacional,
    étnico, racial, religioso), "como tal", e as cinco condutas (a–e) do art. II da
    Convenção. Os arts. 2º, 3º e 5º cobrem associação, incitação e tentativa.
  - Hediondez, para a nota, se quiser: Lei 8.072/1990, art. 1º, parágrafo único, I, com
    a redação da Lei 13.964/2019 (https://www.planalto.gov.br/ccivil_03/leis/l8072.htm).
- `max_penalty` (a mesma página do Código Penal, art. 75):
  - `type: years`, `years: 40`. O art. 75 diz: "O tempo de cumprimento das penas
    privativas de liberdade não pode ser superior a 40 (quarenta) anos", com a redação
    da Lei 13.964/2019.
  - `applies_to_genocide: yes`. O art. 75 vale para toda pena privativa de liberdade. A
    pena mais alta do genocídio é a do art. 1º, a, que remete ao art. 121, § 2º (12 a 30
    anos); o art. 4º da Lei 2.889 a agrava de um terço quando o autor é governante ou
    funcionário público, o que dá 40 anos, o mesmo limite.
- **Notas que eu proporia.** Não estão no dado: são texto nosso (D4). Grave só se
  aprovar, com as suas palavras se preferir, e com `author: "human"`:
  - `domestic_genocide`: "Pena por remissão aos tipos do Código Penal (art. 1º, a–e);
    hediondo pelo art. 1º, parágrafo único, I, da Lei 8.072/1990. Registro detalhado no
    AtlasPen."
  - `max_penalty`: "Art. 75 do Código Penal, com a redação da Lei 13.964/2019."

**Os outros cinco: o que conferir.**

- **Alemanha**: `enacted_year` ficou `null`, porque a página lida não dá a data de 1871.
  O § 6 do VStGB tem os cinco atos e os quatro grupos, com pena perpétua (*lebenslange
  Freiheitsstrafe*). O § 38 do StGB dá 15 anos como máximo da pena temporária.
- **Argentina**: a Ley 26.200 tipifica por remissão ao art. 6º do Estatuto de Roma, que
  repete o art. II da Convenção; gravei `criminalized` e `follows: yes`. `year: 2007` é
  o da promulgação (sancionada em 13/12/2006, *promulgada de hecho* em 05/01/2007). Pena:
  5 a 25 anos, ou perpétua se houver morte. O `03` pede, nesses casos, a hipótese em
  `note`.
- **Bangladesh**: o ICT Act diz "a national, ethnic, racial or religious group, **such
  as**", e não "as such". O grupo político saiu pela emenda de 2026 (Act XIII of 2026,
  com efeito retroativo a 06/01/2009). Por isso `follows: unknown`. Pena: morte, s. 20(2)
  ("sentence of death or such other punishment"). Bangladesh é retencionista; a trava 10
  não pede nota.
- **Rússia**: a ст. 357 acrescenta o deslocamento forçado ("насильственного переселения")
  e não fala em dano mental. É mais larga num ponto e mais estreita noutro: `follows:
  unknown`. Pena: 12 a 20 anos, perpétua ou morte. Gravei `death`; a moratória (o Cornell
  lista a Rússia como *de facto*) é hipótese para `note`. O texto é o consolidado do
  kremlin.ru ("в редакции" até a lei de 04/08/2026); `consolidated_on` ficou `null`.
- **África do Sul**: não há código penal (*common law* e leis esparsas). `exists: no`
  pediria uma nota nossa, então o bloco ficou vazio com `reason`. A lei de 2002 copia as
  cinco condutas e os quatro grupos, com pena até prisão perpétua, s. 4(1).

**Código:**

- **`scripts/stamp.py` (novo).** Vale a pena, como eu tinha dito: são 17 blocos hoje e
  cerca de 70 nos 24 países.
  - Sem argumentos, lista os blocos prontos para carimbo.
  - Com `--field BRA.penal_code` (ou `--field BRA`, todos os prontos do país), `--by "Seu
    Nome"` e `--execute`, grava `checked_by: "human"` e o dia da sua leitura em `read_on`
    (`--read-on`, hoje por padrão).
  - Não muda valor. Recusa bloco vazio, incompleto ou já carimbado, e um recusado impede
    os outros.
  - **Divergência do que você pediu:** o nome não vai para o dado (regra 8: nome de
    pessoa só em `decisions.json`). Vai para a mensagem do commit que o *script* sugere,
    e o autor do commit já diz quem foi.
- **`tests/test_stamp.py`** (15): a lista, a simulação, só o bloco indicado, o país
  inteiro, sete recusas, um recusado impede os outros, `--by` e data. E, numa cópia dos
  dados, carimbar o Brasil deixa o `--strict` sem nada a dizer dele.
- **`tests/test_penal_law.py`** (10):
  - a lista de 24, com o Brasil primeiro;
  - blocos só onde a carga chegou;
  - cada bloco preparado, carimbado por pessoa ou vazio com motivo, nunca do robô;
  - a confiança é a da fonte;
  - vocabulário, nota só de pessoa e trava 10;
  - os valores do Brasil e a ficha `/countries/BRA/` com os três blocos e a fonte, nas
    duas línguas.
- `test_data.py` e `test_transform.py` passaram a aceitar os blocos de lei penal
  preparados.

**Bateria:**

- 372 testes passam; `ruff check` e `ruff format --check` limpos.
- `astraea validate-lexicon data/lexicon/*.json` valida os cinco léxicos.
- `python scripts/transform.py --draft --check` passa.
- `python scripts/build_site.py` simula 406 arquivos.
- **`--strict` reprova, de propósito, só pelos rascunhos: 26 campos em 11 registros.**
  São os mesmos 9 status das situações e os 17 blocos de lei penal que esperam o seu
  carimbo (travas 3 e 6).
- `config/` ainda não existe.

**O que as mensagens novas dizem** (saem em inglês):

- `17 blocks ready to be stamped (checked_by empty, the rest of the stamp in place):`,
  seguida da lista com os valores, o endereço lido, a fonte e a data: o que espera você.
- `-> checked_by: human, read_on: 2026-11-12` e `would stamp: 3 blocks`: o que o
  `--execute` faria.
- `stamped: 3 blocks` e as três linhas `next`: gravado; falta regenerar o derivado e
  comitar.
- `FAIL BRA.max_penalty: already checked by human`, `… asserts nothing (empty, with a
  reason)`, `… lacks url; prepare it first`, sempre com `nothing was written`: o bloco
  não está pronto, e nada foi gravado, nem os outros que você indicou.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **A leitura do Planalto no navegador embutido** (acima). As alternativas são ler o
  texto oficial na Câmara (`camara.leg.br/legin`) ou deixar o Brasil só com o que você
  ler.
- **`consolidated_on` do Brasil é o `Last-Modified`** da página compilada.
- **`read_on` passa a ser o dia da sua leitura** quando você carimba. O dia da leitura
  desta sessão fica no histórico do git.
- **`follows_convention_definition: unknown`** para Bangladesh e Rússia, e **`yes` com
  `criminalized`** para a remissão argentina ao Estatuto.
- **`max_penalty: death` na Rússia**, apesar da moratória.
- **África do Sul com `penal_code` vazio**, e não `exists: no`, até haver a nota.
- **A lista dos 24 está fixada em `tests/test_penal_law.py`.** País fora dela que
  receber bloco de lei penal reprova o teste até a lista crescer, por decisão sua.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver o que espera o seu carimbo** (não grava nada):

   ```powershell
   python scripts\stamp.py
   ```

   Deve começar com `17 blocks ready to be stamped`. Se algum acento vier trocado por
   `?`, é só a janela do PowerShell: o arquivo está certo.
2. **Conferir o Brasil** com a lista "Brasil: o que conferir", acima: abra cada endereço
   no navegador e compare valor por valor. Se algum valor estiver errado, **não
   carimbe**: me diga na próxima sessão, ou corrija antes no `data\countries.json`.
3. **Carimbar o que conferiu.** Primeiro em simulação (troque o nome e, se não for hoje,
   a data):

   ```powershell
   python scripts\stamp.py --field BRA --by "Luccas de Amorim" --read-on 2026-11-11
   ```

   Se estiver tudo como você leu, rode o mesmo comando com `--execute` no fim:

   ```powershell
   python scripts\stamp.py --field BRA --by "Luccas de Amorim" --read-on 2026-11-11 --execute
   ```

   Para carimbar um bloco só, use `--field BRA.max_penalty`. `--field` pode se repetir.
4. **Regenerar o derivado e comitar**, como o *script* mostra ao terminar:

   ```powershell
   python scripts\transform.py --draft --execute
   ```

   ```powershell
   git add data\countries.json static\data
   ```

   ```powershell
   git commit -m "Carimba BRA (conferido por Luccas de Amorim em 2026-11-11)"
   ```

   O `git add` pode mostrar o aviso "LF will be replaced by CRLF". É só aviso: o
   `.gitattributes` grava com LF.
5. **Uma nota, se quiser** (D4). Abra `data\countries.json`, procure `"BRA"` e, dentro
   do bloco, logo depois de `"follows_convention_definition": "yes",`, acrescente a linha
   `"note": {"pt-BR": {"text": "o seu texto", "author": "human"}},`. Depois, repita o
   passo 4. Se o `transform.py` reclamar de vírgula, a linha está fora do lugar; desfaça
   com `git checkout data\countries.json`.
6. **Ver a ficha** (opcional):

   ```powershell
   python scripts\build_site.py --execute
   ```

   ```powershell
   python -m http.server 8000 --directory _site
   ```

   Abra http://localhost:8000/pt-br/countries/BRA/. Os três blocos aparecem como
   "rascunho" até o carimbo, e como "carimbado" depois. Feche o servidor com Ctrl+C. O
   "Firewall do Windows Defender" pode perguntar se o Python pode usar a rede: "Cancelar"
   basta.
7. **Enviar ao GitHub.** O *merge* na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

## 2026-11-10 — Fase 2, sessão 3: `countries.yml` (leitura mensal por PR) e tela `/countries`

Branch `fase2/countries`. Não havia resposta às "Escolhas a revisar" das sessões 3 e 4
da fase 1 nem das sessões 1 e 2 da fase 2; elas continuam abertas, nas entradas
daquelas sessões. **Nenhum dado mudou** nesta sessão: `data/` e `static/data/` estão
como a sessão 2 os deixou.

**O `countries.yml`** (`.github/workflows/countries.yml`), no dia 1 de cada mês às
05:00 UTC (02:00 em Brasília) e também à mão:

- Roda `scripts/countries_monthly.py --execute`, que chama as duas cargas
  (`load_treaties.py` e `load_death_penalty.py`) com `--execute`; se
  `data/countries.json` mudou, roda `transform.py --draft --execute` e acrescenta ao
  `CHANGELOG.md` uma entrada "Leitura mensal dos países (robô)" com a saída das cargas:
  os sha256, as linhas `new:`/`changed:`/`kept`/`left alone` e as contagens.
- Roda a bateria da CI (`transform.py --draft --check`, `pytest`, `build_site.py`) e só
  então abre o PR da branch `robot/countries` para a `main`, com o relatório no corpo.
  **Nunca comita na `main`.** Se o PR do mês anterior ainda estiver aberto, ele é
  atualizado, não duplicado.
- **Mês sem novidade abre PR com commit vazio**: título "Leitura mensal dos países,
  AAAA-MM-DD: sem novidade", diff vazio, e os sha256 no corpo e na mensagem do commit.
- **Carga que falha abre issue, não PR**, com a saída e o que fazer, separado em três
  casos: nome sem mapa, sentinela (a fonte respondeu outra coisa) e leitura (rede,
  bloqueio). As duas cargas são independentes: se uma falha, a outra ainda dá o seu PR,
  que avisa da falha. Validador que reprova os dados novos, ou bateria que falha, também
  abre issue e nenhum PR.
- Permissões: `contents`, `pull-requests` e `issues`, de escrita, e nada mais;
  `concurrency: countries`, sem cancelar; `timeout-minutes: 60`, como no `04`. Versões
  conferidas hoje nas páginas de *releases*: `actions/checkout` v7.0.1 e
  `actions/setup-python` v7.1.0, as duas na linha `v7` que o `ci.yml` já usa. O PR e a
  issue saem pelo `gh`, que já vem no *runner*: nenhuma *action* de terceiro recebe o
  *token*. A issue usa sempre o `GITHUB_TOKEN`, para que um *token* pessoal vencido não
  cale o aviso.
- **O *workflow* não foi executado**: sem *push* não há como. O que dava para conferir
  foi conferido: o *script* rodou pela rede, em simulação, e deu "sem novidade" com os
  mesmos seis sha256 registrados nas sessões 1 e 2 (os dois XML da UNTC, 78.616 e
  119.352 bytes, e as quatro listas do Cornell); e uma leitura de dezembro simulada no
  próprio repositório (Japão movido para abolicionista numa cópia das listas) deixou a
  bateria inteira verde, antes de ser desfeita com o git.

**Decisão minha, como pedido: o Cornell entra no mensal**, e não num *workflow* semanal
próprio, como o `04` previa. Três razões: (1) dois *workflows* escrevendo o mesmo
`countries.json` e o mesmo derivado abririam PRs que entram em conflito um com o outro, e
quem teria de resolver é você; (2) a classificação de pena de morte muda poucas vezes
por ano, e a base do Cornell dá sinais de atraso (`02`, 1.5), então a leitura semanal
traria mais PRs sem trazer dado mais novo; (3) a conferência de verdade é o anexo anual
da Anistia. Quem quiser ler fora do dia 1 usa o botão *Run workflow*. Registrado no `04`.

**Divergência do que você pediu, e por quê:** você pediu "diff vazio quando não houver
novidade", e é o que acontece; mas **o mês com novidade traz, além dos dados, uma
entrada no `CHANGELOG.md`**. O `03` diz que a leitura do robô só vale como carimbo
`robot` com o sha256 da resposta registrado no `CHANGELOG`; sem a entrada, o PR mensal
gravaria `read_on` novo sem o registro que o sustenta.

**Correção que a leitura mensal exigia nos testes.** Os testes das duas cargas exigiam
que as *fixtures* de 10/11 devolvessem exatamente o `countries.json` do repositório: o
primeiro PR com novidade viria vermelho. Agora os testes da carga rodam sobre os
registros como as *fixtures* os leem, e os de dados reais conferem que o repositório
concorda com elas fora dos blocos lidos depois (`read_on` mais novo) ou carimbados por
pessoa. Isso também deixa passar, sem mexer em teste, a sua carga do anexo da Anistia.
A regra entrou no `AGENTS.md`.

**A tela de países**, gerada pelo `build_site.py` no *build*, em `/en/` e `/pt-br/`:

- `/countries/`: a frase da regra 1 ("O Astraea não diz se algum país cometeu o crime de
  genocídio…"); a completude por campo (carimbados, em rascunho, vazios, para
  `un_status` e os seis blocos, lida de `quality.json`) e "0 de 197 países com todos os
  campos carimbados"; e a tabela dos 197 em ordem alfabética da língua, com situação na
  ONU, Convenção, Estatuto, pena de morte e quantos dos 7 campos estão carimbados.
- **Filtros sem JavaScript.** Três grupos (Convenção, Estatuto, pena de morte), cada
  valor com a contagem ("parte (154)", "sem dado (2)"); escolher um valor em cada grupo
  deixa os países que atendem aos três, e um contador diz quantos ficaram. É CSS puro
  (botões de rádio e uma regra por botão); sem CSS, a tabela mostra os 197. O `04` dizia
  que JavaScript entraria com o primeiro filtro: **divergência registrada lá**.
- `/countries/<ISO>/`, as 197 fichas: nome, situação e data na ONU, e os seis blocos,
  cada um com o seu estado (carimbado, rascunho, vazio), os valores com os rótulos de
  `data/i18n/`, e **o carimbo item por item**: fonte, URL, data de leitura, confiança,
  quem conferiu; item que falta aparece como "falta: ainda sem carimbo". Bloco vazio com
  `reason` mostra o motivo; bloco que ainda não existe (`penal_code`,
  `domestic_genocide`, `max_penalty`) diz "Ainda não carregado". Ao fim, as situações em
  que o país aparece, com o papel e o status mais alto.
- **O `reason` na tela pt-BR** (D4 pendente, não decidida): aparece em inglês, como está
  no dado, com `lang="en"` e a marca "(disponível só em inglês)". Traduzi-lo seria
  escrever texto nosso, e quem escreve texto nosso (pessoa ou modelo) é a D4. É a mesma
  regra que o `04` já dava para qualquer texto sem versão na língua da página.
- **Nenhum nome de robô** na tela (D15); "conferido por: robô" é o valor de
  `checked_by`, não um nome.
- **O mapa coroplético ficou fora**: é a D13, pendente. A tabela com filtros dá a mesma
  informação sem a decisão cartográfica.
- A página inicial ganhou o *link* "Os 197 países, campo a campo" e a nota dos países foi
  atualizada (os tratados e a pena de morte já vêm das fontes). As três telas dividem um
  *layout* (`site/templates/layout.html`) com a seção "Países" no cabeçalho.

**Código:** `.github/workflows/countries.yml` e `scripts/countries_monthly.py` (novos);
`scripts/build_site.py` reescrito em volta do *layout*; `site/templates/layout.html`,
`countries.html` e `country.html` (novos), `home.html` virou só o conteúdo;
`site/i18n/en.json` e `pt-BR.json` com os textos novos; `site/assets/style.css`.

**Testes:** 346 passam (eram 297). Novos: `tests/test_countries_monthly.py` (22: mês sem
novidade e com novidade, nome sem mapa, sentinela nas duas cargas, validador que
reprova, simulação, o que cada falha quer dizer, a entrada do `CHANGELOG`, o limite do
corpo do PR; do *workflow*, sem *push*: cron, limites, `concurrency`, permissões, as
mesmas versões do `ci.yml`, que só empurra para `robot/countries`, que propõe só depois
da bateria, que a issue não depende do *token* pessoal, e que todo `run` é *shell*
válido pelo `bash -n`); `tests/test_build_site.py` (de 17 para 42: dois países inventados
cobrem carimbado, rascunho, vazio com motivo, não carregado, nota só em português e
título em língua original; filtros sem JavaScript; contagens; proveniência; as duas
línguas; e, sobre os dados reais, as 197 fichas, as contagens dos filtros contra os
dados, a completude contra `quality.json`, cada carimbo e cada motivo nas fichas, a
palavra só como nome do crime ou nos rótulos da Convenção e do direito interno, em todas
as páginas, e nenhum nome de robô).

**Bateria:** 346 testes passam; `ruff check` e `ruff format --check` limpos; `astraea
validate-lexicon data/lexicon/*.json` valida os cinco; `python scripts/transform.py
--draft --check` passa; `python scripts/build_site.py` simula 406 arquivos (a página
inicial, `/countries/` e as 197 fichas, em cada língua). **`--strict` reprova, de
propósito, só pelos mesmos 9 status em rascunho** (travas 3 e 6). `config/` ainda não
existe.

**O que as mensagens novas dizem:**

- No terminal, `--- outcome: pull request yes, issue no, data changed no`: o que o
  *workflow* faria. Sem `--execute`, o *script* mostra o título e o corpo do PR (ou da
  issue) e não grava nada.
- No GitHub, **PR "Leitura mensal dos países, 2026-12-01: sem novidade"**: nada mudou nas
  fontes. **PR "Leitura mensal dos países, 2026-12-01"** (sem o "sem novidade"): há
  linhas `new:` ou `changed:` no corpo, e a aba *Files changed* mostra cada uma.
- **Issue "Leitura mensal dos países falhou (2026-12-01): pena de morte"** (ou
  "tratados", ou "validação"): o corpo começa por **Nome sem mapa**, **Sentinela** ou
  **Leitura**, e diz o que fazer em cada caso.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **O Cornell no mensal** (acima). Se preferir o semanal, é um segundo *cron* no mesmo
  *workflow*, que só faria sentido com a carga dos tratados desligada nele.
- **Mês sem novidade abre PR** (com commit vazio). A alternativa é não abrir nada e
  deixar o relatório só no resumo da execução, que o GitHub apaga em 90 dias; o PR
  também mantém o *cron* vivo (60 dias sem atividade o desligam, `04`).
- **O PR com novidade traz a entrada do `CHANGELOG`** (acima).
- **`read_on` continua mudando só quando o valor muda**; a linha `confirmed` em
  `verification.json` a cada leitura sem novidade, que a sessão 1 da fase 2 deixou para
  esta, não foi feita, porque é escolha sua e ainda não tem resposta. É uma função no
  `countries_monthly.py`.
- **A tela mostra a fonte pelo `id`** (`untc`, `cornell-dpw`) e a URL, não pelo nome
  longo: o nome está em `data/sources.json`, que não é derivado, e o site só lê o
  derivado. Se quiser o nome, o `transform.py` pode publicar as fontes em
  `static/data/` (o que a tela `/about` vai pedir de qualquer jeito).
- **O título da citação** continua em português nas duas línguas (sessão 4 da fase 1).

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Enviar ao GitHub.** O *merge* na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

   O *push* também publica a tela de países: o `deploy.yml` roda sozinho, porque a
   mudança toca `site/` e `scripts/build_site.py`.
2. **Criar o *token* do PR mensal** (uma vez; recomendado, para que a CI rode no PR):
   1. No GitHub, clique na sua foto (canto superior direito) → **Settings** →
      **Developer settings** (último item do menu da esquerda) → **Personal access
      tokens** → **Fine-grained tokens** → **Generate new token**. O GitHub pode pedir a
      senha ou o código de dois fatores de novo: é esperado.
   2. **Token name**: `astraea countries`. **Expiration**: o maior prazo que a página
      oferecer; anote a data no seu calendário, porque o *token* vence.
   3. **Repository access** → **Only select repositories** → `astraea`.
   4. **Permissions** → **Repository permissions**: **Contents**, **Issues** e **Pull
      requests**, cada um em **Read and write**. (*Metadata* fica em *Read-only* sozinho;
      não mexa no resto.)
   5. **Generate token** e copie o valor que começa com `github_pat_`. Ele só aparece
      uma vez; não o cole em lugar nenhum além do passo seguinte.
   6. No repositório: **Settings** → **Secrets and variables** → **Actions** → **New
      repository secret**. **Name**: `COUNTRIES_PR_TOKEN`; **Secret**: cole o valor;
      **Add secret**.

   **Sem o *token*** também funciona, com uma diferença: o PR chega sem a CI rodar nele
   (a bateria roda dentro do próprio *workflow*, antes de propor). Para isso, ligue em
   **Settings → Actions → General → Workflow permissions** a opção **Allow GitHub
   Actions to create and approve pull requests** e salve. Sem o *token* e sem essa
   opção, a execução falha no passo do PR e abre uma issue dizendo isso.
3. **Rodar a primeira vez, sem esperar o dia 1.** Aba **Actions** → **Countries** (na
   lista da esquerda) → **Run workflow** → deixe *Branch: main* → **Run workflow**. O
   botão só aparece depois do *push*. Leva uns 2 a 3 minutos. Bolinha verde: deu certo.
4. **Ver o PR mensal.** Aba **Pull requests**. Deve haver um "Leitura mensal dos países,
   AAAA-MM-DD: sem novidade" (as fontes não mudaram desde hoje).
   - **Sem novidade:** não há o que conferir. Clique em **Merge pull request** →
     **Confirm merge** (guarda a leitura no histórico e mantém o agendamento vivo), ou
     **Close pull request**, se preferir não guardar.
   - **Com novidade:** abra **Files changed** e leia as mudanças de
     `data/countries.json`; cada uma corresponde a uma linha `new:` ou `changed:` do
     corpo. Se quiser, abra o `url` do bloco na fonte. Espere a bolinha da CI ficar verde
     (com o *token*) e clique em **Merge pull request**. Depois, no seu computador:

     ```powershell
     git pull
     ```

   - Se o PR disser **This branch has conflicts**, não tente resolver: clique em **Close
     pull request** e rode o *workflow* de novo (passo 3). O robô relê as fontes a
     partir da `main` de agora.
   - O GitHub manda *e-mail* quando o PR ou a issue abrem, se você "assiste" ao
     repositório (o dono assiste por padrão).
5. **Quando ele abrir issue.** Aba **Issues**. O título diz qual carga falhou; o corpo
   começa por um destes:
   - **Nome sem mapa**: a fonte trouxe um nome de país novo ou mudado. Confira o nome na
     tabela M49 da ONU, acrescente a linha em `data/untc-names.json` (tratados) ou
     `data/cornell-names.json` (pena de morte), como as linhas que já estão lá, faça o
     commit com `Closes #N` na mensagem (N é o número da issue) e rode o *workflow* de
     novo. Se preferir, traga a issue para uma sessão.
   - **Sentinela**: a fonte respondeu outra coisa (página de erro, arquivo pela metade,
     formato novo). Abra a página da fonte no navegador. Se for instabilidade, rode de
     novo outro dia; se a forma mudou, é trabalho de sessão.
   - **Leitura**: a fonte não respondeu ou bloqueou. Rode de novo outro dia. Bloqueio
     **não se contorna** (regra 7): se persistir, leve à próxima sessão.
   - **Passo do workflow** com "Bad credentials" ou "401": o *token* venceu. Refaça o
     passo 2 (gere outro e troque o valor do *secret* `COUNTRIES_PR_TOKEN` em **Update
     secret**).

   Resolvido, feche a issue: `Closes #N` no commit da correção, ou **Close issue** com um
   comentário dizendo por quê.
6. **Ver a tela antes do *push*** (opcional):

   ```powershell
   python scripts\build_site.py --execute
   python -m http.server 8000 --directory _site
   ```

   Abra http://localhost:8000/pt-br/countries/ no navegador, experimente os filtros e
   clique num país. Feche o servidor com Ctrl+C no PowerShell. O Windows pode perguntar,
   numa janela do "Firewall do Windows Defender", se o Python pode usar a rede:
   "Cancelar" basta, porque o endereço é local.
7. **Ver o que o PR mensal diria, sem gravar nada** (lê as fontes pela internet, uns 40
   segundos):

   ```powershell
   python scripts\countries_monthly.py
   ```

   Deve terminar com o título "… sem novidade" e `simulation: nothing was written`.

## 2026-11-10 — Fase 2, sessão 2: pena de morte (Cornell pelo `listing`; caminho da Anistia)

Branch `fase2/pena-de-morte`. Não havia resposta às "Escolhas a revisar" das sessões 3 e
4 da fase 1 nem da sessão 1 da fase 2; elas continuam abertas, nas entradas daquelas
sessões.

**Dado novo: `death_penalty` nos 197 registros.** 130 carimbados (`source:
cornell-dpw`, confiança B, `checked_by: robot`, `read_on: 2026-11-10`, `url` da lista em
que o país está) e 67 vazios com `reason`. Nenhuma `note`: é texto nosso e depende da
D4. Contagens, conferidas contra a fonte do dia (a última leitura pela rede, ao fim da
sessão, deu `up to date`):

| Lista do Cornell (`lawStatus`) | Nomes na lista | Fora dos 197 | Nos 197 | Gravado como |
|---|---|---|---|---|
| `Abolitionist` | 95 | 6 | **89** | `abolitionist_all_crimes` |
| `Abolitionist For Ordinary Crimes` | 6 | — | **6** | `abolitionist_ordinary_crimes` |
| `Abolitionist de facto` | 45 | — | **45** | vazio com `reason` (não corresponde, adiante) |
| `Retentionist` | 35 | — | **35** | `retentionist` |
| em nenhuma lista | — | — | **22** | vazio com `reason` |
| **total** | **181** | **6** | **197** | 130 carimbados, 67 vazios |

Os seis fora dos 197: Malvinas, Terras Austrais Francesas, Groenlândia, Nova Caledônia,
Porto Rico e Chipre do Norte. Os 22 dos 197 que o Cornell não lista: Andorra, Burkina
Faso, Burundi, Cabo Verde, Congo, Guatemala, Ilhas Marshall, Kiribati, Liechtenstein,
Malta, Maurício, Micronésia, Mônaco, Nauru, Palau, Samoa, San Marino, Santa Sé, São Tomé
e Príncipe, Seicheles, Suriname e Tuvalu. Kosovo (abolicionista), Taiwan e Palestina
(retencionistas) estão nas listas e foram carimbados como os demais. A página não dá
contagem por categoria; as contagens acima são as das próprias listas.

**Leituras desta sessão**, todas pelo cliente HTTP do motor, com o `User-Agent` do
Astraea e o `robots.txt` obedecido, da máquina do dono:

- As quatro listas, `https://cornell-dpw.herokuapp.com/api/countries/by-law-status/1?lawStatus=…`
  (HTTP 200, `application/json`, sem `Last-Modified`), lidas três vezes pela rede (na
  sondagem, na carga em simulação e na conferência final) com os mesmos bytes; as
  *fixtures* são essas respostas, byte a byte:
  - `Abolitionist`: 4.081 bytes, sha256
    `ab64273c83c17156d528e43099d560662db7c4a8339cfa3662de7582cacffd71`;
  - `Abolitionist%20For%20Ordinary%20Crimes`: 247 bytes, sha256
    `4a17359c19be557d945165377da22143fd93d8a748db9d339abc2b94f60eedaf`;
  - `Abolitionist%20de%20facto`: 1.970 bytes, sha256
    `a95d4eec7a1890fad4cd433fad6940a4a80e7c567896683d734fcdc96c57a30e`;
  - `Retentionist`: 1.478 bytes, sha256
    `844e476e8ecb78a9b1597417b38fd9f23bed58c53a6edbfa31b0fb16ce738018`.

  O `--execute` gravou a partir das *fixtures* (`--json-dir tests/fixtures/cornell
  --read-on 2026-11-10`), idênticas à leitura pela rede.
- `https://dpw.lawschool.cornell.edu/robots.txt`: 24 bytes (`User-Agent: *`,
  `Disallow:` vazio), `Last-Modified` 30/10/2026, sha256
  `e1f21c9aa28d50ca112ed357f34b67c550597effd4d42fd55b4e27300dd8f9c1`.
  `https://cornell-dpw.herokuapp.com/robots.txt`: 404 (nada vedado).
- Para achar a tabela e as definições: a página inicial do espelho (112.000 bytes,
  sha256 `9de13bc98ec528e7fdf74d596a4c4967bbbf15e91659155d52e9be01207350d6`), a página
  `/database/` (55.342 bytes,
  `d64f4cee707f049870b90eaec3e8fcf4c3249eef9be04711a82bd54125fd3592`), o `app.js` do
  tema (539.310 bytes, `ac953d4153b56a20dff3c7386a161f5eb9c9d7eb8bf97a66d59eac4ce1c91e92`),
  a raiz da base (93.283 bytes,
  `eccc2b0a27351905e415b544a84efa10a5d7e2db113b974540a1fc184dacc746`, onde está a
  definição de retencionista e de *de facto*) e os cinco `_nuxt/*.js` da base (nenhuma
  definição das outras duas categorias). Duas requisições de sondagem à base, sem
  `lawStatus` e com um valor inexistente, devolveram 400; não fazem parte da carga e não
  se repetem.
- Certificados: o do espelho é válido (Let's Encrypt, até 19/12/2026); o de
  `deathpenaltyworldwide.org` **venceu em 21/12/2025** (GoDaddy), lido só nas datas, sem
  baixar página; `www.deathpenaltyworldwide.org` derrubou a conexão.
- A tabela M49 (`unsd-m49`), relida para conferir os nomes: 1.721.575 bytes, sha256
  `b9048114f6e7f2abda83bf03d4263c9d7cd1bd7230e3d0461025ee7839a7a1fb`, a mesma resposta da
  sessão 1.

**Correções ao plano** (no `02-fontes.md`, 1.5, nova):

- **A tabela não está no espelho.** A página do espelho não traz a classificação; a
  legenda do mapa a pede, uma lista por categoria, a uma base em outro servidor
  (`cornell-dpw.herokuapp.com`). O robô lê essa base, que é o que a página mostra.
- **Sem termos de uso** no espelho nem na base; o certificado vencido do domínio
  principal é da fonte, não do *proxy* da sondagem de 06/11.
- **Sentinela:** como a página não dá contagem por categoria, a sentinela é a forma das
  quatro listas: todas vieram, cada uma lista JSON não vazia de `{displayName,
  isoCode}`, nenhum nome em duas. Registrada no `sources.json`.
- **As categorias não são as quatro da Anistia.** Correspondem três; o *de facto* do
  Cornell (nenhuma execução em pelo menos dez anos, definição da própria base) cobre
  dois valores da Anistia, que para "abolicionista na prática" pede também política ou
  prática estabelecida de não executar. Tabela e razões no `03-modelo-de-dados.md`,
  "Como a pena de morte é preenchida".
- **A página se contradiz:** o mapa da página inicial e a lista da base divergem em sete
  países (Cazaquistão, Israel, Guiné Equatorial, Coreia do Norte, Papua-Nova Guiné,
  Zâmbia, Coreia do Sul), e o mapa pinta cinco que a base não lista. Detalhe no 02, 1.5.

**Decisões suas nesta sessão** (perguntadas e respondidas em 10/11/2026, registradas no
`03` e no `02`):

- **Os 45 países *de facto* ficam vazios com `reason`** até a carga da Anistia; o robô
  nunca escreve `abolitionist_in_practice`.
- **O robô grava a lista da base, e a divergência do mapa fica registrada.** Os quatro
  carimbados apesar dela (Cazaquistão e Israel como `abolitionist_ordinary_crimes`;
  Guiné Equatorial e Coreia do Norte como `retentionist`) são os primeiros a conferir no
  anexo.

**Decisão minha, como pedido: os mapas de nomes ficam em arquivos separados**
(`data/untc-names.json` e `data/cornell-names.json`), com o código comum em
`scripts/country_names.py`. A mesma grafia pode querer dizer coisas diferentes em duas
fontes, e um apelido conferido para uma seria aceito em silêncio para a outra;
separados, cada linha diz para que fonte foi conferida, e tirar uma fonte não mexe na
outra. O preço é repetir algumas linhas (Antígua e Barbuda, RD Congo, São Cristóvão e
Névis…).

**Código:**

- `astraea/sources/listing.py`: tabela publicada em partes (`PARTED_FORMATS`): uma
  requisição por valor do parâmetro, lidas juntas, e a tabela é inteira ou recusada
  inteira. Formato novo `cornell_dpw_status`. `read()` devolve as respostas de todas as
  partes (o `load_treaties.py` acompanha).
- `scripts/country_names.py` (novo): o mapa de nomes, comum à UNTC e ao Cornell.
- `scripts/load_death_penalty.py` (novo): a carga. Simulação por padrão, `--execute`
  grava, `--json-dir` e `--read-on` leem arquivos salvos. Nunca apaga; não toca bloco
  com `checked_by: human` e diz quando o Cornell lê outra coisa; não esvazia bloco
  carimbado de país que sumiu das listas (mantém e avisa); valores iguais mantêm o
  `read_on` antigo; nome sem mapa, ou com `iso2` diferente do conferido, interrompe a
  carga.
- `tests/conftest.py`: o transporte falso distingue URLs que só diferem na *query*.
- Testes: 6 novos em `tests/test_listing.py` (as quatro *fixtures*, sentinela, forma
  desconhecida, nome em duas listas, leitura das quatro partes com `robots.txt`, parte
  que falha) e `tests/test_load_death_penalty.py` (17: a carga das *fixtures* devolve
  exatamente o `countries.json` do repositório; nome sem mapa, código mudado, bloco de
  pessoa, país que sai das listas, leitura sem novidade, mudança campo a campo,
  simulação, leitura que falha; a correspondência; contagens, valores conhecidos, fonte
  e mapa de nomes).

**Dados:** `data/cornell-names.json` (novo): os 22 nomes do Cornell que não são o
`name.en` de `countries.json`, cada um com o `iso2` que a lista dá e a forma da M49 para
esse código; 16 caem nos 197 ("East Timor" → `TLS`, "Ivory Coast" → `CIV`, "Macedonia"
→ `MKD`, "Turkey" → `TUR`…) e 6 ficam fora com `reason`. Os 159 outros nomes casam
letra por letra e, todos os que a M49 tem, com o mesmo alfa-3 do código que o Cornell
dá (Kosovo e Taiwan não estão na M49). `sources.json`: `cornell-dpw` com
`robots_checked_on: 2026-11-10`, `api: yes`, 10 requisições por minuto, a sentinela e o
motivo novo; o `NOTICE` ganhou a fonte. Nenhum campo nem valor novo de vocabulário: os
quatro valores de `death_penalty.status` já tinham rótulo.

**Bateria:** 297 testes passam; `ruff check` e `ruff format --check` limpos; `astraea
validate-lexicon data/lexicon/*.json` valida os cinco; `python scripts/transform.py
--draft --check` passa; `python scripts/build_site.py` simula as duas páginas.
**`--strict` reprova, de propósito, só pelos mesmos 9 status em rascunho** (travas 3 e
6); nenhum campo de pena de morte está em rascunho. `config/` ainda não existe.
`countries.complete` continua 0: faltam os blocos de lei penal e de pena máxima.

**O que as mensagens novas dizem** (saem em inglês):

- `Retentionist: https://…?lawStatus=Retentionist: 1478 bytes, sha256 …` e `4 lists (95
  Abolitionist, …); each one whole, no name in two`: a leitura passou na sentinela; os
  sha256 vão para o CHANGELOG.
- `new: BRA.death_penalty = abolitionist_ordinary_crimes`, `changed: JPN.death_penalty:
  status: …`: o que a carga mudaria. Numa semana sem novidade, nenhuma das duas.
- `left alone (checked by a person): JAM.death_penalty; Cornell reads 'Abolitionist de
  facto', the block says 'abolitionist_in_practice'`: bloco que você carimbou; o robô
  não o toca, e a segunda metade diz que as duas fontes divergem. Não é erro.
- `kept (no longer in the Cornell lists): JPN.death_penalty = 'retentionist', read on
  2026-11-10`: o país sumiu das listas; o robô manteve o que já tinha lido. Vale olhar a
  página do Cornell.
- `FAIL cornell: 'Fooland' is not a name of countries.json nor of
  data/cornell-names.json; check it in the M49 table and add it by hand` e `nothing was
  written`: nome novo ou mudado nas listas. Confira na M49 e acrescente a linha.
- `FAIL cornell: 'Macedonia' now comes with isoCode 'MC', and cornell-names.json was
  checked with 'MK'`: o Cornell mudou o código de um nome do mapa; confira de novo.
- `FAIL Retentionist: not a JSON document`, `FAIL … an empty list`, `FAIL the four lists
  did not come`: a base respondeu outra coisa (erro, página de manutenção, reforma);
  nada foi gravado.

**Anistia: o caminho para a sua carga** (detalhe no `03-modelo-de-dados.md`, "Como a
pessoa carrega o anexo da Anistia"):

- **Campo:** o bloco `death_penalty` do país, inteiro, no lugar do que o robô escreveu:
  `status` (um dos quatro valores, como o anexo classifica), `url` (o documento lido, em
  amnesty.org), `source: "amnesty"`, `read_on` (o dia em que você leu), `confidence:
  "B"`, `checked_by: "human"`. A hipótese de guerra ou de código militar vai em `note`,
  com as suas palavras: `"note": {"pt-BR": {"text": "…", "author": "human"}}`.
- **O que o robô faz com isso:** nada. Bloco com `checked_by: human` nunca é tocado; o
  relatório só avisa quando o Cornell classifica o país de outro jeito.
- **Por onde começar:** os 45 *de facto* (vazios, esperando você) e os quatro em que a
  página do Cornell se contradiz. O `06` fala no anexo de 2024; se já houver um mais
  recente, a escolha de qual carregar é sua.

**Escolhas a revisar** (não decidem nada pendente, mas são suas):

- **`url` é o endereço da lista lida na base** (JSON), não a página do espelho, que é
  mais legível para gente mas não traz a classificação. Se preferir a página, a troca é
  uma linha do *script*.
- **Os 22 que o Cornell não lista ficam vazios com `reason`**, sem nenhuma inferência.
- **Bloco carimbado de país que some das listas fica**, com aviso, e não vira vazio:
  com a base sendo refeita, uma ausência pode ser defeito dela. Se preferir que o robô
  esvazie, é uma condição no `plan`.
- **Confiança B, apesar dos sinais de atraso** (`02`, 1.5). A alternativa seria não
  carimbar nada do Cornell até a Anistia, o que deixaria os 197 vazios.
- **`reason` está em inglês**, como dado, igual ao de `sources.json`.

**Para você (Windows), no PowerShell, dentro da pasta do projeto e com o `.venv`
ativado:**

1. **Ver a carga sem gravar nada** (lê as quatro listas pela internet; leva uns 30
   segundos, porque o robô espera 6 segundos entre as requisições):

   ```powershell
   python scripts\load_death_penalty.py
   ```

   Deve terminar com `up to date: data/countries.json`. Se o Cornell tiver mudado alguma
   classificação, aparecem linhas `changed:` e `would write: data/countries.json`; nada
   foi gravado, e `--execute` grava.
2. **Rodar a bateria:**

   ```powershell
   python scripts\transform.py --draft --check
   python -m pytest
   ```

   O primeiro termina com `static/data is up to date`; o segundo, com `297 passed`.
3. **Ver um país:** abra `data\countries.json` no editor e procure `"JAM"` (vazio, *de
   facto*) ou `"BRA"` (carimbado). O bloco novo está depois de `rome_statute`.
4. **Carregar um país da Anistia**, quando for a hora: troque o bloco `death_penalty`
   desse país pelo modelo do `03`, rode `python scripts\transform.py --draft --execute`
   e faça você o commit (o carimbo `human` é seu, regra 3).
5. **Enviar ao GitHub.** O merge na `main` local já foi feito; o *push* é seu:

   ```powershell
   git push origin main
   ```

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
