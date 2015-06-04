# prcs.py for convertprcs
# Copyright (C) 2015 Kaz Nishimura
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import sys

# from hgext.convert.common import converter_source
from . import _convert
_common = __import__(
        _convert.__name__ + '.common', globals(), locals(),
        ['converter_source', 'commit'])
converter_source = _common.converter_source
commit = _common.commit

from prcslib import PrcsVersion, PrcsProject, PrcsError, PrcsCommandError

# Regular expression pattern that checks for main branches.
_MAIN_BRANCH_RE = re.compile(r"^(\d+)$")

class prcs_source(converter_source):
    """Import a PRCS project."""

    def __init__(self, ui, path=None, rev=None):
        super(prcs_source, self).__init__(ui, path, rev)

        try:
            self._prcs = PrcsProject(path)
            self._revisions = self._prcs.revisions()
        except PrcsCommandError as error:
            ui.note(error.error_message)
            raise _common.NoRepo()
        except PrcsError:
            raise _common.NoRepo()

        self._cached_descriptor = {}

    def _descriptor(self, version):
        """Return a revision descriptor with caching."""
        if not isinstance(version, str):
            version = str(version)
        if self._cached_descriptor.has_key(version):
            return self._cached_descriptor[version]

        descriptor = self._prcs.descriptor(version)
        self._cached_descriptor[version] = descriptor
        return descriptor

    def getheads(self):
        last_minor_version = {}
        for v in self._revisions.iterkeys():
            if not self._revisions[v]['deleted']:
                v = PrcsVersion(v)
                if last_minor_version.get(v.major, 0) < v.minor:
                    last_minor_version[v.major] = v.minor
        return map(
                lambda (major, minor): str(PrcsVersion(major, minor)),
                last_minor_version.iteritems())

    def getfile(self, name, version):
        self.ui.debug("prcs_source.getfile: ", name, " ", version, "\n")
        revision = self._revisions[version]
        descriptor = self._descriptor(version)

        files = descriptor.files()
        try:
            attributes = files[name]
            if attributes.has_key('symlink'):
                return (attributes['symlink'], 'l')

            self._prcs.checkout(version, [name])
            file = open(name, 'rb')
            content = file.read()
            file.close()
            # NOTE: Win32 does not always releases the file name.
            if sys.platform != 'win32':
                os.unlink(name)
            return (content, 'x' if attributes['mode'] & 0100 else '')
        except KeyError:
            # The file with the specified name was deleted.
            raise IOError()

    def getchanges(self, version, full=False):
        self.ui.debug("prcs_source.getchanges: ", version, "\n")
        revision = self._revisions[version]
        descriptor = self._descriptor(version)

        changes = []
        files = descriptor.files()
        parent = descriptor.parentversion()
        if full or parent is None:
            # This is the initial checkin so all files are affected.
            for name in files.iterkeys():
                changes.append((name, version))
        else:
            pf = self._descriptor(parent).files()
            # Handling added or changed files.
            for name, attributes in files.iteritems():
                if pf.has_key(name):
                    pa = pf[name]
                    if attributes.has_key('symlink'):
                        if not pa.has_key('symlink'):
                            # Changed from a regular file to a symlink.
                            changes.append((name, version))
                    elif pa.has_key('symlink'):
                        # Changed from a symlink to a regular file.
                        changes.append((name, version))
                    elif attributes['id'] != pa['id'] \
                            or attributes['revision'] != pa['revision'] \
                            or (attributes['mode'] ^ pa['mode']) & 0100:
                        changes.append((name, version))
                else:
                    # Added.
                    changes.append((name, version))
            # Handling deleted or renamed files.
            for name in pf.iterkeys():
                if not files.has_key(name):
                    # Removed (or renamed).
                    # TODO: Handle renamed files.
                    changes.append((name, version))
        return (changes, {})

    def getcommit(self, version):
        self.ui.debug("getcommit ", version, "\n")
        revision = self._revisions[version]
        descriptor = self._descriptor(version)

        parent = []
        p = descriptor.parentversion()
        if p is not None:
            if self._revisions[str(p)]['deleted']:
                self.ui.debug("Parent version ", p, " was deleted\n")
                p = self._nearest_ancestor(p)
                self.ui.debug("The nearest version is ", p, "\n")
            if p is not None:
                parent.append(str(p))
        for p in descriptor.mergeparents():
            parent.append(p)

        branch = PrcsVersion(version).major
        if _MAIN_BRANCH_RE.match(branch):
            branch = None
        return commit(
                revision['author'], revision['date'].isoformat(" "),
                descriptor.message(), parent, branch)

    def _nearest_ancestor(self, version):
        """Return an indirect parent for a deleted version."""
        if isinstance(version, str):
            version = PrcsVersion(version)

        while self._revisions[str(version)]['deleted']:
            version.minor -= 1
            if version.minor == 0:
                return None
        return version

    def gettags(self):
        """Return an empty dictionary since PRCS has no tags."""
        return {}
