#!/usr/bin/env python3
"""Stratify the registry's satellite counts by regulatory commitment.

The registry exists to answer one question that aggregate figures cannot:
of the satellites described as "planned", how many stand behind a national
licence, how many behind an ITU coordination request, how many behind nothing
but an advance publication or a press release?

Every step down that ladder is a step away from commitment. This script sorts
each record into the strongest rung it has demonstrably reached and reports
the satellite counts per rung, so the shape of the aggregate is visible rather
than the total alone.

    python scripts/analyse.py            # human-readable tables
    python scripts/analyse.py --json     # machine-readable, for the draft

Counts are floors throughout, for the reason set out in data/README.md: a
record with an unrecorded count contributes zero.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "constellations"

# Strongest rung first. A record is placed in the first rung it satisfies.
RUNGS = [
    ("in_orbit", "Satellites actually in orbit"),
    ("licensed", "Authorised by a national regulator"),
    ("national_pending", "Applied to a national regulator, not granted"),
    ("itu_notified", "Notified to the ITU (Part I-S/II-S/III-S)"),
    ("itu_coordination", "ITU coordination request (CR/C) only"),
    ("itu_api", "ITU advance publication (API) only"),
    ("announced", "Announced, no filing identified"),
]
RUNG_NOTE = {
    "in_orbit": "Hardware exists and is operating.",
    "licensed": "A regulator has granted authority, with milestones and, in "
                "the FCC's case, a surety bond behind it.",
    "national_pending": "An application is on a regulator's docket. It can be "
                        "granted in part, deferred or denied, and several in "
                        "this registry already have been.",
    "itu_notified": "The administration has declared assignments to be "
                    "brought into use. The strongest ITU step.",
    "itu_coordination": "Spectrum priority is being staked out. No commitment "
                        "to deploy and no national grant identified.",
    "itu_api": "The first and weakest ITU step. Confers no coordination "
               "priority. Costs an administration almost nothing to file.",
    "announced": "A public statement with no filing behind it that this "
                 "registry could find.",
}
GRANTED = {"granted", "granted-in-part"}


def load():
    recs = []
    for path in sorted(DATA_DIR.glob("*.yaml")):
        rec = yaml.safe_load(path.read_text())
        if isinstance(rec, dict) and not rec.get("superseded_by"):
            recs.append(rec)
    return recs


def count(rec, key):
    c = (rec.get("counts") or {}).get(key) or {}
    v = c.get("value")
    return v if isinstance(v, (int, float)) else None


def itu_stages(rec):
    return {i.get("stage") for i in (rec.get("itu") or []) if isinstance(i, dict)}


def classify(rec):
    """Strongest rung a record has demonstrably reached, and the satellite
    count that belongs to that rung.

    Rung comes from the regulatory record, not from the counts: a record can
    have an application on a docket and no authorised figure, and calling that
    "announced" would understate it exactly as badly as calling a filing a
    plan overstates it.
    """
    stages = itu_stages(rec)
    acts = [a for a in (rec.get("regulatory") or []) if isinstance(a, dict)]
    lic, filed = count(rec, "licensed"), count(rec, "filed")
    ann, launched = count(rec, "announced"), count(rec, "in_orbit")
    if launched is None:
        launched = count(rec, "launched")
    best = next((v for v in (lic, filed, ann) if v is not None), None)

    if rec.get("status") in ("operational", "deploying", "demonstrator"):
        # Report what is up. The paper figure sits in the totals below; the
        # gap between the two is the point of the whole exercise.
        return "in_orbit", launched
    if any(a.get("action") in GRANTED for a in acts):
        return "licensed", (lic if lic is not None else best)
    if any(a.get("action") == "pending" for a in acts):
        return "national_pending", (filed if filed is not None else best)
    if "notification" in stages or "in-force" in stages:
        return "itu_notified", (filed if filed is not None else best)
    if "CR/C" in stages:
        return "itu_coordination", (filed if filed is not None else best)
    if "API" in stages:
        return "itu_api", (filed if filed is not None else best)
    return "announced", (ann if ann is not None else best)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    recs = load()
    buckets = {k: {"records": [], "satellites": 0, "unknown": 0}
               for k, _ in RUNGS}
    for r in recs:
        rung, n = classify(r)
        b = buckets[rung]
        b["records"].append(r["slug"])
        if n is None:
            b["unknown"] += 1
        else:
            b["satellites"] += n

    # Everything ever requested, regardless of outcome: the "planned" number
    # as press coverage would compute it.
    total_filed = sum(v for v in (count(r, "filed") for r in recs)
                      if v is not None)
    total_licensed = sum(v for v in (count(r, "licensed") for r in recs)
                         if v is not None)
    total_launched = sum(v for v in (count(r, "launched") for r in recs)
                         if v is not None)

    out = {
        "records": len(recs),
        "total_launched": total_launched,
        "total_licensed": total_licensed,
        "total_filed_or_requested": total_filed,
        "by_rung": {k: {"label": lbl, "note": RUNG_NOTE[k],
                        "records": len(buckets[k]["records"]),
                        "satellites": buckets[k]["satellites"],
                        "records_without_count": buckets[k]["unknown"],
                        "slugs": buckets[k]["records"]}
                    for k, lbl in RUNGS},
        "caveat": ("Floors, not estimates. Records with an unrecorded count "
                   "contribute zero. Superseded records excluded."),
    }
    if args.json:
        json.dump(out, sys.stdout, indent=1)
        print()
        return

    print(f"\n{len(recs)} records\n")
    print(f"{'':44}{'satellites':>12}  {'records':>7}")
    print("-" * 66)
    for k, lbl in RUNGS:
        b = buckets[k]
        unk = f"  ({b['unknown']} without a count)" if b["unknown"] else ""
        print(f"{lbl:44}{b['satellites']:>12,}  {len(b['records']):>7}{unk}")
    print("-" * 66)
    print(f"{'Cumulative launched (all records)':44}{total_launched:>12,}")
    print(f"{'Cumulative licensed (all records)':44}{total_licensed:>12,}")
    print(f"{'Cumulative filed/requested (all records)':44}{total_filed:>12,}")
    print()
    for k, lbl in RUNGS:
        b = buckets[k]
        if b["records"]:
            print(f"  {lbl}\n    {RUNG_NOTE[k]}\n    {', '.join(sorted(b['records']))}\n")
    print(out["caveat"])


if __name__ == "__main__":
    main()
