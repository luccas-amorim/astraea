# Fixtures

The tests run without network, against these files. They came from Alétheia (see
`NOTICE`) and are **synthetic**: they imitate the documented format of each origin
without having been recorded from it. Their content is in Portuguese, about the Carandiru
massacre, because that was Alétheia's subject; for the engine tests the subject does not
matter. Astraea's own fixtures (UN Treaty Collection, ICJ, ICC feeds) come with the
adapters of phases 2 and 3, recorded from the real source.

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
