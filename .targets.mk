# draft-fraire-spacerg-constellation-registry
# 
versioned:
	@mkdir -p $@
.INTERMEDIATE: versioned/draft-fraire-spacerg-constellation-registry-00.md
versioned/draft-fraire-spacerg-constellation-registry-00.md: draft-fraire-spacerg-constellation-registry.md | versioned
	sed -e 's/draft-fraire-spacerg-constellation-registry-date/2026-08-06/g' -e 's/draft-fraire-spacerg-constellation-registry-latest/draft-fraire-spacerg-constellation-registry-00/g' -e '/^{::include [^\/]/{ s/^{::include /{::include versioned\/draft-fraire-spacerg-constellation-registry-00\//; }' $< >$@
	$(LIBDIR)/make-includes.sh "HEAD" "draft-fraire-spacerg-constellation-registry-00" "$@"
