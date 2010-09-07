#!/usr/bin/make -f

clean:
	rm -rf cache
	#rm -f dist_fallback
	rm -f README.PyDist.html

dist_fallback:
	python ./generate_fallback_list.py --skip-sensible-names

README.PyDist.html:
	rst2html README.PyDist README.PyDist.html

.PHONY: clean
