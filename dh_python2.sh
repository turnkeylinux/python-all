#! /bin/sh

if [ -f /usr/share/dh-python/dh_python2 ] &&\
    grep -q dh-python ./debian/control 2>/dev/null
then
  exec /usr/share/dh-python/dh_python2 $@
else
  exec /usr/share/python/dh_python2 $@
fi
