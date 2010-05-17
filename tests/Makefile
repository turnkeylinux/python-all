#!/usr/bin/make -f

all: test1

test%:
	(cd t$*; debuild -us -uc)

clean:
	rm -f *\.dsc *\.tar\.gz *\.build *\.changes *\.deb
	(cd t1; fakeroot ./debian/rules clean)
	@find . -name '*\.egg-info' -exec rm -rf "{}" \; || true

.PHONY: clean
