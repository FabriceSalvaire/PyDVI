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
#  - 00/01/2010 fabrice
#  - 13/05/2010 fabrice License !
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['TexDaemon']

#####################################################################################################

import os

from select import select

#####################################################################################################

from DaemonSubprocess import *

#####################################################################################################

### # TODO:  This belongs elsewhere.
### class Interface(object):
###     """Stores useful, but format specific, constants."""
### 
###     def __init__(self, **kwargs):
###         # TODO:  Be more specific about the parameters.
###         self.__dict__ = kwargs
### 
### 
### # TeX knows about these fonts, but Python does not yet know.
### # This list created by command: $tex --ini '&plain' \\dump
### preloaded_fonts = ( 'cmr10', 'cmr9', 'cmr8', 'cmr7', 'cmr6', 'cmr5',
###                     'cmmi10', 'cmmi9', 'cmmi8', 'cmmi7', 'cmmi6',
###                     'cmmi5', 'cmsy10', 'cmsy9', 'cmsy8', 'cmsy7',
###                     'cmsy6', 'cmsy5', 'cmex10', 'cmss10', 'cmssq8',
###                     'cmssi10', 'cmssqi8', 'cmbx10', 'cmbx9', 'cmbx8',
###                     'cmbx7', 'cmbx6', 'cmbx5', 'cmtt10', 'cmtt9',
###                     'cmtt8', 'cmsltt10', 'cmsl10', 'cmsl9', 'cmsl8',
###                     'cmti10', 'cmti9', 'cmti8', 'cmti7', 'cmu10',
###                     'cmmib10', 'cmbsy10', 'cmcsc10', 'cmssbx10',
###                     'cmdunh10', 'cmr7 scaled 2074',
###                     'cmtt10 scaled 1440', 'cmssbx10 scaled 1440',
###                     'manfnt', )
### 
### # Ship out a page that starts with a font def.
### load_font_template = \
### r'''%%
### \begingroup
###   \hoffset 0sp
###   \voffset 0sp
###   \setbox0\hbox{\font\tmp %s\relax\tmp M}%%
###   \ht0 0sp
###   \shipout\box 0
### \endgroup
### '''
### 
### secplain_load_font_template = \
### r'''%%
### \_begingroup
###   \_hoffset 0sp
###   \_voffset 0sp
###   \_setbox0\_hbox{\_font\_tmp %s\_relax\_tmp M}%%
###   \_ht0 0sp
###   \_shipout\_box 0
### \_endgroup
### '''
### 
### plain = Interface(format='plain',
###                   start = r'\shipout\hbox{}' '\n',
###                   done = '\n' r'\immediate\write16{DONE}\read-1to\temp ' '\n',
###                   done_str = 'DONE\n',
###                   stop = '\end' '\n',
###                   preloaded_fonts = preloaded_fonts,
###                   load_font_template = load_font_template,
###                   )
### 
### secplain = Interface(format='secplain',
###                   start = r'\_shipout\_hbox{}' '\n',
###                   done = '\n' r'\_immediate\_write16{DONE}\_read-1to\_temp ' '\n',
###                   done_str = 'DONE\n',
###                   stop = '\_end' '\n',
###                   preloaded_fonts = preloaded_fonts,
###                   load_font_template = secplain_load_font_template,
###                   )

#####################################################################################################

class TexDaemon(DaemonSubprocess):

    fifos = ('texput.tex', 'texput.log', 'texput.dvi')

    ###############################################

    def __init__(self, working_directory, format, start_code, done_code, done_string):

        super(TexDaemon, self).__init__(working_directory)

        self.format = format
        self.start_code = start_code
        self.done_code = done_code
        self.done_string = done_string

    ###############################################

    def make_args(self):

        args = ('tex', '--ipc')
        args += ('--output-comment=""',) # Don't record time of run.
        if self.format not in ('plain', 'tex'):
            fmt = '--fmt=' + self.format
            args += (fmt,)
        args += ('texput.tex',)

        return args

    ###############################################
 
    def start(self):
 
        super(TexDaemon, self).start()
 
        # We will now initialise TeX, and connect to file descriptors.  We need to do some low-level
        # input/output, in order to manage long input strings.  Therefore, we use file descriptors
        # rather than file objects.

        working_directory = self.working_directory
        child = self.child 
        
        # We map output fds to what will be a dictionary key.
        output_fd_dict = self.output_fd_dict = {}
 
        # For us, stdin and stdout are special.
        self.stdin_fd  = child.stdin.fileno()
        self.stdout_fd = child.stdout.fileno()
        self.stderr_fd = child.stderr.fileno()
        
        # Read stdout and stderr to 'log' and 'err' respectively.
        output_fd_dict['log'] = self.stdout_fd
        output_fd_dict['err'] = self.stderr_fd
 
        # Open 'texput.tex', and block until it is available, which is when TeX has started.  Then
        # make 'texput.tex' non-blocking, in case of a long write.
        self.tex_input = os.open(os.path.join(working_directory, 'texput.tex'), os.O_WRONLY)
        make_nonblocking(self.tex_input)
            
        for filename, name in (('texput.log', 'logfile'),
                               ('texput.dvi', 'dvi')):
            fd = os.open(os.path.join(working_directory, filename),
                         os.O_RDONLY|os.O_NONBLOCK)
            output_fd_dict[name] = fd
 
        # Ship out blank page
        result = self.process(self.start_code)
        print result

    ###############################################
 
    def process(self, input_string):

        "Return dictionary with dvi, log, logfile and err entries."
        
        # TeX will read the data, following by the 'done' command.  The 'done' command will cause
        # TeX to write the 'done_str', which signals the end of the process.  It will also pause TeX
        # for input.
        
        result = self._process(input_string + self.done_code, self.done_string)
        
        # TODO: Don't know why the pause is required, but else the program hangs.
        
        self.child.stdin.write('\n') # TeX is waiting for input

        return result

    ###############################################
 
    def _process(self, input_string, done_string):
 
        # Write input_string, and read output, until we are done.  Then gather up the accumulated
        # output, and return as a dictionary.  The input string might be long.  Later, we might
        # allow writing to stdin, in response to errors.
 
        # Initialisation
        output_fds = self.output_fd_dict.values()
        input_fds = [self.tex_input]
 
        output_strings = {}
        for fd in output_fds:
            output_strings[fd] = ''
 
        pointer, len_input_string = 0, len(input_string)
 
        # The main input/ouput loop
        # TODO: magic number, timeout
        done = False
        while not done:

            # timeout in s
            readable, writable = select(output_fds, input_fds, [], .1)[0:2]
            if not readable and pointer == len_input_string:
                self.kill()
                raise SubprocessError, 'subprocess I/O timed out'
                
            if pointer != len_input_string and writable:
                written = os.write(self.tex_input, input_string[pointer:pointer+4096])
                pointer += written
                if pointer == len_input_string:
                    input_fds = []
                
            for fd in readable:

                if self.child.poll() is not None:
                    raise SubprocessError, 'read from terminated subprocess'
                    
                tmp = os.read(fd, 4096)

                if fd == self.stdout_fd and tmp.endswith(done_string):
                    tmp = tmp[:-len(done_string)]
                    done = True

                output_strings[fd] += tmp
 
        if pointer != len_input_string:
            raise SystemError, "TeX said 'done' before end of input."
 
        # Return ouput dictionary
        result = {}
        for name, fd in self.output_fd_dict.items():
            result[name] = output_strings[fd]

        return result

#####################################################################################################
#
# End
#
#####################################################################################################
