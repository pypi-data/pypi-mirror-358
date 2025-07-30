# -*- coding: utf-8; -*-
################################################################################
#
#  WuttaSync -- Wutta Framework for data import/export and real-time sync
#  Copyright © 2024 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
WuttaSync - ``wutta`` subcommands

This namespace exposes the following:

* :func:`~wuttasync.cli.base.import_command()`
* :func:`~wuttasync.cli.base.file_import_command()`
* :class:`~wuttasync.cli.base.ImportCommandHandler`
"""

from .base import import_command, file_import_command, ImportCommandHandler

# nb. must bring in all modules for discovery to work
from . import import_csv
