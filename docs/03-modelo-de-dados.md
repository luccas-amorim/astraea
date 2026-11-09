# 03 — Modelo de dados

Quatro entidades, todas em JSON legível, com a mesma disciplina do AtlasPen: a
**fonte** é editável e validada; o **derivado** é gerado e consumido pelo site; todo
campo afirmado carrega fonte, data e confiança; o que não se sabe fica vazio e diz
por quê.

```
data/
  paises.json          função 1: um objeto por país (197)
  situacoes.json       a entidade que liga as três telas
  noticias/AAAA/MM.jsonl   função 2: um documento por linha, particionado por mês
  decisoes.json        função 3: um ato processual por objeto
  fontes.json          cada fonte declarada, com grau de confiança e termos
  lexico/<lingua>.json o léxico por língua, gerado de situacoes.json + termos fixos
  conferencia.json     trilha: o que foi conferido, quando, por quem, com que resultado
  excecoes.json        achado já julgado, com motivo e data
```

## Convenções transversais

| Convenção | Regra | Herança |
|---|---|---|
| **Identificador estável** | `paises.id` é ISO 3166-1 alfa-3 (`XKX` para Kosovo, documentado); `situacoes.id` é *slug* ASCII; `noticias.id` e `decisoes.id` são `hash` curto da URL normalizada. Nenhum `id` é reatribuído; o que sai entra em `ids-aposentados.json` | AtlasPen C3 |
| **Bloco de proveniência** | todo campo afirmado é um objeto `{valor, fonte, url, lido_em, confianca}` ou uma linha em `conferencia.json`; campo sem fonte é `null` com `motivo` | AtlasPen `conferencia.json` |
| **Confiança por fonte** | `A` oficial ou intergovernamental (UN Treaty Collection, tribunal, diário oficial); `B` acadêmica, LII ou ONG especializada com método público (CICV, Cornell, Amnesty); `C` imprensa, comunitária ou secundária (Wikipedia, Wikidata, agregadores). Declarada em `fontes.json`, nunca no registro | nova |
| **Confiança por registro** | `conferido_por`: `robo` (lido por adaptador com sentinela), `humano` (lido por pessoa, com nome e data), `amostra` (caiu na amostra de auditoria e foi conferido); e `nivel` da triagem (0–3) nas funções 2 e 3 | Argos/Alétheia |
| **Vocabulário fechado** | todo campo de enumeração tem lista fixa validada no *build*; valor fora da lista reprova | AtlasPen `--estrito` |
| **Condição, não lacuna** | quando a resposta depende de hipótese (pena de morte só em tempo de guerra; genocídio tipificado por remissão ao Estatuto), o campo principal fica no valor seguro e `nota` diz a hipótese | AtlasPen `*_condicao` |
| **Língua original** | todo texto de terceiro registra `lingua` ISO 639-1; todo texto nosso (resumo, tradução de título) registra `autor` = `humano` ou `modelo:<id>` | nova |
| **Nunca texto integral** | nenhuma entidade tem campo de corpo; `trecho` só nos relatórios de rodada, até 320 caracteres, como no Alétheia | Alétheia |

## Taxonomia de status do rótulo "genocídio"

É a regra mais importante do projeto. "Genocídio" é qualificação jurídica, e o
Astraea registra **quem** a fez e **em que grau**. A escala abaixo é ordinal, mas não
é uma linha única: um mesmo contexto pode ter alegação de Estado, investigação de
comissão da ONU e medida provisória da CIJ ao mesmo tempo, e o registro guarda todas.

| Código | Status | Quem pode produzi-lo | Exemplo |
|---|---|---|---|
| `alegacao` | alguém afirma que há ou houve genocídio | Estado, organismo internacional sem competência jurisdicional, relator especial, ONG, academia, imprensa (o campo `por` diz qual) | Gâmbia, na petição à CIJ (2019); relatório de ONG |
| `reconhecimento_politico` | órgão político reconhece formalmente | parlamento, governo, assembleia internacional, por resolução ou declaração | reconhecimento do genocídio armênio por parlamentos; declaração dos EUA sobre os Rohingya (2022) |
| `investigacao` | órgão com mandato investiga a hipótese | comissão de inquérito ou missão de apuração da ONU, Procuradoria do TPI (exame preliminar ou investigação aberta), procuradoria nacional | investigação do TPI em Darfur (2005) |
| `acusacao` | órgão competente formaliza acusação | Procuradoria do TPI (mandado de prisão, confirmação de acusações), procuradoria nacional (denúncia recebida), Estado requerente na CIJ (petição inicial) | mandado contra Al Bashir por genocídio (2010) |
| `medida_provisoria` | tribunal ordena medidas sem decidir o mérito | CIJ (art. 41 do Estatuto), tribunais regionais | ordem da CIJ de 26/01/2024, África do Sul v. Israel |
| `decisao_merito` | tribunal decide se houve genocídio (ou responsabilidade por ele) | CIJ, TPI, TPII/TPIR/IRMCT, ECCC, tribunal nacional | Bósnia v. Sérvia (2007); Akayesu (TPIR, 1998); Krstić (TPII, 2004) |
| `encerrado` | o procedimento terminou sem decisão de mérito, ou o mérito foi negado | tribunal, procuradoria | arquivamento; absolvição |

Regras:

1. Cada status tem obrigatoriamente `por` (o órgão), `data`, `url` da fonte e
   `confianca`. Sem os quatro, o validador reprova.
2. **A tela mostra o status mais alto já alcançado, sempre com o órgão ao lado:**
   "medida provisória — CIJ, 26/01/2024", "alegação — Gâmbia, 11/11/2019". Nunca a
   palavra "genocídio" como rótulo solto de uma situação ou de um país.
3. `decisao_merito` exige `resultado` (`reconhecido`, `nao_reconhecido`, `parcial`) e o
   dispositivo da decisão. A CIJ pode reconhecer o genocídio e não a responsabilidade
   do Estado (Bósnia v. Sérvia): isso é `parcial` com nota.
4. Alegação de imprensa não vira registro de status: vira notícia (função 2) ligada à
   situação. Só alegação de Estado, organismo internacional ou organização com método
   público entra na taxonomia, e com `confianca` da fonte.
5. O robô só grava `alegacao` e `investigacao` quando a fonte é a própria autora do
   ato (a petição no site da CIJ, o comunicado da Procuradoria no site do TPI). Os
   demais status entram por pessoa, com a decisão lida.

## Entidade 1: país (`paises.json`)

Cada campo abaixo vem com a justificativa de existir. Campos que não respondem a uma
pergunta da pesquisa não entram; a lista cresce por decisão registrada.

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | alfa-3 | URL pública (`/paises/BRA`) e chave de todo cruzamento |
| `nome_pt`, `nome_en` | texto | exibição; o nome oficial longo fica em `nota` |
| `estatuto_onu` | `membro` / `observador` / `nao_membro` | separa os 193 dos 4 e deixa explícito o reconhecimento limitado |
| `membro_desde` | data ou `null` | contexto temporal das obrigações |
| `codigo_penal` | bloco | **a pergunta central da função 1**: há um código penal vigente, de quando, onde se lê o texto oficial. `existe` (`sim` / `nao` / `desconhecido`; `nao` cobre países de *common law* sem código, com `nota`), `titulo`, `ano_promulgacao`, `consolidado_em`, `url_oficial`, `url_alternativa` (LII, tradução), `lingua`, proveniência |
| `genocidio_interno` | bloco | se o país pode julgar genocídio pelo direito próprio: `status` (`tipificado` / `parcial` / `nao` / `desconhecido`), `dispositivo`, `diploma`, `ano`, `definicao_segue_convencao` (`sim` / `mais_ampla` / `mais_estreita` / `desconhecido`), proveniência. `parcial` cobre tipificação por remissão genérica ao direito internacional |
| `convencao_1948` | bloco | obrigação de prevenir e punir: `assinatura`, `vinculacao` (data), `tipo` (`ratificacao` / `adesao` / `sucessao`), `reservas` (`sim` / `nao`), `reservas_nota` (p. ex. ao art. IX, que afasta a jurisdição da CIJ), proveniência |
| `estatuto_roma` | bloco | jurisdição do TPI: `assinatura`, `vinculacao`, `retirada` (data ou `null`), proveniência |
| `pena_maxima` | bloco | escala punitiva: `tipo` (`anos` / `perpetua` / `morte` / `desconhecido`), `anos` (inteiro, se `anos`), `aplicavel_ao_genocidio` (`sim` / `nao` / `desconhecido`), proveniência |
| `pena_de_morte` | bloco | `status` segundo a classificação da Anistia (`abolicionista`, `abolicionista_crimes_comuns`, `abolicionista_na_pratica`, `retencionista`), `nota` para a hipótese condicional (guerra), proveniência |
| `situacoes` | lista de ids | liga o país às situações em que é parte, território ou foro |
| `promocao` | bloco | `nivel` (`superficial` / `em_investigacao` / `detalhado`), `gatilho`, `desde`, `onde` (URL do repositório-filho ou pasta) |
| `vigencia_ate`, `vigencia_nota` | data, texto | país que deixou de existir não sai: ganha data e nota, como o acervo do AtlasPen |
| `atualizado_em` | data | o `max` de todos os `lido_em` do registro, derivado |

Exemplo preenchido (Brasil). Os valores de ratificação são os que constam da UN
Treaty Collection e do Decreto 30.822/1952; a primeira sessão de carga **reconfere**
cada um antes de carimbar `conferido_por`.

```json
{
  "id": "BRA",
  "nome_pt": "Brasil",
  "nome_en": "Brazil",
  "estatuto_onu": "membro",
  "membro_desde": "1945-10-24",
  "codigo_penal": {
    "existe": "sim",
    "titulo": "Código Penal (Decreto-Lei 2.848, de 7 de dezembro de 1940)",
    "ano_promulgacao": 1940,
    "consolidado_em": "2026-10-26",
    "url_oficial": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
    "url_alternativa": "https://atlaspen.com.br/data/crimes.json",
    "lingua": "pt",
    "fonte": "planalto",
    "lido_em": "2026-10-26",
    "confianca": "A",
    "conferido_por": "robo"
  },
  "genocidio_interno": {
    "status": "tipificado",
    "diploma": "Lei 2.889, de 1º de outubro de 1956",
    "dispositivo": "art. 1º",
    "ano": 1956,
    "definicao_segue_convencao": "sim",
    "nota": "Pena por remissão aos tipos do Código Penal (art. 1º, a–e); hediondo por força do art. 1º, parágrafo único, da Lei 8.072/1990. Registro detalhado no AtlasPen.",
    "url": "https://www.planalto.gov.br/ccivil_03/leis/l2889.htm",
    "fonte": "planalto",
    "lido_em": null,
    "confianca": "A",
    "conferido_por": null
  },
  "convencao_1948": {
    "assinatura": "1948-12-11",
    "vinculacao": "1952-04-15",
    "tipo": "ratificacao",
    "reservas": "nao",
    "reservas_nota": null,
    "url": "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=IV-1&chapter=4",
    "fonte": "untc",
    "lido_em": null,
    "confianca": "A",
    "conferido_por": null
  },
  "estatuto_roma": {
    "assinatura": "2000-02-07",
    "vinculacao": "2002-06-20",
    "retirada": null,
    "url": "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XVIII-10&chapter=18",
    "fonte": "untc",
    "lido_em": null,
    "confianca": "A",
    "conferido_por": null
  },
  "pena_maxima": {
    "tipo": "anos",
    "anos": 40,
    "aplicavel_ao_genocidio": "sim",
    "nota": "Art. 75 do Código Penal, com a redação da Lei 13.964/2019.",
    "url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
    "fonte": "planalto",
    "lido_em": null,
    "confianca": "A",
    "conferido_por": null
  },
  "pena_de_morte": {
    "status": "abolicionista_crimes_comuns",
    "nota": "Admitida só em caso de guerra declarada (CF, art. 5º, XLVII, a; CPM).",
    "url": "https://www.amnesty.org/en/what-we-do/death-penalty/",
    "fonte": "amnesty",
    "lido_em": null,
    "confianca": "B",
    "conferido_por": null
  },
  "situacoes": [],
  "promocao": { "nivel": "superficial", "gatilho": null, "desde": null, "onde": null },
  "vigencia_ate": null,
  "vigencia_nota": null
}
```

Os `lido_em: null` com `conferido_por: null` são deliberados: o exemplo diz o que se
espera encontrar, e o carimbo só vem quando o robô ou a pessoa leu a fonte. Um
registro assim **não passa** no validador estrito; passa no modo `--rascunho`, que é o
da carga inicial.

## Entidade 2: situação (`situacoes.json`)

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | *slug* | `rohingya-mianmar`, `gaza-2023`, `darfur`, `srebrenica-1995` |
| `nome_pt`, `nome_en` | texto | exibição |
| `paises` | lista de alfa-3 com papel (`territorio`, `parte`, `foro`, `requerente`, `requerido`) | liga à função 1 |
| `periodo` | `{inicio, fim}` | datas aproximadas aceitas, com `aproximado: true` |
| `status` | lista de objetos da taxonomia, cada um com `por`, `data`, `url`, `confianca`, `conferido_por` | **a resposta à questão transversal 2**; a tela mostra o mais alto |
| `descricao` | texto próprio, até 600 caracteres, `autor` | contexto sem copiar terceiros |
| `termos` | lista de `{lingua, formas[], exclusoes[]}` | gera o léxico; é o que o robô procura |
| `promocao` | igual ao de país | onde vive o detalhamento |
| `atualizado_em` | derivado | |

Exemplo (abreviado):

```json
{
  "id": "rohingya-mianmar",
  "nome_pt": "Rohingya (Mianmar)",
  "nome_en": "Rohingya (Myanmar)",
  "paises": [
    { "id": "MMR", "papel": "territorio" },
    { "id": "GMB", "papel": "requerente" },
    { "id": "MMR", "papel": "requerido" }
  ],
  "periodo": { "inicio": "2016-10-01", "fim": null, "aproximado": true },
  "status": [
    { "codigo": "investigacao", "por": "Missão Internacional Independente de Apuração dos Fatos sobre Mianmar (ONU)", "data": "2018-09-12", "url": "https://www.ohchr.org/en/hr-bodies/hrc/myanmar-ffm/index", "confianca": "A", "conferido_por": "humano" },
    { "codigo": "acusacao", "por": "Gâmbia, petição inicial à CIJ", "data": "2019-11-11", "url": "https://www.icj-cij.org/case/178", "confianca": "A", "conferido_por": "humano" },
    { "codigo": "medida_provisoria", "por": "Corte Internacional de Justiça", "data": "2020-01-23", "url": "https://www.icj-cij.org/case/178", "confianca": "A", "conferido_por": "humano" },
    { "codigo": "reconhecimento_politico", "por": "Secretário de Estado dos Estados Unidos", "data": "2022-03-21", "url": null, "confianca": "B", "conferido_por": null }
  ],
  "descricao": { "texto": "Operações das forças armadas de Mianmar contra a população rohingya no estado de Rakhine a partir de 2016–2017, com deslocamento em massa para Bangladesh. A Gâmbia acionou a CIJ em 2019 com base na Convenção de 1948; a Corte ordenou medidas provisórias em 2020 e o mérito está pendente.", "autor": "humano" },
  "termos": [
    { "lingua": "en", "formas": ["Rohingya", "Rakhine State"], "exclusoes": [] },
    { "lingua": "pt", "formas": ["rohingya", "roingá"], "exclusoes": [] },
    { "lingua": "fr", "formas": ["Rohingya", "Rohingyas"], "exclusoes": [] }
  ],
  "promocao": { "nivel": "superficial", "gatilho": null, "desde": null, "onde": null }
}
```

O status `reconhecimento_politico` do exemplo está com `url: null` e sem carimbo de
propósito: é como um dado entra em rascunho e como o validador o acusa.

## Entidade 3: notícia (`noticias/AAAA/MM.jsonl`)

Uma linha por documento, no formato que o Alétheia já grava, com quatro campos a
mais (língua, situações, veículo, resumo).

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | `hash` da URL normalizada | identidade; dois endereços com o mesmo `hash_texto` são um documento |
| `url` | texto | o *link*, que é o que se publica |
| `dominio`, `veiculo`, `pais_veiculo` | texto, texto, alfa-2 | quem publicou e de onde; `pais_veiculo` vem do GDELT quando houver |
| `titulo_original`, `lingua` | texto, ISO 639-1 | o título como a fonte deu, na língua em que deu |
| `titulo_pt` | `{texto, autor}` ou `null` | tradução nossa, marcada; nunca substitui o original |
| `publicado_em`, `capturado_em` | data, data-hora | |
| `canal`, `fonte` | `gdelt` / `rss` / `lista`; id da fonte | proveniência do achado |
| `situacoes` | lista de ids | o elo com a taxonomia; vazio quando o léxico casou só termos gerais |
| `chaves`, `categorias`, `nivel`, `lexico_versao` | como no Alétheia | auditoria da triagem |
| `resumo` | `{texto, autor}` ou `null` | o resumo próprio, só para itens promovidos ou de nível 3 revisados |
| `snapshot`, `hash_texto` | URL do Wayback, sha256 | cópia de referência e prova do que foi lido |
| `conferido_por` | `robo` / `humano` / `amostra` | |

Exemplo (ilustrativo: a URL é fictícia e marcada como tal; o formato é o real):

```json
{"id": "9c1e4b7a2d03f6e8", "url": "https://exemplo.org/2026/11/cij-ordem-medidas", "dominio": "exemplo.org", "veiculo": "Exemplo Notícias", "pais_veiculo": "BR", "titulo_original": "CIJ ordena novas medidas provisórias em caso de genocídio", "lingua": "pt", "titulo_pt": null, "publicado_em": "2026-11-03", "capturado_em": "2026-11-04T09:21:07+00:00", "canal": "gdelt", "fonte": "gdelt:genocidio-pt", "situacoes": ["gaza-2023"], "chaves": ["genocidio", "cij", "medida-provisoria"], "categorias": ["tribunal", "qualificacao"], "nivel": 3, "lexico_versao": "pt-2026-11-01", "resumo": null, "snapshot": null, "hash_texto": "sha256:…", "conferido_por": "robo"}
```

## Entidade 4: decisão (`decisoes.json`)

| Campo | Tipo | Por que existe |
|---|---|---|
| `id` | `hash` da URL oficial | identidade |
| `tribunal` | vocabulário fechado: `cij`, `tpi`, `irmct`, `tpii`, `tpir`, `eccc`, `rscsl`, `ksc`, `corte_idh`, `cedh`, `corte_africana`, `nacional` | |
| `caso` | `{id_no_tribunal, numero, nome, partes[]}` | a CIJ numera casos (178, 192); o TPI usa `ICC-02/05-01/09` |
| `tipo_ato` | `peticao`, `ordem_medidas_provisorias`, `decisao_incidental`, `sentenca_merito`, `parecer_consultivo`, `mandado_de_prisao`, `confirmacao_de_acusacoes`, `sentenca_condenatoria`, `sentenca_absolutoria`, `recurso`, `andamento`, `comunicado` | a granularidade mínima: o ato, não o caso |
| `data` | data | do ato, não da captura |
| `url_oficial` | texto | sempre o site do tribunal; `url_alternativa` para o PDF |
| `linguas` | lista ISO 639-1 | a CIJ publica em inglês e francês; o TPI, em inglês e francês; a Corte IDH, em espanhol |
| `situacoes` | lista de ids | |
| `status_taxonomia` | código da taxonomia que este ato produz, ou `null` (andamento sem efeito de status) | é daqui que `situacoes.status` é derivado |
| `resultado` | só em `sentenca_*`: `reconhecido` / `nao_reconhecido` / `parcial` | |
| `resumo` | `{texto, autor}` | resumo próprio, obrigatório para `sentenca_merito` e `ordem_medidas_provisorias` |
| `canal`, `fonte`, `capturado_em`, `snapshot`, `hash_texto`, `nivel`, `lexico_versao` | como em notícia | |
| `conferido_por`, `conferido_em` | | ato que muda status exige `humano` |

Exemplo preenchido (ato real; a URL do caso é a página oficial, verificada em
06/11/2026; o PDF específico da ordem deve ser conferido na carga):

```json
{
  "id": "4f2a9e01c7b35d16",
  "tribunal": "cij",
  "caso": {
    "id_no_tribunal": "192",
    "numero": "General List No. 192",
    "nome": "Application of the Convention on the Prevention and Punishment of the Crime of Genocide in the Gaza Strip (South Africa v. Israel)",
    "partes": [ { "pais": "ZAF", "papel": "requerente" }, { "pais": "ISR", "papel": "requerido" } ]
  },
  "tipo_ato": "ordem_medidas_provisorias",
  "data": "2024-01-26",
  "url_oficial": "https://www.icj-cij.org/case/192",
  "url_alternativa": null,
  "linguas": ["en", "fr"],
  "situacoes": ["gaza-2023"],
  "status_taxonomia": "medida_provisoria",
  "resultado": null,
  "resumo": {
    "texto": "A Corte, por maioria, indicou medidas provisórias a Israel com base na plausibilidade dos direitos invocados pela África do Sul sob a Convenção de 1948, sem decidir se houve genocídio. Ordens posteriores (março e maio de 2024) ampliaram as medidas.",
    "autor": "humano"
  },
  "canal": "lista",
  "fonte": "cij:casos",
  "capturado_em": "2026-11-06T13:00:00+00:00",
  "snapshot": null,
  "hash_texto": null,
  "nivel": 3,
  "lexico_versao": "en-2026-11-01",
  "conferido_por": "humano",
  "conferido_em": "2026-11-06"
}
```

## Fontes (`fontes.json`)

Uma entrada por fonte, com o que o `02-fontes.md` apurou, em dado: `id`, `nome`,
`url`, `funcao` (1, 2 ou 3), `confianca` (A/B/C), `licenca`, `termos_url`,
`robots_verificado_em`, `api` (`sim`/`nao`), `limite_por_minuto`, `linguas`,
`sentinela` (string que prova integridade da resposta), `estado` (`ativa`,
`suspensa`, `descartada`, com motivo). O robô recusa fonte sem `robots_verificado_em`
nos últimos 180 dias: é o Arquivista do AtlasPen aplicado às fontes.

## Léxico (`lexico/<lingua>.json`)

Formato do `lexico.schema.json` do Argos, sem alteração. Um arquivo por língua.
Gerado por *script* a partir de duas listas:

- **termos fixos** por língua, mantidos à mão: "genocídio", "Convenção de 1948",
  "Corte Internacional de Justiça", "medidas provisórias", "intenção de destruir"… com
  exclusões ("genocídio cultural" sem contexto jurídico; títulos de obras);
- **termos de situação**, lidos de `situacoes.termos` para a língua.

O `contexto.exige_qualquer` por língua traz os marcadores jurídicos ("tribunal",
"corte", "ordem", "denúncia", "procurador", "convenção") que separam a notícia
relevante do uso retórico da palavra. É a diferença entre nível 1 e nível 2.

## Derivados (`static/data/`)

Gerados por `scripts/transformar.py --estrito`, nunca editados: `paises.json` com
`atualizado_em` e `completude` por campo; `situacoes.json` com `status_maximo`
calculado e o rótulo de exibição montado ("medida provisória — CIJ, 26/01/2024");
`noticias-recentes.json` (últimos 90 dias, para a tela) e `noticias-indice.json`
(contagens por mês, situação e língua, para o gráfico); `decisoes.json` ordenado;
`qualidade.json` com o relatório de cada geração (campos vazios por motivo, fontes
vencidas, itens sem carimbo).

## O que o validador reprova (`--estrito`)

1. `id` fora do padrão, repetido ou reaproveitado (confere `ids-aposentados.json`).
2. Valor fora do vocabulário fechado em qualquer enumeração.
3. Campo afirmado (`valor` não nulo) sem `url`, `fonte`, `lido_em` ou `confianca`.
4. `fonte` que não existe em `fontes.json`, ou com `estado` ≠ `ativa`.
5. Status da taxonomia sem `por`, `data` ou `url`; `decisao_merito` sem `resultado`.
6. Status `medida_provisoria` ou `decisao_merito` com `conferido_por` ≠ `humano`.
7. `situacoes` referenciando id inexistente; país em situação sem `papel`.
8. Qualquer campo de texto com mais de 600 caracteres em `descricao` ou `resumo`
   (resumo é resumo, não cópia).
9. Texto nosso sem `autor`.
10. `pena_maxima.tipo = anos` sem `anos`; `pena_de_morte.status = retencionista` com
    `pena_maxima.tipo ≠ morte` sem `nota`.

O modo `--rascunho` relaxa só 3 e 6, para a carga inicial, e o relatório de qualidade
conta quantos registros ainda estão em rascunho.
