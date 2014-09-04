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
#  - 09/10/2011 Fabrice
#
####################################################################################################

"""
This module provides a wrapper for the **Kpathsea** library, cf. http://www.tug.org/kpathsea.
"""

####################################################################################################

__all__ = ['kpsewhich']

####################################################################################################

import logging
import subprocess

####################################################################################################

logger = logging.getLogger(__name__)

####################################################################################################

def kpsewhich(filename, file_format=None, options=None):

    """Wrapper around the :command:`kpsewhich` command, cf. kpsewhich(1).

    *file_format*
      used to specify the file format, see :command:`kpsewhich` help for the file format list.

    *options*
      additional option for :command:`kpsewhich`.

    Examples::

       >>> kpsewhich('cmr10', file_format='tfm')
       '/usr/share/texmf/fonts/tfm/public/cm/cmr10.tfm'
    """

    command = ['kpsewhich']
    if file_format is not None:
        command.append("--format='%s'" % (file_format))
    if options is not None:
        command.append(options)
    command.append(filename)

    shell_command = ' '.join(command)
    logger.info('Run shell command: ' + shell_command)
    pipe = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE)
    stdout = pipe.communicate()[0]
    logger.info('stdout:\n' + stdout)
    path = stdout.rstrip()

    return path if path else None

####################################################################################################
#
# End
#
####################################################################################################
