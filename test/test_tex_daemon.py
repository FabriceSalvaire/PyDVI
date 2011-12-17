#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
#                                              Audit
#
# - 17/12/2011 Fabrice
#   xx
#
#####################################################################################################

#####################################################################################################

from PyDVI.DviParser import dvi_opcodes_tuple
from PyDVI.TexDaemon import TexDaemon

#####################################################################################################

tex_daemon = TexDaemon(working_directory='/tmp/tex_daemon',
                       format='plain',
                       start_code=r'\shipout\hbox{}' '\n',
                       done_code='\n' r'\immediate\write16{DONE}\read-1to\temp ' '\n',
                       done_string='DONE\n',
                       )
tex_daemon.start()

for input in ('Azerty', 'Qwerty'):

    result = tex_daemon.process(r'\shipout\hbox{%s}\message{A message}' % (input))

    print result['log']
    print map(ord, result['dvi'])
    
    #print dvi_opcodes_tuple[ord(result['dvi'][0])]
    #print dvi_opcodes_tuple[ord(result['dvi'][-1])]

tex_daemon.stop()

#####################################################################################################
#
# End
#
#####################################################################################################
