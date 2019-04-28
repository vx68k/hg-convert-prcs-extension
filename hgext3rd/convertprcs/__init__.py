# __init__.py for convertprcs
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

"""PRCS source add-on for the convert extension"""

from mercurial import extensions

def extsetup(ui):
    try:
        # import hgext.convert
        global _convert
        _convert = extensions.find('convert')

        # from hgext.convert.convcmd import source_converters
        _convcmd = __import__(
                _convert.__name__ + ".convcmd", globals(), locals(),
                ['source_converters'])
        source_converters = _convcmd.source_converters

        # NOTE: The following import requires _convert
        from .prcs import prcs_source
        source_converters.append(('prcs', prcs_source, 'branchsort'))

        ui.debug("The PRCS converter source was added\n")
    except KeyError:
        ui.warn("convertprcs setup failed since it depends on convert\n")
