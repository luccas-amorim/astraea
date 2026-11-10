"""The listing adapter and its first format, the per-treaty XML of the UNTC.

Everything runs without network: the two fixtures in tests/fixtures/untc/ are the files
the engine downloaded on 2026-11-10, with the depositary's prose replaced by markers
(scripts/trim_untc_fixtures.py; the sha256 of the originals is in CHANGELOG.md). The
small XML files written here imitate the same structure for the failure cases.
"""

from __future__ import annotations

from datetime import date

import pytest

from astraea import sources
from astraea.engine.contract import Source
from astraea.engine.http import Client
from astraea.sources.listing import (
    FORMATS,
    Listing,
    TableError,
    articles,
    clean,
    decode_xml,
    parse_untc_treaty,
    untc_date,
)

URL = "https://treaties.un.org/doc/Publication/MTDSG/Volume%20I/Chapter%20IV/IV-1.en.xml"
ROBOTS = "https://treaties.un.org/robots.txt"


def treaty(
    rows: str, *, signatories: int, parties: int, extra: str = "", head: str | None = None
) -> bytes:
    head = head or "Accession(a), Succession(d), Ratification"
    return (
        '<?xml version="1.0" encoding="ISO-8859-1"?><Document><Treaty><Header><ExternalData>'
        "<Titlesect>Test treaty</Titlesect><Status><Signatories>"
        f"{signatories}</Signatories><Parties>{parties}</Parties></Status></ExternalData></Header>"
        '<Participants><Table><TGroup cols="3"><Thead><Row><Entry colname="1">Participant'
        '</Entry><Entry colname="2">Signature</Entry><Entry colname="3">'
        f"{head}</Entry></Row></Thead><Tbody><Rows>{rows}</Rows></Tbody></TGroup></Table>"
        f"</Participants>{extra}</Treaty></Document>"
    ).encode("latin-1")


def row(name: str, signature: str = "", bound: str = "") -> str:
    def cell(value: str) -> str:
        return f"<Entry>{value}</Entry>" if value else "<Entry/>"

    return f"<Row>{cell(name)}{cell(signature)}{cell(bound)}</Row>"


@pytest.fixture
def iv1(fixtures):
    return parse_untc_treaty((fixtures / "untc" / "IV-1.en.xml").read_bytes())


@pytest.fixture
def xviii10(fixtures):
    return parse_untc_treaty((fixtures / "untc" / "XVIII-10.en.xml").read_bytes())


# ------------------------------------------------------------------ the recorded files


def test_the_genocide_convention_as_the_depositary_counts_it(iv1):
    assert iv1.meta == {
        "title": "Convention on the Prevention and Punishment of the Crime of Genocide",
        "signatories": 41,
        "parties": 154,
    }
    assert iv1.sentinel == "Status: 41 signatories, 154 parties; the rows agree"
    assert len(iv1.rows) == 155
    brazil = dict(iv1.row("Brazil").cells)
    assert brazil["signature"] == "1948-12-11"
    assert brazil["bound_since"] == "1952-04-15"
    assert brazil["consent_type"] == "ratification"
    assert brazil["objections"] is True
    assert iv1.row("Afghanistan").cells["consent_type"] == "accession"
    assert iv1.row("Antigua and Barbuda").cells["consent_type"] == "succession"


def test_reservations_and_the_articles_they_refer_to(iv1):
    assert iv1.row("China").cells["articles"] == ["IX"]
    assert "IX" in iv1.row("United States of America").cells["articles"]
    # Myanmar's reservations are on articles VI and VIII, not on the ICJ clause
    assert "IX" not in iv1.row("Myanmar").cells["articles"]
    # Albania's entry keeps only "..." where a withdrawn reservation was, and article XII
    assert iv1.row("Albania").cells["articles"] == ["XII"]
    # an entry with only a footnote mark (a reservation withdrawn) is not a reservation
    assert iv1.row("Czech Republic").cells["declarations"] is False
    assert iv1.row("Brazil").cells["declarations"] is False


def test_footnote_superscripts_leave_the_names(iv1, xviii10):
    names = {r.key for r in iv1.rows} | {r.key for r in xviii10.rows}
    assert "Argentina" in names and "Viet Nam" in names
    assert not [n for n in names if "superscript" in n or any(ch.isdigit() for ch in n)]
    assert "Côte d'Ivoire" in names and "Türkiye" in names  # character references


def test_the_rome_statute_withdrawals(xviii10):
    assert xviii10.meta["signatories"] == 137 and xviii10.meta["parties"] == 125
    burundi = dict(xviii10.row("Burundi").cells)
    assert burundi["struck_out"] is True
    assert burundi["withdrawal_notified"] == "2016-10-27"
    assert burundi["withdrawal_effect"] == "2017-10-27"
    # notified in 2026, effective in 2027: still a party
    niger = dict(xviii10.row("Niger").cells)
    assert niger["struck_out"] is False and niger["withdrawal_effect"] == "2027-06-18"
    # notified and then rescinded
    hungary = dict(xviii10.row("Hungary").cells)
    assert hungary["withdrawal_rescinded"] is True and hungary["withdrawal_effect"] is None
    assert xviii10.row("Netherlands (Kingdom of the)").cells["consent_type"] == "acceptance"
    assert xviii10.row("Cook Islands") is not None  # a participant outside the 197


# ------------------------------------------------------------------ the adapter


def test_listing_fulfils_the_contract_and_is_built_from_a_configuration(network):
    built = sources.build(
        {"type": "listing", "id": "listing:untc-iv-1", "url": URL, "format": "untc_treaty"},
        network,
    )
    assert isinstance(built, Listing) and isinstance(built, Source)
    assert built.respects_robots is True
    with pytest.raises(ValueError, match="unknown listing format"):
        Listing("listing:x", URL, "csv", Client(30, transport=network))
    assert set(FORMATS) == {"untc_treaty"}


def test_list_reads_the_table_once_obeying_robots(network, fixtures):
    network.answer(ROBOTS, "User-agent: *\nCrawl-delay: 2\n")
    network.answer(URL, fixtures / "untc" / "IV-1.en.xml", headers={"content-type": "text/html"})
    listing = Listing("listing:untc-iv-1", URL, "untc_treaty", Client(30, transport=network))
    refs = list(listing.list(date(2026, 1, 1)))
    assert network.urls() == [ROBOTS, URL]
    assert len(refs) == 155
    assert listing.client.crawl_delay(URL) == 2.0
    brazil = next(r for r in refs if r.title == "Brazil")
    assert brazil.source_id.startswith("Brazil#")
    assert brazil.url == URL + "#Brazil"
    doc = listing.fetch(brazil)
    assert listing.sentinel(doc)
    assert "bound_since: 1952-04-15" in doc.text
    assert len(network.urls()) == 2  # fetch does not go back to the network


def test_robots_that_forbid_the_path_stop_the_reading(network):
    from astraea.engine.http import BlockedByRobots

    network.answer(ROBOTS, "User-agent: *\nDisallow: /doc/\n")
    listing = Listing("listing:untc-iv-1", URL, "untc_treaty", Client(30, transport=network))
    with pytest.raises(BlockedByRobots):
        list(listing.list(date(2026, 1, 1)))
    assert network.urls() == [ROBOTS]


def test_a_changed_row_comes_back_as_new_and_the_others_do_not(network):
    before = treaty(row("Aland", "", "1 Jan 1990 a") + row("Borduria", "", "2 Feb 1991 a"),
                    signatories=0, parties=2)  # fmt: skip
    after = treaty(row("Aland", "", "1 Jan 1990 a") + row("Borduria", "", "3 Feb 1991 d"),
                   signatories=0, parties=2)  # fmt: skip
    network.answer(ROBOTS, "", status=404)
    network.answer(URL, before)
    network.answer(URL, after)
    listing = Listing("listing:t", URL, "untc_treaty", Client(30, transport=network))
    first = {r.title: r.source_id for r in listing.list(date(2026, 1, 1))}
    second = {r.title: r.source_id for r in listing.list(date(2026, 1, 1))}
    assert first["Aland"] == second["Aland"]
    assert first["Borduria"] != second["Borduria"]


def test_sentinel_refuses_a_document_without_the_table(network, fixtures):
    network.answer(ROBOTS, "", status=404)
    network.answer(URL, fixtures / "untc" / "IV-1.en.xml")
    listing = Listing("listing:untc-iv-1", URL, "untc_treaty", Client(30, transport=network))
    ref = next(iter(listing.list(date(2026, 1, 1))))
    from dataclasses import replace

    assert not listing.sentinel(listing.fetch(replace(ref, data={})))


# ------------------------------------------------------------------ the sentinel


def test_the_counts_of_the_status_block_must_match_the_rows():
    body = treaty(row("Aland", "1 Jan 1980", "1 Jan 1990"), signatories=1, parties=2)
    with pytest.raises(
        TableError, match="says 1 signatories and 2 parties; the rows count 1 and 1"
    ):
        parse_untc_treaty(body)


def test_a_file_without_the_status_block_is_refused():
    body = b'<?xml version="1.0" encoding="ISO-8859-1"?><Document><Treaty/></Document>'
    with pytest.raises(TableError, match="no Status block"):
        parse_untc_treaty(body)


def test_a_truncated_file_is_refused(fixtures):
    raw = (fixtures / "untc" / "IV-1.en.xml").read_bytes()
    with pytest.raises(TableError, match="not well-formed"):
        parse_untc_treaty(raw[: len(raw) // 2])


def test_an_error_page_served_with_200_is_refused():
    with pytest.raises(TableError):
        parse_untc_treaty(b"<html><body>Page not found</body></html>")


def test_unknown_shapes_are_never_guessed():
    with pytest.raises(TableError, match="action code 'x'"):
        parse_untc_treaty(treaty(row("Aland", "", "1 Jan 1990 x"), signatories=0, parties=1))
    with pytest.raises(TableError, match="unknown shape"):
        parse_untc_treaty(treaty(row("Aland", "", "1990-01-01"), signatories=0, parties=1))
    with pytest.raises(TableError, match="unknown action"):
        parse_untc_treaty(treaty(row("Aland", "", "1 Jan 1990"), signatories=0, parties=1,
                                 head="Denunciation(x), Ratification"))  # fmt: skip
    with pytest.raises(TableError, match="repeated"):
        parse_untc_treaty(treaty(row("Aland", "", "1 Jan 1990") * 2, signatories=0, parties=2))
    extra = "<Objections><Objection><Participant>Nowhere</Participant></Objection></Objections>"
    with pytest.raises(TableError, match="not in the table"):
        parse_untc_treaty(treaty(row("Aland", "", "1 Jan 1990"), signatories=0, parties=1,
                                 extra=extra))  # fmt: skip


def test_a_struck_out_row_needs_the_withdrawals_note():
    body = treaty(row("Aland", "[1 Jan 1980 ]", "[1 Jan 1990 ]"), signatories=0, parties=0)
    with pytest.raises(TableError, match="struck out"):
        parse_untc_treaty(body)


# ------------------------------------------------------------------ decoding and cleaning


def test_iso_8859_1_is_decoded_by_the_declaration_not_by_the_http_header():
    body = treaty(row("C\xf4te d'Ivoire", "", "18 Dec 1995 a"), signatories=0, parties=1)
    assert b"\xf4" in body
    table = parse_untc_treaty(body)
    assert table.rows[0].key == "Côte d'Ivoire"


def test_declared_latin_1_is_read_as_cp1252_without_losing_a_byte():
    raw = b'<?xml version="1.0" encoding="ISO-8859-1"?><a>\x93quoted\x94 \x81</a>'
    assert decode_xml(raw).endswith("<a>“quoted” \x81</a>")
    assert decode_xml(b'<?xml version="1.0" encoding="UTF-8"?><a>\xc3\xa9</a>').endswith("é</a>")


def test_clean_removes_superscripts_markup_and_tabs():
    assert clean("Argentina<superscript>3</superscript>") == "Argentina"
    assert clean("Serbia<superscript>4,16</superscript>  ") == "Serbia"
    assert clean("<i>Ad article IX: </i>  The\tGovernment") == "Ad article IX: The Government"
    assert clean(None) == ""


def test_untc_dates():
    assert untc_date("22 Mar\t 1956 a") == ("1956-03-22", "a", False)
    assert untc_date("  8 Jul\t 1949 ") == ("1949-07-08", "", False)
    assert untc_date("[13 Jan\t 1999 ]") == ("1999-01-13", "", True)
    assert untc_date("17 March 2018") == ("2018-03-17", "", False)
    assert untc_date("17 Jul 2001 AA") == ("2001-07-17", "AA", False)
    with pytest.raises(TableError):
        untc_date("31 Feb 2001")
    with pytest.raises(TableError):
        untc_date("[13 Jan 1999")


def test_articles_as_written():
    assert articles(["With reference to article IX of the Convention"]) == ["IX"]
    assert articles(["articles VIII and IX", "Ad article XII:"]) == ["VIII", "IX", "XII"]
    assert articles(["article 87 (1) of the Statute"]) == ["87"]
    assert articles(["The Government of IX"]) == []
