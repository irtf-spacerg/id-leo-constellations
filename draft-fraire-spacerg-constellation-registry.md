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
They combine quantities that are not comparable: satellites in orbit, satellites a national regulator has authorised, satellites applied for but not granted, and satellites announced without any filing at all.
For a single system these differ by orders of magnitude, and the difference determines whether a figure describes infrastructure or intent.

This document describes a community-maintained registry that keeps those quantities apart and requires every number to carry a citation and an evidence grade.
It sets out the data model, the taxonomy of regulatory commitment, the grading rules that distinguish primary regulatory sources from secondary reporting, and the criteria for inclusion.

--- middle

# Introduction

Research on satellite networking rests on assumptions about how large future constellations will be, how many operators will share the spectrum, and how much coordination load the result will place on national regulators and on the International Telecommunication Union (ITU).
Those assumptions are usually drawn from press coverage and from aggregate trackers.

The difficulty is not that such sources are careless.
It is that the underlying quantities are genuinely different and are reported under one label.
A constellation may have satellites in orbit, a national licence for a larger number, an application pending for a larger number still, an ITU filing declaring more again, and a press release describing something else entirely.
All five are true statements.
Presented as a single figure for "planned satellites", four of them disappear.

This registry exists to keep them apart.
It is not a market forecast and makes no prediction about what will be deployed.
It records what has been filed, by whom, with which authority, at what stage of which process, and it makes every number traceable to a document.

## The four quantities

The registry distinguishes:

* **launched**, satellites placed in orbit, cumulative and including those since deorbited;
* **licensed**, satellites a national regulator has granted authority to operate;
* **filed**, satellites requested from a regulator or declared to the ITU, whatever the outcome;
* **announced**, satellites described publicly with no filing behind them that can be found.

Keeping these apart is the registry's principal design constraint, and most of the schema follows from it.

## Why a filing is not a plan

A filing is a claim on spectrum priority.
It is not a commitment to deploy, and the mechanisms that create commitment are national rather than international.
Some administrations attach dated deployment milestones to an authorisation, with a financial instrument behind them and a defined consequence for failure.
The ITU process has no equivalent: the earliest stage, advance publication, confers no coordination priority and costs an administration very little.

# The registry

The registry is maintained in the repository that also hosts this document and published as a searchable page with JSON and CSV exports {{REGISTRY}}.
It follows the contribution model of the SPACERG research infrastructure registry described in {{I-D.sastry-spacerg-space-research-infra-typology}}: one machine-readable record per entry, added and corrected by pull request, and validated automatically on submission.

## One record, one authorisation

A record describes an authorisation rather than a company or a brand.
Where an operator holds several authorisations for successive generations of a system, each is a separate record anchored on its own filing reference, so that a reader checking a number has one document to open.
Modifications, amendments, waivers and partial grants acting on the same authorisation are recorded as dated events within that record.
Records carry a family identifier so that an operator-level view can be composed without the data model asserting that one licence is one company.

Systems with no public filing, such as constellations procured under classified government contracts, are recorded with an explicit statement of why no filing reference exists.
That is a substantive category rather than missing data, and stating it is more useful than leaving the field empty.

## Evidence grading

Every field that asserts a fact carries a pointer to a source, and every source carries a grade determined by the kind of document it is rather than chosen by the contributor.

Primary sources are the filing itself or the regulator's own act: ITU records and publications, national regulator orders, applications and dockets, and operator technical documentation submitted to a regulator.
Secondary sources are everything else, including operators' own web pages and press releases, trade press, tracker sites, encyclopaedias and conference presentations.

Secondary sources are permitted, and for some jurisdictions they are all that exists.
They must be marked as such, and they may not stand in for a filing that exists and has not been read.
Where a primary source exists but has not been consulted, the record says so explicitly, so that the gap is visible and can be closed by a later contribution.

The failure mode this is designed against is ordinary and difficult to see.
A figure originating in a press release is quoted by a tracker, the tracker is cited by an encyclopaedia, the encyclopaedia is cited by a paper, and the number arrives in the literature indistinguishable from one that was authorised.

## Regulatory commitment as a ladder

Each record is placed at the strongest rung of regulatory commitment it has demonstrably reached: satellites in orbit; authorisation by a national regulator; an application pending before a national regulator; notification to the ITU; an ITU coordination request; ITU advance publication; and public announcement with no filing identified.

The ladder is what allows an aggregate to be reported without collapsing the distinction it exists to preserve.
A total may be given per rung, and the shape of the distribution is more informative than its sum.

## Orbital geometry

Where a system's orbital geometry is known, each shell is recorded with the parameters given in the filing, together with the notation defined in {{I-D.piraux-space-constellation-code}} where the geometry can be expressed in it.
Each code records how much of it came from the cited source and what, if anything, was assumed, so that a consumer receives both the value and the basis for it.

Applying that notation to filings has proved informative in both directions.
Several classes of authorised geometry cannot be expressed in it: orbital parameters given as ranges or as envelopes rather than fixed values; elliptical orbits with station-keeping tolerances; shells whose satellite count is not divisible by their plane count; distinct plane groups sharing an altitude and inclination; and orbits whose defining property is a sun-synchronous local time, a repeating ground track, or formation flying.
These cases are recorded as such rather than forced.

## Point-in-time observations

Registry entries are observations at a date.
Regulatory states move, applications are granted in part or deferred, licences are modified, ITU filings are suppressed, and operators are acquired.
Each record therefore carries a last-verified date, and a record that has not been re-verified recently is flagged as such rather than silently trusted.

Corrections are as welcome as additions.
The most valuable contribution is a provenance upgrade: taking a record that rests on secondary reporting, reading the filing it refers to, and replacing the source.

## Scope

The registry covers constellations providing Internet access or Internet-related services, including orbital data centres.
Systems flown for imaging, remote sensing, navigation, or purely as sensor networks are outside its scope, although general satellite trackers include them.
Totals drawn from this registry are therefore not comparable with those trackers' totals without saying so, and the scope statement is part of what the registry publishes.

# Relationship to other SPACERG work

This registry is complementary to the research infrastructure typology and registry of {{I-D.sastry-spacerg-space-research-infra-typology}}.
That work catalogues what researchers can experiment with; this one catalogues what is being built and what has been claimed.
The two use the same contribution model, the same validation approach and the same publication mechanics, and are intended to be usable together.

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

The initial data set was compiled with assistance from an AI coding assistant working under the direction of the maintainers, and the registry's provenance and validation rules are in part a response to that: every claim resolves to a declared source, source grades are fixed by document type, and the automated checks reject records that violate either.
The repository documents this in full.

TODO: acknowledge IETF 126 discussion participants by name once confirmed.
