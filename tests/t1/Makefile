#!/usr/bin/make -f

all: run check


run: clean
	dpkg-buildpackage -b -us -uc

check:
	grep -q "Depends: .*python-mako" debian/python-foo/DEBIAN/control
	test -f debian/python-foo/usr/lib/python2.6/dist-packages/foo/__init__.py
	test ! -f debian/python-foo/usr/lib/python2.6/dist-packages/foo/spam.py
	grep -q "Breaks: .*python" debian/python-foo/DEBIAN/control

clean:
	./debian/rules clean
	rm -rf lib/Foo.egg-info
