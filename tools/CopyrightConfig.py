####################################################################################################
#
# PyDVI - A Python Library to Process DVI Stream.
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
#  - 16/01/2010 fabrice
#
####################################################################################################

####################################################################################################

__ALL__ = ['mime_extensions', 'mime_copyright']

####################################################################################################

from Logging import format_card, remove_enclosing_new_line

####################################################################################################

mime_extensions = (
    ('sh', ('py', 'sh')),
    ('c',  ('c', 'h', 'cpp', 'hpp', 'cxx', 'hxx', 'i')),
    )

###################################################

copyright_text = remove_enclosing_new_line('''
PyDVI - A Python Library to Process DVI Stream.
Copyright (C) 2009 Salvaire Fabrice
''')

width = 100

mime_copyright = {}

###################################################

mime_copyright['sh'] = format_card(copyright_text,
                                   centered=True,
                                   width=width,
                                   rule_char='#',
                                   border = True,
                                   )

###################################################

def format_c(text):

    text += '\\'

    formated_text = ''

    first_line = True

    for line in text.split('\n'):
        if first_line:
            formated_text += '\\'
            first_line = False
        else:
            formated_text += ' '
        formated_text += line + '\n'
            
    return formated_text

mime_copyright['c'] = format_c(format_card(copyright_text,
                                           centered=True,
                                           width=width,
                                           rule_char='*',
                                           border = True,
                                           ))

####################################################################################################
#
# End
#
####################################################################################################
