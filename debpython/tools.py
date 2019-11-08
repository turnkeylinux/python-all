# -*- coding: UTF-8 -*-
# Copyright © 2010-2019 Piotr Ożarowski <piotr@debian.org>
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

import re
from cPickle import dumps

PUBLIC_DIR_RE = re.compile(r'.*?/usr/lib/python(\d.\d+)/(site|dist)-packages')


def sitedir(version, package=None, gdb=False):
    """Return path to site-packages directory.

    >>> sitedir((2, 5))
    '/usr/lib/python2.5/site-packages/'
    >>> sitedir((2, 7), 'python-foo', True)
    'debian/python-foo/usr/lib/debug/usr/lib/python2.7/dist-packages/'
    """
    if isinstance(version, basestring):
        version = tuple(int(i) for i in version.split('.'))

    if version >= (2, 6):
        path = "/usr/lib/python%d.%d/dist-packages/" % version
    else:
        path = "/usr/lib/python%d.%d/site-packages/" % version

    if gdb:
        path = "/usr/lib/debug%s" % path
    if package:
        path = "debian/%s%s" % (package, path)

    return path


class memoize(object):
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        key = dumps((args, kwargs))
        if key not in self.cache:
            self.cache[key] = self.func(*args, **kwargs)
        return self.cache[key]
