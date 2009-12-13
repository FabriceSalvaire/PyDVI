#####################################################################################################

import subprocess
import string

#####################################################################################################

class Font(object):

    ###############################################

    def __init__(self, font_extension, font_name):

        self.font_extension = font_extension
        self.font_name = font_name

        self.glyphs = {}

        self.font_file_name = self.find_font()

        # if self.font_file_name is None:
        #     self.make_pk()

    ###############################################

    def relative_file_name(self):

        return self.font_name + '.' + self.font_extension

    ###############################################

    def find_font(self):

        process = subprocess.Popen(string.join(('kpsewhich', self.relative_file_name()), sep = ' '),
                                   shell=True,
                                   stdout=subprocess.PIPE)
        
        stdout, stderr = process.communicate()
        
        result = stdout[:-1]

        if len(result) > 0 :
            return result
        else:
            raise NameError('Font not found')

    ###############################################

    def register_glyph(self, glyph):

        self.glyphs[glyph.char_code] = glyph

    ###############################################

    def get_glyph(self, char_code):

        return self.glyphs[char_code]

#####################################################################################################
#
# End
#
#####################################################################################################
