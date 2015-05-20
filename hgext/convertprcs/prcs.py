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

# from common import converter_source
from . import _convert
_common = __import__(
        _convert.__name__ + '.common', globals(), locals(),
        ['converter_source'])
converter_source = _common.converter_source

class prcs_source(converter_source):
    """Import a PRCS project."""

    def __init__(self, ui, path=None, rev=None):
        super(prcs_source, self).__init__(ui, path, rev)

        try:
            from prcslib import PrcsProject, PrcsError, PrcsCommandError
        except ImportError:
            ui.warn("Module prcslib is not available")
            raise _common.NoRepo()

        try:
            self._prcs = PrcsProject(path)
            self._revisions = self._prcs.revisions()
        except PrcsCommandError as error:
            ui.note(error.error_message)
            raise _common.NoRepo()
        except PrcsError:
            raise _common.NoRepo()

    def getheads(self):
        return []

    def getchanges(self, version, full):
        return [], {}, set()

    def gettags(self):
        """Return an empty dictionary since PRCS has no tags."""
        return {}
