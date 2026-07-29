#!/usr/bin/env bash
# Query the ITU Space Network List (SNL) and the BR IFIC publications for a
# satellite network, to turn a secondary-sourced `itu:` block into a primary
# one. Both sources are public and need no login.
#
#   ./scripts/itu_query.sh snl AST-NG-C-3
#       -> the filing history: administration, stage (API/A, CR/C, Part I-S),
#          date of receipt, and the IFIC number each act was published in.
#
#   ./scripts/itu_query.sh ific 3069 AST-NG-C-3
#       -> downloads BR IFIC 3069 and prints the declared satellite count,
#          plane count and shell geometry for that network.
#
# Requires: curl, unzip, and mdbtools (`brew install mdbtools`) for `ific`.
#
# Two limits worth knowing before you rely on this:
#
#  1. Only recent BR IFICs are downloadable. As of July 2026 the window was
#     roughly IFIC 3038 to 3071, about eighteen months. Anything published
#     before that returns 404 and needs the BR IFIC DVD-ROM or a TIES account.
#     Filings whose last publication is older than the window therefore cannot
#     be primary-sourced this way; say so in the record's notes rather than
#     falling back to press coverage without marking it.
#  2. SNS Online (`itu.int/online/sns/...`) has been retired in favour of ITU
#     Space Explorer. The IFIC databases below are the route that still works
#     unauthenticated.
#
# Field semantics (from the SNL Part B explanations page):
#   ssn_ref   API/A, API/B, API/C  advance publication information
#             CR/C, CR/D           coordination request
#             PART I-S/II-S/III-S  notification for the Master Register
#   ssn_rev   A addition, M modification, S SUPPRESSION, C correction
#   adm       notifying administration, which is often NOT the operator's
#             country: Starlink files through Norway, Globalstar through France
set -euo pipefail

SNL_TXT="https://www.itu.int/net/ITU-R/space/snl/bresult/radvancedw_txt.asp"
IFIC_BASE="https://www.itu.int/sns/ific10"
UA="Mozilla/5.0"

usage() { sed -n '2,30p' "$0"; exit 1; }

case "${1:-}" in
  snl)
    name="${2:?usage: $0 snl <NETWORK-NAME>}"
    curl -sS -A "$UA" "$SNL_TXT?sel_satname=${name}&sel_esname=&sel_adm=&sel_org=&sel_ific=&sel_year=&sel_date_from=&sel_date_to=&sel_rcpt_from=&sel_rcpt_to=&sel_orbit_from=&sel_orbit_to=&sup=&q_reference=&q_ref_numero=&q_sns_id=&res32=&norder=&nmod="
    ;;
  ific)
    n="${2:?usage: $0 ific <IFIC-NUMBER> <NETWORK-NAME>}"
    name="${3:?usage: $0 ific <IFIC-NUMBER> <NETWORK-NAME>}"
    work="${TMPDIR:-/tmp}/itu-ific"
    mkdir -p "$work"
    if [ ! -f "$work/ific$n.mdb" ]; then
      echo "fetching BR IFIC $n ..." >&2
      curl -sSL -A "$UA" -o "$work/ific$n.zip" "$IFIC_BASE/ific$n.zip"
      if ! unzip -tq "$work/ific$n.zip" >/dev/null 2>&1; then
        echo "IFIC $n is not available for download (outside the retention" >&2
        echo "window). Record the filing identity from SNL and note in the" >&2
        echo "record that the technical data could not be reached." >&2
        exit 2
      fi
      unzip -o -q "$work/ific$n.zip" -d "$work"
    fi
    db="$work/ific$n.mdb"
    ids=$(mdb-export "$db" non_geo | awk -F, -v n="\"$name\"" '$2==n {print $1}')
    if [ -z "$ids" ]; then
      echo "no non-GSO notice for '$name' in IFIC $n" >&2; exit 3
    fi
    mdb-export "$db" orbit > "$work/orbit$n.csv"
    for id in $ids; do
      echo "=== $name  ntc_id $id  (BR IFIC $n) ==="
      awk -F, -v ID="$id" '$1==ID {tot+=$3; n++} END {
        printf "  declared: %d satellites across %d orbital planes\n", tot, n}' \
        "$work/orbit$n.csv"
      echo "  shells (altitude / inclination / satellites per plane -> planes):"
      awk -F, -v ID="$id" '$1==ID {printf "    %s km  %s deg  %s/plane\n", $14, $7, $3}' \
        "$work/orbit$n.csv" | sort | uniq -c | sort -rn
    done
    ;;
  *) usage ;;
esac
