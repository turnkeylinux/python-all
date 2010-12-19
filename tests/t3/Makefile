#!/usr/bin/make -f

all: run check

DPY=$(shell pyversions -d)

run: clean
	dpkg-buildpackage -b -us -uc

check:
	grep -q "pycompile -p python-foo /usr/lib/python-foo -V $(shell pyversions -vd)"\
		debian/python-foo/DEBIAN/postinst
	test -f debian/python-foo/usr/lib/${DPY}/dist-packages/foo/bar.so
	test ! -f debian/python-foo/usr/share/pyshared/foo/bar.so

clean:
	./debian/rules clean
	rm -rf lib/Foo.egg-info build
