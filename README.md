<!-- regenerate: off -->

# A Registry of Announced, Filed and Deployed Satellite Constellations

This is the working area for the individual Internet-Draft, "A Registry of
Announced, Filed and Deployed Satellite Constellations", and for the SPACERG
constellation registry that backs it.

* [Editor's Copy](https://irtf-spacerg.github.io/id-leo-constellations/#go.draft-york-spacerg-constellation-registry.html)
* Authorship of the draft is provisional pending Dan York's agreement.
* [Datatracker Page](https://datatracker.ietf.org/doc/draft-york-spacerg-constellation-registry)
* [Registry page](https://irtf-spacerg.github.io/id-leo-constellations/registry/)

## What this is

At IETF 126 in Vienna, Dan York surveyed the constellations that are launched,
filed or announced and arrived at an aggregate of more than 2.3 million
planned satellites. In the discussion that followed, the chairs proposed
turning that survey into a shared group resource rather than having everyone
rebuild it independently. This registry is that resource.

It is **not a market forecast**. Nobody here is predicting how many of these
satellites will fly. It is a research resource that lets people reason about
plausible future topology scale, spectrum contention and governance load with
provenance they can check.

Concretely, it exists to fix one failure mode. Four different quantities get
reported interchangeably as "planned satellites":

* how many have been **launched**,
* how many a regulator has actually **licensed**,
* how many have been **filed** for and not granted, and
* how many have merely been **announced**.

For the same system these differ by an order of magnitude, and the difference
is the whole story. Starlink is licensed for 19,408 satellites and has applied
for roughly 115,000 more. A filing is a claim on spectrum priority, not a
commitment to deploy, and the largest numbers in circulation are filings.

So every number in this registry carries a pointer to the document it came
from and a grade saying what kind of document that is. Primary means the ITU
record, the FCC order, the national regulator's docket or the operator's
technical submission. Secondary means trade press, trackers, encyclopaedias
and conference slides, which are allowed, and marked, and never allowed to
stand in silently for a filing that exists.

## What it is for

* **Topology scale.** Researchers building simulators and routing protocols
  need defensible upper and lower bounds on constellation size, and the
  distinction between what is licensed and what is filed is precisely the
  distinction between a plausible bound and an implausible one.
* **Spectrum and coordination load.** Bands, jurisdictions, filing
  administrations and processing rounds, in a form you can query.
* **Governance.** The ITU mechanism was designed for a regime of roughly
  1,800 GEO slots and a handful of launches a year. Reasoning about whether it
  fits a regime of millions of filed satellites requires knowing what has
  actually been filed, by whom, and under which administration.
* **Feasibility.** Regulatory milestone dates and demonstrated launch cadence
  are recorded side by side, so the reader can do the arithmetic that the
  press release does not.

## One record, one authorisation

A record is an authorisation, not a company. Starlink Gen1, Gen2 and Gen3 are
three files, each anchored on a `filing:` block naming one file number and
call sign, so a reader checking a number has exactly one document to open.
Modifications, waivers and partial grants of the same authorisation are dated
events inside that record. Records group by `family:` for roll-up.

`counts.filed` is cumulative of everything requested under that filing,
whatever the outcome, which makes it the prospective number: what operators
want to put up. `counts.licensed` is a subset of it. Summing `filed` across
non-superseded records therefore gives a defensible "applied for" total with
no double counting, which the build writes to
`public/data/aggregates.json`.

Systems with genuinely no public filing, such as classified government
constellations, carry `filing_absent:` with a written justification instead.
That is a real category and the registry states it rather than leaving the
field blank.

## Registry

The registry lives under [`data/constellations/`](data/constellations/), one
YAML file per authorisation, and is published as a searchable page together
with JSON and CSV exports. To add or correct an entry, open a pull request starting from
[`data/TEMPLATE.yaml`](data/TEMPLATE.yaml). See
[data/README.md](data/README.md) for the field reference, the taxonomy, the
evidence-grading rules and the inclusion criteria.

Corrections are as welcome as additions, and *provenance upgrades are the most
welcome contribution of all*: taking a record that rests on a press report,
reading the filing it refers to, and replacing the secondary source with the
primary one. Records that need this carry a line beginning `Provenance gap:`
in their `notes`.

Two public ITU sources make this possible outside the United States: the Space
Network List, for the filing history, and the BR IFIC publications, which
carry the declared satellite counts and orbital geometry.
[`scripts/itu_query.sh`](scripts/itu_query.sh) queries both, and
[data/README.md](data/README.md) explains how to read them without
misinterpreting the stage.

To build and validate locally:

```sh
$ make registry-check    # validate only (what CI runs)
$ make registry-site     # validate and write public/
$ make registry-serve    # build and serve on http://localhost:8000
$ make registry-analyse  # satellite counts stratified by regulatory stage
```

Registry targets are prefixed because `make` on its own builds the
Internet-Draft through [i-d-template](https://github.com/martinthomson/i-d-template),
which defines its own `check`. Run `make setup` once, in a git checkout, to
fetch `lib/`.

CI enforces more than the shape of the file. It checks that every `src:`
resolves to a declared source, that no count is stated without one, that a
source's grade is consistent with its kind (you cannot mark SpaceNews as
primary), that `breakdown:` values sum to their parent, that
`satellites == planes * sats_per_plane`, and that every constellation code
parses against the ABNF in
[draft-piraux-space-constellation-code](https://datatracker.ietf.org/doc/draft-piraux-space-constellation-code/)
and agrees with the shell's own fields.

## What the registry says so far

`make registry-analyse` sorts every record into the strongest rung of
regulatory commitment it has demonstrably reached. As of July 2026, over 31
records:

| Rung | Satellites | Records |
|---|---:|---:|
| In orbit | 14,585 | 12 |
| Authorised by a national regulator | 10,818 | 6 |
| Applied for, not granted | 1,360,800 | 7 |
| ITU coordination request only | 6,080 | 1 |
| ITU advance publication only | 203,428 | 3 |
| Announced, no filing found | 5,408 | 2 |

Roughly 1.6 million satellites are described as planned across these records.
Fewer than one per cent are in orbit. About one and a half per cent stand
behind a national authorisation with milestones and a bond attached. Eighty-
three per cent sit in applications that no regulator has granted, and a
further twelve per cent at the weakest ITU stage, advance publication, which
confers no coordination priority and costs an administration almost nothing to
file.

That is not a prediction about what will fly. It is a statement about what
kind of evidence the headline numbers rest on, and it is the single most
useful thing this registry produces. Every figure in the table is traceable to
a document through the record it came from.

## Cross-link to the constellation code

Where a system's geometry is known, each shell carries the
`draft-piraux-space-constellation-code` string for it, so the registry is
directly consumable by Constellationlab and the Contact Plan Designer. Each
code also carries a `code_status` recording how much of it came from the
filing and how much was assumed.

Running real filings through the notation has already produced feedback for
that draft, recorded in the affected records:

1. **The phasing factor is mandatory in the ABNF and is essentially never in a
   filing.** Every code in this registry that is grounded in a primary source
   is therefore `assumed-phasing`, with the assumed F cited to the literature.
   A syntax for "phasing unknown" would let the code be emitted from primary
   sources without laundering a guess into it. Until there is one, the
   registry does the next best thing: any code that is not `exact` must carry
   `code_assumptions:`, naming each element that did not come from the filing
   and why it was chosen. A consumer gets the string *and* the ability to
   argue with it.
2. **Modern authorisations describe envelopes, not Walker shells.** The
   January 2026 Starlink Gen2 order authorises up to 72 planes of up to 144
   satellites each in five shells, up to 56 planes of up to 120 in two more,
   and explicitly permits redistributing satellites across authorised shells.
   There is no (T, P, F) triple; there is a feasible set.
3. **Filings state elliptical orbits, the code assumes circular ones.**
   Apogee and perigee are given separately, with a station-keeping tolerance
   and often a deployment altitude distinct from the operational one. All five
   of AST SpaceMobile's authorised shells are elliptical.
4. **The divisibility requirement does not survive contact with filings.**
   The code requires satellites to divide evenly among planes; AST is
   authorised for 22 satellites in 6 planes.
5. **Sub-shells sharing altitude and inclination cannot be distinguished.**
   Starlink Gen1 has two 560 km / 97.6 deg groups (6x58 and 4x43). Joining
   them with `+` loses the fact that they are one physical shell.
6. **Sun-synchronous and dawn-dusk orbits have no representation.** Five
   filings here specify a local time of the ascending node. For orbital data
   centres this is not a detail: dawn-dusk is chosen to maximise solar
   exposure, so the unrepresentable parameter is the design's whole point.
7. **Repeating ground tracks, and ranges instead of values.** SpinLaunch
   selects altitude and inclination jointly for ground-track repetition, a
   constraint the code cannot state. Several filings give altitude and
   per-plane population as ranges rather than values.

Nine of the twenty records currently carry at least one shell marked
`not-representable`. That is a result about the notation, produced by trying
to use it, and it is one of the reasons the registry is worth keeping.

## Contributing

Open a pull request that adds or edits a single file under
`data/constellations/`. If you can only reach a secondary source, say so and
grade it honestly: an entry marked secondary is useful, and an entry with an
empty field is honest. An entry with a laundered number is worse than no entry
at all.
