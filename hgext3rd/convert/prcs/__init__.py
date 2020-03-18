# hgext3rd/convert/prcs/__init__.py - package hgext3rd.convert.prcs
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
Mercurial extension to enable the PRCS source for the Convert extension
"""

from __future__ import absolute_import
from hgext.convert.convcmd import source_converters
from .prcs import prcs_source

def extsetup(ui):
    """
    set up the convert.prcs extension
    """
    source_converters.append(
        (b"prcs", prcs_source, b"branchsort")
    )
