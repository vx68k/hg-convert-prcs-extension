# prcs.py - Mercurial convert source for PRCS
# Copyright (C) 2015-2020 Kaz Nishimura
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
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Mercurial convert source for PRCS
"""

import re
import os
import sys
from mercurial import extensions
from hgext.convert.common import NoRepo, commit, converter_source
from hgext.convert.convcmd import source_converters
from prcslib import PrcsVersion, PrcsProject, PrcsError, PrcsCommandError

# Regular expression pattern that checks for main branches.
_MAIN_BRANCH_RE = re.compile(r"^(\d+)$")

class prcs_source(converter_source):
    """Import a PRCS project."""

    def __init__(self, ui, type, path, revs=None):
        """
        initialize a PRCS source
        """
        super(prcs_source, self).__init__(ui, type, path, revs)

        try:
            self._prcs = PrcsProject(path)
            self._revisions = self._prcs.versions()
        except PrcsError:
            raise NoRepo(b"%s does not look like a PRCS project" % path)

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

    def _nearest_ancestor(self, version):
        """Return an indirect parent for a deleted version."""
        if version is None:
            return None
        if isinstance(version, str):
            version = PrcsVersion(version)

        deleted = False
        while self._revisions[str(version)]['deleted']:
            self.ui.note(version, " is deleted\n")
            deleted = True
            version = PrcsVersion(version.major(), version.minor() - 1)
            if version.minor() == 0:
                self.ui.note("No more ancestors on branch ", version.major())
                return None
        if deleted:
            self.ui.note("substituting ", version, "\n")
        return version

    def getheads(self):
        last_minor_version = {}
        for v in self._revisions.iterkeys():
            if not self._revisions[v]['deleted']:
                v = PrcsVersion(v)
                if last_minor_version.get(v.major(), 0) < v.minor():
                    last_minor_version[v.major()] = v.minor()
        return map(
            lambda item: str(PrcsVersion(item[0], item[1])),
            last_minor_version.iteritems())

    def getfile(self, name, version):
        self.ui.debug("prcs_source.getfile: ", name, " ", version, "\n")
        revision = self._revisions[version]
        descriptor = self._descriptor(version)

        files = descriptor.files()
        try:
            a = files[name]
            if a.has_key('symlink'):
                return (a['symlink'], 'l')

            self._prcs.checkout(version, [name])
            file = open(name, 'rb')
            content = file.read()
            file.close()
            # NOTE: Win32 does not always releases the file name.
            if sys.platform != 'win32':
                os.unlink(name)
                dir = os.path.dirname(name)
                if dir:
                    os.removedirs(dir)
            return (content, 'x' if a['mode'] & (0x1 << 6) else '')
        except KeyError:
            # The file with the specified name was deleted.
            raise IOError()

    def getchanges(self, version, full=False):
        self.ui.debug("prcs_source.getchanges: ", version, "\n")
        revision = self._revisions[version]
        descriptor = self._descriptor(version)

        files = []
        copies = {}
        f = descriptor.files()
        p = descriptor.parentversion()
        # Preparing for a deleted parent.
        p = self._nearest_ancestor(p)
        if full or p is None:
            # This is the initial checkin so all files are affected.
            for name in f.iterkeys():
                files.append((name, version))
        else:
            pf = self._descriptor(p).files()
            # Handling added or changed files.
            for name, a in f.iteritems():
                if pf.has_key(name):
                    pa = pf[name]
                    if a.has_key('symlink'):
                        if not pa.has_key('symlink'):
                            # Changed from a regular file to a symlink.
                            files.append((name, version))
                    elif pa.has_key('symlink'):
                        # Changed from a symlink to a regular file.
                        files.append((name, version))
                    elif a['id'] != pa['id'] \
                            or a['revision'] != pa['revision'] \
                            or (a['mode'] ^ pa['mode']) & (0x1 << 6):
                        files.append((name, version))
                else:
                    # Added.
                    files.append((name, version))
            # Handling deleted or renamed files.
            pnamebyid = {}
            for pname, pa in pf.iteritems():
                if not f.has_key(pname):
                    # Removed (or renamed).
                    files.append((pname, version))
                if not pa.has_key('symlink'):
                    pnamebyid[pa['id']] = pname
            # Handling renamed files for copies.
            for name, a in f.iteritems():
                if not a.has_key('symlink') and \
                        pnamebyid.has_key(a['id']):
                    pname = pnamebyid[a['id']]
                    if name != pname:
                        self.ui.note(pname, " was renamed to ", name, "\n")
                        copies[name] = pname
        return files, copies, set()

    def getcommit(self, version):
        self.ui.debug("prcs_source.getcommit: ", version, "\n")
        revision = self._revisions[version]
        descriptor = self._descriptor(version)

        parents = []
        p = descriptor.parentversion()
        # Preparing for a deleted parent.
        p = self._nearest_ancestor(p)
        if p is not None:
            parents.append(str(p))
        for mp in descriptor.mergeparents():
            # Preparing for a deleted merge parent.
            mp = self._nearest_ancestor(mp)
            if mp is not None:
                parents.append(str(mp))

        branch = PrcsVersion(version).major()
        if _MAIN_BRANCH_RE.match(branch):
            branch = None
        return commit(
                revision['author'], revision['date'].isoformat(" "),
                descriptor.message(), parents, branch)

    def gettags(self):
        """Return an empty dictionary since PRCS has no tags."""
        return {}
