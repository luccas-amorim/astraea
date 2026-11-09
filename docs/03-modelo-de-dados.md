# 03 — Modelo de dados

Quatro entidades, todas em JSON legível, com a mesma disciplina do AtlasPen: a
**fonte** é editável e validada; o **derivado** é gerado e consumido pelo site; todo
campo afirmado carrega fonte, data e confiança; o que não se sabe fica vazio e diz
por quê.

**Língua dos dados (D8, decidida em 09/11/2026).** Nomes de arquivo, chaves, valores
de vocabulário fechado, *ids* e comandos são em **inglês**, e não mudam depois de
publicados: são o contrato de quem consome os dados. A documentação continua em
português. O que se lê em várias línguas (rótulos, textos nossos, telas) está na seção
"Várias línguas", no fim deste documento.

```
data/
  countries.json          função 1: um objeto por país (197)
  situations.json         a entidade que liga as três telas
  news/YYYY/MM.jsonl      função 2: um documento por linha, particionado por mês
  decisions.json          função 3: um ato processual por objeto
  sources.json            cada fonte declarada, com grau de confiança e termos
  lexicon/<lang>.json     o léxico por língua, gerado de situations.json + termos fixos
  verification.json       trilha: o que foi conferido, quando, por quem, com que resultado
  exceptions.json         achado já julgado, com motivo e data
  retired-ids.json        ids que já foram públicos e nunca voltam
  i18n/<locale>.json      rótulos de campos e de valores por língua (en, pt-BR)
```

## Convenções transversais

| Convenção | Regra | Herança |
|---|---|---|
| **Identificador estável** | `countries.id` é ISO 3166-1 alfa-3 (`XKX` para Kosovo, documentado); `situations.id` é *slug* ASCII em inglês; `news.id` e `decisions.id` são `hash` curto da URL normalizada. Nenhum `id` é reatribuído; o que sai entra em `retired-ids.json` | AtlasPen C3 |
| **Bloco de proveniência** | todo campo afirmado é um objeto com `source`, `url`, `read_on`, `confidence` e `checked_by`, ou uma linha em `verification.json`; campo sem fonte é `null` com `reason` | AtlasPen `conferencia.json` |
| **Confiança por fonte** | `A` oficial ou intergovernamental (UN Treaty Collection, tribunal, diário oficial); `B` acadêmica, LII ou ONG especializada com método público (CICV, Cornell, Amnesty); `C` imprensa, comunitária ou secundária (Wikipedia, Wikidata, agregadores). Declarada em `sources.json`, nunca no registro | nova |
| **Confiança por registro** | `checked_by`: `robot` (lido por adaptador com sentinela), `human` (lido por pessoa, com nome e data), `sample` (caiu na amostra de auditoria e foi conferido); e `level` da triagem (0–3) nas funções 2 e 3 | Argos/Alétheia |
| **Vocabulário fechado** | todo campo de enumeração tem lista fixa validada no *build*; valor fora da lista reprova | AtlasPen `--estrito` |
| **Condição, não lacuna** | quando a resposta depende de hipótese (pena de morte só em tempo de guerra; genocídio tipificado por remissão ao Estatuto), o campo principal fica no valor seguro e `note` diz a hipótese | AtlasPen `*_condicao` |
| **Língua original** | todo texto de terceiro registra `language` ISO 639-1; todo texto nosso (nota, descrição, resumo, tradução de título) é um **texto localizado** (ver "Várias línguas"), e cada versão registra `author` = `human` ou `model:<id>` | nova |
| **Nunca texto integral** | nenhuma entidade tem campo de corpo; `excerpt` só nos relatórios de rodada, até 320 caracteres, como no Alétheia | Alétheia |

## Taxonomia de status do rótulo "genocídio"

É a regra mais importante do projeto. "Genocídio" é qualificação jurídica, e o
Astraea registra **quem** a fez e **em que grau**. A escala abaixo é ordinal, mas não
é uma linha única: um mesmo contexto pode ter alegação de Estado, investigação de
comissão da ONU e medida provisória da CIJ ao mesmo tempo, e o registro guarda todas.

| Código | Status | Quem pode produzi-lo | Exemplo |
|---|---|---|---|
| `allegation` | alguém afirma que há ou houve genocídio | Estado, organismo internacional sem competência jurisdicional, relator especial, ONG, academia, imprensa (o campo `by` diz qual) | Gâmbia, na petição à CIJ (2019); relatório de ONG |
| `political_recognition` | órgão político reconhece formalmente | parlamento, governo, assembleia internacional, por resolução ou declaração | reconhecimento do genocídio armênio por parlamentos; declaração dos EUA sobre os Rohingya (2022) |
| `investigation` | órgão com mandato investiga a hipótese | comissão de inquérito ou missão de apuração da ONU, Procuradoria do TPI (exame preliminar ou investigação aberta), procuradoria nacional | investigação do TPI em Darfur (2005) |
| `accusation` | órgão competente formaliza acusação | Procuradoria do TPI (mandado de prisão, confirmação de acusações), procuradoria nacional (denúncia recebida), Estado requerente na CIJ (petição inicial) | mandado contra Al Bashir por genocídio (2010) |
| `provisional_measures` | tribunal ordena medidas sem decidir o mérito | CIJ (art. 41 do Estatuto), tribunais regionais | ordem da CIJ de 26/01/2024, África do Sul v. Israel |
| `merits_decision` | tribunal decide se houve genocídio (ou responsabilidade por ele) | CIJ, TPI, TPII/TPIR/IRMCT, ECCC, tribunal nacional | Bósnia v. Sérvia (2007); Akayesu (TPIR, 1998); Krstić (TPII, 2004) |
| `closed` | o procedimento terminou sem decisão de mérito, ou o mérito foi negado | tribunal, procuradoria | arquivamento; absolvição |

Regras:

1. Cada status tem obrigatoriamente `by` (o órgão), `date`, `url` da fonte e
   `confidence`. Sem os quatro, o validador reprova.
2. **A tela mostra o status mais alto já alcançado, sempre com o órgão ao lado:**
   "medida provisória — CIJ, 26/01/2024", "alegação — Gâmbia, 11/11/2019" (e, na tela
   em inglês, "provisional measures — ICJ, 26 Jan 2024"). Nunca a palavra "genocídio"
   como rótulo solto de uma situação ou de um país, em nenhuma língua.
3. `merits_decision` exige `outcome` (`recognized`, `not_recognized`, `partial`) e o
   dispositivo da decisão. A CIJ pode reconhecer o genocídio e não a responsabilidade
   do Estado (Bósnia v. Sérvia): isso é `partial` com nota.
4. Alegação de imprensa não vira registro de status: vira notícia (função 2) ligada à
   situação. Só alegação de Estado, organismo internacional ou organização com método
   público entra na taxonomia, e com `confidence` da fonte.
5. O robô só grava `allegation` e `investigation` quando a fonte é a própria autora do
   ato (a petição no site da CIJ, o comunicado da Procuradoria no site do TPI). Os
   demais status entram por pessoa, com a decisão lida.

## Entidade 1: país (`countries.json`)

Cada campo abaixo vem com a justificativa de existir. Campos que não respondem a uma
pergunta da pesquisa não entram; a lista cresce por decisão registrada.

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | alfa-3 | URL pública (`/countries/BRA`) e chave de todo cruzamento |
| `name` | nome por *locale* (`{"en": …, "pt-BR": …}`) | exibição; o nome oficial longo fica em `note` |
| `un_status` | `member` / `observer` / `non_member` | separa os 193 dos 4 e deixa explícito o reconhecimento limitado |
| `un_member_since` | data ou `null` | contexto temporal das obrigações |
| `penal_code` | bloco | **a pergunta central da função 1**: há um código penal vigente, de quando, onde se lê o texto oficial. `exists` (`yes` / `no` / `unknown`; `no` cobre países de *common law* sem código, com `note`), `title` (na língua original), `enacted_year`, `consolidated_on`, `official_url`, `alternative_url` (LII, tradução), `language`, proveniência |
| `domestic_genocide` | bloco | se o país pode julgar genocídio pelo direito próprio: `status` (`criminalized` / `partial` / `no` / `unknown`), `provision`, `instrument`, `year`, `follows_convention_definition` (`yes` / `broader` / `narrower` / `unknown`), proveniência. `partial` cobre tipificação por remissão genérica ao direito internacional |
| `genocide_convention` | bloco | obrigação de prevenir e punir: `signature`, `bound_since` (data da vinculação), `consent_type` (`ratification` / `accession` / `succession`), `reservations` (`yes` / `no`), `reservations_note` (p. ex. ao art. IX, que afasta a jurisdição da CIJ), proveniência |
| `rome_statute` | bloco | jurisdição do TPI: `signature`, `bound_since`, `withdrawal` (data ou `null`), proveniência |
| `max_penalty` | bloco | escala punitiva: `type` (`years` / `life` / `death` / `unknown`), `years` (inteiro, se `years`), `applies_to_genocide` (`yes` / `no` / `unknown`), proveniência |
| `death_penalty` | bloco | `status` segundo a classificação da Anistia (`abolitionist_all_crimes`, `abolitionist_ordinary_crimes`, `abolitionist_in_practice`, `retentionist`), `note` para a hipótese condicional (guerra), proveniência |
| `situations` | lista de ids | liga o país às situações em que é parte, território ou foro |
| `promotion` | bloco | `level` (`surface` / `under_investigation` / `detailed`), `trigger`, `since`, `where` (URL do repositório-filho ou pasta) |
| `valid_until`, `validity_note` | data, texto localizado | país que deixou de existir não sai: ganha data e nota, como o acervo do AtlasPen |
| `updated_at` | data | o `max` de todos os `read_on` do registro, derivado |

Exemplo preenchido (Brasil). Os valores de ratificação são os que constam da UN
Treaty Collection e do Decreto 30.822/1952; a primeira sessão de carga **reconfere**
cada um antes de carimbar `checked_by`. Os títulos e diplomas ficam na língua
original; as notas são textos nossos, por *locale*.

```json
{
  "id": "BRA",
  "name": { "en": "Brazil", "pt-BR": "Brasil" },
  "un_status": "member",
  "un_member_since": "1945-10-24",
  "penal_code": {
    "exists": "yes",
    "title": "Código Penal (Decreto-Lei 2.848, de 7 de dezembro de 1940)",
    "enacted_year": 1940,
    "consolidated_on": "2026-10-26",
    "official_url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
    "alternative_url": "https://atlaspen.com.br/data/crimes.json",
    "language": "pt",
    "source": "planalto",
    "read_on": "2026-10-26",
    "confidence": "A",
    "checked_by": "robot"
  },
  "domestic_genocide": {
    "status": "criminalized",
    "instrument": "Lei 2.889, de 1º de outubro de 1956",
    "provision": "art. 1º",
    "year": 1956,
    "follows_convention_definition": "yes",
    "note": {
      "pt-BR": { "text": "Pena por remissão aos tipos do Código Penal (art. 1º, a–e); hediondo por força do art. 1º, parágrafo único, da Lei 8.072/1990. Registro detalhado no AtlasPen.", "author": "human" }
    },
    "url": "https://www.planalto.gov.br/ccivil_03/leis/l2889.htm",
    "source": "planalto",
    "read_on": null,
    "confidence": "A",
    "checked_by": null
  },
  "genocide_convention": {
    "signature": "1948-12-11",
    "bound_since": "1952-04-15",
    "consent_type": "ratification",
    "reservations": "no",
    "reservations_note": null,
    "url": "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=IV-1&chapter=4",
    "source": "untc",
    "read_on": null,
    "confidence": "A",
    "checked_by": null
  },
  "rome_statute": {
    "signature": "2000-02-07",
    "bound_since": "2002-06-20",
    "withdrawal": null,
    "url": "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XVIII-10&chapter=18",
    "source": "untc",
    "read_on": null,
    "confidence": "A",
    "checked_by": null
  },
  "max_penalty": {
    "type": "years",
    "years": 40,
    "applies_to_genocide": "yes",
    "note": {
      "pt-BR": { "text": "Art. 75 do Código Penal, com a redação da Lei 13.964/2019.", "author": "human" }
    },
    "url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
    "source": "planalto",
    "read_on": null,
    "confidence": "A",
    "checked_by": null
  },
  "death_penalty": {
    "status": "abolitionist_ordinary_crimes",
    "note": {
      "pt-BR": { "text": "Admitida só em caso de guerra declarada (CF, art. 5º, XLVII, a; CPM).", "author": "human" }
    },
    "url": "https://www.amnesty.org/en/what-we-do/death-penalty/",
    "source": "amnesty",
    "read_on": null,
    "confidence": "B",
    "checked_by": null
  },
  "situations": [],
  "promotion": { "level": "surface", "trigger": null, "since": null, "where": null },
  "valid_until": null,
  "validity_note": null
}
```

Os `read_on: null` com `checked_by: null` são deliberados: o exemplo diz o que se
espera encontrar, e o carimbo só vem quando o robô ou a pessoa leu a fonte. Um
registro assim **não passa** no validador estrito; passa no modo `--draft`, que é o
da carga inicial.

## Entidade 2: situação (`situations.json`)

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | *slug* em inglês | `rohingya-myanmar`, `gaza-2023`, `darfur`, `srebrenica-1995` |
| `name` | nome por *locale* | exibição |
| `countries` | lista de `{id, role}`, com `role` em `territory`, `party`, `forum`, `applicant`, `respondent` | liga à função 1 |
| `period` | `{start, end, approximate}` | datas aproximadas aceitas, com `approximate: true` |
| `statuses` | lista de objetos da taxonomia, cada um com `code`, `by`, `date`, `url`, `confidence`, `checked_by` | **a resposta à questão transversal 2**; a tela mostra o mais alto |
| `description` | texto localizado, até 600 caracteres por versão | contexto sem copiar terceiros |
| `terms` | lista de `{lang, forms[], exclusions[]}` | gera o léxico; é o que o robô procura |
| `promotion` | igual ao de país | onde vive o detalhamento |
| `updated_at` | derivado | |

Exemplo (abreviado):

```json
{
  "id": "rohingya-myanmar",
  "name": { "en": "Rohingya (Myanmar)", "pt-BR": "Rohingya (Mianmar)" },
  "countries": [
    { "id": "MMR", "role": "territory" },
    { "id": "GMB", "role": "applicant" },
    { "id": "MMR", "role": "respondent" }
  ],
  "period": { "start": "2016-10-01", "end": null, "approximate": true },
  "statuses": [
    { "code": "investigation", "by": "Independent International Fact-Finding Mission on Myanmar (UN)", "date": "2018-09-12", "url": "https://www.ohchr.org/en/hr-bodies/hrc/myanmar-ffm/index", "confidence": "A", "checked_by": "human" },
    { "code": "accusation", "by": "The Gambia, application instituting proceedings (ICJ)", "date": "2019-11-11", "url": "https://www.icj-cij.org/case/178", "confidence": "A", "checked_by": "human" },
    { "code": "provisional_measures", "by": "International Court of Justice", "date": "2020-01-23", "url": "https://www.icj-cij.org/case/178", "confidence": "A", "checked_by": "human" },
    { "code": "political_recognition", "by": "United States Secretary of State", "date": "2022-03-21", "url": null, "confidence": "B", "checked_by": null }
  ],
  "description": {
    "pt-BR": { "text": "Operações das forças armadas de Mianmar contra a população rohingya no estado de Rakhine a partir de 2016–2017, com deslocamento em massa para Bangladesh. A Gâmbia acionou a CIJ em 2019 com base na Convenção de 1948; a Corte ordenou medidas provisórias em 2020 e o mérito está pendente.", "author": "human" }
  },
  "terms": [
    { "lang": "en", "forms": ["Rohingya", "Rakhine State"], "exclusions": [] },
    { "lang": "pt", "forms": ["rohingya", "roingá"], "exclusions": [] },
    { "lang": "fr", "forms": ["Rohingya", "Rohingyas"], "exclusions": [] }
  ],
  "promotion": { "level": "surface", "trigger": null, "since": null, "where": null }
}
```

O status `political_recognition` do exemplo está com `url: null` e sem carimbo de
propósito: é como um dado entra em rascunho e como o validador o acusa. O campo `by`
guarda o nome do órgão como ele mesmo se apresenta (em geral em inglês ou francês); a
tela o exibe tal como está.

## Entidade 3: notícia (`news/YYYY/MM.jsonl`)

Uma linha por documento, no formato que o Alétheia já grava (com as chaves traduzidas),
com quatro campos a mais (língua, situações, veículo, resumo).

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | `hash` da URL normalizada | identidade; dois endereços com o mesmo `text_hash` são um documento |
| `url` | texto | o *link*, que é o que se publica |
| `domain`, `outlet`, `outlet_country` | texto, texto, alfa-2 | quem publicou e de onde; `outlet_country` vem do GDELT quando houver |
| `title`, `language` | texto, ISO 639-1 | o título como a fonte deu, na língua em que deu |
| `title_translations` | texto localizado ou `null` | tradução nossa, marcada; nunca substitui o original |
| `published_at`, `captured_at` | data, data-hora | |
| `channel`, `source` | `gdelt` / `rss` / `listing`; id da fonte | proveniência do achado |
| `situations` | lista de ids | o elo com a taxonomia; vazio quando o léxico casou só termos gerais |
| `matched_keys`, `categories`, `level`, `lexicon_version` | como no Alétheia | auditoria da triagem |
| `summary` | texto localizado ou `null` | o resumo próprio, só para itens promovidos ou de nível 3 revisados |
| `snapshot`, `text_hash` | URL do Wayback, sha256 | cópia de referência e prova do que foi lido |
| `checked_by` | `robot` / `human` / `sample` | |

Exemplo (ilustrativo: a URL é fictícia e marcada como tal; o formato é o real):

```json
{"id": "9c1e4b7a2d03f6e8", "url": "https://exemplo.org/2026/11/cij-ordem-medidas", "domain": "exemplo.org", "outlet": "Exemplo Notícias", "outlet_country": "BR", "title": "CIJ ordena novas medidas provisórias em caso de genocídio", "language": "pt", "title_translations": null, "published_at": "2026-11-03", "captured_at": "2026-11-04T09:21:07+00:00", "channel": "gdelt", "source": "gdelt:genocide-pt", "situations": ["gaza-2023"], "matched_keys": ["genocide", "icj", "provisional-measures"], "categories": ["court", "qualification"], "level": 3, "lexicon_version": "pt-2026-11-01", "summary": null, "snapshot": null, "text_hash": "sha256:…", "checked_by": "robot"}
```

## Entidade 4: decisão (`decisions.json`)

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | `hash` da URL oficial | identidade |
| `court` | vocabulário fechado: `icj`, `icc`, `irmct`, `icty`, `ictr`, `eccc`, `rscsl`, `ksc`, `iacthr` (Corte IDH), `echr` (TEDH), `afchpr` (Corte Africana), `national` | |
| `case` | `{court_case_id, number, name, parties[]}` | a CIJ numera casos (178, 192); o TPI usa `ICC-02/05-01/09` |
| `act_type` | `application`, `provisional_measures_order`, `incidental_decision`, `merits_judgment`, `advisory_opinion`, `arrest_warrant`, `confirmation_of_charges`, `conviction`, `acquittal`, `appeal`, `procedural_step`, `press_release` | a granularidade mínima: o ato, não o caso |
| `date` | data | do ato, não da captura |
| `official_url` | texto | sempre o site do tribunal; `alternative_url` para o PDF |
| `languages` | lista ISO 639-1 | a CIJ publica em inglês e francês; o TPI, em inglês e francês; a Corte IDH, em espanhol |
| `situations` | lista de ids | |
| `taxonomy_status` | código da taxonomia que este ato produz, ou `null` (andamento sem efeito de status) | é daqui que `situations.statuses` é derivado |
| `outcome` | só em `merits_judgment`, `conviction` e `acquittal`: `recognized` / `not_recognized` / `partial` | |
| `summary` | texto localizado | resumo próprio, obrigatório para `merits_judgment` e `provisional_measures_order` |
| `channel`, `source`, `captured_at`, `snapshot`, `text_hash`, `level`, `lexicon_version` | como em notícia | |
| `checked_by`, `checked_on` | | ato que muda status exige `human` |

Exemplo preenchido (ato real; a URL do caso é a página oficial, verificada em
06/11/2026; o PDF específico da ordem deve ser conferido na carga):

```json
{
  "id": "4f2a9e01c7b35d16",
  "court": "icj",
  "case": {
    "court_case_id": "192",
    "number": "General List No. 192",
    "name": "Application of the Convention on the Prevention and Punishment of the Crime of Genocide in the Gaza Strip (South Africa v. Israel)",
    "parties": [ { "country": "ZAF", "role": "applicant" }, { "country": "ISR", "role": "respondent" } ]
  },
  "act_type": "provisional_measures_order",
  "date": "2024-01-26",
  "official_url": "https://www.icj-cij.org/case/192",
  "alternative_url": null,
  "languages": ["en", "fr"],
  "situations": ["gaza-2023"],
  "taxonomy_status": "provisional_measures",
  "outcome": null,
  "summary": {
    "pt-BR": { "text": "A Corte, por maioria, indicou medidas provisórias a Israel com base na plausibilidade dos direitos invocados pela África do Sul sob a Convenção de 1948, sem decidir se houve genocídio. Ordens posteriores (março e maio de 2024) ampliaram as medidas.", "author": "human" }
  },
  "channel": "listing",
  "source": "icj:cases",
  "captured_at": "2026-11-06T13:00:00+00:00",
  "snapshot": null,
  "text_hash": null,
  "level": 3,
  "lexicon_version": "en-2026-11-01",
  "checked_by": "human",
  "checked_on": "2026-11-06"
}
```

## Fontes (`sources.json`)

Uma entrada por fonte, com o que o `02-fontes.md` apurou, em dado: `id`, `name`,
`url`, `function` (1, 2 ou 3), `confidence` (A/B/C), `license`, `terms_url`,
`robots_checked_on`, `api` (`yes`/`no`), `rate_limit_per_minute`, `languages`,
`sentinel` (string que prova integridade da resposta), `state_media` (`true` para
agência estatal, que a tela marca), `no_text_by_policy` (`true` para domínio com
*opt-out* de mineração de texto), `state` (`active`, `suspended`, `discarded`, com
`reason`). O robô recusa fonte sem `robots_checked_on` nos últimos 180 dias: é o
Arquivista do AtlasPen aplicado às fontes.

## Léxico (`lexicon/<lang>.json`)

Formato do `lexico.schema.json` do Argos, com as chaves traduzidas e sem outra
alteração: `terms[]` com `key`, `forms`, `exclusions`, `categories`, `weight`, e
`context.requires_any`. Um arquivo por língua. Gerado por *script* a partir de duas
listas:

- **termos fixos** por língua, mantidos à mão: "genocídio", "Convenção de 1948",
  "Corte Internacional de Justiça", "medidas provisórias", "intenção de destruir"… com
  exclusões ("genocídio cultural" sem contexto jurídico; títulos de obras);
- **termos de situação**, lidos de `situations.terms` para a língua.

O `context.requires_any` por língua traz os marcadores jurídicos ("tribunal",
"corte", "ordem", "denúncia", "procurador", "convenção") que separam a notícia
relevante do uso retórico da palavra. É a diferença entre nível 1 e nível 2. As
**formas** do léxico ficam, claro, na língua do arquivo: só as chaves são em inglês.

## Derivados (`static/data/`)

Gerados por `scripts/transform.py --strict`, nunca editados: `countries.json` com
`updated_at` e `completeness` por campo; `situations.json` com `highest_status`
calculado e o rótulo de exibição montado por *locale* ("medida provisória — CIJ,
26/01/2024" / "provisional measures — ICJ, 26 Jan 2024"); `news-recent.json` (últimos
90 dias, para a tela) e `news-index.json` (contagens por mês, situação e língua, para
o gráfico); `decisions.json` ordenado; `i18n/<locale>.json` copiado de `data/i18n/`;
`quality.json` com o relatório de cada geração (campos vazios por motivo, fontes
vencidas, itens sem carimbo, textos sem versão em cada *locale*).

## O que o validador reprova (`--strict`)

1. `id` fora do padrão, repetido ou reaproveitado (confere `retired-ids.json`).
2. Valor fora do vocabulário fechado em qualquer enumeração.
3. Campo afirmado (valor não nulo) sem `url`, `source`, `read_on` ou `confidence`.
4. `source` que não existe em `sources.json`, ou com `state` ≠ `active`.
5. Status da taxonomia sem `by`, `date` ou `url`; `merits_decision` sem `outcome`.
6. Status `provisional_measures` ou `merits_decision` com `checked_by` ≠ `human`.
7. `situations` referenciando id inexistente; país em situação sem `role`.
8. Qualquer versão de `description` ou `summary` com mais de 600 caracteres
   (resumo é resumo, não cópia).
9. Texto nosso sem `author` em alguma versão; texto localizado com *locale* fora da
   lista de `data/i18n/`.
10. `max_penalty.type = years` sem `years`; `death_penalty.status = retentionist` com
    `max_penalty.type ≠ death` sem `note`.
11. Chave de campo ou valor de enumeração sem rótulo em `data/i18n/en.json` ou
    `data/i18n/pt-BR.json` (a tela não pode mostrar chave crua).

O modo `--draft` relaxa só 3 e 6, para a carga inicial, e o relatório de qualidade
conta quantos registros ainda estão em rascunho. A falta de uma versão de texto num
*locale* não reprova: a tela mostra a versão que existe, marcada com a língua, e
`quality.json` conta a lacuna.

## Várias línguas

O contrato dos dados é em inglês e não se traduz. O que se traduz é o que se lê:

| Camada | Onde vive | Regra |
|---|---|---|
| **Rótulos** de campos e de valores | `data/i18n/<locale>.json`: `{"fields": {"domestic_genocide": "Genocídio no direito interno"}, "values": {"death_penalty.status.retentionist": "Retencionista"}}` | todo campo e todo valor de enumeração tem rótulo nos *locales* ativos (trava 11); o dicionário de dados abertos é gerado daqui |
| **Textos nossos** (`note`, `description`, `summary`, `title_translations`, `validity_note`) | no próprio registro, como **texto localizado**: `{"<locale>": {"text": …, "author": …}}` | cada versão tem o seu `author`; uma tradução por modelo é `model:<id>` e segue a política da D4 |
| **Nomes** de país e de situação | `name` por *locale* no registro | nome em inglês obrigatório; o de cada *locale* ativo, cobrado no relatório |
| **Telas** | textos da interface em `site/i18n/<locale>.json` | uma versão por *locale* ativo; rotas iguais nas duas línguas (ver `04-arquitetura.md`) |
| **Texto de terceiro** (título de notícia, nome do caso, título de código penal, `by` de status) | no registro, na língua original, com `language` | nunca traduzido no lugar; a tradução, se houver, vai para `title_translations` |

*Locales* ativos no MVP: `en` e `pt-BR`. As chaves de *locale* seguem a BCP 47
(`pt-BR`); a língua de documento de terceiro segue a ISO 639-1 (`pt`), que é o que as
fontes informam. *Locale* novo entra pela fase multilíngue do `06-roteiro.md`.
