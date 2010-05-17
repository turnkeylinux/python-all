#! /usr/bin/python

import os, re, sys
try:
    SetType = set
except NameError:
    import sets
    SetType = sets.Set
    set = sets.Set

def parse_versions(vstring):
    import operator
    operators = { None: operator.eq, '=': operator.eq,
                  '>=': operator.ge, '<=': operator.le,
                  '<<': operator.lt
                  }
    vinfo = {}
    exact_versions = set([])
    version_range = set(supported_versions(version_only=True))
    relop_seen = False
    for field in vstring.split(','):
        field = field.strip()
        if field == 'all':
            vinfo['all'] = 'all'
            continue
        if field in ('current', 'current_ext'):
            vinfo['current'] = field
            continue
        vinfo.setdefault('versions', set())
        ve = re.compile('(>=|<=|<<|=)? *(\d\.\d)$')
        m = ve.match(field)
        try:
            op, v = m.group(1), m.group(2)
            if op in (None, '='):
                exact_versions.add(v)
            else:
                relop_seen = True
                filtop = operators[op]
                version_range = [av for av in version_range if filtop(av ,v)]
        except Exception:
            raise ValueError, 'error parsing Python-Version attribute'
    if 'versions' in vinfo:
        vinfo['versions'] = exact_versions
        if relop_seen:
            vinfo['versions'] = exact_versions.union(version_range)
    return vinfo

_supported_versions = None
def supported_versions(version_only=False):
    global _supported_versions
    if not _supported_versions:
        if os.path.exists('/usr/share/python/debian_defaults'):
            from ConfigParser import SafeConfigParser
            config = SafeConfigParser()
            config.readfp(file('/usr/share/python/debian_defaults'))
            value = config.get('DEFAULT', 'supported-versions')
            _supported_versions = [s.strip() for s in value.split(',')]
        else:
            cmd = ['/usr/bin/apt-cache', '--no-all-versions',
                   'show', 'python-all']
            try:
                import subprocess
                p = subprocess.Popen(cmd, bufsize=1,
                                     shell=False, stdout=subprocess.PIPE)
                fd = p.stdout
            except ImportError:
                fd = os.popen(' '.join(cmd))
            depends = None
            for line in fd:
                if line.startswith('Depends:'):
                    depends = line.split(':', 1)[1].strip().split(',')
            fd.close()
            depends = [re.sub(r'\s*(\S+)[ (]?.*', r'\1', s) for s in depends]
            _supported_versions = depends
    if version_only:
        return [v[6:] for v in _supported_versions]
    else:
        return _supported_versions

_default_version = None
def default_version(version_only=False):
    global _default_version
    if not _default_version:
        _default_version = link = os.readlink('/usr/bin/python')
    if version_only:
        return _default_version[6:]
    else:
        return _default_version

def requested_versions(vstring, version_only=False):
    versions = None
    vinfo = parse_versions(vstring)
    supported = supported_versions(version_only=True)
    if len(vinfo) == 1:
        if 'all' in vinfo:
            versions = supported
        elif 'current' in vinfo:
            versions = [default_version(version_only=True)]
        else:
            versions = vinfo['versions'].intersection(supported)
    elif 'all' in vinfo and 'current' in vinfo:
        raise ValueError, "both `current' and `all' in version string"
    elif 'all' in vinfo:
        versions = versions = vinfo['versions'].intersection(supported)
    elif 'current' in vinfo:
        current = default_version(version_only=True)
        if not current in vinfo['versions']:
            raise ValueError, "`current' version not in supported versions"
        versions = [current]
    else:
        raise ValueError, 'error in version string'
    if not versions:
        raise ValueError, 'empty set of versions'
    if version_only:
        return versions
    else:
        return ['python%s' % v for v in versions]

def installed_versions(version_only=False):
    import glob
    supported = supported_versions()
    versions = [os.path.basename(s)
                for s in glob.glob('/usr/bin/python[0-9].[0-9]')
                if os.path.basename(s) in supported]
    versions.sort()
    if version_only:
        return [v[6:] for v in versions]
    else:
        return versions

def extract_pyversion_attribute(fn, pkg):
    """read the debian/control file, extract the XS-Python-Version
    field; check that XB-Python-Version exists for the package."""

    version = None
    sversion = None
    section = None
    for line in file(fn):
        line = line.strip()
        if line == '':
            section = None
        elif line.startswith('Source:'):
            section = 'Source'
        elif line.startswith('Package: ' + pkg):
            section = self.name
        elif line.startswith('XS-Python-Version:'):
            if section != 'Source':
                raise ValueError, \
                      'attribute XS-Python-Version not in Source section'
            sversion = line.split(':', 1)[1].strip()
        elif line.startswith('XB-Python-Version:'):
            if section == pkg:
                version = line.split(':', 1)[1].strip()
    if pkg == 'Source':
        if sversion == None:
            raise ValueError, 'missing XS-Python-Version in control file'
        return sversion
    if version == None:
        raise ValueError, \
              'missing XB-Python-Version for package `%s' % pkg
    return version


def main():
    from optparse import OptionParser
    usage = '[-v] [-h] [-d|--default] [-s|--supported] [-i|--installed] [-r|--requested <version string>|<control file>]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--default',
                      help='print the default python version',
                      action='store_true', dest='default')
    parser.add_option('-s', '--supported',
                      help='print the supported python versions',
                      action='store_true', dest='supported')
    parser.add_option('-r', '--requested',
                      help='print the python versions requested by a build; the argument is either the name of a control file or the value of the XS-Python-Version attribute',
                      action='store', dest='versions')
    parser.add_option('-i', '--installed',
                      help='print the installed supported python versions',
                      action='store_true', dest='installed')
    parser.add_option('-v', '--version',
                      help='print just the version number(s)',
                      default=False, action='store_true', dest='version_only')
    opts, args = parser.parse_args()
    program = os.path.basename(sys.argv[0])

    if opts.default:
        print default_version(opts.version_only)
    elif opts.supported:
        print ' '.join(supported_versions(opts.version_only))
    elif opts.installed:
        print ' '.join(installed_versions(opts.version_only))
    elif opts.versions:
        try:
            if os.path.isfile(opts.versions):
                vs = extract_pyversion_attribute(opts.versions, 'Source')
            else:
                vs = opts.versions
            print ' '.join(requested_versions(vs, opts.version_only))
        except ValueError, msg:
            print "%s: %s" % (program, msg)
            sys.exit(1)
    else:
        print "usage: %s %s" % (program, usage)
        sys.exit(1)

if __name__ == '__main__':
    main()
