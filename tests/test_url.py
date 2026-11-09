import pytest

from astraea.engine.url import domain, identity, normalize, original_from_wayback


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.Jornal.br/a/b/", "jornal.br/a/b"),
        ("http://jornal.br/a/b?utm_source=x&id=3", "jornal.br/a/b?id=3"),
        ("https://web.archive.org/web/20021002080000id_/http://www.jornal.br/a/b", "jornal.br/a/b"),
        ("https://web.archive.org/web/2002/https://jornal.br/a/b", "jornal.br/a/b"),
        (
            "http://www1.folha.uol.com.br:80/cotidiano/x.shtml",
            "www1.folha.uol.com.br/cotidiano/x.shtml",
        ),
        ("jornal.br", "jornal.br/"),
    ],
)
def test_normalize(url, expected):
    assert normalize(url) == expected


def test_same_article_live_and_archived_has_the_same_id():
    live = "https://www.jornal.br/2016/carandiru.shtml?fbclid=abc"
    archived = "https://web.archive.org/web/20160927090000id_/http://jornal.br/2016/carandiru.shtml"
    assert identity(live) == identity(archived)
    assert len(identity(live)) == 16
    assert domain(archived) == "jornal.br"
    assert original_from_wayback(archived) == "http://jornal.br/2016/carandiru.shtml"
    assert original_from_wayback(live) == live
