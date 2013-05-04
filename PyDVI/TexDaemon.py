####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
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
#   License !
#
####################################################################################################

""" This module provides a TeX Daemon interface.
"""

####################################################################################################

__all__ = ['TexDaemon']

####################################################################################################

import logging
import os

from select import select

####################################################################################################

from PyDVI.Tools.DaemonSubprocess import *

####################################################################################################

logger = logging.getLogger(__name__)

####################################################################################################

class TexDaemon(DaemonSubprocess):

    """ This class implements a TeX Daemon Subprocess.
    """

    #: Defines the FIFOs used by the TeX daemon to communicate.
    fifos = ('texput.tex', 'texput.log', 'texput.dvi')

    ##############################################

    def __init__(self, working_directory, tex_format, start_code, done_code, done_string):

        """ The TeX process run in the working directory *working_directory*.

        The argument *tex_format* specify the format to be used by TeX.

        The argument *start_code* defines the code to be executed first by TeX.

        The argument *done_code* defines to code to be appended to the input code.  This code must
        print on the standard output a *done_string* string in order to indicate the page was
        successfully and completely ship-out.
        """

        super(TexDaemon, self).__init__(working_directory)

        self.tex_format = tex_format
        self.start_code = start_code
        self.done_code = done_code
        self.done_string = done_string

    ##############################################

    def make_args(self):

        """ Return the TeX calling sequence. """

        args = ('tex', '--ipc')
        args += ('--output-comment=""',) # Don't record time of run.
        if self.tex_format not in ('plain', 'tex'):
            fmt = '--fmt=' + self.tex_format
            args += (fmt,)
        args += ('texput.tex',)

        return args

    ##############################################
 
    def start(self):

        """ Start the TeX daemon. """
 
        super(TexDaemon, self).start()
 
        # We will now initialise TeX, and connect to file descriptors.  We need to do some low-level
        # input/output, in order to manage long input strings.  Therefore, we use file descriptors
        # rather than file objects.

        # We map output fds to a dictionary
        self.output_fd_dict = {}
        self.stdout_fd = self.output_fd_dict['stdout'] = self.child.stdout.fileno()
        self.stderr_fd = self.output_fd_dict['stderr'] = self.child.stderr.fileno()
 
        # Open 'texput.tex', and block until it is available, which is when TeX has started.
        # Then make 'texput.tex' non-blocking, in case of a long write.
        self.tex_input_fd = os.open(os.path.join(self.working_directory, 'texput.tex'), os.O_WRONLY)
        make_nonblocking(self.tex_input_fd)
            
        # Open 'texput.log' and 'texput.dvi'
        for filename, name in (('texput.log', 'logfile'),
                               ('texput.dvi', 'dvi')):
            fd = os.open(os.path.join(self.working_directory, filename), os.O_RDONLY|os.O_NONBLOCK)
            self.output_fd_dict[name] = fd
 
        # Ship out a blank page
        logger.info("Ship out start page")
        result = self.process(self.start_code)

        return result

    ##############################################
 
    def process(self, input_string):

        """ Process the input string and return a dictionary with 'dvi', 'stdout', 'logfile' and
        'stderr' entries.
        """
        
        # TeX will read the data, following by the 'done' command.  The 'done' command will cause
        # TeX to write the 'done_string', which signals the end of the process.  It will also pause
        # TeX for input.
        
        result = self._process(input_string + self.done_code, self.done_string)
        
        # TeX is waiting for input
        self.child.stdin.write('\n')

        return result

    ##############################################
 
    def _process(self, input_string, done_string):

        """ Process the input string. """

        logger.info("Write to 'input.tex':\n" + input_string)
 
        # Write input_string, and read output, until we are done.  Then gather up the accumulated
        # output, and return as a dictionary.  The input string might be long.  Later, we might
        # allow writing to stdin, in response to errors.
 
        # Initialise input/output file descriptor list
        output_fds = self.output_fd_dict.values()
        input_fds = [self.tex_input_fd]

        # Initialise output string dictionary
        output_strings = {}
        for fd in output_fds:
            output_strings[fd] = ''
 
        input_pointer, input_string_length = 0, len(input_string)
 
        # The main input/ouput loop
        # TODO: magic number, timeout
        done = False
        while not done:

            # Wait for input/ouput to be ready
            timeout = .1 # s
            readable, writable = select(output_fds, input_fds, (), timeout)[:2]

            # If input string was sent and output_fds are not readable
            if not readable and input_pointer == input_string_length:
                self.kill()
                raise SubprocessError('Subprocess I/O timed out')
                
            # If input has to be filled and input_fd is writable
            if input_pointer != input_string_length and writable:
                # Try to write 4096 bytes on input_fd
                written = os.write(self.tex_input_fd, input_string[input_pointer:input_pointer+4096])
                # If input_pointer was completely sent then disable input_fd
                input_pointer += written
                if input_pointer == input_string_length:
                    input_fds = ()
                
            # Read output_fds
            for fd in readable:
                if self.child.poll() is not None:
                    raise SubprocessError('Read from terminated subprocess')
                # Read 4096 bytes
                output_string = os.read(fd, 4096)
                # Remove done_string in stdout if necessary
                if fd == self.stdout_fd and output_string.endswith(done_string):
                    output_string = output_string[:-len(done_string)]
                    done = True
                # Concatenate output
                output_strings[fd] += output_string

        # Check input was completely read
        if input_pointer != input_string_length:
            raise SystemError("TeX said 'done' before end of input.")
 
        # Return ouput dictionary
        result = {}
        for name, fd in self.output_fd_dict.items():
            result[name] = output_strings[fd]

        return result

####################################################################################################
#
# End
#
####################################################################################################
