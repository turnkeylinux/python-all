# -*- coding: UTF-8 -*-
# Copyright © 2010 Piotr Ożarowski <piotr@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import with_statement
import logging
import os
import re
from os.path import join, isdir
from subprocess import PIPE, Popen
from sys import exit
from debpython.version import vrepr, getver, parse_vrange

log = logging.getLogger('dh_python')

PYDIST_RE = re.compile(r"""
    (?P<name>[A-Za-z][A-Za-z0-9_.]*)             # Python distribution name
    \s+
    (?P<vrange>(?:-?\d\.\d+(?:-(?:\d\.\d+)?)?)?) # version range
    \s*
    (?P<dependency>[a-z][^;]*)                   # Debian dependency
    (?: # optional upstream version -> Debian version translator
        ;\s*
        (?P<standard>PEP386)?                    # PEP-386 mode
        \s*
        (?P<rules>s/.*)?                         # translator rules
    )?
    """, re.VERBOSE)


def validate(fpath, exit=False):
    """Check if pydist file looks good."""
    with open(fpath) as fp:
        for line in fp:
            line = line.strip('\r\n')
            if line.startswith('#') or not line:
                continue
            if not PYDIST_RE.match(line):
                log.error('invalid pydist data in file %s: %s', \
                          fpath.rsplit('/', 1)[-1], line)
                if exit:
                    sys.exit(3)
                return False
    return True


def load(dname='/usr/share/python/dist/'):
    """Load iformation about installed Python distributions."""
    # use cached data if possible
    global _data
    if dname in _data:
        return _data[dname]
    if not isdir(dname):
        log.warn('%s is not a dir', dname)
        return {}

    result = {}
    for fname in os.listdir(dname):
        with open(join(dname, fname)) as fp:
            for line in fp:
                line = line.strip('\r\n')
                if line.startswith('#') or not line:
                    continue
                    line = line.strip()
                dist = PYDIST_RE.search(line).groupdict()
                name = dist['name'].lower()
                if name in result:
                    log.error('Python distribution %s already listed twice'
                              ' (last file: %s)', join(dname, fname))
                dist['vrange'] = parse_vrange(dist['vrange'])
                if dist['rules']:
                    dist['rules'] = dist['rules'].split(';')
                else:
                    dist['rules'] = []
                result[name] = dist

    _data[dname] = result
    return result
_data = {}


def guess_dependency(req, version):
    log.debug('trying to guess dependency for %s (python=%s)',
              req, vrepr(version))
    if isinstance(version, basestring):
        version = getver(version)
    pydist_data = load()
    req = req.split(' ', 1)
    name = req[0]
    if len(req) > 1:
        req_version = req[1].split(',')  # FIXME: check requires.txt syntax
    if name in pydist_data:
        # FIXME: rules, versions
        return pydist_data[name]['dependency']

    # try dpkg -S

    query = "'%s-?*\.egg-info'" % name  # TODO: .dist-info
    if version and version[0] == 3:
        query = "%s | grep '/python3" % query
    else:
        if version:
            query = "%s | grep '/python%s/\|/pyshared/'" %\
                    (query, vrepr(version))
        else:
            query = "%s | grep '/python2\../\|/pyshared/'" % query

    log.debug("invoking dpkg -S %s", query)
    process = Popen("/usr/bin/dpkg -S %s" % query,\
                    shell=True, stdout=PIPE, stderr=PIPE)
    if process.wait() != 0:
        log.error('Cannot find package that provides %s.', name)
        log.info("hint: `apt-file search -x '(packages|pyshared)/" +\
                  "%s' -l` might help", name)
        # TODO: false positive - .pydist
        exit(8)

    result = set()
    for line in process.stdout:
        result.add(line.split(':')[0])
    if len(result) > 1:
        log.error('more than one package name found for %s dist', name)
        exit(9)
    return result.pop()
