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
#  - 17/01/2010 fabrice
#  - 13/05/2010 fabrice
#
#####################################################################################################

#####################################################################################################

__all__ = ['FontMap']

#####################################################################################################

from Logging import print_card
from TextFile import TextFile

#####################################################################################################

class FontMapEntry(object):

    ###############################################

    def __init__(self, tex_name, ps_font_name, effects, encoding, filename):

        self.tex_name = tex_name
        self.ps_font_name = ps_font_name
        self.effects = effects
        self.encoding = encoding
        self.filename = filename

    ###############################################

    def print_summary(self):

        text = '''Font Map Entry %s

 - PS font name %s
 - effects      %s
 - encoding     %s
 - filename     %s''' % (
            self.tex_name,
            self.ps_font_name,
            self.effects,
            self.encoding,
            self.filename,
            )

        print_card(text)

#####################################################################################################

class FontMap(object):

    """The FontMap class parse a fontmap file.
    """

    ###############################################

    def __init__(self, name, filename=None):

        """Create a FontMap instance.
        """

        self.name = name

        self.map = {}

        if filename is not None:
            try:
                text_file = TextFile(filename)
                for line in text_file:
                    self.__parse_line(line)
            except:
                raise NameError('Bad fontmap file')

    ###############################################
 
    def __getitem__(self, tex_name):
 
        return self.map[tex_name]
 
    ###############################################
 
    def register_entry(self, font_map_entry):
 
        self.map[font_map_entry.tex_name] = font_map_entry
 
    ###############################################
 
    def __parse_line(self, line):
 
        words = [x for x in line.split() if x]
 
        # Merge words enclosed by double quote
        i = 0
        while i < len(words):
 
            word = words[i]
            if word.startswith('"'):
                while not word.endswith('"'):
                    # merge words
                    word += ' ' + words.pop(i+1)
                # and supress enclosing double quotes
                words[i] = word[1:-1]
 
            i += 1
 
        self.__parse_font_map_line(words)
 
    ###############################################
 
    def __parse_font_map_line(self, words):
        
        """Parse a font map line
 
        The format is:
 
          tex_name ps_font_name [effects] [filenames]
 
          - effects are PostScript snippets like ".177 SlantFont",
 
          - filenames begin with one or two '<'.  A filename with the extension '.enc' is an
            encoding file, other filenames are font files. This can be overridden with a left
            bracket: '<[encfile' indicates an encoding file named encfile.
         """
 
        tex_name, ps_font_name = words[:2]
 
        effects, encoding, filename = None, None, None
        for word in words[2:]:
 
            if not word.startswith('<'):
                effects = self.__parse_effects(word)
 
            else:
                word = word.lstrip('<')
 
                if word.startswith('['):
                    assert encoding is None
                    encoding = word[1:]
 
                elif word.endswith('.enc'):
                    assert encoding is None
                    encoding = word
 
                else:
                    assert filename is None
                    filename = word
 
        font_map_entry = FontMapEntry(tex_name, ps_font_name, effects, encoding, filename)
        self.register_entry(font_map_entry)
 
    ###############################################
 
    @staticmethod
    def __parse_effects(word):
 
        effects_list = word.split()
   
        effects = {}
        for key_word in 'SlantFont', 'ExtendFont':
            
            try:
                # parameter is followed by the command
                parameter_index = effects_list.index(key_word) -1
                effects[key_word] = float(effects_list[parameter_index])
                
            except ValueError: # key word was not found
                pass
            
        return effects
 
    ###############################################
 
    def print_summary(self):
 
        print_card('Font Map %s' % (self.name))
 
        for font_map_entry in self.map.values():
            font_map_entry.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################

