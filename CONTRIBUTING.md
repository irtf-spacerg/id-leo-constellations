# Contributing

Add or correct one constellation record per pull request: a single YAML file
under [`data/constellations/`](data/constellations/), started from
[`data/TEMPLATE.yaml`](data/TEMPLATE.yaml).

Read [`data/README.md`](data/README.md) first. It defines the taxonomy, the
evidence-grading rules and the one rule that matters: **every field that
asserts a fact carries a `src:` naming an entry in the record's own
`sources:` list.**

Run `make registry-check` before opening the PR; CI runs the same validator.

## What is most useful

1. **Provenance upgrades.** Take a record that rests on a press report, read
   the filing it refers to, and replace the secondary source with the primary
   one. Records that need this carry a line beginning `Provenance gap:` in
   their `notes:`. This is the single most valuable contribution.
2. **Non-US jurisdictions.** Most of the registry's FCC records have a primary
   source and most of the rest do not. If you can navigate ITU SNS, or a
   national regulator's records in China, Russia, India, Canada, Korea or the
   EU, you can close gaps nobody else here can.
3. **Corrections.** If a number is wrong, send a PR that fixes it and bumps
   `verified:`. If a widely circulated number disagrees with the filing,
   record both in `discrepancies:` rather than silently preferring one.
4. **New records**, following the inclusion criteria in `data/README.md`.

## What not to do

Do not fill a field from a source you have not read. Do not promote a
secondary source to `primary` because the number looks right; the validator
checks the `kind`/`grade` mapping and will reject it. Do not write `0` for an
unknown count: leave the key out. An empty field is honest, a laundered one is
not, and the entire value of this registry is that its numbers are traceable.

If a system genuinely has no public filing, say so in `filing_absent:` with
the reason. If a filing exists and you have not read it, give the record the
`filing:` block it deserves and add a `Provenance gap:` line.
