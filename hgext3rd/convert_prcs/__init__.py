# __init__.py - initialization of the 'hgext3rd.convert_prcs' package
# Copyright (C) 2020 Kaz Nishimura
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

"""
Mercurial extension to enable the PRCS source in the convert extension

PRCS is a legacy version control system. This extension makes it possible to
convert a PRCS project to a new Mercurial repository.
"""

from __future__ import absolute_import, unicode_literals

from hgext.convert import convcmd
from .prcs import prcs_source

# Mercurial versions with which this extension has been tested.
testedwith = "5.2.2"

def extsetup(ui):
    """
    set up the 'convert_prcs' extension
    """
    convcmd.source_converters.append(
        (b"prcs", prcs_source, b"branchsort")
    )
