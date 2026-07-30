# Two independent build paths in one repo, deliberately kept from colliding:
#
#   make                  builds the Internet-Draft, via martinthomson/i-d-template
#   make registry-check   validates data/constellations/*.yaml (what CI runs)
#   make registry-site    validates and builds public/
#   make registry-serve   builds and serves the page on :8000
#
# The draft targets come from lib/main.mk, which i-d-template provides and
# which defines its own `check::`, `clean::` and friends. Registry targets are
# therefore prefixed rather than named `check`/`clean`, or make refuses to run
# with "target file has both : and :: entries".
#
# Run `make setup` once, inside a git checkout, to fetch lib/.
export UPLOAD_EMAIL ?= juan.fraire@inria.fr

LIBDIR := lib
-include $(LIBDIR)/main.mk

.PHONY: setup
setup:
	@if [ -f $(LIBDIR)/main.mk ]; then \
	  echo "$(LIBDIR)/ is already present, nothing to do"; \
	  echo "(to refresh it: rm -rf $(LIBDIR) && make setup)"; \
	elif [ -f .gitmodules ] && grep -q "path *= *$(LIBDIR)" .gitmodules; then \
	  git submodule sync && git submodule update --init; \
	elif [ -n "$(ID_TEMPLATE_HOME)" ] && [ -d "$(ID_TEMPLATE_HOME)" ]; then \
	  ln -sf "$(ID_TEMPLATE_HOME)" $(LIBDIR); \
	else \
	  git clone -q --depth 10 -b main \
	    https://github.com/martinthomson/i-d-template $(LIBDIR); \
	fi

# ---------------------------------------------------------------- registry --
VENV := .venv
PY   := $(VENV)/bin/python

$(VENV):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet --upgrade pip pyyaml

.PHONY: fmt fmt-wrap fmt-check registry-check registry-site registry-serve registry-analyse registry-clean

# Lay the draft out one sentence per line. Idempotent, so it is safe after
# every edit or from a hook. One sentence per line keeps review diffs to the
# sentences that actually changed.
#   make fmt                       the draft
#   make fmt FILES="README.md"     something else (still sentence-per-line)
#   make fmt-wrap FILES="README.md"  fixed-width instead
#   make fmt-check                 exit 1 if a reflow is needed
FILES ?=
fmt:
	python3 scripts/reflow.py --sentences $(FILES)

fmt-wrap:
	python3 scripts/reflow.py $(FILES)

fmt-check:
	python3 scripts/reflow.py --sentences --check $(FILES)

registry-check: $(VENV)
	$(PY) scripts/build_site.py --check

registry-site: $(VENV)
	$(PY) scripts/build_site.py

registry-serve: registry-site
	cd public && python3 -m http.server 8000

registry-analyse: $(VENV)
	$(PY) scripts/analyse.py

registry-clean:
	rm -rf public $(VENV)
