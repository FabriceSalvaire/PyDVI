####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Audit
#
#  - 10/01/2010 fabrice
#  - 13/05/2010 fabrice
#
####################################################################################################

####################################################################################################

__ALL__ = ['remove_enclosing_new_line', 'format_card', 'print_card']

####################################################################################################

def remove_enclosing_new_line(text):

    """ Return a copy of the string *text* with leading and trailing newline removed.
    """
    
    i_min =  1 if text[1]  == '\n' else 0
    i_max = -1 if text[-1] == '\n' else None

    return text[i_min:i_max]

####################################################################################################

def format_card(text,
               centered=False,
               width=80,
               rule_char='#',
               newline=False,
               border=False,
               bottom_rule=True):

    """ Format the string *text* as a card::

***************************************************
*
*                      Title
*
* xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx
* xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx
* xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx
* xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx xxxxxxxxxx
*
***************************************************

    *centered*
      center the text in the card

    *width*
      width of the card

    *rule_char*
      character used to draw the rule

    *newline*
      insert a new line before the card

    *border*
      draw a left vertical rule

    *bottom_rule*
      draw a bottom horizontal rule
    """

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

####################################################################################################

def print_card(text, **kwargs):

    """ Print the string *text* formated by :meth:`format_card`.  The remaining keyword arguments
    *kwargs* are passed to :meth:`format_card`.
    """
    
    print format_card(text, **kwargs)
    
####################################################################################################
#
# End
#
####################################################################################################
