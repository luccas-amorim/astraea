# 01 — Visão e escopo

## O nome

Astreia (*Astraea*), a deusa da justiça que foi a última imortal a abandonar a Terra
ao fim da Idade do Ferro e que, segundo o mito, voltará. O Astraea não julga: observa
de longe, de cima, o que o mundo diz e decide sobre o crime que a Convenção de 1948
chamou pelo nome. O `MITO.md`, como nos projetos-irmãos, conta o mito por
inteiro (escrito em 09/11/2026, na fase 1).

## Objetivo

Manter, com robôs e revisão humana por amostragem, três camadas de observação sobre
o crime de genocídio e sobre a lei penal do mundo:

1. **Leis penais do mundo** — por país, o que existe: há código penal, de quando, onde
   está o texto oficial; o genocídio é crime interno e em que dispositivo; a Convenção
   de 1948 e o Estatuto de Roma foram ratificados, com que reservas; qual a pena máxima
   e se há pena de morte. Pouca profundidade, cobertura total.
2. **Notícias sobre genocídios** — o que o noticiário mundial publica sobre genocídios
   e alegações de genocídio, em dezenas de línguas, com metadados e resumo próprio,
   nunca o texto de terceiros.
3. **Decisões de tribunais internacionais** — ordens, decisões, pareceres e andamentos
   da CIJ, do TPI, do IRMCT, das câmaras extraordinárias e dos tribunais regionais de
   direitos humanos em que o genocídio é imputado, alegado ou decidido.

A ordem é **escala primeiro, detalhamento depois**: o Astraea cobre tudo com pouca
profundidade e promove, por gatilho explícito e decisão humana, o que merece registro
detalhado. É o inverso do AtlasPen, que começou pelo detalhe de um país só.

## Público

Pesquisa acadêmica em Direito Penal Internacional, Direito Penal comparado e estudos
sobre genocídio: pesquisadores, docentes, mestrandos e doutorandos, clínicas de
direitos humanos, jornalismo de dados. Em segundo plano, quem precisa saber, numa
pergunta só, "este país tipifica genocídio?" ou "o que a CIJ decidiu sobre aquele caso
e quando?".

O usuário sabe o que é uma medida provisória da CIJ e não precisa que o site explique.
Precisa que o site **diga de onde veio cada dado, quando foi lido e com que
confiança**.

## Três compromissos herdados do AtlasPen

1. **Descrever, não qualificar.** O Astraea registra quem disse o quê: que a Gâmbia
   alegou genocídio, que a CIJ ordenou medidas provisórias, que um relator especial
   usou a palavra. **O sistema nunca afirma genocídio**; afirma que um órgão o afirmou,
   e diz qual. A taxonomia de status (ver `03-modelo-de-dados.md`) separa alegação,
   investigação, denúncia, medida provisória e decisão de mérito.
2. **Dizer o que se sabe e calar o que não se sabe.** Campo sem fonte é campo vazio,
   com o motivo. Nenhum dado é preenchido por plausibilidade, por modelo de linguagem
   ou por dedução a partir de outro país.
3. **Nada entra sem conferência, adaptado à escala.** No AtlasPen, cada registro é
   conferido contra o texto compilado. Aqui há 197 países, milhares de notícias por
   mês e dezenas de tribunais; a conferência é **por nível**: o robô carimba o que leu
   e de onde, cada fonte tem um grau de confiança declarado, cada registro carrega o
   seu, e a revisão humana é **por amostragem pré-registrada**, com taxa de erro
   publicada (ver `05-viabilidade-e-riscos.md` e `06-roteiro.md`).

## O que o Astraea é

- Um **observatório de superfície** com três telas e uma página inicial, publicado como
  site estático no GitHub Pages em inglês e em português do Brasil, com os dados
  abertos em JSON ao lado (chaves em inglês, rótulos nas duas línguas; as demais
  línguas mais usadas entram depois do MVP).
- Um **índice com proveniência**: cada item diz URL, data de captura, hash do texto lido,
  língua original, fonte, nível de triagem e versão do léxico que o aceitou.
- Um **mecanismo de promoção**: o registro superficial que acumula evidência (ordem da
  CIJ, denúncia do TPI, pico de notícias) sobe para investigação detalhada, com dono,
  prazo e lugar próprios (ver `04-arquitetura.md`, seção "Promoção").
- Um projeto **de uma pessoa**, desenhado para sobreviver a meses sem atenção: rodadas
  que falham sem perder estado, relatórios que acusam o que não foi lido, nenhum
  componente que precise de servidor ligado.

## O que o Astraea não é

- **Não é o AtlasPen do mundo.** Não cataloga tipos penais de cada país, não calcula
  institutos, não simula alteração legislativa. O registro de país tem uma dezena de
  campos, não mil.
- **Não é um acervo de texto.** Não armazena nem exibe texto integral de notícia ou de
  decisão. Armazena metadados, *link*, data, fonte e resumo próprio. A cópia de
  referência, quando houver, é a do Internet Archive.
- **Não é um alerta precoce de genocídio.** Não prevê, não pontua risco, não ordena
  países por probabilidade. Isso existe (Early Warning Project, Genocide Watch) e o
  Astraea pode apontar para eles; não os replica.
- **Não é um buscador.** Não cobre "tudo o que existe": cobre o que as fontes declaradas
  publicam, e mede quanto falta, como o Alétheia.
- **Não é um tribunal nem um relatório de direitos humanos.** Não investiga fatos, não
  ouve vítimas, não nomeia perpetradores por conta própria. Pessoas aparecem só como a
  fonte as nomeia, e há política de remoção a pedido (`docs/pessoas.md`, herdado do
  Alétheia).
- **Não usa modelo de linguagem para decidir o que entra.** A triagem é determinística,
  por léxico em arquivo, como no Argos. Um modelo pode, por decisão registrada,
  produzir o resumo próprio ou a tradução de um título, sempre marcado como tal e
  nunca como critério de aceitação (decisão pendente em `07-decisoes-pendentes.md`).

## Unidade de análise de cada função

| Função | Unidade | Chave | Granularidade mínima |
|---|---|---|---|
| Leis penais do mundo | o país (ou entidade) | ISO 3166-1 alfa-3, com extensão para Kosovo | um registro por país, campos fechados, cada campo com fonte e data |
| Notícias | o documento (uma URL normalizada) | `hash` da URL normalizada, como no Alétheia | título, data, veículo, língua, situação monitorada, nível de triagem |
| Decisões | o ato processual | tribunal + caso + data + tipo de ato | tribunal, caso, partes, tipo (ordem, decisão, parecer, andamento), data, URL oficial, status na taxonomia |

A **situação monitorada** (um conflito ou contexto em que genocídio é alegado,
investigado ou julgado: Mianmar/Rohingya, Gaza, Darfur, Tigré, Xinjiang, Ucrânia,
Ruanda 1994, Srebrenica…) é a entidade que liga as três telas: a notícia cita uma
situação, a decisão pertence a uma situação, e a situação aponta para os países
envolvidos. É dela que o léxico é gerado.

## Universo de países

Decidido em 09/11/2026 (D1, como recomendado; o argumento contrário está em
`07-decisoes-pendentes.md`):

- **193 Estados-membros da ONU**: entram todos.
- **2 Estados observadores** (Palestina `PSE`, Santa Sé `VAT`): entram, com o campo
  `un_status` = `observer`. Ambos são partes na Convenção de 1948 e a Palestina é
  parte no Estatuto de Roma; deixá-los fora apagaria registros centrais da função 3.
- **Entidades de reconhecimento limitado** (Kosovo, Taiwan): entram, com `un_status`
  = `non_member` e nota de reconhecimento. Kosovo não tem código ISO oficial; usa-se o
  código reservado `XKX` (como o Banco Mundial e a Comissão Europeia), documentado como
  exceção. Taiwan tem `TWN` na ISO 3166. Outras entidades (Saara Ocidental `ESH`,
  Somalilândia, Transnístria…) **não** entram como registro na fase 1; entram como
  `situation` quando houver alegação de genocídio a elas ligada.
- **Total: 197 registros** na fase 1.

O `id` é o código alfa-3 e nunca muda; um país que mude de nome (Suazilândia →
Essuatíni) mantém o código, e um que deixe de existir ganha `valid_until` em vez de
sair, como no acervo do AtlasPen.

## Licenças

Herdadas do AtlasPen e do Alétheia: **Apache-2.0** para o código, **CC BY 4.0** para
dados, documentação e resumos próprios. Metadados de documentos de terceiros (título,
URL, data) não são obra protegida; o texto integral nunca é redistribuído. Dados de
fontes com licença própria (GDELT pede citação; a UN Treaty Collection tem termos de
uso da ONU) são consumidos como dado e a fonte é citada no registro, no `NOTICE` e na
página de fontes do site.

## O que decide se o projeto deu certo

Ao fim do MVP (`06-roteiro.md`):

- 197 registros de país com os campos de ratificação preenchidos e com fonte, e o campo
  de tipificação interna preenchido para pelo menos os países com situação monitorada;
- a tela de notícias atualizada semanalmente, sem intervenção, por quatro semanas
  seguidas, com taxa de falso positivo na amostra abaixo de um limiar declarado;
- a tela de decisões com todos os atos da CIJ e do TPI sobre genocídio desde 2019
  registrados, com status na taxonomia e URL oficial;
- um registro promovido de ponta a ponta, da descoberta superficial ao detalhamento,
  como prova do fluxo.
