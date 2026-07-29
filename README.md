<!-- regenerate: off -->

# A Registry of Announced, Filed and Deployed Satellite Constellations

Working area for the individual Internet-Draft of the same name, and for the
SPACERG constellation registry that backs it.

* [Registry page](https://irtf-spacerg.github.io/id-leo-constellations/registry/)
* [Editor's Copy](https://irtf-spacerg.github.io/id-leo-constellations/#go.draft-york-spacerg-constellation-registry.html)
* [Datatracker Page](https://datatracker.ietf.org/doc/draft-york-spacerg-constellation-registry)
* Authorship of the draft is provisional pending Dan York's agreement.

## What this is

At IETF 126 in Vienna, Dan York surveyed the constellations that are launched,
filed or announced and arrived at an aggregate above 2.3 million planned
satellites. The chairs proposed turning that survey into a shared group
resource rather than having everyone rebuild it. This registry is that
resource.

It is **not a market forecast**. It is a research resource for reasoning about
plausible topology scale, spectrum contention and governance load with
provenance you can check.

It exists to fix one failure mode. Four different quantities get reported
interchangeably as "planned satellites": how many have been **launched**, how
many a regulator has **licensed**, how many have been **filed** for, and how
many have merely been **announced**. For the same system these differ by
orders of magnitude. Starlink is licensed for 19,408 satellites and has
applied for roughly 115,000 more.

So every number here carries a pointer to the document it came from and a
grade saying what kind of document that is. Primary means an ITU record, an
FCC order, a national regulator's docket or an operator's technical
submission. Secondary means trade press, trackers, encyclopaedias and
conference slides: allowed, marked, and never permitted to stand in silently
for a filing that exists.

## What the registry says so far

`make registry-analyse` sorts each record into the strongest rung of
regulatory commitment it has demonstrably reached:

| Rung | Satellites | Records |
|---|---:|---:|
| In orbit | 14,585 | 12 |
| Authorised by a national regulator | 10,818 | 6 |
| Applied for, not granted | 1,360,800 | 7 |
| ITU coordination request only | 6,080 | 1 |
| ITU advance publication only | 206,092 | 4 |
| Announced, no filing found | 5,408 | 2 |

Of roughly 1.64 million satellites described as planned, under one per cent
are in orbit and about two per cent are covered by a national licence with
milestones and a bond behind it. Eighty-three per cent sit in applications no
regulator has granted, and a further thirteen per cent at the weakest ITU
stage, advance publication, which confers no coordination priority and costs
an administration almost nothing to file.

That is not a prediction about what will fly. It is a statement about what
kind of evidence the headline numbers rest on, and every figure traces to a
document through the record it came from. Counts are floors: a record whose
count could not be sourced contributes zero.

## How this was compiled

The initial data set was compiled with assistance from an AI coding assistant
(Anthropic's Claude), working under the direction of the maintainers. It was
used to read regulatory filings, query the ITU Space Network List and BR IFIC
publications, draft the records, and write the validator and the site build.

This is disclosed for the same reason the registry grades its sources: a
reader should be able to judge how much weight to put on a number, and that
judgement depends on knowing where it came from.

Every primary source cited was retrieved and read, and the tooling that
reached the harder ones is in the repository so the work can be repeated
rather than trusted. [`scripts/itu_query.sh`](scripts/itu_query.sh)
reproduces the ITU lookups; [`scripts/analyse.py`](scripts/analyse.py)
regenerates the table above. Where something could not be verified, the record
says so in a `Provenance gap:` line rather than filling the gap with something
that reads well.

That makes the data checkable, which is the most any registry can offer.
Corrections are welcome as pull requests.

## How records work

A record is an **authorisation, not a company**. Starlink Gen1, Gen2 and Gen3
are three files, each anchored on a `filing:` block naming one file number and
call sign, so a reader checking a number has exactly one document to open.
Modifications, waivers and partial grants of the same authorisation are dated
events inside that record. Records group by `family:` for roll-up. Systems
with genuinely no public filing, such as classified government
constellations, carry `filing_absent:` with a written justification.

`counts.filed` is cumulative of everything requested under a filing, whatever
the outcome, so it is the prospective number and `counts.licensed` is a subset
of it. Summing `filed` across non-superseded records gives an "applied for"
total with no double counting, written to `public/data/aggregates.json`.

Full field reference, taxonomy, evidence-grading rules and inclusion criteria:
[data/README.md](data/README.md).

## Building and contributing

Records live in [`data/constellations/`](data/constellations/), one YAML file
per authorisation. To add or correct one, open a pull request starting from
[`data/TEMPLATE.yaml`](data/TEMPLATE.yaml).

```sh
$ make registry-check    # validate only (what CI runs)
$ make registry-site     # validate and write public/
$ make registry-serve    # build and serve on http://localhost:8000
$ make registry-analyse  # counts stratified by regulatory stage
```

Registry targets are prefixed because `make` alone builds the Internet-Draft
through [i-d-template](https://github.com/martinthomson/i-d-template), which
defines its own `check`. Run `make setup` once, in a git checkout, to fetch
`lib/`.

CI enforces provenance, not just shape: every `src:` must resolve to a
declared source, no count may be stated without one, a source's grade must
match its kind (you cannot mark SpaceNews as primary), `breakdown:` values
must sum to their parent, `satellites` must equal `planes * sats_per_plane`,
and every constellation code must parse and agree with its shell's fields.

**Provenance upgrades are the most welcome contribution**: taking a record
that rests on a press report, reading the filing it refers to, and replacing
the source. Records needing one carry a `Provenance gap:` line. Two public ITU
sources make this possible outside the United States, the Space Network List
for filing history and the BR IFIC publications for declared counts and
geometry; `scripts/itu_query.sh` queries both.

## Cross-link to the constellation code

Where geometry is known, each shell carries the notation of
[draft-piraux-space-constellation-code](https://datatracker.ietf.org/doc/draft-piraux-space-constellation-code/),
plus a `code_status` recording how much came from the filing and
`code_assumptions:` naming anything that did not. A consumer gets the string
*and* the ability to argue with it.

Encoding real filings surfaced limits in the notation, recorded in the
affected records and summarised for that draft's authors:

1. The mandatory phasing factor is essentially never in a filing, so every
   primary-sourced code here is `assumed-phasing`.
2. Modern authorisations describe **envelopes**, not fixed Walker shells:
   Starlink Gen2 allows up to 72 planes of up to 144 satellites plus
   redistribution between shells. There is no (T, P, F) triple.
3. Filings state **elliptical** orbits with station-keeping tolerances; the
   code assumes a single circular altitude.
4. The divisibility requirement fails in practice: AST is authorised for 22
   satellites in 6 planes.
5. Sub-shells sharing altitude and inclination cannot be distinguished.
6. Sun-synchronous local time, repeating ground tracks and formation flying
   have no representation at all.

Thirteen of the current records carry at least one shell marked
`not-representable`. That is a result about the notation, produced by trying
to use it.
