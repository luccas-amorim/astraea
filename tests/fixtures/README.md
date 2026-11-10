# Fixtures

The tests run without network, against these files. They came from Alétheia (see
`NOTICE`) and are **synthetic**: they imitate the documented format of each origin
without having been recorded from it. Their content is in Portuguese, about the Carandiru
massacre, because that was Alétheia's subject; for the engine tests the subject does not
matter. Astraea's own fixtures come with the adapters of phases 2 and 3, recorded from
the real source; the first ones are in `untc/` and `cornell/`.

Fixtures are stored byte for byte (`.gitattributes`: `-text`): one of the pages is in
cp1252 on purpose, and line-ending conversion would break the tests that compare bytes.

| File | Imitates |
|---|---|
| `rss/feed.xml`, `rss/atom.xml` | RSS 2.0 of an outlet and Atom 1.0 of a repository |
| `rss/article-carandiru.html` | article in windows-1252 declared as iso-8859-1 |
| `rss/article-other.html`, `rss/error-200.html` | article unrelated to the lexicon; error page served with 200 |
| `html/archived-page.html` | an archived copy (`id_` mode) of an article |
| `gdelt/day.json` | DOC 2.0 `artlist` in JSON |
| `lexicon-carandiru.json` | sample lexicon for the run and triage tests |
| `lexicon-example.json` | minimal lexicon of another domain, for the format tests |
| `untc/IV-1.en.xml`, `untc/XVIII-10.en.xml` | **recorded**: the per-treaty XML of the UN Treaty Collection (Genocide Convention, Rome Statute), downloaded by the engine on 2026-11-10, with the depositary's prose replaced by markers (see below) |
| `cornell/*.json` | **recorded**: the four death penalty lists of the Cornell Center on the Death Penalty Worldwide (one per category), downloaded by the engine on 2026-11-10, byte for byte (see below) |

## The UNTC fixtures

They are the files the engine's client downloaded on 2026-11-10 (robots.txt read,
`Crawl-delay: 2` kept), byte for byte, except that every paragraph of the declarations,
reservations, objections, notifications and end notes, and the treaty note of the
header, is replaced by a marker such as `[text of the depositary omitted in this
fixture; refers to article IX]`. The participants table, the `Status` block, the dates
and the table of withdrawals are untouched. The repository does not carry third-party
text (AGENTS.md, rule 2), and the UN terms do not allow redistributing it.

`scripts/trim_untc_fixtures.py --xml-dir DIR --execute` makes them from the downloaded
files, and refuses to write if the adapter reads the fixture differently from the
original. The sha256 of the originals is in `CHANGELOG.md` (phase 2, session 1).

## The Cornell fixtures

They are the four responses of the database API behind the world map of
dpw.lawschool.cornell.edu (`https://cornell-dpw.herokuapp.com/api/countries/by-law-status/1`,
one per value of `lawStatus`), as the engine's client downloaded them on 2026-11-10
(robots.txt read: 404 on that host, so nothing is forbidden), **byte for byte**. Each is a
JSON list of `{displayName, isoCode}`: names and ISO codes, no prose of the source, so
nothing had to be cut. The file names are the ones `scripts/load_death_penalty.py
--json-dir` expects:

| File | `lawStatus` |
|---|---|
| `abolitionist.json` | `Abolitionist` |
| `abolitionist-for-ordinary-crimes.json` | `Abolitionist For Ordinary Crimes` |
| `abolitionist-de-facto.json` | `Abolitionist de facto` |
| `retentionist.json` | `Retentionist` |

Their sha256 is in `CHANGELOG.md` (phase 2, session 2).
