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


"""Reference: Adobe Font Metrics File Format Specification, Version 4.1, 7 October 1998

All measurements in AFM files are given in terms of units equal to 1/1000 of the scale factor (point
size) of the font being used. To compute actual sizes in a document (in points; with 72 points = 1
inch), these amounts should be multiplied by (scale factor of font) / 1000.

"""

####################################################################################################

# __all__ = []

####################################################################################################

import logging

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def boolean(x):
    if x == 'false':
        return False
    elif x == 'true':
        return True
    else:
        raise ValueError("Can't convert {} to boolean".format(x))

####################################################################################################

def hex(x):
    if x.startswith('<') and x.endswith('>'):
        return int(x[1:-1], base=16)
    else:
        raise ValueError('Wrong hexadecimal number {}'.format(x))

####################################################################################################

global_font_information_keys = {
    'MetricsSets': int,
    'FontName': str,
    'FullName': str,
    'FamilyName': str,
    'Weight': str,
    'FontBBox': (float, float, float, float),
    'Version': str,
    'Notice': str,
    'EncodingScheme': str,
    'MappingScheme': int,
    'EscChar': int,
    'CharacterSet': str,
    'Characters': int,
    'IsBaseFont': boolean,
    'VVector': (float, float),
    'IsFixedV': boolean,
    'CapHeight': float,
    'XHeight': float,
    'Ascender': float,
    'Descender': float,
    # ???
    'IsCIDFont': boolean,
}

direction_keys = {
    'UnderlinePosition': float,
    'UnderlineThickness': float,
    'ItalicAngle': float,
    'CharWidth': (float, float),
    'IsFixedPitch': boolean,
    }

# if omitted, StartDirection 0 is implied.
global_font_information_keys.update(direction_keys)

character_metric_keys = {
    'C': int,
    'CH': hex,
    'WX': float,
    'W0X': float,
    'W1X': float,
    'WY': float,
    'W0Y': float,
    'W1Y': float,
    'W': (float, float),
    'W0': (float, float),
    'W1': (float, float),
    'VV': (float, float),
    'N': str,
    'B': (float, float, float, float),
    'L': (str, str),
}

track_kern_keys = {
    'TrackKern': (int, float, float, float, float),
}

kern_keys = {
    'KP': (str, str, float, float),
    'KPH': (hex,  hex, float, float),
    'KPX': (str, str, float),
    'KPY': (str, str, float),
}

composite_keys = { 
    'CC': (str, int),
    'PCC': (str, float, float),
}

# afm_sections = {
#     'FontMetrics': (str, global_font_information_keys, {
#         'Direction': (int, direction_keys, None),
#         'CharMetrics': (int, character_metric_keys, None),
#         'KernData': (int, None, {
#             'KernPairs': (int, kern_keys, None),
#             'KernPairs0': (int, kern_keys, None),
#             'KernPairs1': (int, kern_keys, None),
#         }),
#         'Composites': (int, composite_keys, None),
#     }),
# }

afm_sections = {
    'FontMetrics': (str, global_font_information_keys), 
    'Direction': (int, direction_keys),
    'CharMetrics': (int, character_metric_keys),
    'KernData': (int, None), 
    'TrackKern': (int, track_kern_keys), 
    'KernPairs': (int, kern_keys),
    'KernPairs0': (int, kern_keys),
    'KernPairs1': (int, kern_keys),
    'Composites': (int, composite_keys),
}

section_hiearachy = {'FontMetrics': {
    'Direction': None,
    'CharMetrics': None,
    'KernData': {
        'TrackKern': None,
        'KernPairs': {
            'KernPairs0': None,
            'KernPairs1': None,
            'Composites': None,
        },
    },
    'Composites': None,
}}

####################################################################################################

class BadAfmFile(NameError):
    pass

####################################################################################################

class AfmParser(object):

    _logger = _module_logger.getChild('AfmParser')

    ##############################################

    @staticmethod
    def parse(filename):

        afm_parser = AfmParser(filename)
        return afm_parser

    ##############################################

    def __init__(self, filename):

        with open(filename) as f:
            self._parse(f)

    ##############################################

    def _parse(self, stream):

        self._section_stack = []
        self._stack = []
        self._section = None
        self._keys = None
        self._sections = section_hiearachy

        for line in stream:
            line = line.strip()
            # self._logger.info('\n' + line)
            if not line or line.startswith('Comment'):
                continue
            elif line.startswith('Start'):
                values = self._parse_start(line)
            elif line.startswith('End'):
                self._parse_end(line)
            else:
                if self._section in ('CharMetrics', 'Composites'):
                    properties = self._parse_key_values_list(self._keys, line)
                elif self._keys is not None:
                    key, values = self._parse_key_values(self._keys, line)
                else:
                    raise BadAfmFile("This file doesn't look like an AFM file")

    ##############################################

    def _get_values(self, types, line):

        line = line.strip()
        if isinstance(types, tuple):
            start = 0
            values = []
            for data_type in types:
                stop = line.find(' ', start)
                if stop == -1:
                    value_string = line[start:]
                else:
                    value_string = line[start:stop]
                value = data_type(value_string)
                values.append(value)
                start = stop + 1
            return values
        else:
            return types(line)

    ##############################################

    def _parse_start(self, line):

        index = line.find(' ')
        if index == -1:
            section = line[5:]
        else:
            section = line[5:index]
        if self._section is None and section != 'FontMetrics':
            raise BadAfmFile('File start with section {} '.format(section))
        elif section not in self._sections:
            raise BadAfmFile('Wrong section order: {} -> {}'.format(self._section_stack, section))
        self._section_stack.append(section)
        self._stack.append((self._keys, self._sections))
        self._section = section
        data_types, self._keys = afm_sections[section]
        self._sections = self._sections[section]
        if index == -1:
            values = None
        else:
            values = self._get_values(data_types, line[index:])
        self._logger.info('Enter section {}: {}'.format(section, values))
        return values

    ##############################################

    def _parse_end(self, line):

        section = line[3:]
        if self._section == section:
            if len(self._stack) == 1:
                self._section = None
                self._keys = None
                self._sections = None
            else:
                self._section = self._section_stack[-2]
                self._keys, self._sections = self._stack[-1]
            del self._section_stack[-1]
            del self._stack[-1]
            self._logger.info('Leave section {}'.format(section))
        else:
            raise BadAfmFile("Misplaced end of section {}".format(section))

    ##############################################

    def _parse_key_values(self, keys, line):

        index = line.find(' ')
        if index != -1:
            key = line[:index]
            if key in keys:
                values = self._get_values(keys[key], line[index:])
                self._logger.info('key {}: {}'.format(key, values))
                return key, values
            else:
                # raise NameError()
                self._logger.warning("Unknown key {} in section {}".format(key, self._section))
                return None, None
        else:
            raise NameError("Bad line")

    ##############################################

    def _parse_key_values_list(self, keys, line):

        self._logger.info('')
        properties = {}
        for pair in line.split(';'):
            pair = pair.strip()
            if pair:
                key, values = self._parse_key_values(keys, pair)
                if key is not None:
                    properties[key] = values
        return properties

####################################################################################################
#
# End
#
####################################################################################################
