####################################################################################################
# 
# PyDVI - A Python Library to Process DVI Stream
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
####################################################################################################

####################################################################################################
#
# Audit
#
#  - 09/10/2011 fabrice
#
####################################################################################################

####################################################################################################

__all__ = ['pydvi_version']

####################################################################################################

from PyDVI.Tools.RevisionVersion import RevisionVersion

####################################################################################################

#: defines the PyDvi revision version.
pydvi_version = RevisionVersion((0, # major version
                                 1, # minor version
                                 0, # revision version
                                 ))

####################################################################################################
#
# End
#
####################################################################################################
