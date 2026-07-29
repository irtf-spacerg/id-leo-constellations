#!/usr/bin/env python3
"""Validate data/constellations/*.yaml and build the static site into public/.

Usage:
    python scripts/build_site.py            # validate + build public/
    python scripts/build_site.py --check    # validate only (CI on pull requests)
    python scripts/build_site.py --artifact FILE  # also emit a body-only preview

One record is one authorisation: one application or licence, one anchoring
filing reference, one set of counts.  Modifications, waivers and partial
grants of that same authorisation are events inside the record's
``regulatory:`` list, not records of their own.  Records are grouped for
roll-up by ``family:``.

The validator enforces the registry's provenance discipline, not just its
shape.  In particular:

  * every record carries an anchoring ``filing:`` or an explicit
    ``filing_absent:`` explanation
  * every ``src:`` resolves to an id declared in the record's own ``sources:``
  * every populated ``counts:`` entry carries value, asof and src
  * ``licensed`` never exceeds ``filed`` (filed is cumulative of everything
    requested, whatever the outcome)
  * a source's ``grade:`` is consistent with its ``kind:`` (you cannot mark
    SpaceNews as primary)
  * ``breakdown:`` values sum to their parent count
  * ``satellites == planes * sats_per_plane`` in every Walker shell
  * every ``code:`` parses against the ABNF in
    draft-piraux-space-constellation-code and agrees with the shell's own
    fields, and any code that is not ``exact`` declares what was assumed
  * ``supersedes:`` / ``superseded_by:`` resolve to real slugs
"""
import argparse
import csv
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "constellations"
TEMPLATE = ROOT / "site" / "template.html"
STATIC = ROOT / "site" / "static"
PUBLIC = ROOT / "public"

# --------------------------------------------------------------------- enums

SYSTEM_CLASSES = {
    "broadband", "direct-to-device", "iot-m2m", "backhaul-trunking",
    "orbital-compute", "earth-observation", "navigation",
    "government-military", "relay-data-transport", "technology-demo", "other",
}
STATUSES = {
    "operational", "deploying", "demonstrator", "licensed", "filed",
    "announced", "dormant", "cancelled", "retired",
}
SERVICES = {
    "broadband", "direct-to-device", "iot", "backhaul", "orbital-compute",
    "government-secure", "military", "voice", "messaging", "relay",
    "earth-observation", "navigation", "other",
}
ORBIT_REGIMES = {"VLEO", "LEO", "MEO", "GEO", "HEO", "cislunar"}
DUAL_USE = {"civil", "military", "dual", "unknown"}
AUTHORITIES = {
    "FCC", "Ofcom", "ANFR", "BNetzA", "AGCOM", "IN-SPACe", "MIIT", "SASTIND",
    "Roskomnadzor", "ACMA", "ISED", "MIC", "KCC", "ANATEL", "EUSPA", "ESA",
    "NTIA", "none", "other",
}
REG_KINDS = {
    "application", "license-grant", "modification", "waiver", "public-notice",
    "denial", "termination",
}
REG_ACTIONS = {
    "granted", "granted-in-part", "pending", "deferred", "dismissed", "denied",
    "withdrawn",
}
ITU_STAGES = {"API", "CR/C", "notification", "in-force", "expired"}
SHELL_STATUSES = {
    "deployed", "deploying", "authorised", "proposed", "superseded", "cancelled",
}
GEOMETRY_KINDS = {"walker", "envelope", "sso-band", "irregular", "unknown"}
WALKERS = {"D", "S", "none"}
CODE_STATUSES = {
    "exact", "assumed-phasing", "derived", "not-representable", "unknown",
}
# Codes in these states must say, field by field, what was assumed.
CODE_NEEDS_ASSUMPTIONS = {"assumed-phasing", "derived"}
ISL = {
    "optical", "rf", "optical-planned", "rf-planned", "none", "external",
    "unknown",
}
SPECTRUM = {
    "L", "S", "C", "X", "Ku", "K", "Ka", "Q", "V", "W", "E", "D", "optical",
}
COMPLETION_KINDS = {"regulatory-milestone", "operator-target"}
COUNT_KEYS = ["launched", "in_orbit", "licensed", "filed", "announced"]

# A source's grade is a function of its kind, not a free choice.
PRIMARY_KINDS = {
    "itu-filing", "itu-publication", "fcc-order", "fcc-application",
    "fcc-public-notice", "regulator-docket", "operator-technical",
    "treaty-registry",
}
SECONDARY_KINDS = {
    "operator-web", "trade-press", "tracker", "encyclopedia", "academic",
    "analyst", "presentation",
}
KIND_GRADE = {k: "primary" for k in PRIMARY_KINDS}
KIND_GRADE.update({k: "secondary" for k in SECONDARY_KINDS})

REQUIRED = ["name", "slug", "family", "operator", "status", "sources", "verified"]

TOP_LEVEL_KEYS = {
    "name", "slug", "family", "aka", "operator", "parent", "country",
    "jurisdiction", "system_class", "status", "status_detail", "status_asof",
    "services", "orbit_regimes", "dual_use", "filing", "filing_absent",
    "supersedes", "superseded_by", "counts", "regulatory", "itu", "shells",
    "constellation_code", "constellation_code_status", "spectrum",
    "spectrum_detail", "isl", "isl_detail", "sat_mass_kg", "first_launch",
    "service_start", "target_completion", "target_completion_kind", "launch",
    "sources", "discrepancies", "notes", "added", "verified", "contributor",
}

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# draft-piraux-space-constellation-code ABNF, single shell
SHELL_CODE_RE = re.compile(
    r"^(?P<walker>[DS]):(?P<alt>\d+(?:\.\d+)?):(?P<inc>\d+(?:\.\d+)?):"
    r"(?P<t>\d+)/(?P<p>\d+)/(?P<f>\d+)(?::(?P<ma>\d+(?:\.\d+)?))?$"
)


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _months_between(then, now):
    return (now.year - then.year) * 12 + (now.month - then.month)


def _as_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.datetime.strptime(str(v), fmt).date()
        except (ValueError, TypeError):
            continue
    return None


# ---------------------------------------------------------------- validation

def check_sources(rec, name, err):
    """Declare source ids and enforce the kind/grade mapping."""
    ids = set()
    for i, s in enumerate(rec.get("sources") or []):
        where = f"{name}: sources[{i}]"
        if not isinstance(s, dict):
            err(f"{where}: expected a mapping")
            continue
        sid = s.get("id")
        if not sid:
            err(f"{where}: missing 'id'")
        elif sid in ids:
            err(f"{where}: duplicate source id '{sid}'")
        else:
            ids.add(sid)
        kind, grade = s.get("kind"), s.get("grade")
        if kind not in KIND_GRADE:
            err(f"{where}: unknown source kind '{kind}'")
        elif grade != KIND_GRADE[kind]:
            err(f"{where}: kind '{kind}' is {KIND_GRADE[kind]}, "
                f"but grade says '{grade}'")
        for k in ("title", "url", "retrieved"):
            if not s.get(k):
                err(f"{where}: missing '{k}'")
        url = str(s.get("url") or "")
        if url and not url.startswith(("http://", "https://")):
            err(f"{where}: url must be absolute, got '{url}'")
    return ids


def check_ref(value, ids, where, err):
    if value is None:
        return
    if value not in ids:
        err(f"{where}: src '{value}' is not declared in sources:")


def check_filing(rec, ids, name, err):
    """One record, one anchoring filing reference - or a stated reason."""
    filing, absent = rec.get("filing"), rec.get("filing_absent")
    if not filing and not absent:
        err(f"{name}: needs either a 'filing:' block naming the authorisation "
            f"this record is about, or 'filing_absent:' explaining why no "
            f"public filing reference exists")
        return
    if filing and absent:
        err(f"{name}: has both 'filing:' and 'filing_absent:'")
    if not filing:
        return
    if not isinstance(filing, dict):
        err(f"{name}: 'filing' must be a mapping")
        return
    where = f"{name}: filing"
    if filing.get("authority") not in AUTHORITIES:
        err(f"{where}: unknown authority '{filing.get('authority')}'")
    if not filing.get("file_number") and not filing.get("document"):
        err(f"{where}: needs a 'file_number' or, failing that, a 'document'")
    if not filing.get("src"):
        err(f"{where}: the anchoring filing needs a 'src'")
    check_ref(filing.get("src"), ids, where, err)


def check_counts(rec, ids, name, err):
    counts = rec.get("counts")
    if counts is None:
        return
    if not isinstance(counts, dict):
        err(f"{name}: 'counts' must be a mapping")
        return
    for key, c in counts.items():
        where = f"{name}: counts.{key}"
        if key not in COUNT_KEYS:
            err(f"{where}: unknown count '{key}' "
                f"(expected one of {sorted(COUNT_KEYS)})")
            continue
        if not isinstance(c, dict):
            err(f"{where}: expected a mapping with value/asof/src")
            continue
        for k in ("value", "asof", "src"):
            if c.get(k) in (None, ""):
                err(f"{where}: missing '{k}' (every count needs a source)")
        if c.get("value") is not None and not _num(c.get("value")):
            err(f"{where}: 'value' must be a number")
        check_ref(c.get("src"), ids, where, err)
        bd = c.get("breakdown")
        if bd is None:
            continue
        if not isinstance(bd, list):
            err(f"{where}: 'breakdown' must be a list")
            continue
        total = 0
        for j, b in enumerate(bd):
            if not isinstance(b, dict) or not _num(b.get("value")):
                err(f"{where}: breakdown[{j}] needs a numeric 'value'")
                continue
            total += b["value"]
            check_ref(b.get("src"), ids, f"{where}: breakdown[{j}]", err)
        if _num(c.get("value")) and total != c["value"]:
            err(f"{where}: breakdown sums to {total}, but value is {c['value']}")

    # filed is cumulative of everything requested, whatever the outcome, so a
    # licensed figure larger than the filed figure is always a data error.
    lic = (counts.get("licensed") or {}).get("value")
    filed = (counts.get("filed") or {}).get("value")
    if _num(lic) and _num(filed) and lic > filed:
        err(f"{name}: counts.licensed ({lic}) exceeds counts.filed ({filed}); "
            f"'filed' is cumulative of everything requested, so it must "
            f"include whatever was granted")


def check_shell_code(sh, ids, where, err):
    code = sh.get("code")
    status = sh.get("code_status")
    assumptions = sh.get("code_assumptions")
    geom = sh.get("geometry_kind")

    if geom is not None and geom not in GEOMETRY_KINDS:
        err(f"{where}: unknown geometry_kind '{geom}'")
    if status is not None and status not in CODE_STATUSES:
        err(f"{where}: unknown code_status '{status}'")

    if geom == "envelope":
        if not (sh.get("max_planes") or sh.get("max_sats_per_plane")):
            err(f"{where}: geometry_kind 'envelope' needs 'max_planes' and/or "
                f"'max_sats_per_plane' recording the authorised bound")
        if code:
            err(f"{where}: an envelope authorisation has no single (T, P, F) "
                f"triple; remove 'code'")

    if status == "not-representable":
        if code:
            err(f"{where}: code_status 'not-representable' must not carry a code")
        if not sh.get("code_note"):
            err(f"{where}: code_status 'not-representable' needs a code_note")
        return

    if status in CODE_NEEDS_ASSUMPTIONS:
        if not assumptions:
            err(f"{where}: code_status '{status}' requires 'code_assumptions' "
                f"stating which elements were assumed and on what basis")
    for j, a in enumerate(assumptions or []):
        aw = f"{where}: code_assumptions[{j}]"
        if not isinstance(a, dict):
            err(f"{aw}: expected a mapping")
            continue
        for k in ("element", "value", "basis"):
            if a.get(k) in (None, ""):
                err(f"{aw}: missing '{k}'")
        check_ref(a.get("src"), ids, aw, err)

    if code is None:
        return
    if not status:
        err(f"{where}: 'code' present without 'code_status'")
    m = SHELL_CODE_RE.match(str(code))
    if not m:
        err(f"{where}: '{code}' is not a valid constellation code "
            f"(draft-piraux-space-constellation-code ABNF)")
        return
    g = m.groupdict()
    t, p, f = int(g["t"]), int(g["p"]), int(g["f"])
    if p == 0 or t % p:
        err(f"{where}: code '{code}': {t} satellites not divisible by {p} planes")
    if not 0 <= f <= max(p - 1, 0):
        err(f"{where}: code '{code}': phasing factor {f} outside [0, {p - 1}]")
    if not 0 <= float(g["inc"]) <= 180:
        err(f"{where}: code '{code}': inclination outside [0, 180]")
    pairs = [("walker", g["walker"]), ("altitude_km", float(g["alt"])),
             ("inclination_deg", float(g["inc"])), ("satellites", t),
             ("planes", p), ("phasing", f)]
    for field, coded in pairs:
        have = sh.get(field)
        if have is None:
            continue
        if field in ("altitude_km", "inclination_deg"):
            if abs(float(have) - coded) > 1e-9:
                err(f"{where}: code says {field}={coded}, record says {have}")
        elif str(have) != str(coded):
            err(f"{where}: code says {field}={coded}, record says {have}")


def check_shells(rec, ids, name, err):
    shells = rec.get("shells")
    if shells is None:
        return
    if not isinstance(shells, list):
        err(f"{name}: 'shells' must be a list")
        return
    labels = set()
    for i, sh in enumerate(shells):
        where = f"{name}: shells[{i}]"
        if not isinstance(sh, dict):
            err(f"{where}: expected a mapping")
            continue
        label = sh.get("label")
        if label:
            where = f"{name}: shells[{label}]"
            if label in labels:
                err(f"{where}: duplicate shell label")
            labels.add(label)
        st = sh.get("status")
        if st is not None and st not in SHELL_STATUSES:
            err(f"{where}: unknown shell status '{st}'")
        w = sh.get("walker")
        if w is not None and w not in WALKERS:
            err(f"{where}: unknown walker '{w}'")
        planes = sh.get("planes")
        spp = sh.get("sats_per_plane")
        sats = sh.get("satellites")
        if all(_num(x) for x in (planes, spp, sats)) and planes * spp != sats:
            err(f"{where}: satellites={sats} but planes*sats_per_plane="
                f"{planes * spp}")
        inc = sh.get("inclination_deg")
        if _num(inc) and not 0 <= inc <= 180:
            err(f"{where}: inclination_deg {inc} outside [0, 180]")
        check_ref(sh.get("src"), ids, where, err)
        check_ref(sh.get("code_src"), ids, where, err)
        check_shell_code(sh, ids, where, err)


def check_regulatory(rec, ids, name, err):
    for i, r in enumerate(rec.get("regulatory") or []):
        where = f"{name}: regulatory[{i}]"
        if not isinstance(r, dict):
            err(f"{where}: expected a mapping")
            continue
        if r.get("authority") not in AUTHORITIES:
            err(f"{where}: unknown authority '{r.get('authority')}'")
        if r.get("kind") not in REG_KINDS:
            err(f"{where}: unknown kind '{r.get('kind')}'")
        if r.get("action") not in REG_ACTIONS:
            err(f"{where}: unknown action '{r.get('action')}'")
        if not r.get("src"):
            err(f"{where}: every regulatory act needs a 'src'")
        check_ref(r.get("src"), ids, where, err)
        for j, m in enumerate(r.get("milestones") or []):
            if not isinstance(m, dict) or "due" not in m:
                err(f"{where}: milestones[{j}] needs at least a 'due' date")
    for i, it in enumerate(rec.get("itu") or []):
        where = f"{name}: itu[{i}]"
        if not isinstance(it, dict):
            err(f"{where}: expected a mapping")
            continue
        if it.get("stage") not in ITU_STAGES:
            err(f"{where}: unknown ITU stage '{it.get('stage')}'")
        if not it.get("src"):
            err(f"{where}: every ITU filing needs a 'src'")
        check_ref(it.get("src"), ids, where, err)


def check_enum_list(rec, key, allowed, name, err):
    v = rec.get(key)
    if v is None:
        return
    if not isinstance(v, list):
        err(f"{name}: '{key}' must be a list")
        return
    for item in v:
        if item not in allowed:
            err(f"{name}: unknown {key} value '{item}'")


def load_records():
    errors, warnings, records = [], [], []
    files = sorted(DATA_DIR.glob("*.yaml"))
    if not files:
        errors.append(f"no YAML files found in {DATA_DIR}")
    seen_names, seen_slugs = {}, {}
    for path in files:
        name = path.name
        err = errors.append
        try:
            rec = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            err(f"{name}: YAML parse error: {e}")
            continue
        if not isinstance(rec, dict):
            err(f"{name}: expected a mapping")
            continue

        for k in REQUIRED:
            if not rec.get(k):
                err(f"{name}: missing required field '{k}'")
        unknown = set(rec) - TOP_LEVEL_KEYS
        if unknown:
            err(f"{name}: unknown fields {sorted(unknown)}")

        slug = rec.get("slug")
        if slug:
            if not SLUG_RE.match(str(slug)):
                err(f"{name}: slug '{slug}' must match [a-z0-9]+(-[a-z0-9]+)*")
            if slug != path.stem:
                err(f"{name}: slug '{slug}' does not match filename stem "
                    f"'{path.stem}'")
            if slug in seen_slugs:
                err(f"{name}: duplicate slug (also in {seen_slugs[slug]})")
            seen_slugs[slug] = name
        fam = rec.get("family")
        if fam and not SLUG_RE.match(str(fam)):
            err(f"{name}: family '{fam}' must match [a-z0-9]+(-[a-z0-9]+)*")
        nm = rec.get("name")
        if nm in seen_names:
            err(f"{name}: duplicate name '{nm}' (also in {seen_names[nm]})")
        seen_names[nm] = name

        if rec.get("status") and rec["status"] not in STATUSES:
            err(f"{name}: unknown status '{rec['status']}'")
        if rec.get("system_class") and rec["system_class"] not in SYSTEM_CLASSES:
            err(f"{name}: unknown system_class '{rec['system_class']}'")
        if rec.get("dual_use") and rec["dual_use"] not in DUAL_USE:
            err(f"{name}: unknown dual_use '{rec['dual_use']}'")
        if rec.get("isl") and rec["isl"] not in ISL:
            err(f"{name}: unknown isl '{rec['isl']}'")
        tck = rec.get("target_completion_kind")
        if tck and tck not in COMPLETION_KINDS:
            err(f"{name}: unknown target_completion_kind '{tck}'")
        ccs = rec.get("constellation_code_status")
        if ccs and ccs not in CODE_STATUSES:
            err(f"{name}: unknown constellation_code_status '{ccs}'")
        if rec.get("constellation_code") and not ccs:
            err(f"{name}: 'constellation_code' without "
                f"'constellation_code_status'")
        check_enum_list(rec, "services", SERVICES, name, err)
        check_enum_list(rec, "orbit_regimes", ORBIT_REGIMES, name, err)
        check_enum_list(rec, "spectrum", SPECTRUM, name, err)

        ids = check_sources(rec, name, err)
        check_filing(rec, ids, name, err)
        check_counts(rec, ids, name, err)
        check_shells(rec, ids, name, err)
        check_regulatory(rec, ids, name, err)
        launch = rec.get("launch")
        if isinstance(launch, dict):
            check_ref(launch.get("src"), ids, f"{name}: launch", err)
        for i, d in enumerate(rec.get("discrepancies") or []):
            if isinstance(d, dict):
                check_ref(d.get("claimed_by"), ids,
                          f"{name}: discrepancies[{i}]", err)

        cc = rec.get("constellation_code")
        if cc:
            for part in str(cc).split("+"):
                if not SHELL_CODE_RE.match(part):
                    err(f"{name}: constellation_code segment '{part}' is not a "
                        f"valid constellation code")

        rec["_file"] = name
        records.append(rec)

    # Cross-record checks, once every slug is known.
    slugs = {r.get("slug") for r in records}
    for r in records:
        for key in ("supersedes", "superseded_by"):
            v = r.get(key)
            if v is None:
                continue
            if not isinstance(v, list):
                errors.append(f"{r['_file']}: '{key}' must be a list of slugs")
                continue
            for s in v:
                if s not in slugs:
                    errors.append(f"{r['_file']}: {key} references unknown "
                                  f"record slug '{s}'")
    return records, errors, warnings


def staleness(records, ttl_months, today):
    stale = []
    for r in records:
        d = _as_date(r.get("verified"))
        if d is None:
            continue
        age = _months_between(d, today)
        if age >= ttl_months:
            stale.append((r.get("slug"), r.get("verified"), age))
    return sorted(stale, key=lambda x: -x[2])


# ------------------------------------------------------------------- export

def flatten(rec, ttl_months, today):
    counts = rec.get("counts") or {}

    def cv(key):
        return (counts.get(key) or {}).get("value")

    sources = [s for s in (rec.get("sources") or []) if isinstance(s, dict)]
    grades = {s.get("grade") for s in sources}
    shells = [s for s in (rec.get("shells") or []) if isinstance(s, dict)]
    filing = rec.get("filing") or {}
    d = _as_date(rec.get("verified"))
    age = _months_between(d, today) if d else None
    return {
        "slug": rec.get("slug", ""),
        "name": rec.get("name", ""),
        "family": rec.get("family", ""),
        "aka": "; ".join(rec.get("aka") or []),
        "operator": rec.get("operator", ""),
        "parent": rec.get("parent", ""),
        "country": rec.get("country", ""),
        "jurisdiction": "; ".join(rec.get("jurisdiction") or []),
        "system_class": rec.get("system_class", ""),
        "status": rec.get("status", ""),
        "status_detail": rec.get("status_detail", ""),
        "services": "; ".join(rec.get("services") or []),
        "orbit_regimes": "; ".join(rec.get("orbit_regimes") or []),
        "dual_use": rec.get("dual_use", ""),
        "filing_authority": filing.get("authority", ""),
        "filing_number": filing.get("file_number", ""),
        "filing_call_sign": filing.get("call_sign", ""),
        "filing_absent": rec.get("filing_absent", ""),
        "launched": cv("launched"),
        "in_orbit": cv("in_orbit"),
        "licensed": cv("licensed"),
        "filed": cv("filed"),
        "announced": cv("announced"),
        "n_shells": len(shells),
        "constellation_code": rec.get("constellation_code", ""),
        "constellation_code_status": rec.get("constellation_code_status", ""),
        "spectrum": "; ".join(rec.get("spectrum") or []),
        "isl": rec.get("isl", ""),
        "first_launch": str(rec.get("first_launch") or ""),
        "service_start": str(rec.get("service_start") or ""),
        "target_completion": str(rec.get("target_completion") or ""),
        "target_completion_kind": rec.get("target_completion_kind", ""),
        "launch_providers": "; ".join(
            (rec.get("launch") or {}).get("providers") or []),
        "n_regulatory": len(rec.get("regulatory") or []),
        "n_itu": len(rec.get("itu") or []),
        "n_sources": len(sources),
        "has_primary": "yes" if "primary" in grades else "no",
        "n_discrepancies": len(rec.get("discrepancies") or []),
        "supersedes": "; ".join(rec.get("supersedes") or []),
        "superseded_by": "; ".join(rec.get("superseded_by") or []),
        "notes": rec.get("notes", ""),
        "added": str(rec.get("added") or ""),
        "verified": str(rec.get("verified") or ""),
        "verified_age_months": age,
        "stale": "yes" if age is not None and age >= ttl_months else "no",
    }


def aggregates(rows):
    """Roll-up totals. Superseded records are excluded so that a family's
    numbers are not counted twice."""
    live = [r for r in rows if not r["superseded_by"]]
    def total(key):
        return sum(r[key] for r in live if isinstance(r[key], (int, float)))
    by_status, by_family = {}, {}
    for r in live:
        by_status[r["status"]] = by_status.get(r["status"], 0) + (
            r["filed"] if isinstance(r["filed"], (int, float)) else 0)
        f = r["family"]
        e = by_family.setdefault(f, {"records": 0, "licensed": 0, "filed": 0})
        e["records"] += 1
        for k in ("licensed", "filed"):
            if isinstance(r[k], (int, float)):
                e[k] += r[k]
    # A record may honestly carry a licensed figure without a filed one: the
    # grant is documented but the size of the original request is not. Summing
    # anyway would understate the filed total and can make a family's licensed
    # figure exceed its filed figure, which looks like a data error and is not.
    # Report the coverage so every total is read as the floor it is.
    missing = [r["slug"] for r in live
               if not isinstance(r["filed"], (int, float))]
    for f, e in by_family.items():
        e["filed_is_floor"] = any(
            r["family"] == f and not isinstance(r["filed"], (int, float))
            for r in live)
    return {
        "records": len(rows),
        "records_counted": len(live),
        "records_with_primary_source": sum(
            1 for r in live if r["has_primary"] == "yes"),
        "total_launched": total("launched"),
        "total_licensed": total("licensed"),
        "total_filed": total("filed"),
        "total_announced": total("announced"),
        "totals_are_floors": True,
        "records_missing_filed": missing,
        "note": (
            "Totals are floors, not estimates. They sum only what is recorded "
            "and sourced; records with an unrecorded count contribute zero. "
            f"{len(missing)} of {len(live)} records have no filed figure, so "
            "total_filed understates by an unknown amount, and a family's "
            "licensed total may exceed its filed total for that reason. "
            "Superseded records are excluded."),
        "filed_by_status": by_status,
        "by_family": by_family,
    }


def build(records, cfg, ttl_months, today, artifact_out=None):
    ordered = sorted(records, key=lambda r: (r.get("name") or "").lower())
    clean = [{k: v for k, v in r.items() if k != "_file"} for r in ordered]
    rows = [flatten(r, ttl_months, today) for r in ordered]
    agg = aggregates(rows)

    PUBLIC.mkdir(exist_ok=True)
    (PUBLIC / "data").mkdir(exist_ok=True)
    (PUBLIC / "data" / "constellations.json").write_text(
        json.dumps(clean, ensure_ascii=False, indent=1, default=str))
    (PUBLIC / "data" / "constellations-summary.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1, default=str))
    (PUBLIC / "data" / "aggregates.json").write_text(
        json.dumps(agg, ensure_ascii=False, indent=1, default=str))
    cols = list(rows[0].keys()) if rows else []
    with (PUBLIC / "data" / "constellations.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow(["" if r[c] is None else r[c] for c in cols])

    print(f"  totals over {agg['records_counted']} non-superseded records: "
          f"{agg['total_launched']:,} launched, "
          f"{agg['total_licensed']:,} licensed, "
          f"{agg['total_filed']:,} filed, "
          f"{agg['total_announced']:,} announced (floors; "
          f"{len(agg['records_missing_filed'])} record(s) have no filed figure)")

    if not TEMPLATE.is_file():
        print(f"built public/ data exports for {len(rows)} records "
              f"(no site/template.html yet, HTML page skipped)")
        return

    if STATIC.is_dir():
        shutil.copytree(STATIC, PUBLIC / "static", dirs_exist_ok=True)
    # The page shows provenance, not just counts, so it needs the nested
    # blocks alongside the flat summary fields.
    page_rows = []
    for rec, row in zip(ordered, rows):
        merged = dict(row)
        # Note: scalar/joined fields such as `aka` stay as flatten() rendered
        # them; only the nested blocks the page needs are merged back in.
        for k in ("counts", "filing", "filing_absent", "regulatory", "itu",
                  "shells", "sources", "discrepancies", "spectrum_detail",
                  "isl_detail", "status_detail"):
            v = rec.get(k)
            if v not in (None, "", [], {}):
                merged[k] = v
        page_rows.append(merged)
    data_js = json.dumps({"records": page_rows, "aggregates": agg},
                         ensure_ascii=False, default=str).replace("</", "<\\/")
    body = (TEMPLATE.read_text()
            .replace("__MAINTAINER_EMAIL__", cfg["maintainer_email"])
            .replace("__REPO_URL__", cfg["repo_url"])
            .replace("__BUILD_DATE__", today.isoformat())
            .replace("const PAYLOAD = /*__DATA__*/{records: [], aggregates: {}};",
                     f"const PAYLOAD = {data_js};"))
    if "const PAYLOAD = /*__DATA__*/" in body:
        raise SystemExit("site/template.html: the /*__DATA__*/ placeholder was not "
                         "substituted; its surrounding line must match exactly "
                         "'const PAYLOAD = /*__DATA__*/{records: [], aggregates: {}};'")
    desc = cfg.get("description", "").replace("{n}", str(len(rows)))
    pages = cfg.get("pages_url", "").rstrip("/") + "/"
    title = cfg["site_title"]
    og_img = pages + "static/logo.png"
    head = (f'<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n'
            f'<meta name="description" content="{desc}">\n'
            f'<link rel="canonical" href="{pages}">\n'
            f'<link rel="icon" type="image/png" href="static/favicon.png">\n'
            f'<link rel="apple-touch-icon" href="static/favicon.png">\n'
            f'<meta name="theme-color" content="#F6F7F9" media="(prefers-color-scheme: light)">\n'
            f'<meta name="theme-color" content="#0F131B" media="(prefers-color-scheme: dark)">\n'
            f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="{title}">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n'
            f'<meta property="og:url" content="{pages}">\n'
            f'<meta property="og:image" content="{og_img}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{title}">\n'
            f'<meta name="twitter:description" content="{desc}">\n'
            f'<meta name="twitter:image" content="{og_img}">\n')
    (PUBLIC / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n' + head
        + "</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    if artifact_out:
        Path(artifact_out).write_text(
            f"<title>{cfg['site_title']}</title>\n" + body)
    print(f"built public/ with {len(rows)} records")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--artifact", help="write a body-only preview page here")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    ttl = int(cfg.get("verify_ttl_months", 12))
    today = datetime.date.today()

    records, errors, warnings = load_records()
    if errors:
        print(f"{len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print("  -", e, file=sys.stderr)
        sys.exit(1)

    graded = sum(1 for r in records
                 if any(s.get("grade") == "primary"
                        for s in (r.get("sources") or [])))
    print(f"{len(records)} records validated "
          f"({graded} with at least one primary source)")
    for w in warnings:
        print(f"  warning: {w}")
    stale = staleness(records, ttl, today)
    if stale:
        print(f"  {len(stale)} record(s) not re-verified in {ttl}+ months:")
        for slug, when, age in stale:
            print(f"    - {slug} (verified {when}, {age} months ago)")
    if not args.check:
        build(records, cfg, ttl, today, artifact_out=args.artifact)


if __name__ == "__main__":
    main()
