# Tarefa: plano de implementação e viabilidade do Astraea

Você vai produzir um PLANO, não código. Não crie nenhuma funcionalidade nem
altere nenhum outro repositório. Leia tudo o que existir e escreva documentos.

## Quem sou e como trabalho
Sou Luccas de Amorim, advogado em formação e pesquisador em Direito Penal. Fui
engenheiro de software e hoje sou PM técnico, mas não programo no dia a dia e
sou iniciante em linha de comando. Por isso:
- todo passo que eu precise executar deve vir explícito, com os avisos que o
  Windows/PowerShell vai mostrar;
- todo script que altere arquivos roda em modo simulação por padrão e nunca
  apaga nada;
- quando uma escolha sua divergir do que pedi, avise e diga por quê;
- em texto corrido, termos estrangeiros em itálico (ex.: *crawler*).

## O que é o Astraea
Um repositório único (`astraea`, já criado e ainda vazio em
https://github.com/luccas-amorim/astraea), publicado no GitHub Pages, com uma
landing page e três telas:

1. **Leis penais do mundo**: mapear, por robôs, a legislação penal dos países
   do mundo. O ponto de partida brasileiro é o AtlasPen, mas o detalhamento
   aqui é muito menor. Interessa saber o que existe em cada país, não cada tipo
   penal.
2. **Notícias sobre genocídios**: monitorar continuamente o noticiário mundial
   sobre genocídios (e alegações de genocídio).
3. **Decisões de tribunais internacionais sobre genocídio**: monitorar
   decisões, ordens e andamentos relevantes.

A estratégia é deliberadamente inversa à do AtlasPen: primeiro escala (monitorar
tudo, com pouca profundidade), depois detalhamento seletivo de cada descoberta.
O plano deve preservar essa ordem e mostrar como uma descoberta superficial
vira, mais tarde, um registro detalhado.

## Ativos que já existem (mobilize-os antes de propor qualquer coisa nova)
- **AtlasPen**: https://github.com/luccas-amorim/atlaspen (site:
  https://atlaspen.com.br). Data set de tipos penais brasileiros em JSON,
  crawler de auditoria contra o compilado do planalto.gov.br, snapshots
  versionados. Convenções em `CONTRIBUTING.md`, `CLAUDE.md` e `AGENTS.md`:
  nada entra sem conferência contra a fonte; "uma sessão = uma release" com
  changelog; `id` é URL pública e nunca é reatribuído; dados legíveis por
  humanos; `CITATION.cff`.
- **ctresb/leis** (https://github.com/ctresb/leis): legislação brasileira
  inteira convertida em markdown, hoje apoio do AtlasPen (o Curador do AtlasPen
  faz a triagem nesse markdown). É repositório de terceiro, não meu: trate-o
  como dado consumido e verifique a licença (o GitHub a mostra como "Other").
- **Argos** (https://github.com/luccas-amorim/argos): vigilância determinística
  dos tribunais superiores e do CNJ para o AtlasPen (STJ, STF, STM, DataJud,
  DJEN), com léxico em arquivo, proveniência por item e descarte com motivo.
  É o motor de que o Alétheia descende e o candidato natural para a função 3.
- **Alétheia** (https://github.com/luccas-amorim/aletheia): observatório do que
  a internet guarda sobre o Massacre do Carandiru. Robô que descobre por canais
  independentes, lê o texto inteiro, confronta com um léxico, anota a cópia no
  Internet Archive e estima quanto ainda falta. Motor descendente do Argos;
  catálogo ainda vazio e léxico provisório.

## Fase 0: inventário (faça primeiro e registre em `docs/00-inventario.md`)
Leia os quatro repositórios e documente, para cada um, a arquitetura, o formato
dos dados, os robôs/pipelines existentes, os agendamentos (GitHub Actions), as
dependências e as convenções. Termine com uma tabela: o que pode ser reusado no
Astraea tal como está, o que pode ser reusado com adaptação, o que deve ser
consumido como dado (sem copiar código) e o que não serve. Seja honesto. Um
crawler específico do planalto.gov.br provavelmente não escala para 193 países,
e quero saber disso agora.

## O que o plano precisa responder

### Para cada uma das três funções
- **Unidade de análise e granularidade mínima.** Ex.: para leis, por país,
  quais campos? (existência de código penal, data e fonte oficial,
  criminalização interna do genocídio, ratificação da Convenção de 1948 e do
  Estatuto de Roma, pena máxima/pena de morte etc.). Proponha um esquema mínimo
  e justifique cada campo.
- **Fontes candidatas**, com licença, termos de uso, `robots.txt`, API ou não,
  idiomas, frequência de atualização e confiabilidade. Pesquise e verifique,
  não liste de memória. Considere, entre outras: UN Treaty Collection, bases da
  UNODC (SHERLOC), Legislationline, a base de implementação nacional do CICV,
  Global Legal Monitor (Library of Congress), LIIs nacionais, GDELT e RSS de
  agências para notícias; CIJ, TPI, IRMCT (sucessor de TPII/TPIR), ECCC e
  tribunais regionais de direitos humanos para decisões.
- **Viabilidade por robô**: o que se automatiza totalmente, o que exige revisão
  humana e o que é inviável. Estime volume, custo e esforço.
- **Como o Alétheia e o Argos entram**: se eles já resolvem parte do
  monitoramento de notícias e de tribunais, prefira reusá-los a duplicar.

### Questões transversais (não pule nenhuma)
1. **Universo de países.** "193" são os membros da ONU. Decida e justifique
   como tratar Estados observadores (Palestina, Santa Sé) e entidades de
   reconhecimento limitado (Kosovo, Taiwan), que podem ser centrais no
   monitoramento de genocídio. Use códigos ISO 3166 estáveis como `id`.
2. **Rótulo "genocídio".** É uma qualificação jurídica, não descritiva. O
   esquema deve separar alegação (por quem), investigação, denúncia, medida
   provisória e decisão de mérito, sem que o sistema afirme genocídio onde
   nenhum órgão competente afirmou. Proponha a taxonomia de status e a regra de
   exibição nas telas.
3. **Direitos autorais.** Para notícias e decisões, armazenar metadados, link,
   data, fonte e resumo próprio, nunca o texto integral de terceiros.
4. **Multilinguismo.** Fontes em dezenas de idiomas: como coletar, classificar
   e traduzir com custo controlado, e como registrar a língua original.
5. **Infraestrutura.** GitHub Pages é estático, e Actions e tamanho de
   repositório têm limites. Estime o crescimento dos dados em 1, 3 e 5 anos e
   diga quando (e se) a arquitetura estática deixa de servir. Compare um
   repositório único com uma separação entre código e dados, e diga se minha
   ideia de um repositório só se sustenta.
6. **Qualidade e auditoria.** Adapte a filosofia do AtlasPen ("nada entra sem
   conferência") a um projeto de escala, com níveis de confiança por registro
   e pela fonte, e com revisão por amostragem.
7. **Do monitoramento ao detalhamento.** Defina o gatilho e o fluxo pelo qual
   um registro superficial é promovido a investigação detalhada, e onde esse
   detalhamento vive (no Astraea ou em repositório-filho).

## Entregáveis (em `docs/`, todos em markdown)
- `00-inventario.md`: Fase 0.
- `01-visao-e-escopo.md`: objetivo, público (pesquisa acadêmica, sobretudo
  Direito Penal Internacional), o que o Astraea é e não é.
- `02-fontes.md`: tabela de fontes por função, com status verificado.
- `03-modelo-de-dados.md`: esquemas JSON propostos, com exemplo preenchido.
- `04-arquitetura.md`: robôs, agendamentos, armazenamento e telas; diagrama
  em Mermaid.
- `05-viabilidade-e-riscos.md`: matriz risco × probabilidade, incluindo riscos
  jurídicos, éticos, de custo e de manutenção por uma pessoa só.
- `06-roteiro.md`: fases com MVP claramente delimitado (o menor Astraea útil),
  critérios de pronto e estimativa de esforço por fase.
- `07-decisoes-pendentes.md`: perguntas que só eu posso responder. Para cada
  uma: sua leitura recomendada, grau de confiança (A/M/B), fundamento e o
  melhor argumento contrário.

## Como trabalhar
- Antes de escrever os documentos, apresente um sumário do inventário e um
  esboço do plano, e espere meu ok.
- Pesquise na web quando a resposta depender do estado atual de uma fonte, API
  ou tribunal. Cite a URL.
- Se algo for inviável, diga com clareza em vez de propor um contorno frágil.
- Ao final, proponha o primeiro `CLAUDE.md` e o primeiro `CONTRIBUTING.md` do
  Astraea, herdando o que fizer sentido do AtlasPen.
