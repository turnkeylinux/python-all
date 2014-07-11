#!/usr/bin/make -f

clean:
	rm -rf cache
	#rm -f dist_fallback

dist_fallback: sources.list
	python ./generate_fallback_list.py --skip-sensible-names

.PHONY: clean
