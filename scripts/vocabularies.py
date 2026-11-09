"""Closed vocabularies and field paths of the data model (docs/03-modelo-de-dados.md).

This is the single list the validator (scripts/transform.py, check 2 and check 11) and
the tests read. A new value or field enters by a PR that changes this file and
docs/03-modelo-de-dados.md together (CONTRIBUTING.md, C5).

Key convention for labels in data/i18n/<locale>.json:

- a field is labelled by its path inside the record, with dots for nested blocks and
  without list indices: "penal_code.exists", "statuses.code", "case.parties.role";
- the provenance and text fields, which mean the same in every block (url, source,
  read_on, confidence, checked_by, note, reason, author, text), are labelled once, by
  their bare name;
- a value is labelled as "<field key>.<value>": "death_penalty.status.retentionist",
  "confidence.A", "level.3".
"""

from __future__ import annotations

# Fields shared by every block: labelled by the bare name, whatever the parent.
SHARED_FIELDS: tuple[str, ...] = (
    "id",
    "name",
    "url",
    "source",
    "read_on",
    "confidence",
    "checked_by",
    "note",
    "reason",
    "author",
    "text",
    "language",
    "languages",
    "date",
    "situations",
    "summary",
    "description",
    "updated_at",
    "promotion",
    "promotion.level",
    "promotion.trigger",
    "promotion.since",
    "promotion.where",
)

COUNTRY_FIELDS: tuple[str, ...] = (
    "un_status",
    "un_member_since",
    "penal_code",
    "penal_code.exists",
    "penal_code.title",
    "penal_code.enacted_year",
    "penal_code.consolidated_on",
    "penal_code.official_url",
    "penal_code.alternative_url",
    "domestic_genocide",
    "domestic_genocide.status",
    "domestic_genocide.provision",
    "domestic_genocide.instrument",
    "domestic_genocide.year",
    "domestic_genocide.follows_convention_definition",
    "genocide_convention",
    "genocide_convention.signature",
    "genocide_convention.bound_since",
    "genocide_convention.consent_type",
    "genocide_convention.reservations",
    "genocide_convention.reservations_note",
    "rome_statute",
    "rome_statute.signature",
    "rome_statute.bound_since",
    "rome_statute.withdrawal",
    "max_penalty",
    "max_penalty.type",
    "max_penalty.years",
    "max_penalty.applies_to_genocide",
    "death_penalty",
    "death_penalty.status",
    "valid_until",
    "validity_note",
)

SITUATION_FIELDS: tuple[str, ...] = (
    "countries",
    "countries.role",
    "period",
    "period.start",
    "period.end",
    "period.approximate",
    "statuses",
    "statuses.code",
    "statuses.by",
    "statuses.outcome",
    "terms",
    "terms.lang",
    "terms.forms",
    "terms.exclusions",
)

NEWS_FIELDS: tuple[str, ...] = (
    "domain",
    "outlet",
    "outlet_country",
    "title",
    "title_translations",
    "published_at",
    "captured_at",
    "channel",
    "matched_keys",
    "categories",
    "level",
    "lexicon_version",
    "snapshot",
    "text_hash",
)

DECISION_FIELDS: tuple[str, ...] = (
    "court",
    "case",
    "case.court_case_id",
    "case.number",
    "case.name",
    "case.parties",
    "case.parties.country",
    "case.parties.role",
    "act_type",
    "official_url",
    "alternative_url",
    "taxonomy_status",
    "outcome",
    "checked_on",
)

SOURCE_FIELDS: tuple[str, ...] = (
    "function",
    "license",
    "terms_url",
    "robots_checked_on",
    "api",
    "rate_limit_per_minute",
    "sentinel",
    "state_media",
    "no_text_by_policy",
    "state",
)

FIELDS: tuple[str, ...] = (
    SHARED_FIELDS
    + COUNTRY_FIELDS
    + SITUATION_FIELDS
    + NEWS_FIELDS
    + DECISION_FIELDS
    + SOURCE_FIELDS
)

_TAXONOMY = (
    "allegation",
    "political_recognition",
    "investigation",
    "accusation",
    "provisional_measures",
    "merits_decision",
    "closed",
)
_OUTCOME = ("recognized", "not_recognized", "partial")
_ROLE = ("territory", "party", "forum", "applicant", "respondent")

VOCABULARIES: dict[str, tuple[str, ...]] = {
    # provenance and texts (every block)
    "confidence": ("A", "B", "C"),
    "checked_by": ("robot", "human", "sample"),
    "author": ("human", "model"),
    "promotion.level": ("surface", "under_investigation", "detailed"),
    # countries
    "un_status": ("member", "observer", "non_member"),
    "penal_code.exists": ("yes", "no", "unknown"),
    "domestic_genocide.status": ("criminalized", "partial", "no", "unknown"),
    "domestic_genocide.follows_convention_definition": ("yes", "broader", "narrower", "unknown"),
    "genocide_convention.consent_type": ("ratification", "accession", "succession"),
    "genocide_convention.reservations": ("yes", "no"),
    "max_penalty.type": ("years", "life", "death", "unknown"),
    "max_penalty.applies_to_genocide": ("yes", "no", "unknown"),
    "death_penalty.status": (
        "abolitionist_all_crimes",
        "abolitionist_ordinary_crimes",
        "abolitionist_in_practice",
        "retentionist",
    ),
    # situations
    "countries.role": _ROLE,
    "statuses.code": _TAXONOMY,
    "statuses.outcome": _OUTCOME,
    # news and decisions
    "channel": ("gdelt", "rss", "listing"),
    "level": ("0", "1", "2", "3"),
    "court": (
        "icj",
        "icc",
        "irmct",
        "icty",
        "ictr",
        "eccc",
        "rscsl",
        "ksc",
        "iacthr",
        "echr",
        "afchpr",
        "national",
    ),
    "case.parties.role": _ROLE,
    "act_type": (
        "application",
        "provisional_measures_order",
        "incidental_decision",
        "merits_judgment",
        "advisory_opinion",
        "arrest_warrant",
        "confirmation_of_charges",
        "conviction",
        "acquittal",
        "appeal",
        "procedural_step",
        "press_release",
    ),
    "taxonomy_status": _TAXONOMY,
    "outcome": _OUTCOME,
    # sources
    "function": ("1", "2", "3"),
    "api": ("yes", "no"),
    "state": ("active", "suspended", "discarded"),
}

# Locales active in the MVP (docs/03-modelo-de-dados.md, "Várias línguas").
LOCALES: tuple[str, ...] = ("en", "pt-BR")


def value_keys() -> list[str]:
    """Every "<field>.<value>" key that needs a label."""
    return [f"{field}.{value}" for field, values in VOCABULARIES.items() for value in values]
