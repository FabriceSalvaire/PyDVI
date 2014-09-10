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

####################################################################################################

import os

####################################################################################################

import PyDviGui.Tools.Path as PathTools # due to Path class

####################################################################################################

_this_file = PathTools.to_absolute_path(__file__)

class Path(object):

    module_directory = PathTools.parent_directory_of(_this_file, step=2)
    config_directory = os.path.dirname(_this_file)
    share_directory = os.path.realpath(os.path.join(config_directory, '..', '..', 'share'))

####################################################################################################

class Logging(object):

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file):

        return PathTools.find(config_file, Logging.directories)

####################################################################################################

class Icon(object):

    size = '32x32'
    icon_directory = os.path.join(Path.share_directory, 'icons', size)
    
    ##############################################

    @staticmethod
    def find(file_name):

        return PathTools.find(file_name, (Icon.icon_directory,))

####################################################################################################
#
# End
#
####################################################################################################
