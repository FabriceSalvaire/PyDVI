#####################################################################################################

import subprocess
import string

#####################################################################################################

class Font(object):

    ###############################################

    def __init__(self, extension, name):

        self.extension = extension
        self.name = name

        self.glyphs = {}

        self.file_name = self.find_font()

        # if self.file_name is None:
        #     self.make_pk()

    ###############################################

    def __len__(self):

        return len(self.glyphs)

    ###############################################

    def relative_file_name(self):

        return self.name + '.' + self.extension

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
