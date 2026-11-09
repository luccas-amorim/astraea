# 07 — Decisões pendentes

Perguntas que só o dono do projeto responde. Para cada uma: a leitura que recomendo,
o grau de confiança (**A** alta, **M** média, **B** baixa), o fundamento e o melhor
argumento contrário. O plano foi escrito **assumindo a leitura recomendada**; onde a
resposta for outra, o documento afetado está indicado.

## D1. Universo de países: 197, com Kosovo como `XKX`

**Recomendo:** 193 membros + Palestina e Santa Sé (`observador`) + Kosovo e Taiwan
(`nao_membro`), total 197; outras entidades só como `situacao`. **Confiança: A.**

**Fundamento.** Palestina e Santa Sé são partes na Convenção de 1948 e a Palestina no
Estatuto de Roma; a situação de Gaza é a de maior volume na função 2 e 3. Kosovo e
Taiwan têm ordenamento penal próprio e aparecem em alegações. `XKX` é o código
reservado que o Banco Mundial e a Comissão Europeia usam; `TWN` é ISO. Afeta
`01-visao-e-escopo.md` e `03-modelo-de-dados.md`.

**Contra.** Incluir entidades de reconhecimento limitado é, em si, uma tomada de
posição que um projeto acadêmico sobre genocídio pode preferir evitar; a alternativa
é 195 (membros + observadores) e Kosovo/Taiwan só como `situacao`. O custo é perder
o registro de lei penal deles.

## D2. Onde vive o motor: dependência do Alétheia agora, `argos-core` depois

**Recomendo:** opção A do `04-arquitetura.md` no MVP (`pip install` do Alétheia por
`sha`), extração de `argos-core` quando o adaptador `lista` com *parser* por página
estiver provado em dois tribunais. **Confiança: M.**

**Fundamento.** Zero cópia, correção compartilhada, e o Alétheia já é a versão mais
completa do motor. A extração antes de haver um terceiro consumidor real seria
refatorar por antecipação.

**Contra.** O pacote se chama `aletheia`, o README fala de Carandiru, e mudar o
contrato para servir ao Astraea (p. ex. `Documento.linguas`) obriga a mexer no
repositório do outro projeto a cada passo. Quem prefere independência total escolhe
a opção C (vendorizar) e aceita três cópias.

## D3. Repositório único ou código separado de dados

**Recomendo:** único no MVP, com gatilho objetivo de separação (árvore acima de
500 MB ou mais de um commit de robô por dia) e com a regra de que robôs só comitam
em `data/`, `estado/` e `saidas/`. **Confiança: M.**

**Fundamento.** É a sua ideia, e ela se sustenta por 1 a 2 anos pelas contas do
`04-arquitetura.md`; o AtlasPen e o Alétheia já operam assim. Separar antes de ter
dado é criar um segundo repositório vazio.

**Contra.** Os commits semanais do robô poluem o histórico do código desde o
primeiro dia, e migrar depois exige reescrever caminhos, *workflows* e o site. Quem
já sabe que vai separar prefere nascer separado (`astraea` + `astraea-dados`).

## D4. Modelo de linguagem: só para texto marcado, nunca para triagem

**Recomendo:** permitir modelo de linguagem para **(a)** tradução de título para
português e **(b)** rascunho de resumo próprio de atos de tribunal, sempre com
`autor: "modelo:<id>"`, revisão humana obrigatória antes de `conferido_por: humano`,
e nunca na triagem nem no preenchimento de campo de país. **Confiança: M.**

**Fundamento.** A política do Argos ("nenhum modelo na triagem; um nível opt-in,
marcado") é a certa para auditabilidade. Tradução de título e rascunho de resumo são
tarefas em que o erro é visível e barato de corrigir. Custo estimado para 300 títulos
por dia, 40 *tokens* cada, com Claude Haiku 5.5 (US$ 0,10 por milhão de *tokens* de
entrada, US$ 0,50 de saída, preços de 06/11/2026): abaixo de **US$ 1 por mês**; com
Claude Opus 5.5 (US$ 4 e US$ 20 por milhão): cerca de **US$ 15 por mês**. Resumos de
atos (300 por ano, 2.000 *tokens* de entrada e 200 de saída cada, com Opus 5.5):
abaixo de **US$ 5 por ano**. O custo não é o obstáculo; a política é.

**Contra.** Um projeto cujo valor é "nada entra sem conferência" perde parte da
credibilidade se qualquer texto publicado foi gerado por modelo, mesmo marcado; e a
tradução automática de títulos sobre genocídio erra justamente nos termos que
importam (o que é "massacre", "limpeza", "genocídio" em cada língua). A alternativa é
publicar só o título original e resumos escritos à mão, aceitando que a tela de
notícias seja menos legível para quem não lê a língua.

## D5. Línguas da fase 1

**Recomendo:** inglês, francês, espanhol, português e árabe. **Confiança: M.**

**Fundamento.** Inglês e francês são as línguas da CIJ e do TPI; espanhol, da Corte
IDH e de boa parte da imprensa latino-americana; português, do público; árabe, da
situação de maior volume. As demais entram pela busca em inglês do GDELT e ficam no
nível 1 até ganharem léxico, e o relatório diz qual língua pede o próximo léxico.

**Contra.** Birmanês, tigrínia, amárico, uigur, ucraniano e russo são as línguas das
situações centrais, e deixá-las para depois enviesa o observatório para o que a
imprensa ocidental cobre. O custo de cada léxico é de algumas horas com um falante;
sem falante, é risco de erro silencioso.

## D6. Situações iniciais

**Recomendo:** dez situações na carga inicial: Rohingya/Mianmar, Gaza (2023–),
Ucrânia (2022–, com a ação Ucrânia v. Rússia na CIJ), Darfur, Tigré/Etiópia,
Xinjiang/uigures, Iazidis/Sinjar (Daesh), Ruanda 1994, Srebrenica/Bósnia, Camboja
(ECCC). **Confiança: M.**

**Fundamento.** Cobrem os três tribunais principais, os três status mais altos da
taxonomia, línguas distintas e casos encerrados (para testar `decisao_merito`) e em
curso (para testar medida provisória e promoção).

**Contra.** Dez é pouco para um observatório "do mundo" e muito para uma pessoa
conferir no primeiro trimestre; a lista omite Sudão 2023–, Armênia/Nagorno-Karabakh,
RD Congo, Guatemala (sentença nacional de 2013) e Namíbia/herero (histórico). A
alternativa é começar com as cinco que têm ato de tribunal internacional e deixar o
resto para o gatilho de promoção.

## D7. Licença dos dados: CC BY 4.0

**Recomendo:** Apache-2.0 para código e CC BY 4.0 para dados, resumos e
documentação, com `NOTICE` listando o que é de terceiro (GDELT pede citação; a UN
Treaty Collection tem termos da ONU). **Confiança: A.**

**Fundamento.** É o que o AtlasPen e o Alétheia usam; a atribuição é o que um projeto
acadêmico precisa para ser citado.

**Contra.** CC0 (domínio público) facilita o reúso por Wikidata e por bases que não
aceitam atribuição em cadeia; metadados de documentos de terceiros talvez nem sejam
protegíveis, e a CC BY sobre eles pode ser pretensão vazia. Quem quer máxima
reutilização escolhe CC0 para `data/` e CC BY só para os textos.

## D8. Chaves dos dados em português

**Recomendo:** chaves em português (`pena_de_morte`, `convencao_1948`), como no
AtlasPen, com dicionário bilíngue em `docs/dados-abertos.md`. **Confiança: B.**

**Fundamento.** Coerência com os três projetos-irmãos e com o público primário; o
dicionário resolve o reúso.

**Contra.** O Astraea é o único dos quatro cujo público natural é internacional;
chaves em inglês (`death_penalty`, `genocide_convention`) tornariam o JSON legível
para quem o encontrar sem passar pelo site. É a decisão mais barata de tomar agora e
a mais cara de mudar depois (quebra todo consumidor).

## D9. Pessoas nomeadas

**Recomendo:** adotar o `docs/pessoas.md` do Alétheia tal como está, com uma regra a
mais: nome de pessoa só aparece em `decisoes.json` e como o **tribunal** o escreve
(nome do caso, mandado); nunca em `paises.json`, `situacoes.json` nem em resumo de
notícia. Remoção a pedido em 7 dias; base legal LGPD e, para fontes europeias, GDPR
art. 85 (pesquisa e liberdade de expressão). **Confiança: A.**

**Contra.** Uma situação de genocídio sem o nome do acusado principal (Al Bashir,
Karadžić) é menos útil à pesquisa; e o nome já é público em todo lugar. A alternativa
é um campo `acusados` em situação, alimentado só de fontes de confiança A.

## D10. Nível 2 ("pede juízo") de notícias: ler ou não ler

**Recomendo:** não assumir leitura semanal do nível 2 de notícias. O nível 2 é
gravado, contado e amostrado na auditoria trimestral; só o nível 3 vai para a tela.
Para decisões, o nível 2 **é** lido toda semana, porque o volume é pequeno e é dele
que saem os status. **Confiança: M.**

**Fundamento.** Centenas de itens de nível 2 por semana é mais do que uma pessoa lê;
prometer leitura e não cumprir é o que mata projetos de uma pessoa.

**Contra.** O nível 2 é onde estão os falsos negativos do léxico (a notícia que fala
de "extermínio" e não de "genocídio"); não lê-lo é aceitar que o léxico nunca melhora
pelo que ele não casou. A alternativa é ler uma amostra fixa (20 por semana) com
esse fim explícito.

## D11. Retroativo: desde quando

**Recomendo:** decisões desde 01/01/2019 (abrange Gâmbia v. Mianmar, Gaza, Ucrânia e
as últimas sentenças do IRMCT); notícias desde a primeira rodada (o GDELT só volta 90
dias); países sem retroativo (o status de tratado já é histórico). Casos anteriores a
2019 entram como `decisao_merito` histórica, à mão, só para as situações iniciais.
**Confiança: M.**

**Contra.** Para a pesquisa, o valor está no histórico completo (Akayesu, Krstić,
Bósnia v. Sérvia), e a cobertura a partir de 2019 parece arbitrária. A alternativa é
um dossiê-filho "jurisprudência histórica" carregado à mão, fora do ritmo do robô.

## D12. Frequência: semanal

**Recomendo:** semanal para notícias e tribunais, mensal para países, diária só
durante a calibração do léxico (primeiras 4 semanas). **Confiança: M.**

**Contra.** Uma ordem de medidas provisórias da CIJ vira notícia no mesmo dia, e uma
semana de atraso pode parecer desleixo num observatório. A alternativa é diária para
tribunais (volume pequeno, custo baixo) e semanal para notícias.

## D13. Mapa na tela de países

**Recomendo:** sim, coroplético em SVG gerado no *build* a partir de um mapa-múndi
em domínio público (Natural Earth), sem biblioteca, com os quatro estados do
`genocidio_interno` como cor. **Confiança: M.**

**Contra.** Mapa de genocídio tipificado é mapa político: fronteiras de Kosovo,
Taiwan, Saara Ocidental, Crimeia e Palestina viram decisão cartográfica, com
reclamação garantida. A tabela com filtros entrega a mesma informação sem a
disputa.

## D14. Autoria e citação

**Recomendo:** `CITATION.cff` com autoria pessoal (Luccas de Amorim) na fase 1, como
no Alétheia, e coletivo ("Equipe Astraea") se e quando houver colaboração acadêmica
formal, como no AtlasPen. **Confiança: M.**

**Contra.** Nascer coletivo evita trocar a citação depois, e o AtlasPen já passou
por isso. Mas uma "equipe" de uma pessoa é citação enganosa.

## D15. Nomes dos robôs

**Recomendo:** manter a tradição dos nomes em português por função (Tabelião,
Cartógrafo, Vigia, Escrivão, Recenseador, Arquivista, Auditor); o robô da pena de
morte está como "Sentenciador" no `04-arquitetura.md`, nome provisório a trocar antes
de qualquer página pública. **Confiança: B.** Decisão barata; registro aqui só para
não a esquecer.

## D16. Google e agregadores comerciais

**Recomendo:** manter a política do Alétheia: fora, por `robots.txt` e por ausência
de API; APIs comerciais de notícias (NewsAPI, Event Registry) também fora, pela
cláusula que proíbe publicar os dados. **Confiança: A.**

**Contra.** Nenhum argumento de método; só de cobertura. O GDELT já cobre o que
esses agregadores cobrem, com licença aberta.

## D17. Dossiês-filhos: modelo e nome

**Recomendo:** `astraea-<situacao>` para dossiê de situação (modelo Alétheia) e
registro no AtlasPen (ou projeto equivalente do país) para detalhamento de lei;
`promocao.onde` guarda a URL. **Confiança: M.**

**Contra.** Multiplicar repositórios multiplica manutenção; a alternativa é uma pasta
`dossies/<situacao>/` dentro do Astraea até o segundo dossiê existir.
