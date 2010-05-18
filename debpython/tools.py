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
import re
from os import symlink
from subprocess import PIPE, Popen
from sys import exit
from debpython.version import getver, vrepr

log = logging.getLogger('dh_python')
SHEBANG_RE = re.compile(r'^#!\s*/usr/bin/(?:env\s+)?(python(\d+\.\d+)?(?:-dbg)?).*')


def sitedir(version, package=None, gdb=False):
    """Return path to site-packages directory.

    >>> sitedir((2, 5))
    '/usr/lib/python2.5/site-packages/'
    >>> sitedir((2, 7), 'python-foo', True)
    'debian/python-foo/usr/lib/debug/usr/lib/python2.7/dist-packages/'
    >>> sitedir((3, 2))
    '/usr/lib/python3/'
    """
    if isinstance(version, basestring):
        version = tuple(int(i) for i in version.split('.'))

    if version >= (3, 2):
        path = '/usr/lib/python3/'
    elif version >= (2, 6):
        path = "/usr/lib/python%d.%d/dist-packages/" % version
    else:
        path = "/usr/lib/python%d.%d/site-packages/" % version

    if gdb:
        path = "/usr/lib/debug%s" % path
    if package:
        path = "debian/%s%s" % (package, path)

    return path


def relpath(target, link):
    """Return relative path.

    >>> relpath('/usr/share/python-foo/foo.py', '/usr/bin/foo', )
    '../share/python-foo/foo.py'
    """
    t = target.split('/')
    l = link.split('/')
    while l[0] == t[0]:
        del l[0], t[0]
    return '/'.join(['..'] * (len(l) - 1) + t)


def relative_symlink(target, link):
    """Create relative symlink."""
    return symlink(relpath(target, link), link)


def guess_dependency(req, version):
    log.debug('trying to guess dependency for %s (python=%s)',
              req, vrepr(version))
    if isinstance(version, basestring):
        version = getver(version)
    name = req.split()[0]  # only dist name, without version
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


def shebang2pyver(fname):
    """Check file's shebang.

    :rtype: tuple
    :returns: pair of Python interpreter string and Python version
    """
    try:
        with open(fname) as fp:
            data = fp.read(32)
            match = SHEBANG_RE.match(data)
            if not match:
                return None
            res = match.groups()
            if res != (None, None):
                if res[1]:
                    res = res[0], getver(res[1])
                return res
    except IOError:
        log.error('cannot open %s', fname)
