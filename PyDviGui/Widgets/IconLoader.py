####################################################################################################
# 
# PyDvi - A Python Library to Process DVI Stream
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

""" Inspired from KIcon. """

####################################################################################################

from PyQt4 import QtCore, QtGui

####################################################################################################

from ..Tools.Singleton import singleton
import PyDviGui.Config.ConfigInstall as ConfigInstall

####################################################################################################

@singleton
class IconLoader(object):

    ##############################################

    def __init__(self):

        self._cache = {}

    ##############################################

    def __getitem__(self, file_name):

        if file_name not in self._cache:
            absolut_file_name = self._find(file_name)
            self._cache[file_name] = QtGui.QIcon(absolut_file_name)
        return self._cache[file_name]

    ##############################################

    def _find(self, file_name, extension='.png'):

        return ConfigInstall.Icon.find(file_name + extension)

####################################################################################################
# 
# End
# 
####################################################################################################
