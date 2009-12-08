#####################################################################################################

import string

#####################################################################################################

from OpcodeParser import *

#####################################################################################################

SEEK_RELATIVE_TO_START   = 0
SEEK_RELATIVE_TO_CURRENT = 1
SEEK_RELATIVE_TO_END     = 2

#####################################################################################################

PK_ID = 89

CHAR_000_OPCODE = 0
CHAR_239_OPCODE = 239
XXX1_OPCODE     = 240
XXX3_OPCODE     = 241
XXX2_OPCODE     = 242
XXX4_OPCODE     = 243
YYY_OPCODE      = 244
POST_OPCODE     = 245
NOP_OPCODE      = 246
PRE_OPCODE      = 247

#####################################################################################################

class OpcodeParser_char(OpcodeParser):

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_char, self).__init__(opcode, 'char', '')

    ###############################################

    def read_parameters(self, dvi_processor):

        flag = self.flag = self.opcode

        self.dyn_f = flag >> 4
        self.first_pixel_is_black = (flag & 8) != 0
        self.two_bytes =  (flag & 4) != 0

        three_least_significant = flag & 7
        two_least_significant = flag & 3

        if three_least_significant <= 3:
            self.format = 1
        elif three_least_significant == 7:
            self.format = 3
        else:
            self.format = 2

        if self.format == 1:
            # (flag mod 4)*256 + pl
            self.packet_length = (two_least_significant << 8) + dvi_processor.read_unsigned_byte1()
            self.preambule_length = 3 + 5
        elif self.format == 2:
            self.packet_length = (two_least_significant << 16) + dvi_processor.read_unsigned_byte2()
            self.preambule_length = 3 + 5*2
        else:
            self.packet_length = dvi_processor.read_unsigned_byte4()
            self.preambule_length = 7*4

        if self.format == 3:
            (self.char_code, self.tfm,
             self.dx, self.dy,
             self.width, self.height,
             self.horizontal_offset, self.vertical_offset) = [dvi_processor.read_unsigned_byte4() for i in xrange(8)]
            self.dm = None
        else:
            self.char_code = dvi_processor.read_unsigned_byte1()
            self.tfm = dvi_processor.read_unsigned_byte3()
            if self.format == 1:
                (self.dm, self.width, self.height) = [dvi_processor.read_unsigned_byte1() for i in xrange(3)]
                (self.horizontal_offset, self.vertical_offset) = [dvi_processor.read_signed_byte1() for i in xrange(2)]
            else:
                (self.dm, self.width, self.height) = [dvi_processor.read_unsigned_byte2() for i in xrange(3)]
                (self.horizontal_offset, self.vertical_offset) = [dvi_processor.read_signed_byte2() for i in xrange(2)]
            self.dx = self.dm
            self.dy = 0

        print '''
Char %u
 - Flag: %u
 - Dynamic Packing Variable: %u
 - First pixel is black: %s
 - Two Bytes: %s
 - Format: %u
 - Packet Length: %u
 - TFM width: %u
 - dm: %u
 - dx: %u
 - dy: %u
 - Height: %u
 - Width: %u
 - Horizontal Offset: %u
 - Vertical Offset: %u
''' % (self.char_code,
       self.flag, self.dyn_f, self.first_pixel_is_black, self.two_bytes, self.format, self.packet_length,
       self.tfm, self.dm, self.dx, self.dy,
       self.height, self.width,
       self.horizontal_offset, self.vertical_offset)

        self.nybbles = dvi_processor.read_stream(self.packet_length-self.preambule_length)
        print 'nybbles: ', map(hex, map(ord, self.nybbles))
        self.nybble_index = 0
        self.nybble_index_max = len(self.nybbles) -1
        self.upper_nybble = True

        self.decode()

        return [self.opcode]

    ###############################################

    def get_nybble(self):

        # print 'get_nybble', self.nybble_index, self.upper_nybble

        if self.upper_nybble is True:
            nybble = ord(self.nybbles[self.nybble_index]) >> 4
        else:
            nybble = ord(self.nybbles[self.nybble_index]) & 0xF
            self.nybble_index += 1

        self.upper_nybble = not self.upper_nybble

        # print '  ', nybble

        return nybble

    ###############################################

    def pk_packed_num(self):

        # cf. pktype.web

        i = self.get_nybble()

        if i == 0:
            while True:
                j  = self.get_nybble()
                i += 1
                if j != 0: break
            while i > 0:
                j  = j * 16 + self.get_nybble()
                i -= 1
            return j - 15 + (13 - self.dyn_f) * 16 + self.dyn_f

        elif i <= self.dyn_f:
            return i

        elif i < 14:
            return (i - self.dyn_f - 1) * 16 + self.get_nybble() + self.dyn_f + 1

        else:
            if i == 14:
                self.repeat_count = self.pk_packed_num()
            else :
                self.repeat_count = 1;
            return self.pk_packed_num()

    ###############################################

    def decode(self):

        char_bitmap = [0]*(4*self.height*self.width)

        if self.dyn_f == 14:
            pass
##     { /* get raster by bits */
##       int bitweight = 0
##       for (j = j_offset j < (int) height j++)
## 	{ /* get all rows */
## 	  for (i = i_offset i < (int) width i++)
## 	    { /* get one row */
## 	      bitweight /= 2
## 	      if (bitweight == 0)
## 		{
## 		  count = *pos++
## 		  bitweight = 128
## 		}
## 	      if (count & bitweight)
## 		{
## 		  char_bitmap[i + j * width] = 1
## 		}
## 	    }
## 	  DEBUG_PRINT (DEBUG_GLYPH, ("|\n"))
## 	}
##     }
        else: # get packed raster

            black_pixel = self.first_pixel_is_black
            transition = False
            self.repeat_count = 0

            packed_string = ''

            line = ''
            y = 0
            y_max = self.width -1

            while True:

                if self.nybble_index > self.nybble_index_max:
                    break

                count = self.pk_packed_num()

                if transition is True:
                    packed_string += '[%u]' % (self.repeat_count)
                if black_pixel is True:
                    packed_string += '%u' % (count)
                else:
                    packed_string += '(%u)' % (count)

                if black_pixel is True:
                    pixel = 'X'
                else:
                    pixel = ' '

                y += count

                if y >= y_max:
                    y = y - self.width
                    count -= y
                    line += pixel*count 
                    for i in xrange(self.repeat_count +1):
                        print line
                    line = pixel*y
                else:
                    line += pixel*count 

                black_pixel = not black_pixel
                transition = not transition

            print packed_string

#####################################################################################################

class OpcodeParser_xxx(OpcodeParser):

    base_opcode = XXX1_OPCODE

    ###############################################

    def __init__(self, opcode):

        super(OpcodeParser_xxx, self).__init__(opcode, 'xxx', 'special')

        self.read_unsigned_byten = OpcodeStreamParser.read_unsigned_byten_pointer[opcode-self.base_opcode]

    ###############################################

    def read_parameters(self, dvi_processor):

        return dvi_processor.read_stream(self.read_unsigned_byten(dvi_processor))

#####################################################################################################

class PkFont(OpcodeStreamParser):

    opcode_definitions = (
        ( [CHAR_000_OPCODE, CHAR_239_OPCODE], OpcodeParser_char ),
        ( NOP_OPCODE, 'nop', 'no operation', None, None ),
        ( [XXX1_OPCODE, XXX4_OPCODE], OpcodeParser_xxx ),
        ( YYY_OPCODE, 'yyy', 'numspecial', tuple([4]), None ),
        ( PRE_OPCODE, 'pre', 'preamble', (), None ),
        ( POST_OPCODE, 'post', 'postamble', None, None ),
        )
   
    ###############################################

    def __init__(self, pk_file_name):

        super(PkFont, self).__init__(self.opcode_definitions)

        self.pk_file_name = pk_file_name

        stream = open(pk_file_name)

        self.set_stream(stream)

        self.process_preambule()
        self.process_characters()

        self.set_stream(None)

        stream.close()

    ###############################################

    def process_preambule(self):

        self.stream.seek(0)

        if self.read_unsigned_byte1() != PRE_OPCODE:
            raise NameError('Bad PK File')

        self.pk_id = self.read_unsigned_byte1()
        if self.pk_id != PK_ID:
            raise NameError('Bad PK File')

        self.comment = self.read_stream(self.read_unsigned_byte1())

        self.design_size = self.read_signed_byte4()
        self.checksum = self.read_signed_byte4()
        self.horizontal_pixels_per_point = self.read_signed_byte4()
        self.vertical_pixels_per_point = self.read_signed_byte4()

    ###############################################

    def process_characters(self):
        
        while True:

            opcode = self.read_unsigned_byte1()

            if opcode == POST_OPCODE:
                break
            else:
                opcode_parser = self.opcode_parsers[opcode]

                parameters = opcode_parser.read_parameters(self)

                print opcode_parser, parameters

                break

    ###############################################

    def print_summary(self):

        print '''PK File %s

Preambule
  - PK ID        %u
  - Comment      '%s'
  - Design Size  %u
  - Checksum     %u
  - Horizontal Pixels per Point %u
  - Vertical   Pixels per Point %u
  ''' % (self.pk_file_name,
         self.pk_id,
         self.comment,
         self.design_size,
         self.checksum,
         self.horizontal_pixels_per_point,
         self.vertical_pixels_per_point)

#####################################################################################################
#
#                                               Test
#
#####################################################################################################
        
if __name__ == '__main__':

    from optparse import OptionParser

    usage = 'usage: %prog [options]'

    parser = OptionParser(usage)

    opt, args = parser.parse_args()

    pk_file_name = args[0]

    pk_font = PkFont(pk_file_name)

    pk_font.print_summary()

#####################################################################################################
#
# End
#
#####################################################################################################
