#!/usr/bin/make -f
INSTALL ?= install
PREFIX ?= /usr/local

clean:
	make -C tests clean
	find . -name '*.py[co]' -delete
	rm -f .coverage

install-dev:
	$(INSTALL) -m 755 -d $(DESTDIR)$(PREFIX)/bin \
		$(DESTDIR)$(PREFIX)/share/python/runtime.d \
		$(DESTDIR)$(PREFIX)/share/debhelper/autoscripts/ \
		$(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Sequence/
	$(INSTALL) -m 755 runtime.d/* $(DESTDIR)$(PREFIX)/share/python/runtime.d/
	$(INSTALL) -m 644 autoscripts/* $(DESTDIR)$(PREFIX)/share/debhelper/autoscripts/
	$(INSTALL) -m 755 dh_python2 $(DESTDIR)$(PREFIX)/bin/
	$(INSTALL) -m 644 python2.pm $(DESTDIR)$(PREFIX)/share/perl5/Debian/Debhelper/Sequence/

install-runtime:
	$(INSTALL) -m 755 -d $(DESTDIR)$(PREFIX)/share/python/debpython $(DESTDIR)$(PREFIX)/bin
	$(INSTALL) -m 644 debpython/*.py $(DESTDIR)$(PREFIX)/share/python/debpython/
	$(INSTALL) -m 755 pycompile $(DESTDIR)$(PREFIX)/bin/
	$(INSTALL) -m 755 pyclean $(DESTDIR)$(PREFIX)/bin/

install: install-dev install-runtime

nose:
	nosetests --with-doctest --with-coverage

tests: nose
	make -C tests

test%:
	make -C tests $@

check_versions:
	@PYTHONPATH=. set -e; \
	DEFAULT=`python -c 'import debpython.version as v; print v.vrepr(v.DEFAULT)'`;\
	SUPPORTED=`python -c 'import debpython.version as v; print " ".join(sorted(v.vrepr(v.SUPPORTED)))'`;\
	DEB_DEFAULT=`sed -rn 's,^default-version = python([0.9.]*),\1,p' debian/debian_defaults`;\
	DEB_SUPPORTED=`sed -rn 's|^supported-versions = (.*)|\1|p' debian/debian_defaults | sed 's/python//g;s/,//g'`;\
	[ "$$DEFAULT" = "$$DEB_DEFAULT" ] || \
	(echo 'Please update DEFAULT in debpython/version.py' >/dev/stderr; false);\
	[ "$$SUPPORTED" = "$$DEB_SUPPORTED" ] || \
	(echo 'Please update SUPPORTED in debpython/version.py' >/dev/stderr; false)

.PHONY: clean tests test% check_versions
