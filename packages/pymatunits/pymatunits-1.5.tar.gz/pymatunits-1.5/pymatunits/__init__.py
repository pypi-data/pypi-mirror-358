"""
This file is a part of pymatunits, a package of assorted utilities
related to material properties, unit systems, and other helper functions
for computational model development

Copyright (C) 2023 Adam Cox

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""
import logging

__version__ = '1.5'

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(levelname)s - %(name)s - %(asctime)s :\n%(message)s\n',
    r'%b %d, %Y %I:%M:%S %p')
numerical_tolerance = 1e-5
