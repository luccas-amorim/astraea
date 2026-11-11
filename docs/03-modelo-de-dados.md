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
  lexicon/fixed/<lang>.json  os termos fixos de cada língua, mantidos à mão
  lexicon/<lang>.json     o léxico por língua, gerado de situations.json + termos fixos
  verification.json       trilha: o que foi conferido, quando, por quem, com que resultado
  untc-names.json         nome da UN Treaty Collection → alfa-3, à mão, conferido na M49
  cornell-names.json      nome das listas do Cornell → alfa-3, à mão, conferido na M49
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
| **Confiança por registro** | `checked_by`: `robot` (lido por máquina: adaptador com sentinela ou *script* de carga com o `hash` da resposta registrado no `CHANGELOG.md`), `human` (lido por pessoa, com nome e data), `sample` (caiu na amostra de auditoria e foi conferido); e `level` da triagem (0–3) nas funções 2 e 3 | Argos/Alétheia |
| **Data parcial** | data de ato ou de período pode ser `AAAA`, `AAAA-MM` ou `AAAA-MM-DD`: grava-se a precisão que a fonte dá ("June 2005" é `2005-06`), nunca um dia inventado. `read_on` e as datas de tratado são sempre completas | nova (10/11/2026) |
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

Leitura adotada em 10/11/2026 (fase 1, sessão 3), para o `transform.py` calcular o
"status mais alto":

- A ordem é `allegation` < `political_recognition` < `investigation` < `accusation` <
  `provisional_measures` < `merits_decision`. **`closed` fica abaixo de todos**: diz
  que um procedimento terminou, não é um grau da qualificação, e só aparece quando a
  situação não tem outro status (do contrário um arquivamento esconderia uma medida
  provisória de outro tribunal). A ordem está em `scripts/vocabularies.py`
  (`STATUS_ORDER`).
- Entre dois status do mesmo grau vale o **mais antigo**: a data em que o grau foi
  alcançado pela primeira vez.
- O rótulo é `<status> — <órgão>, <data>`; em `merits_decision` o resultado vai junto,
  entre parênteses ("decisão de mérito (parcial) — International Court of Justice,
  26/02/2007"), porque "decisão de mérito" sozinha não diz se o genocídio foi
  reconhecido. O órgão aparece como está em `by`, na língua em que foi gravado.
- Um status carrega `code`, `by`, `date`, `url`, `confidence` e `checked_by` (e
  `outcome`, quando couber). Não tem `source` nem `read_on`: a leitura por pessoa que o
  confirma fica em `checked_by: human` e, se quiser data, numa linha de
  `verification.json`.

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
| `genocide_convention` | bloco | obrigação de prevenir e punir: `participation` (`party` / `signatory` / `none`), `signature`, `bound_since` (data da vinculação), `consent_type` (`ratification` / `accession` / `succession`), `reservations` (`yes` / `no`), `reservations_article_ix` (`yes` / `no`: alguma declaração ou reserva trata do art. IX, que dá jurisdição à CIJ), `objections` (`yes` / `no`: o país objetou a reserva de outro), `reservations_note` (texto nosso, à mão), proveniência |
| `rome_statute` | bloco | jurisdição do TPI: `participation` (`party` / `signatory` / `withdrawn` / `none`), `signature`, `bound_since`, `consent_type` (`ratification` / `acceptance` / `approval` / `accession` / `succession`), `withdrawal` (data em que a retirada do art. 127 produz efeito, ou `null`), `withdrawal_notified` (data da notificação), `objections` (`yes` / `no`), proveniência |
| `max_penalty` | bloco | escala punitiva: `type` (`years` / `life` / `death` / `unknown`), `years` (inteiro, se `years`), `applies_to_genocide` (`yes` / `no` / `unknown`), proveniência |
| `death_penalty` | bloco | `status` segundo a classificação da Anistia (`abolitionist_all_crimes`, `abolitionist_ordinary_crimes`, `abolitionist_in_practice`, `retentionist`), `note` para a hipótese condicional (guerra), proveniência |
| `situations` | lista de ids | liga o país às situações em que é parte, território ou foro; existe nos 197 registros (lista vazia onde não há elo) e é o espelho de `situations.countries`: o validador cobra os dois lados |
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

**Carimbo dos campos escalares** (decidido em 10/11/2026). `name`, `un_status` e
`un_member_since` são valores soltos, sem bloco onde guardar fonte e data. O carimbo
deles é uma linha de `verification.json` (seção "Trilha de conferência", adiante) que
cobre o campo e o registro. Sem linha que o cubra, o campo é rascunho: reprova em
`--strict` (trava 3) e é contado em `--draft`. Em 10/11/2026 os 197 nomes e o
`un_status` e a data dos 193 membros estão carimbados; o `un_status` de Palestina,
Santa Sé, Kosovo e Taiwan foi carimbado na sessão 4 pela página de Estados não membros
da ONU (`un-non-member-states`): Santa Sé e Palestina com confiança A, porque a página
os lista; Kosovo e Taiwan com confiança B, porque o carimbo vem da ausência nas duas
listas da ONU, que juntas são o rol inteiro de Estados.

**Como o Tabelião preenche os tratados** (fase 2, sessão 1, 10/11/2026). O
`scripts/load_treaties.py` lê os dois XML da UN Treaty Collection pelo adaptador
`listing` e grava os dois blocos nos 197 registros, com `source: untc`, `url` do XML lido,
confiança A e `checked_by: robot`:

- **`participation`** existe para que o bloco afirme alguma coisa também de quem não
  participa: a tabela do depositário é o rol inteiro de participantes, e a ausência
  nela é lida como `none`, carimbada. `signatory` é quem assinou e não se vinculou;
  `withdrawn`, quem saiu pelo art. 127 (a UNTC põe as datas entre colchetes).
- **Taiwan e Kosovo ficam vazios com `reason`** (`{"reason": …}`), não como `none`: não
  têm linha própria na UNTC, e a ausência de quem não pode depositar não é escolha de não
  aderir. A linha "China" é da República Popular da China, e vai para `CHN` como a UNTC a
  publica (assinatura de 1949, ratificação de 1983). Santa Sé e Palestina são lidas como
  qualquer Estado: a Palestina é parte das duas; a Santa Sé, de nenhuma.
- **`reservations`** é `yes` quando o depositário lista, para o país, declaração ou reserva
  com texto. A UNTC reúne as duas numa seção só ("Declarations and Reservations") e o
  robô não as separa; uma entrada que só tem a marca de nota (reserva retirada) não conta.
  **`reservations_article_ix`** é `yes` quando algum desses textos cita o art. IX
  ("article IX", "articles VIII and IX", "Ad article IX"). Nenhum dos dois é juízo sobre o
  alcance da reserva; `reservations_note` fica para a pessoa (é texto nosso, D4).
- **`objections`**: o país aparece na seção de objeções, como autor.
- **Retirada do Estatuto.** `withdrawal` é a data de efeito que a nota do depositário
  dá; uma retirada notificada que ainda não produziu efeito (Níger, Burkina Faso, Mali,
  Venezuela, Chade e Nauru, com efeito em 2027) deixa o país como `party`, com as duas
  datas. Retirada revogada (África do Sul, Gâmbia, Hungria) não deixa rastro no bloco: a
  nota do depositário é a referência.
- **Datas de tratado são sempre completas** (`AAAA-MM-DD`): o validador reprova o
  contrário (estrutura, `check 0`).
- **Leitura sem novidade não muda o arquivo.** Se os valores de um bloco são os mesmos,
  o bloco fica como estava, com o `read_on` antigo, para que o PR mensal mostre diff
  vazio. Bloco com `checked_by: human` nunca é tocado pelo robô.
- **A leitura mensal** (`countries.yml`, desde a fase 2, sessão 3) roda as duas cargas,
  a dos tratados e a da pena de morte, com `--execute`. Quando algum bloco muda, o PR do
  robô traz também o derivado e uma entrada no `CHANGELOG.md` com o sha256 de cada
  resposta lida: é esse registro que faz o novo `read_on` valer como carimbo `robot`
  ("Confiança por registro"). Mês sem novidade não muda dado nem `CHANGELOG`; os sha256
  ficam no corpo do PR e na mensagem do commit vazio. Gravar também uma linha
  `confirmed` em `verification.json` a cada leitura sem novidade, para que o carimbo
  diga a última leitura e não só a primeira, é escolha que continua aberta (fase 2,
  sessão 1, "Escolhas a revisar"); não foi feita.
- **Nomes.** O nome da UNTC casa letra por letra com `name.en` de `countries.json` ou
  está em `data/untc-names.json`, tabela feita à mão e conferida na tabela M49 da Divisão
  de Estatística da ONU (`unsd-m49`), que liga os nomes da ONU ao alfa-3. Nome que não
  casa interrompe a carga antes de gravar qualquer coisa. As Ilhas Cook, parte do
  Estatuto, estão na tabela com `id: null` e `reason`: ficam fora dos 197 da D1.

**Como a pena de morte é preenchida** (fase 2, sessão 2, 10/11/2026). Duas fontes, dois
caminhos, o mesmo bloco `death_penalty`:

- **O robô lê o Cornell, com confiança B.** `scripts/load_death_penalty.py` lê, pelo
  adaptador `listing` (formato `cornell_dpw_status`), as quatro listas que a base do
  Cornell Center on the Death Penalty Worldwide publica, uma por categoria
  (`https://cornell-dpw.herokuapp.com/api/countries/by-law-status/1?lawStatus=…`, a base
  por trás do mapa do espelho `dpw.lawschool.cornell.edu`; `02-fontes.md`, 1.5), e grava
  `status` com `source: cornell-dpw`, `url` da lista em que o país está, confiança B e
  `checked_by: robot`.
- **Correspondência das categorias.** O 03 define `status` pela classificação da
  Anistia; o Cornell tem outra, de quatro categorias também, e só três correspondem:

  | Cornell (`lawStatus`) | O que o Cornell publica | `status` (Anistia) | O robô grava? |
  |---|---|---|---|
  | `Abolitionist` | rótulo "Abolitionist"; sem definição publicada | `abolitionist_all_crimes` | sim |
  | `Abolitionist For Ordinary Crimes` | rótulo "Abolitionist for common law crimes"; sem definição publicada | `abolitionist_ordinary_crimes` | sim |
  | `Abolitionist de facto` | nenhuma execução em pelo menos dez anos | `abolitionist_in_practice` **ou** `retentionist` | **não**: vazio com `reason` |
  | `Retentionist` | executou nos últimos dez anos | `retentionist` | sim |

  As duas primeiras são categorias de lei e, pelo rótulo, fazem o mesmo corte nas duas
  classificações. As duas últimas, não: o *de facto* do Cornell é só o critério dos dez
  anos, e a Anistia, para "abolicionista na prática", pede também uma política ou
  prática estabelecida de não executar, e chama de retencionista quem retém a pena para
  crimes comuns sem essa prática (definições da Anistia como as conhecemos em
  10/11/2026, **a conferir no próprio anexo** na primeira carga). O retencionista do
  Cornell executou nos últimos dez anos e é, pelas duas definições, retencionista também
  para a Anistia; o *de facto* do Cornell cobre dois valores da Anistia, e o robô não
  escolhe entre eles. **Decisão do dono (10/11/2026):** os países *de facto* ficam vazios
  com `reason`, que diz a categoria do Cornell e por que não foi gravada, até a carga da
  Anistia; `abolitionist_in_practice` só entra por pessoa.
- **Guerra e crimes excepcionais.** `abolitionist_ordinary_crimes` já diz que a lei
  mantém a pena só para crimes excepcionais (militares, em tempo de guerra). Dizer qual é
  a hipótese é `note`, texto nosso com `author` (D4); o robô não escreve `note`.
- **País fora das listas** fica vazio com `reason` (22 dos 197 em 10/11/2026). Kosovo,
  Taiwan e Palestina estão nas listas e são carimbados como os demais (nos tratados,
  Kosovo e Taiwan ficam vazios porque não têm linha na UNTC).
- **O que a carga nunca faz.** Não toca bloco com `checked_by: human` (o relatório diz
  quando o Cornell lê outra coisa); não esvazia bloco carimbado de país que sumiu das
  listas (o mantém e avisa: a ausência pode ser defeito da base, que está sendo
  refeita); não muda o arquivo quando os valores não mudaram (o `read_on` antigo fica).
- **Nomes.** `data/cornell-names.json`, mesma regra de `untc-names.json`: nome que não
  é, letra por letra, o `name.en` de `countries.json` precisa de linha conferida na M49,
  e nome sem linha interrompe a carga. Cada linha guarda também o `iso2` que a lista do
  Cornell deu e que a M49 liga ao mesmo alfa-3; se a lista passar a dar outro código para
  aquele nome, a carga para. **Os dois mapas ficam em arquivos separados**, com o código
  comum em `scripts/country_names.py`: a mesma grafia pode querer dizer coisas diferentes
  em duas fontes, e um apelido conferido para uma seria aceito em silêncio para a outra;
  separados, cada linha diz para que fonte foi conferida, e tirar uma fonte não mexe na
  outra.

**Como a pessoa carrega o anexo da Anistia** (carga anual à mão, CC BY-NC-ND 4.0). A
licença impede redistribuir ou derivar o PDF; não impede registrar a classificação de
cada país com a citação. O que se grava, por país, é o bloco `death_penalty` inteiro, no
lugar do que o robô escreveu:

```json
"death_penalty": {
  "status": "abolitionist_in_practice",
  "url": "<endereço, em amnesty.org, do documento lido (o PDF do relatório)>",
  "source": "amnesty",
  "read_on": "<AAAA-MM-DD, o dia em que a pessoa leu o anexo>",
  "confidence": "B",
  "checked_by": "human"
}
```

- `status` é um dos quatro valores, como o anexo classifica o país. Quando o anexo diz em
  que hipótese a pena sobrevive (guerra, código militar), isso vai em `note`, com as
  palavras da pessoa e não as da Anistia:
  `"note": {"pt-BR": {"text": "…", "author": "human"}}`.
- O bloco da pessoa substitui o do robô por inteiro (não se misturam `source` nem
  `reason`). Depois de editar, `python scripts/transform.py --draft --execute` regenera o
  derivado; `static/data/` nunca se edita à mão.
- **Como a carga do Cornell trata esse bloco:** não o toca, nunca. A cada leitura, o
  relatório mostra `left alone (checked by a person): JAM.death_penalty` e, quando o
  Cornell classifica o país de outro jeito, acrescenta `; Cornell reads 'Abolitionist de
  facto', the block says 'abolitionist_in_practice'`. Essa linha é a lista de
  divergências entre as duas fontes, para a pessoa olhar; não é erro.

**Como a carga humana preenche a lei penal** (fase 2, sessão 4, 10/11/2026). `penal_code`,
`domestic_genocide` e `max_penalty` não têm robô (`02-fontes.md`, 1.2): entram país a
país, na ordem da lista de 24 países aprovada pelo dono (`06-roteiro.md`, fase 2, item 4).

- **Quem lê e quem carimba.** Uma sessão lê a fonte oficial e **prepara** o bloco com
  `url` (a página lida), `source`, `read_on` (o dia da leitura) e `confidence`, e deixa
  `checked_by: null`. O bloco preparado é rascunho: passa no `--draft`, reprova no
  `--strict` (trava 3) e aparece na ficha como "rascunho". Quem confere na fonte e
  carimba `checked_by: "human"` é o dono, com `scripts/stamp.py` (regra 3); o robô nunca
  escreve estes blocos.
- **`scripts/stamp.py`** lista os blocos prontos (dado afirmado, os quatro itens do
  carimbo, `checked_by` vazio) e, com `--field BRA.penal_code` (ou `--field BRA`, todos os
  prontos do país), `--by "Nome"` e `--execute`, grava `checked_by: "human"` e o dia da
  leitura da pessoa em `read_on` (`--read-on`, hoje por padrão). Não muda valor nenhum.
  **O nome não entra no dado**: vai na mensagem do commit que o *script* sugere, e o
  autor do commit já diz quem foi (regra 8: nome de pessoa só em `decisions.json`).
- **`confidence` é a da fonte**, como em `sources.json`: `A` para portal oficial
  (Planalto, Gesetze im Internet, InfoLEG…), `B` para o AtlasPen e para consolidação não
  oficial publicada em site oficial (a do Código Penal sérvio na Procuradoria para Crimes
  de Guerra, 11/11/2026).
- **`consolidated_on`** é a data que a fonte dá para a versão do texto; quando a fonte não
  dá, fica `null`. A exceção desta sessão é o Brasil: o Planalto não data a compilação, e
  o valor gravado é o `Last-Modified` da página compilada (09/10/2026), a conferir pelo
  dono.
- **`max_penalty`** é a pena mais alta que a lei permite aplicar ao genocídio: `years` com
  o limite em anos, `life` para prisão perpétua, `death` quando a lei a comina, mesmo com
  moratória (a moratória é hipótese, e vai em `note`, D4). `years` só existe com `type:
  years`.
- **`follows_convention_definition`** compara os grupos e os atos da lei com o art. II da
  Convenção. Remissão expressa ao art. 6º do Estatuto de Roma, que repete o art. II, é
  `yes`; lei que acrescenta um ato e omite outro (Rússia) ou troca "as such" por "such as"
  (Bangladesh) fica `unknown`, e a pessoa decide ao carimbar.
- **País sem leitura** fica com `penal_code` e `domestic_genocide` vazios com `reason`
  (em inglês, como dado), dizendo o que impediu a leitura (portal que veda robôs, que não
  responde, certificado que não se verifica, texto só por JavaScript). `max_penalty` sem
  leitura fica ausente ("ainda não carregado"). Nada se preenche por analogia.
- **Lei lida que não traz o crime** (Gâmbia e China, 11/11/2026): o `penal_code` entra, e
  o `domestic_genocide` fica vazio com `reason`. `status: no` diria que nenhuma lei do país
  tipifica o crime, e a leitura de uma lei não sustenta isso. `max_penalty` fica ausente.
- **`robots.txt` que veda agentes de IA pelo nome**, ou `Content-Signal: ai-input=no`:
  uma sessão que é modelo de linguagem não lê o portal, mesmo que o `User-Agent` do
  Astraea passe; o país espera a leitura do dono (`02-fontes.md`, 1.7).
- **`consolidated_on` continua `null`** quando a fonte dá só a data da última lei
  incorporada ("zuletzt geändert durch", "в редакции"): essa data é de uma alteração, não
  da versão compilada. Gravá-la é escolha do dono.
- **`note` é texto nosso** (D4 pendente): só com as palavras do dono, `author: "human"`.
  A trava 10 (retencionista com pena máxima que não é a morte) pede essa nota; nenhum dos
  países carregados nesta sessão caiu nela.

## Entidade 2: situação (`situations.json`)

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | *slug* em inglês | `rohingya-myanmar`, `gaza-2023`, `darfur`, `srebrenica-1995` |
| `name` | nome por *locale* | exibição |
| `countries` | lista de `{id, role}`, com `role` em `territory`, `party`, `forum`, `applicant`, `respondent` | liga à função 1 |
| `period` | `{start, end, approximate}` | datas aproximadas aceitas, com `approximate: true`; data parcial aceita (`2003`, `2016-10`) |
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

Leitura adotada na carga de 09/11/2026 (fase 1, sessão 2):

- **Uma entrada por canal**, não por organização: a Anistia tem `amnesty` (relatório
  anual, função 1) e `amnesty-news` (RSS, função 2); o TEDH tem `echr` (RSS) e `hudoc`
  (JSON). Assim `function` continua um número só.
- `state` vale para todas: `active` quer dizer que a fonte pode ser citada e usada como o
  `02-fontes.md` decidiu, inclusive só à mão (CICV, N-Lex, Corte IDH); `suspended` é o
  que espera reconferência ou gesto humano (ReliefWeb sem `appname`, LoC, WorldLII; as
  quatro bases de lei penal, o Cartógrafo reconfere todo mês e reabre quando respondem,
  exceto o SHERLOC, suspenso pelo conteúdo);
  `discarded`, o que ficou fora por termos, `robots.txt`, custo ou irrelevância.
- `reason` existe em **toda** entrada e diz o veredito em uma frase, em inglês, como
  dado. Não é texto localizado: a página de fontes, quando existir, decide se o traduz
  (depende da D4).
- `api` = `yes` quando há saída legível por máquina verificada ou documentada (XML,
  JSON, SPARQL), sem contar RSS.
- `robots_checked_on` = `2026-11-06` onde o `02-fontes.md` registra o resultado da
  leitura do `robots.txt` do host (regras citadas, ou 404 simples, que pela RFC 9309 não
  restringe); `null` onde ele diz "não lido", 403, 500, 202, *timeout*, ou lista o host
  em "O que a sondagem não conseguiu".
- `rate_limit_per_minute` vem do `Crawl-delay` (10 s → 6) ou do limite declarado pela
  fonte (GDELT, 5 s → 12); sem nenhum dos dois, `null`.

## Trilha de conferência (`verification.json`)

Uma linha diz **quais campos de quais registros foram lidos onde, quando, por quem e
com que resultado**. É o carimbo dos campos que não são bloco (ver "Carimbo dos campos
escalares") e o registro de qualquer reconferência posterior.

| Campo | Tipo | Por que existe |
|---|---|---|
| `entity` | `countries` / `situations` / `news` / `decisions` / `sources` | de que arquivo são os registros |
| `records` | lista de ids, por extenso | a linha nunca se estende sozinha a um registro novo: quem entra depois precisa de leitura própria |
| `fields` | lista de chaves de campo | o que foi conferido |
| `source`, `url`, `read_on`, `confidence`, `checked_by` | o carimbo | os mesmos cinco de um bloco |
| `result` | `confirmed` / `corrected` / `unconfirmed` | `corrected` quer dizer que a leitura mudou o dado; só `confirmed` e `corrected` carimbam |
| `method` | texto em inglês, como dado | como foi lido (o que foi casado com o quê, onde está o `hash`) |

Quando duas linhas cobrem o mesmo campo, vale a de `read_on` mais recente. A linha
segue as travas 2, 3 e 4 como qualquer bloco.

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

Como ficou em 10/11/2026 (fase 1, sessão 3):

- **Onde vivem os termos fixos:** `data/lexicon/fixed/<lang>.json`, um por língua, no
  próprio formato do léxico (`id`, `version` com a data da última edição, `terms`,
  `context`). São dado, editado à mão. As doze chaves são as mesmas nas cinco línguas
  (`genocide`, `genocide-convention`, `intent-to-destroy`, `icj`, `icc`, `icty`,
  `ictr`, `irmct`, `eccc`, `provisional-measures`, `rome-statute`,
  `universal-jurisdiction`), para que `matched_keys` se compare entre línguas.
- **Quem gera:** `scripts/build_lexicon.py` (simulação por padrão, `--execute` grava).
  Cada situação entra como um termo cuja chave é o `id` da situação, com a categoria
  `situation`; é por essa chave que a notícia ganha o elo em `situations`.
  `data/lexicon/<lang>.json` **não se edita**: o `transform.py` e os testes reprovam o
  arquivo que não bate com as duas fontes.
- **Versão:** `<língua>-<data dos termos fixos>-<resumo do conteúdo>`
  (`pt-2026-11-10-24ff3d5c`). O resumo muda sozinho quando qualquer termo muda, mesmo
  de situação, e é ele que `lexicon_version` grava em cada item.
- **Categorias** (vocabulário fechado, com rótulo em `data/i18n/`): `qualification`
  (a palavra e a intenção), `instrument` (Convenção de 1948, Estatuto de Roma), `court`
  (os tribunais), `procedure` (medidas provisórias, jurisdição universal) e `situation`
  (só para os termos gerados das situações).
- **Formas amarradas.** A reticência (`…`) do motor liga duas partes a até 60
  caracteres. Usa-se onde a palavra sozinha é ruído: "medidas provisórias … CIJ" (no
  Brasil, medida provisória é ato do Executivo), "Tigré … Etiópia" (sem acento a forma
  casa "tigre"), "genocide … Ukraine" (o nome do país sozinho traria toda a guerra).
  Siglas ambíguas ficam fora: `ICC` em inglês (críquete) e `CPI` em português.
- **Nome de país não é termo de situação.** Entram o grupo, o lugar específico e o nome
  do caso ("Rohingya", "Srebrenica", "South Africa v. Israel"). Como um termo de
  situação sozinho já leva o item ao nível 2, a tela de notícias deve exigir alguma
  categoria além de `situation` (decisão da fase 4, quando a tela existir).
- **Árabe:** escrito sem falante, marcado `DRAFT` na `description` dos dois arquivos.
  O casamento é por palavra inteira, e por isso as formas listam as partículas
  prefixadas (و، بـ، لـ، كـ) uma a uma.

## Derivados (`static/data/`)

Gerados por `scripts/transform.py --strict`, nunca editados: `countries.json` com
`updated_at` e `completeness` por campo; `situations.json` com `highest_status`
calculado e o rótulo de exibição montado por *locale* ("medida provisória — CIJ,
26/01/2024" / "provisional measures — ICJ, 26 Jan 2024"); `news-recent.json` (últimos
90 dias, para a tela) e `news-index.json` (contagens por mês, situação e língua, para
o gráfico); `decisions.json` ordenado; `i18n/<locale>.json` copiado de `data/i18n/`;
`quality.json` com o relatório de cada geração (campos vazios por motivo, fontes
vencidas, itens sem carimbo, textos sem versão em cada *locale*).

O que o `transform.py` gera desde 10/11/2026 (o resto entra com as fases 3 e 4):

- `countries.json`: o registro, mais `provenance` (o carimbo de cada campo escalar,
  tirado de `verification.json`), `completeness` (o estado de `un_status` e de cada um
  dos seis blocos: `stamped`, `draft` ou `empty`, e a contagem de cada estado) e
  `updated_at`.
- `situations.json`: o registro, mais `highest_status` (o status mais alto com o seu
  `label` por *locale*, ou `null` quando a situação ainda não tem status) e
  `updated_at`.
- `i18n/<locale>.json`: cópia.
- `quality.json`: `drafts` (quantos campos e registros estão em rascunho, e a lista);
  por campo de país, quantos carimbados, em rascunho e vazios; `countries.complete`
  (países com tudo carimbado); `countries.priority` (país sem `domestic_genocide`
  conferido que é território ou requerido de situação com status ≥ `investigation`:
  o gatilho de promoção do `04-arquitetura.md`); situações por status mais alto e sem
  status; termos e textos que faltam por língua; fontes por estado, sem leitura de
  `robots.txt` e com leitura vencida; versão e tamanho de cada léxico.

O relatório não usa o relógio: `as_of` é a data da leitura mais recente gravada nos
dados, e a validade de 180 dias do `robots.txt` é contada a partir dela. Assim os
mesmos dados dão sempre os mesmos arquivos, e a CI pode exigir sincronia
(`transform.py --check`). Os arquivos são os mesmos em `--strict` e em `--draft`.
O *script* roda em simulação por padrão, grava com `--execute` e nunca apaga: arquivo
que ele não gera e encontra em `static/data/` é só avisado.

## O que o validador reprova (`--strict`)

1. `id` fora do padrão, repetido ou reaproveitado (confere `retired-ids.json`).
2. Valor fora do vocabulário fechado em qualquer enumeração.
3. Campo afirmado (valor não nulo) sem `url`, `source`, `read_on`, `confidence` ou
   `checked_by` (os cinco do carimbo, C1 do `CONTRIBUTING.md`); campo escalar sem linha
   de `verification.json` que o cubra; status sem `checked_by`.
4. `source` que não existe em `sources.json`, ou com `state` ≠ `active`.
5. Status da taxonomia sem `by`, `date`, `url` ou `confidence`; `merits_decision` sem
   `outcome`.
6. Status `provisional_measures` ou `merits_decision` com `checked_by` ≠ `human`.
7. `situations` referenciando id inexistente; país em situação sem `role`; situação
   apontando país inexistente; elo que existe só de um lado.
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

Além das onze, o validador reprova nos dois modos o que impede a leitura (aparece
como `check 0 (structure)`): arquivo ausente ou que não é JSON, registro que não é
objeto, campo com rótulo mas de outra entidade, período ou termos malformados, linha
da trilha apontando registro inexistente, e **léxico gerado que não bate com as suas
fontes**. A trava 10 só vale quando `max_penalty` já foi carregado: enquanto o bloco
não existe, um país retencionista não é contradição. As mensagens saem em inglês, uma
por linha, no formato `check N (nome): onde: o quê`.

## Várias línguas

O contrato dos dados é em inglês e não se traduz. O que se traduz é o que se lê:

| Camada | Onde vive | Regra |
|---|---|---|
| **Rótulos** de campos e de valores | `data/i18n/<locale>.json`: `{"fields": {"domestic_genocide": "Genocídio no direito interno"}, "values": {"death_penalty.status.retentionist": "Retencionista"}}` | todo campo e todo valor de enumeração tem rótulo nos *locales* ativos (trava 11); o dicionário de dados abertos é gerado daqui |
| **Textos nossos** (`note`, `description`, `summary`, `title_translations`, `validity_note`) | no próprio registro, como **texto localizado**: `{"<locale>": {"text": …, "author": …}}` | cada versão tem o seu `author`; uma tradução por modelo é `model:<id>` e segue a política da D4 |
| **Nomes** de país e de situação | `name` por *locale* no registro | nome em inglês obrigatório; o de cada *locale* ativo, cobrado no relatório |
| **Telas** | textos da interface em `site/i18n/<locale>.json` | uma versão por *locale* ativo; rotas iguais nas duas línguas (ver `04-arquitetura.md`) |
| **Texto de terceiro** (título de notícia, nome do caso, título de código penal, `by` de status) | no registro, na língua original, com `language` | nunca traduzido no lugar; a tradução, se houver, vai para `title_translations` |
| **Motivo de campo vazio** (`reason`) | no registro, em inglês, como dado (D8) | não tem versão por *locale*; a tela pt-BR o mostra como está, com `lang="en"` e a marca "disponível só em inglês" (`04-arquitetura.md`, "A tela de países"); uma versão em português, se vier, é texto nosso e segue a D4 |

**Chave dos rótulos** (adotada em 09/11/2026, lista em `scripts/vocabularies.py`): o
campo é rotulado pelo caminho dentro do registro, com ponto para bloco aninhado e sem
índice de lista (`penal_code.exists`, `statuses.code`, `case.parties.role`); os campos
que significam o mesmo em qualquer bloco (`url`, `source`, `read_on`, `confidence`,
`checked_by`, `note`, `reason`, `author`, `text`) são rotulados uma vez, pelo nome solto;
o valor é `<chave do campo>.<valor>` (`death_penalty.status.retentionist`,
`confidence.A`, `level.3`, `function.1`, `categories.court`). Os booleanos ainda não
têm rótulo. As categorias do léxico, os campos da trilha e os campos derivados
(`completeness`, `provenance`, `highest_status`, `label`) ganharam rótulo em
10/11/2026.

**Datas por *locale*.** Cada `data/i18n/<locale>.json` traz `formats`: os padrões
`date`, `month` e `year` (com as marcas `D`, `DD`, `MM`, `MMM` e `YYYY`) e
`months_short`. É dali que sai "26 Jan 2024" em `en` e "26/01/2024" em `pt-BR` no
rótulo de status, e a data parcial usa o padrão da sua precisão ("Jun 2005",
"06/2005"). A tela deve ler os mesmos padrões.

*Locales* ativos no MVP: `en` e `pt-BR`. As chaves de *locale* seguem a BCP 47
(`pt-BR`); a língua de documento de terceiro segue a ISO 639-1 (`pt`), que é o que as
fontes informam. *Locale* novo entra pela fase multilíngue do `06-roteiro.md`.
