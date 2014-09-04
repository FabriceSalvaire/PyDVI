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
#
# Derived from: Mathtran
#   Copyright: (c) 2007 The Open University, Milton Keynes, UK
#   License: GPL version 2 or (at your option) any later version.
#
####################################################################################################

####################################################################################################
#
# Audit
# 
# - 17/12/2011 fabrice
#  - license !
#
####################################################################################################

""" This module provides functions to run Daemon process.
"""

####################################################################################################

__ALL__ = ['make_nonblocking', 'SubprocessError', 'DaemonSubprocess']

####################################################################################################

import fcntl # For non-blocking file descriptor
import logging
import os
import signal

from subprocess import Popen, PIPE

####################################################################################################

logger = logging.getLogger(__name__)

####################################################################################################

def make_nonblocking(fd):

    """ Makes a file descriptor non-blocking.

    When a non-blocking file is read, the read does not wait for end-of-file.  Instead, the read can
    return just as soon as there is nothing left to read.  This might be because a buffer is empty.

    See Python Cookbook, Recipe 6.6.
    """

    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags |= os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

####################################################################################################

class SubprocessError(EnvironmentError):
    pass

####################################################################################################

class DaemonSubprocess(object):

    """ This class implements a Daemon sub-process.
    """

    #: List of fifos to be created.
    fifos = ()

    ##############################################

    def __init__(self, working_directory):

        # Create the working directory
        self.working_directory = os.path.abspath(working_directory)
        logger.info('Create working directory %s' % (self.working_directory))
        # try
        os.mkdir(working_directory)

        # Create the Fifos
        for name in self.fifos:
            os.mkfifo(os.path.join(self.working_directory, name))

        self.child = None

    ##############################################

    def __del__(self):

        """ Stop the child process and cleanup the working directory. """

        try:
            self.stop()
        finally:
            if self.working_directory is not None:
                logger.info('Cleanup working directory %s' % (self.working_directory))
                for filename in os.listdir(self.working_directory):
                    os.remove(os.path.join(self.working_directory, filename))
                os.rmdir(self.working_directory)

    ##############################################

    def start(self):

        """ Start the child process. """

        args = self.make_args()
        logger.info('Start child process: ' + ' '.join(args))
        
        child = self.child = Popen(args,
                                   cwd=self.working_directory,
                                   stdin=PIPE, stdout=PIPE, stderr=PIPE)

        for fd in child.stdin, child.stdout, child.stderr:
            make_nonblocking(fd)

    ##############################################

    def make_args(self):

        """ Return the args for Popen. To be implemented in subclass. """
        
        raise NotImplementedError

    ##############################################

    def stop(self):

        """ Stop the child process. """

        logger.info('Stop child process')

        # poll: Check if child process has terminated.
        if self.child is not None and self.child.poll() is None:
            self.kill()

        self.child = None

    ##############################################

    def kill(self):

        """ Send Kill signal to the child process. """

        logger.info('Kill child process')
        self.child.kill()
        # Wait for child process to terminate.
        self.child.wait()

    ##############################################

    def restart(self):

        """ Restart the child process. """

        logger.info('Restart child process')
        self.stop()
        self.start()

####################################################################################################
#
# End
#
####################################################################################################
