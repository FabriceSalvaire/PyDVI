#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
# Audit
#
#####################################################################################################

#####################################################################################################

from Logging import *

#####################################################################################################

text = remove_enclosing_new_line('''
PyDVI - Python Library to Process DVI Stream
Copyright (C) 2009 Salvaire Fabrice
''')

print_card(text,
           centered=False,
           width=80,
           rule_char='#',
           newline=False,
           border=False,
           bottom_rule=True)
print '>'
print_card(text,
           centered=True,
           width=80,
           rule_char='#',
           newline=False,
           border=False,
           bottom_rule=True)
print '>'
print_card(text,
           centered=False,
           width=80,
           rule_char='#',
           newline=True,
           border=False,
           bottom_rule=True)
print '>'
print_card(text,
           centered=False,
           width=80,
           rule_char='#',
           newline=False,
           border=True,
           bottom_rule=True)
print '>'
print_card(text,
           centered=False,
           width=80,
           rule_char='#',
           newline=False,
           border=False,
           bottom_rule=False)
print '>'
print_card(text,
           centered=False,
           width=80,
           rule_char='*',
           newline=False,
           border=True,
           bottom_rule=True)

#####################################################################################################
#
# End
#
#####################################################################################################
