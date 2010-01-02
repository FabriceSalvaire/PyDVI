#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
# Derived from: Mathtran
#   Copyright: (c) 2007 The Open University, Milton Keynes, UK
#   License: GPL version 2 or (at your option) any later version.
#
#####################################################################################################

#####################################################################################################
#
# Audit
#
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['make_nonblocking', 'SubprocessError', 'DaemonSubprocess']

#####################################################################################################

import fcntl # For non-blocking file descriptor
import os
import signal

from subprocess import Popen, PIPE

#####################################################################################################

def make_nonblocking(fd):

    '''Makes a file descriptor non-blocking.

    When a non-blocking file is read, the read does not wait for end-of-file.  Instead, the read can
    return just as soon as there is nothing left to read.  This might be because a buffer is empty.

    See Python Cookbook, Recipe 6.6
    '''

    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

#####################################################################################################

class SubprocessError(EnvironmentError):
 
    pass

#####################################################################################################

class DaemonSubprocess(object):

    fifos = ()

    ###############################################

    def __init__(self, working_directory):

        self.working_directory = os.path.abspath(working_directory)

        # try
        os.mkdir(working_directory)

        for name in self.fifos:
            os.mkfifo(os.path.join(self.working_directory, name))

        self.child = None

    ###############################################

    def __del__(self):

        try:
            self.stop()

        finally:

            if self.working_directory is not None:

                for filename in os.listdir(self.working_directory):
                    os.remove(os.path.join(self.working_directory, filename))

                os.rmdir(self.working_directory)

    ###############################################

    def restart(self):

        self.stop()
        self.start()

    ###############################################

    def start(self):

        child = self.child = Popen(self.make_args(),
                                   cwd=self.working_directory,
                                   stdin=PIPE, stdout=PIPE, stderr=PIPE)

        for fd in child.stdin, child.stdout, child.stderr:
            make_nonblocking(fd)

    ###############################################

    def stop(self):

        # poll: check if child process has terminated

        if self.child is not None and self.child.poll() is None:
            self.kill()

        self.child = None

    ###############################################

    def kill(self):

        os.kill(self.child.pid, signal.SIGKILL)
        self.child.wait()

    ###############################################

    def make_args(self):

        raise NotImplementedError

#####################################################################################################
#
# End
#
#####################################################################################################
