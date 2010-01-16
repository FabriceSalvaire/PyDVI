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
#  - 10/01/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__= ['remove_enclosing_new_line', 'format_card', 'print_card']

#####################################################################################################

def remove_enclosing_new_line(text):
    return text[1:-1]

#####################################################################################################

def format_card(text,
               centered=False,
               width=80,
               rule_char='#',
               newline=False,
               border=False,
               bottom_rule=True):

    formated_text = ''

    rule_line = rule_char*width

    if border:
        border_string = rule_char + ' '
    else:
        border_string = ''

    def format_lines(text):

        formated_text = ''
        for line in text.split('\n'):
            formated_text += format_line(line) + '\n'

        return formated_text

    def format_line(text):

        line = border_string
        if centered:
            line += text.center(width)
        else:
            line += text

        return line

    if newline:
        formated_text += '\n'

    formated_text += rule_line + '\n' + border_string + '\n'
             
    if isinstance(text, list):
        for item in text:
            formated_text += format_lines(item)
    else:
        formated_text += format_lines(text)

    formated_text += border_string + '\n'

    if bottom_rule:
        formated_text += rule_line

    return formated_text

#####################################################################################################

def print_card(text, **kwargs):
    
    print format_card(text, **kwargs)
    
#####################################################################################################
#
# End
#
#####################################################################################################
