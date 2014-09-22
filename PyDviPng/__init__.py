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

import logging

####################################################################################################

from PyDvi.Dvi.DviParser import DviParser 
from PyDvi.Font.FontManager import FontManager
from PyDvi.TeXUnit import *
from PyDvi.Tools.Stream import FileStream

####################################################################################################

from .DviMachine import ImageDviMachine

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class DviPng(object):

    _logger = _module_logger.getChild('DviPng')

    ###############################################

    def __init__(self):

        self._init_dvi_machine()

    ##############################################

    def _init_dvi_machine(self):

        self._dvi_parser = DviParser()
        self._font_manager = FontManager(font_map='pdftex', use_pk=False)
        self._dvi_machine = ImageDviMachine(self._font_manager)

    ##############################################

    @property
    def dvi_machine(self):
        return self._dvi_machine

    ##############################################

    def process_dvi_stream(self, dvi_path):

        dvi_stream = FileStream(dvi_path)
        dvi_program = self._dvi_parser.process_stream(dvi_stream)
        # dvi_program.print_summary()
        self.number_of_pages = len(dvi_program.pages)
        self._dvi_machine.load_dvi_program(dvi_program)

    ##############################################

    def run_page(self, png_path, page_index=0, dpi=100, tight=False):

        if page_index >= 0 and page_index < self.number_of_pages:
            self._logger.info("Run page: {}".format(page_index))
            # page_bounding_box = self._dvi_machine.compute_page_bounding_box(page_index)
            program_page = self._dvi_machine.dvi_program[page_index] # Fixme: simplify
            self._dvi_machine.process_page_xxx_opcodes(program_page)
            self._dvi_machine.run_page(page_index, dpi=dpi, png_path=png_path, tight=tight)

####################################################################################################
# 
# End
# 
####################################################################################################
