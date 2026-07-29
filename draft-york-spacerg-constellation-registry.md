---
title: "A Registry of Announced, Filed and Deployed Satellite Constellations"
abbrev: "Constellation Registry"
category: info
docname: draft-york-spacerg-constellation-registry-latest
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

# TODO: authorship is provisional pending Dan York's agreement. The survey
# this draft is built on is his; the registry and the analysis below are the
# follow-up the chairs proposed at IETF 126. Draft name and docname change to
# draft-york-* on confirmation.
author:
 -
    fullname: "Dan York"
    organization: Internet Society
    email: "york@isoc.org"
 -
    fullname: "Juan A. Fraire"
    organization: Inria
    email: "juan.fraire@inria.fr"

normative:

informative:
  I-D.piraux-space-constellation-code:
  I-D.sastry-spacerg-space-research-infra-typology:
  REGISTRY:
    title: "SPACERG Satellite Constellation Registry"
    target: https://irtf-spacerg.github.io/id-leo-constellations/registry/
    date: 2026

--- abstract

Aggregate figures for the number of satellites "planned" for low Earth orbit
now exceed two million. Those figures combine four quantities that are not
comparable: satellites in orbit, satellites a national regulator has
authorised, satellites applied for but not granted, and satellites merely
announced. For a single system these differ by orders of magnitude.

This document describes a community-maintained registry that keeps the four
apart and requires every number to carry a citation and an evidence grade. It
reports what the resulting data shows: across the systems recorded so far,
under one per cent of the satellites described as planned are in orbit, and
around one and a half per cent stand behind a national authorisation. The rest
sit in ungranted applications and in early-stage ITU filings that confer no
deployment obligation.

--- middle

# Introduction

At IETF 126 the SPACE Research Group heard a survey of satellite
constellations that are launched, filed or announced, arriving at an aggregate
above 2.3 million planned satellites. In discussion, participants asked how
much of that total is real. The honest answer was that the question could not
be settled from the sources available, because those sources do not
distinguish between very different kinds of claim.

This document and its registry {{REGISTRY}} are the follow-up. The registry is
not a market forecast and makes no prediction about what will fly. It is a
research resource: it records what has been filed, by whom, with which
regulator, at what stage, and it makes every number traceable to a document.

## The four numbers problem

Press coverage, and much of the research literature that draws on it, reports
these four quantities interchangeably:

* how many satellites have been **launched**;
* how many a regulator has **licensed**;
* how many have been **filed** for and not granted;
* how many have merely been **announced**.

Starlink is a worked example. As of January 2026 the FCC has authorised 4,408
first-generation and 15,000 second-generation satellites, 19,408 in total,
having expressly deferred action on the remaining 14,988 of the 29,988 Gen2
satellites requested; a further 100,000 third-generation satellites were
applied for in July 2026 and not granted. A single column labelled "planned"
cannot carry that, and which number a reader takes changes any conclusion
about topology scale by a factor of five.

## Why a filing is not a plan

A filing is a claim on spectrum priority. It is not a commitment to deploy,
and the mechanisms that do create commitment are national rather than
international. The FCC requires 50 per cent deployment within six years of
grant and 100 per cent within nine, backed by a surety bond, with the
authorisation reduced to the number actually in orbit on failure. The ITU
process has no equivalent: an advance publication costs an administration
almost nothing and confers no coordination priority at all.

This asymmetry is why aggregates that sum across jurisdictions and stages are
adding quantities that do not mean the same thing.

# What the data shows

Each record in the registry is placed at the strongest rung of regulatory
commitment it has demonstrably reached. Over the {{RECORDS}} records
collected so far:

| Rung | Satellites | Records |
|:-----|-----------:|--------:|
| In orbit | 14,585 | 12 |
| Authorised by a national regulator | 10,818 | 6 |
| Applied for, not granted | 1,360,800 | 7 |
| ITU coordination request only | 6,080 | 1 |
| ITU advance publication only | 203,428 | 3 |
| Announced, no filing found | 5,408 | 2 |
{: #ladder title="Satellite counts by regulatory commitment, July 2026"}

Roughly 1.63 million satellites are described as planned across these records.
Under one per cent are in orbit. About one and a half per cent stand behind a
national authorisation with milestones attached. Eighty-three per cent sit in
applications no regulator has granted, dominated by a single application for
up to one million orbital data centre satellites. A further twelve per cent
sit at the weakest ITU stage.

These are floors, not estimates: a record whose count could not be sourced
contributes zero. The table regenerates from the data as records improve.

TODO: the analysis is currently a snapshot. Decide whether the draft carries
numbers inline, as here, or points at the registry's generated export.

# Evidence grading

Every field that asserts a fact carries a pointer to a source, and every
source carries a grade fixed by its kind rather than chosen by the
contributor.

Primary sources are the filing or the regulator's own act: ITU records, FCC
orders and applications, other national regulators' dockets, and operator
technical documentation submitted to a regulator. Secondary sources are
everything else, including operators' own web pages and press releases, trade
press, trackers, encyclopaedias and conference slides. Secondary sources are
permitted and are often all that exists, but they are marked, and they may not
stand in for a filing that exists and has not been read.

The failure mode this is designed against is ordinary and hard to see: a
number originating in a press release is quoted by a tracker, the tracker is
cited by an encyclopaedia, the encyclopaedia is cited by a paper, and the
figure arrives in the literature indistinguishable from a licensed one.

# Observations on the ITU record

The ITU Space Network List and the BR IFIC publications are public and
queryable without an account, and appear to be little used outside the
regulatory community. Reading them directly produced four observations that
bear on how aggregate figures should be interpreted.

**Stage is not a detail.** The same network can declare very different
satellite counts at different stages. Guowang's GW-2 network declares a
reported 6,912 satellites in its coordination request and 1,728 in the
notification filed five years later.

**Declarations are envelopes.** The Globalstar C-3 system is described by the
FCC as 48 satellites licensed by France. The ITU filing that backs it,
AST-NG-C-3, declares 6,221 satellites across 401 orbital planes: a ratio of
about 130 to 1 between the international declaration and the operational plan,
on one instrument.

**The notifying administration is often not the operator's country.** The ITU
networks carrying Starlink are notified by Norway. Any jurisdiction tally
built from ITU data alone attributes the largest constellation in orbit to
Norway rather than to the United States.

**Withdrawals are visible only in the ITU record.** In December 2025 the
Russian administration suppressed both the advance publication and the
coordination request for two of the three Rassvet networks, three weeks before
the system's first production launch. No secondary source consulted mentions
it.

TODO: quantify the declaration-to-plan ratio across more systems. One case is
an anecdote; a distribution would be a result.

# Relationship to other SPACE RG work

The registry complements the tools and infrastructure typology of
{{I-D.sastry-spacerg-space-research-infra-typology}}: that work catalogues
what researchers can experiment with, this one what is being built. Both use
the same contribution model.

Where a system's geometry is known, each orbital shell carries the notation of
{{I-D.piraux-space-constellation-code}}, so the registry is directly
consumable by tools that accept it. Encoding real filings surfaced limits in
that notation, recorded in the affected records and summarised for that
draft's authors: the mandatory phasing factor is essentially never present in
a filing; modern authorisations describe envelopes rather than fixed Walker
shells; filings state elliptical orbits where the code assumes circular ones;
and sun-synchronous local time, repeating ground tracks and formation flying
have no representation at all.

# Open questions

TODO: this section is for the group, and is deliberately unfinished.

* Should the registry record ITU-declared and nationally authorised figures as
  separate quantities everywhere, rather than only where both are known?
* How should publicly procured systems be handled? IRIS2 has no spectrum
  licence of its own; its defining instrument is a concession contract.
* What is the right treatment of systems with no public filing at all, such as
  classified government constellations?
* Can the declaration-to-plan ratio be estimated well enough to correct
  aggregate figures, or only to discredit them?

# Contributing

The registry is one YAML file per authorisation, contributed by pull request,
with a validator that enforces the provenance rules described above. Field
reference, taxonomy and inclusion criteria are in the repository. The most
valuable contribution is a provenance upgrade: taking a record that rests on a
press report, reading the filing it refers to, and replacing the source.

# Security Considerations

This document describes a registry of public information about satellite
systems and introduces no protocol mechanisms.

# IANA Considerations

This document has no IANA actions.

--- back

# Acknowledgments
{:numbered="false"}

This work grew out of the talk "Beyond Starlink: Understanding the Coming
Waves of LEO Satellite Deployments" presented at IETF 126 in Vienna, and the
discussion that followed it in the SPACE Research Group.

TODO: acknowledge IETF 126 discussion participants by name once the list is
confirmed from the minutes.
