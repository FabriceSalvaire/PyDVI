####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
#                                              Audit
#
# - 17/12/2011 Fabrice
#   xx
#
####################################################################################################

####################################################################################################

import logging

####################################################################################################

from PyDVI.DviParser import dvi_opcodes_tuple, DviParser
from PyDVI.TexDaemon import TexDaemon
from PyDVI.Tools.Stream import ByteStream

####################################################################################################

logging.basicConfig(level=logging.DEBUG)

####################################################################################################

def print_result(result):
    line = '-'*80
    for key, value in result.iteritems():
        # print line
        if key != 'dvi':
            print key, ':\n', value
        else:
            print 'DVI :\n', [ord(x) for x in value]
        print line


####################################################################################################

class TeXParameters(object):
    """ Stores useful, but format specific, constants. """
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

# TeX knows about these fonts, but Python does not yet know.
# This list created by command: $tex --ini '&plain' \\dump
preloaded_fonts = ( 'cmr10', 'cmr9', 'cmr8', 'cmr7', 'cmr6', 'cmr5',
                    'cmmi10', 'cmmi9', 'cmmi8', 'cmmi7', 'cmmi6',
                    'cmmi5', 'cmsy10', 'cmsy9', 'cmsy8', 'cmsy7',
                    'cmsy6', 'cmsy5', 'cmex10', 'cmss10', 'cmssq8',
                    'cmssi10', 'cmssqi8', 'cmbx10', 'cmbx9', 'cmbx8',
                    'cmbx7', 'cmbx6', 'cmbx5', 'cmtt10', 'cmtt9',
                    'cmtt8', 'cmsltt10', 'cmsl10', 'cmsl9', 'cmsl8',
                    'cmti10', 'cmti9', 'cmti8', 'cmti7', 'cmu10',
                    'cmmib10', 'cmbsy10', 'cmcsc10', 'cmssbx10',
                    'cmdunh10', 'cmr7 scaled 2074',
                    'cmtt10 scaled 1440', 'cmssbx10 scaled 1440',
                    'manfnt', )

# Ship out a page that starts with a font def.
load_font_template = \
r'''%%
\begingroup
  \hoffset 0sp
  \voffset 0sp
  \setbox0\hbox{\font\tmp %s\relax\tmp M}%%
  \ht0 0sp
  \shipout\box 0
\endgroup
'''

secplain_load_font_template = \
r'''%%
\_begingroup
  \_hoffset 0sp
  \_voffset 0sp
  \_setbox0\_hbox{\_font\_tmp %s\_relax\_tmp M}%%
  \_ht0 0sp
  \_shipout\_box 0
\_endgroup
'''

plain = TeXParameters(tex_format='plain',
                      start=r'\shipout\hbox{}' '\n',
                      done='\n' r'\immediate\write16{DONE}\read-1to\temp ' '\n',
                      done_str='DONE\n',
                      stop='\end' '\n',
                      preloaded_fonts=preloaded_fonts,
                      load_font_template=load_font_template,
                      )

secplain = TeXParameters(tex_format='secplain',
                         start=r'\_shipout\_hbox{}' '\n',
                         done='\n' r'\_immediate\_write16{DONE}\_read-1to\_temp ' '\n',
                         done_str='DONE\n',
                         stop='\_end' '\n',
                         preloaded_fonts=preloaded_fonts,
                         load_font_template=secplain_load_font_template,
                         )

####################################################################################################

dvi_parser = DviParser()

tex_daemon = TexDaemon(working_directory='/tmp/tex_daemon',
                       tex_format='plain',
                       start_code=r'\shipout\hbox{}' '\n',
                       done_code='\n' r'\immediate\write16{DONE}\read-1to\temp ' '\n',
                       done_string='DONE\n',
                       )
result = tex_daemon.start()
print_result(result)
print dvi_opcodes_tuple[ord(result['dvi'][0])]
print dvi_opcodes_tuple[ord(result['dvi'][-1])]

dvi_parser._reset()
dvi_parser.stream = ByteStream(result['dvi'])
dvi_parser._process_preambule()
dvi_parser.dvi_program.print_summary()

for text in 'Azerty', 'Qwerty':

    text_input = r'\shipout\hbox{%s}\message{Shipout a page}' % (text)
    result = tex_daemon.process(text_input)
    print_result(result)
    print dvi_opcodes_tuple[ord(result['dvi'][0])]
    print dvi_opcodes_tuple[ord(result['dvi'][-1])]

    dvi_parser.stream = ByteStream(result['dvi'])
    dvi_parser.process_page_forward()
    dvi_parser.dvi_program.print_summary()
    dvi_parser.dvi_program.pages[-1].print_program()

###text_input = '\_end' '\n'
###result = tex_daemon.process(text_input)
###print_result(result)

# Done by dtor
# tex_daemon.stop()

####################################################################################################
#
# End
#
####################################################################################################
