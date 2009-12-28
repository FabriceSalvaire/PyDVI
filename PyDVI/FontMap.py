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
#
#####################################################################################################

#####################################################################################################

__all__ = ['FontMap']

#####################################################################################################

import string

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

        print '''
Font Map Entry %s

 - PS font name %s
 - effects      %s
 - encoding     %s
 - filename     %s
''' % (self.tex_name,
       self.ps_font_name,
       self.effects,
       self.encoding,
       self.filename,
       )

#####################################################################################################

class FontMap(object):

    ###############################################

    def __init__(self, name, filename = None):

        self.name = name

        self.map = {}

        if filename is not None:
            self.parse(filename)

    ###############################################

    def __getitem__(self, tex_name):

        return self.map[tex_name]

    ###############################################

    def register_font_map_entry(self, font_map_entry):

        self.map[font_map_entry.tex_name] = font_map_entry

    ###############################################

    def parse(self, filename):

        file = open(filename, 'r')

        for line in file:
        
            line = line.strip()
            
            if len(line) == 0 or line.startswith('%'):
                continue

            words = filter(len, line.split())

            i = 0
            while i < len(words):

                word = words[i]

                if word.startswith('"'):

                    while word.endswith('"') is False:
                        word += ' ' + words.pop(i + 1)
                        
                    words[i] = word[1:-1]

                i += 1

            self.parse_font_map_line(words)

        file.close()

    ###############################################

    def parse_font_map_line(self, words):

         '''
         Parse a font map line
 
         The format is:

           tex_name ps_font_name [effects] [filenames]

           - effects are PostScript snippets like ".177 SlantFont",

           - filenames begin with one or two '<'.  A filename with the extension '.enc' is an
             encoding file, other filenames are font files. This can be overridden with a left
             bracket: '<[encfile' indicates an encoding file named encfile.
 
         '''

         tex_name, ps_font_name = words[:2]

         effects, encoding, filename = None, None, None

         for word in words[2:]:

             if word.startswith('<') is False:
                 effects = self.parse_effects(word)

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

         self.register_font_map_entry(FontMapEntry(tex_name,
                                                   ps_font_name, effects, encoding, filename))

    ###############################################

    def parse_effects(self, word):

        effects_list = word.split()
     
        effects = {}
        
        for key_word in ('SlantFont', 'ExtendFont'):
            
            try:
                parameter_index = effects_list.index(key_word) -1
                
                effects[key_word] = float(effects_list[parameter_index])
                
            except ValueError:
                pass
            
        return effects

    ###############################################

    def print_summary(self):

        print '''
Font Map %s
''' % (self.name)

        for font_map_entry in self.map.values():
            font_map_entry.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################

