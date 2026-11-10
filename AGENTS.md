# Instruções para agentes de IA — Astraea

Observatório de superfície sobre o crime de genocídio e a lei penal do mundo: três
telas (leis penais por país, notícias, decisões de tribunais internacionais), site
estático no GitHub Pages, dados abertos em JSON. **O valor central é a proveniência**:
todo dado diz de onde veio, quando foi lido e com que confiança. Um dado sem fonte é
pior que um dado ausente.

Este arquivo é lido pelo Codex e demais agentes pelo nome; o Claude Code o lê via
`CLAUDE.md`, que só o importa. Regra nova entra **aqui**. O plano do projeto está em
`docs/00` a `docs/07`; o que ainda não foi decidido está em
`docs/07-decisoes-pendentes.md`, e **decisão pendente não se decide em código**.

## Estado do projeto

Em 10/11/2026 o repositório tem o plano, o motor (`astraea/engine/`, `astraea/sources/`,
`astraea/cli.py`), as licenças e os dados da fase 1: `data/countries.json` (197 registros,
só `id`, `name`, `un_status`, `un_member_since`, `situations`), `data/situations.json`
(as dez da D6; nove status, todos sem carimbo de pessoa), `data/sources.json` (87
fontes), `data/verification.json` (a trilha que carimba os campos escalares),
`data/lexicon/` (termos fixos em `fixed/` e o léxico gerado em cinco línguas; o árabe é
rascunho), `data/retired-ids.json` e `data/i18n/`. `scripts/vocabularies.py` é a lista
única dos vocabulários fechados e das chaves de rótulo; `scripts/build_lexicon.py` gera o
léxico; `scripts/transform.py` valida com as onze travas e gera `static/data/`. 210
testes. Não há site nem *workflows*. O `06-roteiro.md` diz a ordem; a fase 1 segue pela
sessão 4 (`build_site.py`, `ci.yml`, `deploy.yml`, página inicial, política de robô em
código). Antes de escrever código, leia o `00-inventario.md` e o
`04-arquitetura.md` ("Onde o motor vive"): o motor é **próprio**,
nascido de uma cópia do Alétheia (`luccas-amorim/aletheia`) com o aviso MIT e o `sha` de
origem no `NOTICE`, traduzido para inglês e livre para divergir. O Alétheia não é
dependência; correção que valha a pena trazer de lá é portada à mão e registrada no
`CHANGELOG.md`.

## Regras que não se negociam

1. **O sistema nunca afirma genocídio.** Registra quem afirmou, em que grau, com URL e
   data, na taxonomia de `docs/03-modelo-de-dados.md`. Tela, resumo, commit e issue
   dizem "alegado por X", "medida provisória da CIJ", nunca "genocídio" solto.
2. **Nunca texto integral de terceiros.** Metadados, *link*, data, fonte, língua e
   resumo próprio. `excerpt` só em relatório de rodada, até 320 caracteres.
3. **Robô não muda status nem promove.** `situations.statuses`, `promotion` e qualquer
   campo com `checked_by: human` só mudam por commit de pessoa. O validador
   reprova o contrário.
4. **Fonte secundária aponta, não escreve.** Wikipedia, Wikidata, agregadores e
   modelos de linguagem geram perguntas e rascunhos marcados; nunca preenchem campo
   de país nem decidem triagem.
5. **`id` é append-only.** País é ISO 3166-1 alfa-3 (`XKX` para Kosovo); situação é
   *slug*; documento é `hash` da URL normalizada. Nunca reatribuído; o que sai vai para
   `data/retired-ids.json`.
6. **Fonte × derivado.** `data/` é editável; `static/data/` é gerado por
   `scripts/transform.py` e a CI exige sincronia. Nunca edite o derivado. A exceção
   dentro de `data/` é `data/lexicon/<lang>.json`, gerado por
   `scripts/build_lexicon.py`: edita-se `data/lexicon/fixed/<lang>.json` e
   `situations.terms`, e o validador reprova o léxico que não bate com eles.
7. **Robots, limites e bloqueios são política.** O cliente HTTP obedece `robots.txt`
   e o limite declarado por fonte; WAF, CAPTCHA e bloqueio por país não se contornam.
   Google e APIs comerciais de notícias ficam fora.
8. **Pessoas.** Nome de pessoa só em `decisions.json`, como o tribunal o escreve.
   Política de remoção em `docs/pessoas.md`.
9. **Nada entra sem carimbo.** Campo afirmado tem `url`, `source`, `read_on`,
   `confidence` e `checked_by`. `--draft` só na carga inicial, e o relatório de
   qualidade conta o que ainda está em rascunho.

## Como trabalhar neste repositório

- **Antes de concluir**, rode a bateria (quando ela existir; até lá, o que houver):

  ```
  python scripts/transform.py --strict
  python scripts/transform.py --draft --check
  python -m pytest
  astraea validate-lexicon data/lexicon/*.json
  astraea validate-config config/*.json
  ruff check . && ruff format --check .
  ```

  Enquanto durar a carga inicial, `--strict` **reprova de propósito** e só pelos
  rascunhos (travas 3 e 6: campo sem carimbo, status de tribunal sem `checked_by:
  human`); qualquer outra trava na saída dele é erro seu. `--draft --check` tem de
  passar: valida relaxando só essas duas e confere que `static/data/` está em dia. Se
  não estiver, `python scripts/transform.py --draft --execute`; se o léxico estiver
  velho, `python scripts/build_lexicon.py --execute` antes. Rascunho não se "resolve"
  preenchendo `checked_by`: quem carimba como `human` é a pessoa (regra 3).

- **Línguas.** Dados e código em **inglês**: nomes de arquivo, chaves, valores de
  vocabulário fechado, *ids*, *slugs*, comandos, opções, nomes de módulo e de
  *workflow*. Chave publicada não se traduz nem se renomeia depois. Documentação
  (`docs/`, este arquivo, `CHANGELOG.md`), commits e issues continuam em português, e
  os nomes dos robôs (Tabelião, Escrivão…) também, como nomes próprios. As telas
  nascem em `en` e `pt-BR`; o que se traduz são rótulos e textos nossos, nunca as
  chaves (`03-modelo-de-dados.md`, "Várias línguas").
- **Uma sessão = uma entrada no `CHANGELOG.md`**, com data e o que mudou de dado, de
  fonte ou de regra. Correção de dado antigo entra como correção; alteração de status
  de situação entra com o ato que a sustentou.
- **Issue que o robô abre, a pessoa fecha** com `Closes #N` no PR ou no commit.
- **Decisão nova vai para `docs/`** (o documento afetado) e, se for regra, para cá.
  Não escreva regra em comentário de código.
- **Para o dono do projeto**, que não programa no dia a dia e usa Windows: todo passo
  que ele precise executar vem explícito, com os avisos que o PowerShell vai mostrar;
  todo *script* que altere arquivo roda em modo simulação por padrão (`--execute`
  para valer) e nunca apaga; quando uma escolha sua divergir do que ele pediu, diga e
  diga por quê; em prosa, termo estrangeiro em itálico.
- **Trabalhe em branch própria** quando houver código; commits pequenos que expliquem
  o porquê. **Não faça `git push` nem abra PR sem o usuário pedir.**
- Editar `.md` com Python ou `sed` no Windows introduz CRLF; grave bytes ou confira o
  fim de linha (lição do AtlasPen). O `.gitattributes` grava texto com LF e as
  *fixtures* byte a byte (`-text`); não mude isso.
- Todo `open`, `read_text` e `write_text` de texto leva `encoding="utf-8"`, inclusive
  nos testes: no Windows o padrão é cp1252, e foi o que derrubou dois testes do motor
  copiado (lição da sessão de 09/11/2026).
- Ambiente: `python -m venv .venv`, `pip install -e ".[dev]"`; a bateria roda com o
  Python e o `ruff` de dentro do `.venv`.

## O que não entra, e onde entra

- Texto de notícia ou de decisão: não entra. Entra o *link* e, se houver, o
  `snapshot` do Internet Archive.
- Alegação de imprensa como status: não entra. Entra como notícia ligada à situação.
- Previsão, pontuação de risco, ranking de países: não entra. O Astraea aponta para o
  Early Warning Project e para o Genocide Watch.
- Campo de país preenchido "por analogia" com país vizinho ou com a mesma tradição
  jurídica: não entra. Fica vazio com `reason`.
- Léxico em código: não entra. Léxico é dado, um arquivo por língua, gerado de
  `situations.json` mais os termos fixos.
