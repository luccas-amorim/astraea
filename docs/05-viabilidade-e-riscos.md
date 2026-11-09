# 05 — Viabilidade e riscos

## Viabilidade por função

Legenda: **automatiza** (robô faz e carimba), **propõe** (robô faz, pessoa confirma),
**humano** (só pessoa), **inviável** (não se faz, com o motivo).

### Função 1: leis penais do mundo

| Campo | Modo | Fonte | Volume | Esforço inicial | Esforço recorrente |
|---|---|---|---|---|---|
| `genocide_convention`, `rome_statute` (datas, tipo, reservas, retiradas) | **automatiza** | XML da UN Treaty Collection | 197 registros; 154 + 125 partes | 1 sessão para o adaptador `listing` sobre o XML (limpar `<superscript>`, mapear nome → ISO, 20–30 nomes irregulares à mão) | 0: rodada mensal; PR só quando algo muda (poucas vezes por ano) |
| `death_penalty.status` | **propõe** | espelho do Cornell (4 categorias) + anexo anual da Anistia | 197 | 1 sessão para o adaptador `listing` + 1 sessão para a carga do anexo | 1 h/trimestre |
| `penal_code` (existe, título, ano, `official_url`) | **humano**, com índice de partida | N-Lex (44 países), sites oficiais, Wikidata (70 códigos) como *links* | 197 | **10 a 20 sessões** (10–20 países por sessão; *common law* sem código exige nota) | reconferência por amostra |
| `domestic_genocide` | **humano**, com índice de partida | seção "Municipal laws" da Wikipedia (semente C), texto oficial ou Legal Tools (consulta manual) para conferir | 197 | nas mesmas sessões; ~60 países têm dispositivo conhecido; os demais exigem leitura do código | reconferência por amostra |
| `max_penalty` | **humano** | o próprio código penal | 197 | nas mesmas sessões | — |
| cobertura total "193 + 4" | — | — | — | **realista em 6 a 12 meses** de sessões quinzenais; o MVP entrega os campos automatizados para todos e os humanos só para os países com situação monitorada (~25) | — |

**O que é inviável e por quê.** Mapear a legislação penal do mundo por *crawler* é
inviável em 06/11/2026: não existe base aberta e viva de códigos penais (Legislationline
em reconstrução, SHERLOC vazio para genocídio, Prevent Genocide morta, LIIs e Legal
Tools vetando robôs), e raspar 197 portais nacionais é o problema que o AtlasPen levou
um ano para resolver para **um** portal. O plano não propõe contorno: propõe carga
humana ordenada por prioridade, com uma fonte automatizada (tratados) que já responde
à metade das perguntas da pesquisa.

### Função 2: notícias

| Etapa | Modo | Volume estimado | Esforço |
|---|---|---|---|
| listar (GDELT por língua e por tema; RSS; ReliefWeb) | **automatiza** | 5 línguas × 7 dias × 4 fatias ≈ 140 consultas/semana ao GDELT; ~15 *feeds*; 1–3 chamadas ReliefWeb | adaptadores existem (GDELT, RSS); ReliefWeb é 1 sessão |
| ler o texto e triar (níveis 0–3) | **automatiza** | 300–1.500 itens/dia chegam ao nível 2; nível 3 (termo em manchete) talvez 50–300/dia | léxico por língua: 1 sessão por língua com falante |
| gravar nível ≥ 2 com metadados | **automatiza** | 75–380 MB/ano | 0 |
| ligar o item a uma situação | **automatiza** pelo léxico de situação; **propõe** quando casa só termo geral | — | — |
| resumo próprio, tradução de título | **humano** ou **modelo marcado** (D4) | só itens promovidos | ver custo abaixo |
| estimar cobertura (captura e recaptura) | **automatiza** | — | herdado do Alétheia; precisa de 2.º canal (Media Cloud) na fase 2 |
| revisão do nível 2 | **humano por amostra** (D10) | 20 itens/semana | 1 h/semana |

**Limite do método.** O léxico casa grafias; não entende. A notícia que fala de
"extermínio" sem a palavra "genocídio" fica no nível 1. Isso é aceito e medido (a
amostra trimestral inclui nível 1), não escondido.

### Função 3: tribunais

| Etapa | Modo | Volume | Esforço |
|---|---|---|---|
| TPI por RSS (registros e notícias) | **automatiza** | centenas de registros/semana, poucos sobre genocídio (só Darfur hoje) | adaptador `rss` + filtro por situação: 0,5 sessão |
| CIJ por `listing` (casos pendentes + *press releases*) | **automatiza** a listagem; **propõe** o ato | dezenas de atos/ano | adaptador `listing` com *parser* da página de caso: 1–2 sessões |
| IRMCT, RSCSL, KSC, Corte Africana, TRIAL por RSS | **automatiza** | baixo | 0,5 sessão |
| OHCHR (páginas de mandato), HUDOC (RSS) | **automatiza** a listagem | baixo | 1 sessão |
| Corte IDH, CIDH, TPII/TPIR/ECCC históricos | **humano** (`listing` curada) | carga única + poucos atos/ano | 2 sessões de carga |
| classificar `act_type` e `taxonomy_status` | **propõe** (pelo título) / **humano** (status) | dezenas/ano | 1 h/semana |
| resumo próprio de ordem e sentença | **humano** (ou rascunho de modelo, D4) | 20–60/ano | 30 min por ato |

**Inviável:** Corte IDH por robô (Cloudflare em tudo), UCR do IRMCT (login), Legal
Tools (robôs de IA vetados, API sem documentação), ODS e UN Digital Library
(`Disallow`), WorldCourts (termos), ORIL (pago).

## Custo

| Item | Custo | Observação |
|---|---|---|
| GitHub (repositório público, Pages, Actions) | **US$ 0** | Actions gratuito em repositório público; 6 h por *job*; Pages até 1 GB |
| GDELT, UN News, RSS, UNTC, Cornell, OHCHR | US$ 0 | citação obrigatória ao GDELT |
| ReliefWeb (`appname`), Media Cloud (chave) | US$ 0 | gesto humano único cada |
| Modelo de linguagem (opcional, D4): tradução de 300 títulos/dia com Claude Haiku 5.5 | **< US$ 1/mês** | US$ 0,10 por milhão de *tokens* de entrada e US$ 0,50 de saída (preços de 06/11/2026) |
| Idem com Claude Opus 5.5 | ~US$ 15/mês | US$ 4 e US$ 20 por milhão |
| Rascunho de resumo de 300 atos/ano com Opus 5.5 | < US$ 5/ano | 2.000 *tokens* de entrada e 200 de saída por ato |
| Zenodo (DOI trimestral) | US$ 0 | |
| Domínio próprio (opcional) | ~US$ 15/ano | o AtlasPen tem `atlaspen.com.br` |
| Event Registry (se um dia a cobertura do GDELT não bastar) | US$ 90/mês | único agregador comercial cujos termos permitem a tela; **fora do MVP** |
| **Tempo da pessoa** | **o custo real**: 2–4 h/semana em regime, 6–10 h/semana nos três primeiros meses | ver "Manutenção por uma pessoa" |

## Matriz de riscos

Probabilidade e impacto em três níveis (B/M/A). Ordenada por produto.

| # | Risco | Prob. | Impacto | Mitigação | Dono |
|---|---|---|---|---|---|
| R1 | **Abandono por falta de tempo** (os três projetos-irmãos são de uma pessoa; o Argos já parou) | A | A | o MVP é o menor Astraea útil; rodadas que falham sem perder estado; nenhuma promessa de leitura semanal de notícias (D10); o cron sobrevive enquanto o robô comita; o Arquivista avisa 3 falhas seguidas | pessoa |
| R2 | **Afirmar genocídio onde nenhum órgão afirmou** (erro de rótulo na tela, no resumo ou no commit) | M | A | taxonomia com órgão obrigatório; validador reprova status sem `por`; tela nunca mostra a palavra solta; `AGENTS.md` regra 1; amostra trimestral confere rótulos | pessoa + CI |
| R3 | **Dependência do GDELT** (um único índice; limitação a 1 req/5 s; blog anuncia conjuntos "temporários") | M | A | RSS como segundo canal desde o dia 1; ReliefWeb; `timelinevol` como censo; GKG de 15 min como plano B; Media Cloud na fase 2; o relatório diz quando o GDELT não respondeu | robô |
| R4 | **Direitos autorais e mineração de texto** (ler a página para triar é mineração; El País, EFE, Al Jazeera e Anistia fazem *opt-out* expresso; TASS proíbe base de dados) | M | A | só metadados gravados; `no_text_by_policy` para domínios com *opt-out*; TASS, Reuters, AP, AFP fora; política de `User-Agent` próprio sem se passar por navegador; `NOTICE` com as fontes | pessoa |
| R5 | **Dados pessoais** (vítimas, acusados, testemunhas em títulos e nomes de caso; LGPD e GDPR) | M | A | `docs/pessoas.md` do Alétheia; nome só em `decisions.json` como o tribunal escreve; sem coluna de pessoa; remoção em 7 dias; base legal art. 7º, IV, LGPD e art. 85 GDPR (pesquisa) | pessoa |
| R6 | **Campo de país errado publicado** (ratificação com data errada, "tipifica genocídio" quando não tipifica) | M | A | carimbo obrigatório; `--draft` visível no relatório de qualidade; amostra estratificada por fonte; "dizer o que não se sabe" | CI + amostra |
| R7 | **Fonte muda de forma ou some** (Legislationline já sumiu; EMM mudou de domínio; TPI bloqueia por UA; CIJ bloqueia PDF) | A | M | sentinela por fonte; ensaio de sexta; `robots_checked_on` com validade de 180 dias; `state: suspended` com data de reconferência; fixture e teste por adaptador | robô |
| R8 | **Falso negativo silencioso** (o que o léxico não casa, a língua sem léxico, o teto de 250 do GDELT) | A | M | Recenseador compara `timelinevol` com o gravado; relatório conta nível 0–1 por língua; a próxima língua é decidida pelo número; nível 1 entra na amostra | robô + pessoa |
| R9 | **Viés de cobertura** (imprensa ocidental em inglês domina; situações sem léxico na língua local somem) | A | M | contagem por língua e por `outlet_country` publicada na tela; léxicos em árabe na fase 1 e línguas das situações na fase 2; o Astraea mede e declara o viés em vez de fingir que não existe | pessoa |
| R10 | **Crescimento do repositório** (até 380 MB/ano de notícias) | M | M | só nível ≥ 2; JSONL por mês; site com 90 dias; gatilho objetivo de separação em `astraea-dados`; release trimestral no Zenodo | robô |
| R11 | **Cron desligado após 60 dias sem atividade** em repositório público | B | A | o commit do robô conta como atividade; Arquivista abre issue na 3.ª falha seguida; `workflow_dispatch` para religar | robô |
| R12 | **Bloqueio por `User-Agent` ou IP no *runner* do GitHub** (o TPI já bloqueia ferramentas; a Comissão Africana derrubou o banco por um *crawler*) | M | M | identificação clara com contato; `Crawl-delay` honrado; limite por fonte; `BlockedByRobots`/`BlockedByCountry` como política; pedido formal de acesso quando valer a pena (CIJ, OHCHR) | robô |
| R13 | **Mapa coroplético como ato político** (Kosovo, Taiwan, Palestina, Crimeia) | M | M | D13: mapa opcional; se houver, usa Natural Earth sem alterações e com nota de que fronteiras não são posição do projeto | pessoa |
| R14 | **Modelo de linguagem contamina o dado** (tradução errada de "massacre" como "genocídio"; resumo que afirma o que a decisão não afirma) | M | M | D4: só texto marcado com `author`, revisão humana antes de carimbo, nunca na triagem nem em campo de país; domínios `ai-train=no` excluídos | pessoa |
| R15 | **O motor próprio diverge do Alétheia e perde correções feitas lá** (D2: cópia, não dependência) | M | B | `sha` de origem no `NOTICE`; leitura do `git log` do Alétheia no começo de cada fase, com o que for portado registrado no `CHANGELOG.md`; testes e *fixtures* próprios | pessoa |
| R18 | **Tela em duas línguas desencontrada** (rótulo em `pt-BR` dizendo outra coisa que o `en`; texto nosso só numa língua; rótulo de status que, traduzido, soa como afirmação de genocídio) | M | M | trava 11 (nenhum valor sem rótulo nos *locales* ativos); rótulo de status revisado nas duas línguas contra a regra 1 do `AGENTS.md`; texto sem versão no *locale* aparece marcado com a língua; `quality.json` conta as lacunas | pessoa + CI |
| R16 | **Pedido de remoção ou contestação pública** (um Estado ou pessoa contesta um status) | B | M | o registro só cita atos oficiais com URL; resposta padrão: "o Astraea registra que o órgão X disse Y em Z"; processo em `docs/pessoas.md` | pessoa |
| R17 | **A sondagem foi feita de rede corporativa** e alguns bloqueios podem ser dela, não da fonte | A | B | repetir Library of Congress, WorldLII, Cornell, Minority Rights e EMM da sua máquina e do *runner* na primeira sessão | pessoa |

## Riscos jurídicos e éticos em prosa

**Direitos autorais.** O Astraea guarda e publica título, URL, data, veículo e língua:
fatos, não obra. Os resumos são próprios. Dois cuidados que o plano assume: (1) **ler**
o texto para triar é mineração de texto, e onde a fonte faz *opt-out* expresso (os
avisos de El País e EFE citam o art. 67.3 do RDL 24/2021, que é a transposição
espanhola da diretiva europeia), o robô não lê; (2) títulos são por vezes protegidos
como obra mínima em algumas jurisdições; publicar título + *link* é o uso que o
próprio RSS pressupõe, e é o que BBC (§15) e JusticeInfo autorizam expressamente.
Fontes cujos termos proíbem base de dados (TASS) ficam fora mesmo que o *feed* exista.

**Dados pessoais.** Genocídio tem vítimas com nome, acusados com nome e testemunhas.
O Astraea descreve documentos e atos, não pessoas: sem coluna de nome fora do nome
oficial do caso; sem cruzamento para montar perfil; sem texto. A base legal é a
pesquisa (LGPD art. 7º, IV, e art. 4º, II, b; GDPR art. 85 e art. 89 para fontes
europeias). O risco residual, uma pessoa nomeada num título de notícia que o Astraea
exibe, é tratado por remoção a pedido, com registro público da decisão.

**O rótulo.** O risco ético central é o projeto parecer um tribunal. A resposta está
no esquema (status com órgão), na tela (rótulo sempre com o órgão) e na linguagem de
tudo o que o projeto publica, inclusive commits e issues. A regra vale para o
contrário também: o Astraea não "desqualifica" uma alegação; registra que é alegação
e de quem.

**Neutralidade de fontes.** Xinhua, Anadolu e TASS são agências estatais com linha
editorial sobre situações específicas (Xinjiang, curdos, Ucrânia). TASS está fora
por termos; as outras entram marcadas como `state_media` em `sources.json`, e a tela mostra
a marca. Excluí-las seria escolher um viés; incluí-las sem marca seria esconder outro.

**Manutenção por uma pessoa.** O risco R1 é o que decide o desenho: tudo o que exige
leitura humana semanal foi reduzido ao nível 2 de tribunais (dezenas de itens) e a
uma amostra de notícias; o resto é trimestral ou sob demanda. O plano aceita que o
Astraea rode meses sem ninguém olhar e continue correto no que publica, porque o que
ele publica sem gente é só o que o robô leu e carimbou.
