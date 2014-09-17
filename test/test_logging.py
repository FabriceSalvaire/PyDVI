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
# Audit
#
####################################################################################################

####################################################################################################

from PyDvi.Tools.Logging import *

####################################################################################################

text = remove_enclosing_new_line('''
PyDvi - A Python Library to Process DVI Stream.
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

####################################################################################################
#
# End
#
####################################################################################################
