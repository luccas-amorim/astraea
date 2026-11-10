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
  "confidence.A", "level.3", "categories.court".

Besides the vocabularies, this file holds the few constants of the model that the
validator and the lexicon builder share: the languages that have a lexicon, the fields
that are localized texts, the stamp, and the order of the taxonomy.
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
    "genocide_convention.participation",
    "genocide_convention.signature",
    "genocide_convention.bound_since",
    "genocide_convention.consent_type",
    "genocide_convention.reservations",
    "genocide_convention.reservations_article_ix",
    "genocide_convention.objections",
    "genocide_convention.reservations_note",
    "rome_statute",
    "rome_statute.participation",
    "rome_statute.signature",
    "rome_statute.bound_since",
    "rome_statute.consent_type",
    "rome_statute.withdrawal",
    "rome_statute.withdrawal_notified",
    "rome_statute.objections",
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

# data/verification.json: one line says which fields of which records were read where.
VERIFICATION_FIELDS: tuple[str, ...] = (
    "entity",
    "records",
    "fields",
    "result",
    "method",
)

# Written only by scripts/transform.py, in static/data/ (never in data/).
DERIVED_FIELDS: tuple[str, ...] = (
    "completeness",
    "provenance",
    "highest_status",
    "label",
)

FIELDS: tuple[str, ...] = (
    SHARED_FIELDS
    + COUNTRY_FIELDS
    + SITUATION_FIELDS
    + NEWS_FIELDS
    + DECISION_FIELDS
    + SOURCE_FIELDS
    + VERIFICATION_FIELDS
    + DERIVED_FIELDS
)

# The fields each entity of data/ may carry (the shared ones are allowed everywhere).
ENTITY_FIELDS: dict[str, tuple[str, ...]] = {
    "countries": COUNTRY_FIELDS,
    "situations": SITUATION_FIELDS,
    "sources": SOURCE_FIELDS,
    "verification": VERIFICATION_FIELDS,
}

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
    "genocide_convention.participation": ("party", "signatory", "none"),
    "genocide_convention.consent_type": ("ratification", "accession", "succession"),
    "genocide_convention.reservations": ("yes", "no"),
    "genocide_convention.reservations_article_ix": ("yes", "no"),
    "genocide_convention.objections": ("yes", "no"),
    "rome_statute.participation": ("party", "signatory", "withdrawn", "none"),
    "rome_statute.consent_type": (
        "ratification",
        "acceptance",
        "approval",
        "accession",
        "succession",
    ),
    "rome_statute.objections": ("yes", "no"),
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
    # lexicon: the facets of a term; they travel to news.categories
    "categories": ("qualification", "instrument", "court", "procedure", "situation"),
    # sources
    "function": ("1", "2", "3"),
    "api": ("yes", "no"),
    "state": ("active", "suspended", "discarded"),
    # verification trail
    "entity": ("countries", "situations", "news", "decisions", "sources"),
    "result": ("confirmed", "corrected", "unconfirmed"),
    # derived (static/data/countries.json)
    "completeness": ("stamped", "draft", "empty"),
}

# Locales active in the MVP (docs/03-modelo-de-dados.md, "Várias línguas").
LOCALES: tuple[str, ...] = ("en", "pt-BR")

# Languages that have a lexicon in phase 1 (ISO 639-1). It follows the recommendation of
# D5 (docs/07-decisoes-pendentes.md) until the owner answers otherwise.
LEXICON_LANGUAGES: tuple[str, ...] = ("en", "fr", "es", "pt", "ar")

# Texts of ours: {"<locale>": {"text": ..., "author": ...}} (docs/03, "Várias línguas").
LOCALIZED_TEXT_FIELDS: tuple[str, ...] = (
    "note",
    "description",
    "summary",
    "title_translations",
    "validity_note",
    "genocide_convention.reservations_note",
)
# A summary is a summary, not a copy (check 8).
LIMITED_TEXT_FIELDS: tuple[str, ...] = ("description", "summary")
TEXT_LIMIT = 600

# The stamp (CONTRIBUTING.md, C1): what an asserted field carries, in the block itself or
# in a line of data/verification.json.
STAMP_FIELDS: tuple[str, ...] = ("url", "source", "read_on", "confidence", "checked_by")

# The blocks of a country and its asserted scalar fields, stamped by verification.json.
COUNTRY_BLOCKS: tuple[str, ...] = (
    "penal_code",
    "domestic_genocide",
    "genocide_convention",
    "rome_statute",
    "max_penalty",
    "death_penalty",
)
COUNTRY_STAMPED_SCALARS: tuple[str, ...] = ("name", "un_status", "un_member_since")
# Dates of a treaty block: always full (docs/03, "Data parcial").
TREATY_DATE_FIELDS: dict[str, tuple[str, ...]] = {
    "genocide_convention": ("signature", "bound_since"),
    "rome_statute": ("signature", "bound_since", "withdrawal", "withdrawal_notified"),
}

# Taxonomy, lowest to highest, for "the highest status reached". "closed" says that one
# proceeding ended; it is not a degree of the qualification, so it only shows when the
# situation has nothing else.
STATUS_ORDER: tuple[str, ...] = (
    "closed",
    "allegation",
    "political_recognition",
    "investigation",
    "accusation",
    "provisional_measures",
    "merits_decision",
)
# Statuses that only a person records (check 6).
HUMAN_ONLY_STATUSES: tuple[str, ...] = ("provisional_measures", "merits_decision")
# A verification line stamps a field only with one of these results.
STAMPING_RESULTS: tuple[str, ...] = ("confirmed", "corrected")


def value_keys() -> list[str]:
    """Every "<field>.<value>" key that needs a label."""
    return [f"{field}.{value}" for field, values in VOCABULARIES.items() for value in values]
