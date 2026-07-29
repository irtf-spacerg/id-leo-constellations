# Registry data: field reference and inclusion criteria

One YAML file per constellation under `data/constellations/`. The registry
page and the JSON/CSV exports are built from these files by
`scripts/build_site.py`. Start from [`TEMPLATE.yaml`](TEMPLATE.yaml).

The organising principle of this registry is that **every number carries a
pointer and a grade**. A record with three well-sourced fields is more useful
than a record with thirty unsourced ones. An empty field is better than a
laundered one.

## Contents

- [The one rule](#the-one-rule)
- [One record, one authorisation](#one-record-one-authorisation)
- [Inclusion criteria](#inclusion-criteria)
- [Record structure](#record-structure)
- [Identity block](#identity-block)
- [Filing block](#filing-block)
- [Counts block](#counts-block)
- [Regulatory block](#regulatory-block)
- [Shells block and constellation codes](#shells-block-and-constellation-codes)
- [Technical block](#technical-block)
- [Deployment block](#deployment-block)
- [Sources block and evidence grading](#sources-block-and-evidence-grading)
- [Discrepancies block](#discrepancies-block)
- [Housekeeping](#housekeeping)

## The one rule

Any field that asserts a fact about the world carries a `src:` key naming an
entry in the record's own `sources:` list. CI rejects a record where a `src:`
does not resolve, and rejects a `counts:` entry with no `src:` at all. This is
the single mechanism that keeps the registry honest: you cannot state a
satellite count without saying where you got it and what kind of thing that
source is.

## One record, one authorisation

**A record is an authorisation, not a company and not a brand.** Starlink Gen1,
Gen2 and Gen3 are three records; Amazon Leo Gen1 and the 2021 V-band round
grant are two. Each one anchors on a single concrete filing reference in its
[`filing:`](#filing-block) block, so that a reader who wants to check a number
has exactly one document to open.

What is *not* a separate record: modifications, amendments, waivers, partial
grants and public notices that act on the same authorisation. Those are dated
events inside that record's `regulatory:` list. A modification changes the
numbers in an existing licence; it does not create a new system.

Records are grouped for roll-up by **`family:`**, a slug shared by every record
belonging to the same commercial system (`starlink`, `amazon-leo`,
`spacex-orbital-compute`). Family is what lets the site present an operator
view without the data model pretending that one licence is one company.

Where one record's authorisation replaces another's, link them with
`supersedes:` and `superseded_by:`, both lists of record slugs. CI checks that
they resolve. Aggregation excludes any record with a non-empty
`superseded_by:`, which is how the registry avoids counting a system twice
when a replacement licence is granted.

## Inclusion criteria

An entry should be:

1. **a satellite constellation or orbital system of ten or more spacecraft**
   that is operational, deploying, licensed, filed with a regulator, or
   publicly announced by an identifiable operator. Orbital data centres and
   compute constellations count: they occupy orbital shells, consume spectrum
   and generate coordination load exactly as communication constellations do;
2. **traceable**: at minimum one citable source with a stable URL. A
   constellation that exists only as an unattributed figure in a slide deck
   does not get a record; it gets an issue asking for a pointer;
3. **anchored**: a record either names the authorisation it is about in its
   `filing:` block, or states in `filing_absent:` why no public filing
   reference exists. Classified government systems and pre-filing
   announcements are legitimately in the second category; silence is not.

**Scope: Internet-related systems.** The registry follows the scope of the
IETF 126 survey it grew from. Dan York set that scope explicitly: LEO
constellations providing Internet access, or Internet-related services such as
orbital data centres. Constellations flown for imaging, remote sensing,
navigation, or as pure IoT or sensor networks are out of scope, even though
general trackers such as Jonathan McDowell's tables include them. This is why
the registry's totals are smaller than those trackers' and should not be
compared with them without saying so.

The boundary is not always clean. Direct-to-device systems carrying messaging
and IoT alongside voice are in scope because the service is connectivity.
A constellation whose only purpose is Earth observation is not, even if it
downlinks over the same bands. When in doubt, record it and say why in
`notes:`.

Cancelled and defunct systems stay in the registry with `status: cancelled` or
`status: retired`. The point of the registry is partly historical: the ratio
of announced to flown is itself a research result.

## Record structure

A record is a YAML mapping with these top-level keys. Everything except
`name`, `operator`, `status`, `sources` and `verified` is optional.

```
name              slug            family          aka
operator          parent          country         jurisdiction
system_class      status          status_detail   status_asof
services          orbit_regimes   dual_use        filing
filing_absent     supersedes      superseded_by   counts
regulatory        itu             shells          constellation_code
constellation_code_status         spectrum        spectrum_detail
isl               isl_detail      sat_mass_kg     first_launch
service_start     target_completion               target_completion_kind
launch            sources         discrepancies   notes
added             verified        contributor
```

Required: `name`, `slug`, `family`, `operator`, `status`, `sources`,
`verified`, and either `filing` or `filing_absent`.

## Identity block

| Field | Type | Notes |
|---|---|---|
| `name` | string | Name of *this authorisation*, qualified where a family has several: `Starlink Gen2`, not `Starlink`. Required. |
| `slug` | string | Must equal the filename stem. Lowercase, `[a-z0-9-]`. |
| `family` | slug | Groups records belonging to one commercial system for roll-up. Required. |
| `aka` | list | Alternative names, transliterations, programme names, former names. Searchable. |
| `operator` | string | The **licensee**, i.e. the legal entity named on the authorisation, not the marketing name. `Space Exploration Holdings, LLC`, not `SpaceX`. |
| `parent` | string | Parent company or controlling body, with ownership note if relevant. |
| `country` | string | ISO 3166-1 alpha-2 of the operator's home jurisdiction. |
| `jurisdiction` | list | ISO 3166-1 alpha-2 codes of the administration(s) that licensed or filed on the system's behalf. Often equal to `country`, but not always (flag-of-convenience filings are a real phenomenon and worth being able to query). |
| `system_class` | enum | See below. |
| `status` | enum | See below. Required. |
| `status_detail` | string | One line of prose justifying the status value. |
| `status_asof` | date | When the status was last assessed. |
| `services` | list | See below. |
| `orbit_regimes` | list | `VLEO`, `LEO`, `MEO`, `GEO`, `HEO`, `cislunar`. Multi-orbit systems (IRIS², Blue Origin TeraWave) list several. |
| `dual_use` | enum | `civil`, `military`, `dual`, `unknown`. Recorded because it changes which regulator holds the file and how much of it is public. |

**`system_class`** — one of:

`broadband` · `direct-to-device` · `iot-m2m` · `backhaul-trunking` ·
`orbital-compute` · `earth-observation` · `navigation` ·
`government-military` · `relay-data-transport` · `technology-demo` · `other`

**`status`** — a ladder of commitment, from most to least. Pick the *highest*
rung the system has demonstrably reached, and justify it in `status_detail`:

| Value | Means |
|---|---|
| `operational` | Providing service to end users beyond a test population. |
| `deploying` | Production satellites launching at rate; service partial, regional or in beta. |
| `demonstrator` | Only prototype, pathfinder or test articles in orbit. |
| `licensed` | A regulator has granted authority; nothing operational is in orbit yet. |
| `filed` | An application or ITU filing is on record; no grant. **A filing is a claim on spectrum priority, not a commitment to deploy.** |
| `announced` | Public statement by an identifiable operator; no traceable filing found. |
| `dormant` | Was deploying or operational; no launches or filings for 24+ months. |
| `cancelled` | Publicly abandoned, licence surrendered, or licence terminated. |
| `retired` | Deliberately deorbited or superseded after a service life. |

The `filed` / `licensed` distinction is the single most important axis in this
registry. The largest numbers in circulation, including most of the mass in
the widely quoted 2.3 million aggregate, sit at `filed` or below.

**`services`** — one or more of:

`broadband` · `direct-to-device` · `iot` · `backhaul` · `orbital-compute` ·
`government-secure` · `military` · `voice` · `messaging` · `relay` ·
`earth-observation` · `navigation` · `other`

## Filing block

The anchoring reference: the one document a reader opens to check this record.

```yaml
filing:
  authority: FCC
  administration: USA           # ITU administration code, where applicable
  file_number: SAT-LOA-20200526-00055
  call_sign: S2992/3069
  document: DA 26-36            # most recent order acting on this filing
  src: fcc-gen2-2026
```

Every record needs this, **or** a `filing_absent:` string saying why it cannot
have one:

```yaml
filing_absent: >-
  No public FCC or ITU filing identifies this system. It is procured and
  operated under classified US government contracts; satellite counts come
  from launch reporting and catalogue observation only.
```

`filing_absent` is not an escape hatch for "I did not look". It is for systems
that genuinely have no public filing: classified government constellations,
and announcements made before any application. If a filing exists and has not
been consulted, the record gets the `filing:` block it deserves and a
`Provenance gap:` line in `notes:`.

## Counts block

The failure mode this registry exists to fix. Four different numbers get
reported as "planned satellites" in press coverage, and they differ by an
order of magnitude for the same system. Keep them apart:

```yaml
counts:
  launched:   # cumulative ever launched, including deorbited and failed
    value: 12612
    asof: 2026-07
    src: mcdowell-conlist
  in_orbit:   # currently on orbit; usually smaller than `launched`
    value: 8900
    asof: 2026-07
    src: mcdowell-conlist
  licensed:   # a regulator has granted authority for this many
    value: 15000
    asof: 2026-01-09
    src: fcc-gen2-2026
    breakdown:
      - {label: 'First partial grant', value: 7500, src: fcc-gen2-2022}
      - {label: 'Second tranche', value: 7500, src: fcc-gen2-2026}
  filed:      # cumulative: everything ever requested under this filing
    value: 29988
    asof: 2022-12-01
    src: fcc-gen2-2022
  announced:  # stated publicly, no filing found that covers it
    value: 34864
    asof: 2026-07
    src: york-ietf126
```

Rules:

- Every populated count needs `value`, `asof` and `src`. CI enforces this.
- **`filed` is cumulative of everything requested under this record's filing,
  whatever the outcome.** It includes satellites that were subsequently
  granted, deferred or dismissed. It is the *intention* number, and it is
  deliberately the one that answers "how many satellites do operators want to
  put up", which is what a prospective registry is for. It follows that
  `licensed` is always a subset of `filed`; CI rejects a record where
  `licensed > filed`.
- `licensed` is what a regulator has actually granted, as of `asof`.
- `announced` is for figures with *no* regulatory correlate at all. Do not
  restate a filed figure here. An `announced` value sitting next to a smaller
  `filed` or `licensed` value is exactly the signal a reader needs.
- `breakdown:` is optional; when present its `value`s must sum to the parent
  `value`. CI checks the arithmetic.
- If you cannot source a count, omit the key. Do not write `0` for unknown.

Because `filed` is cumulative and each record is one authorisation, summing
`filed` across records gives a defensible answer to "how many satellites have
been applied for", with no double counting, as long as superseded records are
excluded. The build does that automatically and writes the totals to
`public/data/aggregates.json`.

## Regulatory block

A list, one entry per authorisation event. Every grant, modification, waiver
and pending application that changes the numbers gets an entry. This is what
makes a record auditable years later.

```yaml
regulatory:
  - authority: FCC              # see enum below
    country: US
    kind: license-grant         # application | license-grant | modification |
                                # waiver | public-notice | denial | termination
    file_number: SAT-LOA-20200526-00055
    call_sign: S2992/3069
    document: DA 26-36
    action: granted-in-part     # granted | granted-in-part | pending |
                                # deferred | dismissed | denied | withdrawn
    date: 2026-01-09
    satellites: 15000
    scope: 'Second tranche of 7,500 Gen2 satellites; total authorised 15,000'
    milestones:
      - {fraction: 0.5, count: 7500, due: 2028-12-01, status: pending}
      - {fraction: 1.0, count: 15000, due: 2031-12-01, status: pending}
    src: fcc-gen2-2026
```

**`authority`** — the national or supranational body, not the ITU:

`FCC` (US) · `Ofcom` (UK) · `ANFR` (FR) · `BNetzA` (DE) · `AGCOM` (IT) ·
`IN-SPACe` (IN) · `MIIT` (CN) · `SASTIND` (CN) · `Roskomnadzor` (RU) ·
`ACMA` (AU) · `ISED` (CA) · `MIC` (JP) · `KCC` (KR) · `ANATEL` (BR) ·
`EUSPA` (EU) · `ESA` (EU) · `NTIA` (US, federal spectrum) · `other`

Add values by PR when a new administration appears; the enum lives in
`scripts/build_site.py`.

**`milestones`** matter more than target dates in press releases. A regulatory
milestone is a hard, dated, enforceable obligation with a known consequence
for failure (in the FCC's case, reduction of the authorisation to the number
actually in orbit, plus forfeiture of the surety bond). Recording milestones
lets a reader see when a paper constellation must either fly or shrink.

## ITU block

Separate from `regulatory:` because the ITU holds filings rather than granting
licences, and because the filing identity is what establishes spectrum
priority date.

```yaml
itu:
  - administration: USA         # notifying administration, ITU 3-letter code
    network_name: STEAM-2
    stage: CR/C                 # API | CR/C | notification | in-force | expired
    date: 2020-05-26
    satellites: 29988
    src: itu-srs-steam2
    note: 'Identity not independently confirmed against SNS; see provenance gap'
```

Two public ITU sources back this block, and
[`scripts/itu_query.sh`](../scripts/itu_query.sh) queries both:

- **Space Network List (SNL) Part B** gives the filing history: notifying
  administration, stage, date of receipt and the BR IFIC each act was
  published in. Source `kind: itu-filing`.
- **BR IFIC (Space Services)** is the publication itself, distributed as an
  Access database. Its `non_geo` and `orbit` tables carry the declared
  satellite count, plane count, altitudes and inclinations. Source
  `kind: itu-publication`.

Neither needs a login. SNS Online, the interface most documentation still
points at, has been retired in favour of ITU Space Explorer.

Three things to get right when reading them:

1. **Stage is not a detail.** `API` (advance publication) is the first and
   weakest step and confers no coordination priority. `CR/C` (coordination
   request) stakes out spectrum. `notification` (Part I-S/II-S/III-S) is the
   administration declaring assignments actually to be brought into use. The
   same network can declare wildly different satellite counts at different
   stages: Guowang's GW-2 has a reported 6,912 in its coordination request and
   1,728 in its notification. Record the stage with the count, always.
2. **The notifying administration is often not the operator's country.**
   Starlink files through Norway, Globalstar's C-3 through France. A
   jurisdiction tally built from ITU data alone attributes the largest
   constellation in orbit to Norway. This is why `country` and `jurisdiction`
   are separate fields.
3. **`ssn_rev` code `S` means suppression**, a deliberate withdrawal by the
   notifying administration. Two of Russia's three Rassvet networks were
   suppressed in December 2025. Suppressions do not appear in press coverage
   at all, and they are the only public signal that a filing has been given
   up.

**Only recent BR IFICs are downloadable.** As of July 2026 the window was
roughly IFIC 3038 to 3071, about eighteen months. Older publications need the
BR IFIC DVD-ROM or a TIES account. Where a filing's last publication falls
outside the window, record the identity from SNL, leave the count secondary,
and say so in `notes:` rather than quietly falling back on press coverage.

## Shells block and constellation codes

The cross-link to
[`draft-piraux-space-constellation-code`](https://datatracker.ietf.org/doc/draft-piraux-space-constellation-code/).
Where a system's geometry is known, carry the code so the registry is directly
consumable by Constellationlab and the Contact Plan Designer.

```yaml
shells:
  - label: gen1-s1
    generation: Gen1
    status: deployed            # deployed | deploying | authorised | proposed |
                                # superseded | cancelled
    geometry_kind: walker       # walker | envelope | sso-band | irregular | unknown
    altitude_km: 550
    inclination_deg: 53.0
    planes: 72
    sats_per_plane: 22
    satellites: 1584
    walker: D                   # D (delta) | S (star) | none
    phasing: 39
    code: 'D:550:53.0:1584/72/39'
    code_status: assumed-phasing
    code_assumptions:
      - element: phasing
        value: 39
        basis: >-
          Not stated in FCC 21-48. Value used in the example table of
          draft-piraux-space-constellation-code and in the LEO networking
          literature.
        src: piraux-code-draft
    code_src: piraux-code-draft
    src: fcc-gen1-2021
```

`satellites` must equal `planes * sats_per_plane` when both are present, and
`code` must be consistent with `walker`, `altitude_km`, `inclination_deg`,
`satellites`, `planes` and `phasing`. CI checks both.

### Say what you assumed

A code derived from a filing is almost always partly assumed, and the registry
is only useful to a simulator author if it says *which part*. Any shell whose
`code_status` is `assumed-phasing` or `derived` must carry
`code_assumptions:`, a list of `{element, value, basis, src}` entries, one per
element of the code that did not come from the cited filing. CI rejects the
record otherwise.

This is the difference between a registry that hands a consumer
`D:550:53.0:1584/72/39` and one that hands them the same string plus "the 39
is ours, here is where it came from, the filing is silent". The second can be
argued with.

### Envelope authorisations

Where the authorisation bounds the geometry rather than fixing it, set
`geometry_kind: envelope`, record the bounds, and emit no code:

```yaml
  - label: gen2-lower-shells
    status: authorised
    geometry_kind: envelope
    altitude_km: 340
    inclination_deg: 53.0
    max_planes: 72
    max_sats_per_plane: 144
    code_status: not-representable
    code_note: >-
      DA 26-36 authorises up to 72 planes of up to 144 satellites in this
      shell and permits redistribution across authorised shells. There is no
      (T, P, F) triple, only a feasible set.
    src: fcc-gen2-2026
```

CI requires `max_planes` and/or `max_sats_per_plane` on an envelope shell and
forbids a `code` on one.

**`code_status`** — how much of the code came from the filing:

| Value | Means |
|---|---|
| `exact` | Every element of the code, including the phasing factor, is in the cited source. |
| `assumed-phasing` | Altitude, inclination, T and P are from the source; F is assumed or taken from the literature. Cite it in `code_src`. |
| `derived` | The code was reconstructed from partial data (e.g. plane count inferred from T and sats/plane). |
| `not-representable` | The authorised or filed geometry cannot be expressed in the code. Explain in `code_note`. |
| `unknown` | Geometry not published. |

`not-representable` is a first-class outcome and should be recorded rather
than forced. Every case below was found by trying to encode an actual filing,
and each names the record where it can be inspected:

- **Missing phasing factor.** The ABNF makes F mandatory, and it is
  essentially never in a filing. Every Walker code in this registry that is
  grounded in a primary source is `assumed-phasing`.
  (`starlink-gen1`, `iridium-next`)
- **Envelope authorisations.** Modern FCC grants authorise *up to* N planes
  with *up to* M satellites per plane, with explicit permission to
  redistribute satellites across authorised shells. There is no single
  (T, P, F) triple; there is a feasible set. (`starlink-gen2`)
- **Elliptical orbits.** Filings routinely state apogee and perigee
  separately, with a station-keeping tolerance, and sometimes a deployment
  altitude different from the operational one. The code carries a single
  circular altitude. Every one of AST SpaceMobile's five authorised shells is
  elliptical. (`ast-spacemobile`)
- **Satellites not divisible by planes.** The code requires T to be divisible
  by P. Real authorisations are not so tidy: AST is authorised for 22
  satellites in 6 planes. (`ast-spacemobile`)
- **Degenerate and extreme plane populations.** One satellite per plane, 192
  times over (`ast-spacemobile`); 300 to 1,000 satellites *per plane*
  (`blue-origin-sunrise`). Both parse, but neither is what the notation is
  designed to describe, and the second is two orders of magnitude beyond any
  operational shell here.
- **Sub-shells sharing altitude and inclination.** Starlink Gen1 has two
  distinct 560 km / 97.6° groups (6×58 and 4×43). The code can express them as
  two `+`-joined shells, but cannot say they are one physical shell
  partitioned into two plane groups. (`starlink-gen1`)
- **Sun-synchronous and dawn-dusk orbits.** The local time of the ascending
  node has no field. For orbital data centre proposals this is not a detail:
  dawn-dusk is chosen precisely to maximise solar exposure, so the
  unrepresentable parameter is the design's whole point.
  (`starcloud`, `cowboy-space-stampede`, `orbital-compute`,
  `blue-origin-sunrise`, `spacex-orbital-data-center`)
- **Repeating ground tracks.** An altitude and inclination chosen jointly so
  that passes recur over fixed points. The code records the resulting numbers
  but cannot state the constraint that produced them. (`spinlaunch-meridian`)
- **Altitude and population given as ranges.** "500 to 2,000 km", "600 to
  850 km in shells up to 50 km thick". A range is not a shell.
  (`spacex-orbital-data-center`, `starcloud`)
- **Multi-orbit systems** mixing LEO and MEO in one constellation.
  (`blue-origin-terawave`)

The record-level `constellation_code` is the `+`-join of the shell codes that
are in a `deployed`, `deploying` or `authorised` state, with
`constellation_code_status` set to the weakest `code_status` among them.
Proposed-but-unauthorised shells are excluded so that the record-level code
describes something that actually may exist.

## Technical block

| Field | Type | Notes |
|---|---|---|
| `spectrum` | list | Band letters: `L`, `S`, `C`, `X`, `Ku`, `Ka`, `Q`, `V`, `W`, `E`, `D`, `optical`. |
| `spectrum_detail` | string | Exact frequency ranges and directions where known, ideally quoting the grant. |
| `isl` | enum | `optical`, `rf`, `optical-planned`, `rf-planned`, `none`, `external`, `unknown`. `external` means the system relies on somebody else's crosslinks (several orbital data centre proposals do). |
| `isl_detail` | string | Topology, capacity, degree, vendor where known. |
| `sat_mass_kg` | number | Per-satellite dry or wet mass; say which in `notes`. Drives launch-cadence feasibility. |

## Deployment block

| Field | Type | Notes |
|---|---|---|
| `first_launch` | date | First satellite of this system, prototypes included; note in `notes` if a prototype. |
| `service_start` | date | First service to users outside the operator. |
| `target_completion` | date | With `target_completion_kind`: `regulatory-milestone` (hard, dated, enforceable) or `operator-target` (a stated intention). Never mix them. |
| `launch` | mapping | `providers:` list, `vehicles:` list, `cadence:` free text with `src`, `contracted:` number of booked launches. |

Demonstrated cadence is the field that most often contradicts a completion
date, so record it with a source and let the reader do the division.

## Sources block and evidence grading

Sources are declared once, with an id, and referenced by every claim.

```yaml
sources:
  - id: fcc-gen2-2026
    grade: primary
    kind: fcc-order
    title: 'FCC Space Bureau, Authorization and Order, DA 26-36'
    url: https://docs.fcc.gov/public/attachments/DA-26-36A1.pdf
    date: 2026-01-09
    retrieved: 2026-07-29
```

**`grade`** is `primary` or `secondary`, and it is not a free choice: it is
determined by `kind`. CI enforces the mapping.

**Primary** — the filing itself, the regulator's own act, or the operator's
technical documentation submitted to a regulator:

| `kind` | Example |
|---|---|
| `itu-filing` | ITU SNS/SRS record, API, CR/C or notification |
| `itu-publication` | BR IFIC, ITU-R circular |
| `fcc-order` | FCC or Space Bureau order, authorisation, grant stamp |
| `fcc-application` | ICFS/IBFS application, amendment, modification as filed |
| `fcc-public-notice` | Accepted-for-filing notices, processing round notices |
| `regulator-docket` | Any other national regulator's docket, licence or decision |
| `operator-technical` | Technical narrative, Schedule S, ICD, orbital debris assessment attached to a filing |
| `treaty-registry` | UN Register of Objects Launched into Outer Space |

**Secondary** — everything else. Allowed, and often the only thing available,
but it must be marked, and it must not stand in for a filing that exists:

| `kind` | Example |
|---|---|
| `operator-web` | Company website, press release, investor deck |
| `trade-press` | SpaceNews, Via Satellite, Ars Technica |
| `tracker` | Jonathan McDowell's tables, Gunter's Space Page, CelesTrak, Space-Track |
| `encyclopedia` | Wikipedia |
| `academic` | Papers, including the constellation-code draft's own literature values |
| `analyst` | Market research, consultancy reports |
| `presentation` | Conference or meeting slides, including Dan York's IETF 126 deck |

Note that `operator-web` is **secondary**. A number on a company's marketing
page is not a filing; when the two disagree, the filing wins and the
disagreement goes in `discrepancies:`.

Every source needs `url`, `retrieved` (the date somebody actually opened it),
and `date` where the source itself is dated. Prefer permanent document URLs
(`docs.fcc.gov/public/attachments/...`) over search-result or portal URLs.

**Anti-laundering rule.** If a primary source exists and is reachable, a
secondary source must not be cited for the same claim. If a primary source
exists but has not been consulted, say so in the record's `notes:` under a
`provenance gap` line so the gap is visible and PR-able.

## Discrepancies block

Where a widely circulated figure disagrees with what the filing says, record
both. This is a deliverable of the registry, not a footnote.

```yaml
discrepancies:
  - field: counts.licensed
    claim: '34,864 satellites planned'
    claimed_by: york-ietf126
    registry_value: '19,408 licensed; 34,396 licensed-or-requested'
    note: >-
      The slide's figure aggregates the Gen1 authorisation with the full Gen2
      *request* rather than the Gen2 grant. As of 2026-01-09 the FCC has
      authorised 15,000 of the 29,988 Gen2 satellites requested and expressly
      deferred the remainder.
```

`claimed_by` is a source id, so the disputed claim is itself traceable.

## Housekeeping

| Field | Notes |
|---|---|
| `notes` | Free text. Caveats, provenance gaps, acquisition activity, anything a researcher should know before using the numbers. |
| `added` | `YYYY-MM` when the record entered the registry. |
| `verified` | `YYYY-MM-DD` when a human last checked the record's sources by hand. Required. Records older than `verify_ttl_months` in `config.yaml` (default 12) are flagged stale by the build, listed in its output, and carry `stale: yes` in the exports. Staleness is a warning, never a build failure: a stale record is still data, and pretending otherwise would push contributors to bump the date without rechecking. |
| `contributor` | Name or handle, optional. |

Entries are point-in-time observations. A record says what was true when it
was `verified`, and nothing more; regulatory states move, and a stale record
that is honestly dated is far more useful than one that silently rots. If you
know better than a record, send a PR that fixes it and bumps `verified`.
