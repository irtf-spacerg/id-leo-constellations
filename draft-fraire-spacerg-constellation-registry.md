---
title: "A Registry of Announced, Filed and Deployed Satellite Constellations"
abbrev: "Constellation Registry"
category: info
docname: draft-fraire-spacerg-constellation-registry-latest
submissiontype: IRTF
number:
date:
consensus: true
v: 3
area: IRTF
workgroup: "Systems and Protocol Aspects for Circumstellar Environments"
keyword:
 - satellite constellation
 - LEO
 - spectrum filing
 - ITU
 - megaconstellation
venue:
  group: "Systems and Protocol Aspects for Circumstellar Environments"
  type: "Research Group"
  mail: "space@irtf.org"
  github: "irtf-spacerg/id-leo-constellations"

author:
 -
    fullname: "Juan A. Fraire"
    organization: Inria
    email: "juan.fraire@inria.fr"
 -
    fullname: "Dan York"
    organization: Internet Society
    email: "york@isoc.org"

normative:

informative:
  I-D.piraux-space-constellation-code:
  I-D.sastry-spacerg-space-research-infra-typology:
  REGISTRY:
    title: "SPACERG Satellite Constellation Registry"
    target: https://irtf-spacerg.github.io/id-leo-constellations/registry/
    date: 2026

--- abstract

Aggregate figures for the number of satellites planned for low Earth orbit are widely quoted and rarely traceable.
They mix quantities that are not comparable: satellites already in orbit, satellites a national regulator has authorised, satellites applied for and not yet granted, and satellites that exist only in an announcement.
For a single system these can differ by orders of magnitude.
Which one a headline figure refers to decides whether it describes infrastructure or intent.

This document describes a community-maintained registry that keeps the four apart and requires every number in it to carry a citation and an evidence grade.
It sets out the data model, the taxonomy of regulatory commitment, the rules that separate primary regulatory sources from secondary reporting, and the criteria for inclusion.

--- middle

# Introduction

Research on satellite networking rests on assumptions about scale.
How large will future constellations be, how many operators will share the spectrum, and how much coordination load will land on national regulators and on the International Telecommunication Union (ITU)?
Those assumptions usually come from press coverage and from aggregate trackers.

The problem runs deeper than careless reporting.
The quantities underneath are genuinely different, and they are all published under one label.
A constellation may have satellites in orbit, a national licence for a larger number, an application pending for a larger number still, an ITU filing declaring more again, and a press release describing something else entirely.
All five are true statements.
However, presented as a single figure for "planned satellites", four of them disappear.

This registry exists to keep them apart.
It forecasts nothing and predicts nothing about what will eventually fly.
What it records is narrower: who filed what, with which authority, at what stage of which process, and every number traceable to a document.

## The four quantities

The registry distinguishes:

* **launched**, satellites placed in orbit, cumulative and including those since deorbited;
* **licensed**, satellites a national regulator has granted authority to operate;
* **filed**, satellites requested from a regulator or declared to the ITU, whatever the outcome;
* **announced**, satellites described publicly with no filing behind them that can be found.

Keeping these four apart is the registry's main design constraint.
Most of the schema follows from it.

## Why a filing is not a plan

A filing is a claim on spectrum priority, and nothing in it obliges anyone to build.
Commitment, where it exists at all, comes from national regulators.
Some administrations attach dated deployment milestones to an authorisation, with a financial instrument behind them and a defined consequence for missing them.
The ITU process has no equivalent.
Its earliest stage, advance publication, confers no coordination priority and costs an administration very little.

# The registry

The registry is maintained in the repository that also hosts this document, and published as a searchable page with JSON and CSV exports {{REGISTRY}}.
It follows the contribution model of the SPACERG research infrastructure registry described in {{I-D.sastry-spacerg-space-research-infra-typology}}: one machine-readable record per entry, added and corrected by pull request, validated automatically on submission.

## One record, one authorisation

A record describes one authorisation.
Where an operator holds several authorisations for successive generations of a system, each gets its own record, anchored on its own filing reference, so a reader checking a number has exactly one document to open.
Modifications, amendments, waivers and partial grants acting on that same authorisation become dated events inside the record.
A family identifier lets a reader roll several records up to the operator level, without the data model having to claim that one licence equals one company.

Some systems have no public filing at all, constellations procured under classified government contracts being the obvious case.
Those records carry a written statement of why no filing reference exists.
An empty field would say the same thing far less usefully.

## Evidence grading

Every field that asserts a fact points to a source.
Every source carries a grade, and that grade follows from the kind of document it is.
Contributors do not choose it.

Primary sources are the filing itself or the regulator's own act: ITU records and publications, national regulator orders, applications and dockets, and operator technical documentation submitted to a regulator.
Secondary sources are everything else, including operators' own web pages and press releases, trade press, tracker sites, encyclopaedias and conference presentations.

Secondary sources are permitted, and for some jurisdictions they are all that exists.
What they may not do is stand in for a filing that exists and simply has not been read.
Where a primary source exists and nobody has consulted it, the record says so, so the gap stays visible and someone can close it later.

The failure mode this guards against is ordinary, and almost invisible once it has happened.
A figure originating in a press release is quoted by a tracker, the tracker is cited by an encyclopaedia, the encyclopaedia is cited by a paper, and the number arrives in the literature indistinguishable from one that was authorised.

## Regulatory commitment as a ladder

Each record sits at the strongest rung of regulatory commitment it has demonstrably reached: satellites in orbit; authorisation by a national regulator; an application pending before one; notification to the ITU; an ITU coordination request; ITU advance publication; and a public announcement with no filing identified.

The ladder is what makes an aggregate safe to publish.
Totals are given per rung, and the shape of that distribution usually says more than the sum does.

## Orbital geometry

Where a system's orbital geometry is known, each shell is recorded with the parameters given in the filing, together with the notation defined in {{I-D.piraux-space-constellation-code}} where the geometry can be expressed in it.
Each code also records how much of it came from the cited source and what was assumed, so a consumer gets the value and the grounds for it together.

Applying that notation to real filings turned out to be informative in both directions.
Several classes of authorised geometry cannot be expressed in it: orbital parameters given as ranges or as envelopes instead of fixed values; elliptical orbits with station-keeping tolerances; shells whose satellite count is not divisible by their plane count; distinct plane groups sharing an altitude and inclination; and orbits whose defining property is a sun-synchronous local time, a repeating ground track, or formation flying.
Those cases are flagged as unrepresentable.
Forcing them into a code would only misdescribe them.

## Point-in-time observations

Registry entries are observations at a date.
Regulatory states move, applications are granted in part or deferred, licences are modified, ITU filings are suppressed, and operators are acquired.
Each record therefore carries a last-verified date.
A record nobody has re-checked in a long time is flagged, so that staleness shows on the page instead of being quietly trusted.

Corrections are as welcome as additions.
The most valuable contribution is a provenance upgrade: taking a record that rests on secondary reporting, reading the filing it refers to, and replacing the source.

## Scope

The registry covers constellations providing Internet access or Internet-related services, including orbital data centres.
Systems flown for imaging, remote sensing, navigation, or purely as sensor networks are outside its scope, although general satellite trackers include them.
Totals from this registry therefore will not match a general tracker's totals, which is why the scope statement is published alongside them.

# Relationship to other SPACERG work

This registry is complementary to the research infrastructure typology and registry of {{I-D.sastry-spacerg-space-research-infra-typology}}.
That work catalogues what researchers can experiment with; this one catalogues what is being built and what has been claimed.
The two share a contribution model, a validation approach and the publication mechanics, and they are meant to be used together.

The orbital geometry recorded here is expressed, where possible, in the notation of {{I-D.piraux-space-constellation-code}}, so that entries can be consumed directly by tooling that accepts it.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Security Considerations

This document describes a registry of public information about satellite systems and introduces no protocol mechanisms.
Records are compiled from public regulatory filings and public reporting.

# IANA Considerations

This document has no IANA actions.

--- back

# Acknowledgments
{:numbered="false"}

This registry grew out of a survey of announced and filed constellations presented to the SPACE Research Group at IETF 126 in Vienna, and the discussion that followed it.

The initial data set was compiled with the assistance of an AI coding assistant, working under the direction of the maintainers.
The registry's provenance and validation rules are partly a response to that fact: every claim resolves to a declared source, grades are fixed by document type, and the automated checks reject any record that breaks either rule.
The repository documents this in full.

TODO: acknowledge IETF 126 discussion participants by name once confirmed.
