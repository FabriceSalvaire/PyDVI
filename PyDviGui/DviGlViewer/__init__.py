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

from PyQt4 import QtCore, QtGui

####################################################################################################

from PyOpenGLng.Tools.Interval import IntervalInt2D

####################################################################################################

from PyDvi.Dvi.DviParser import DviParser 
from PyDvi.Font.FontManager import FontManager
from PyDvi.TeXUnit import *
from PyDvi.Tools.Stream import FileStream

####################################################################################################

from ..Widgets.ApplicationBase import ApplicationBase
from .DviMachine import GlDviMachine
from .MainWindow import MainWindow

####################################################################################################

class Application(ApplicationBase):

    ###############################################

    def __init__(self, args):

        super(Application, self).__init__(args)

        self._main_window = MainWindow()
        self._main_window.showMaximized()

        self._init_dvi_machine()

        self._post_init()

    ##############################################

    def _init_dvi_machine(self):

        self._dvi_parser = DviParser()
        self._font_manager = FontManager(font_map='pdftex', use_pk=False)
        self._dvi_machine = GlDviMachine(self._font_manager)

    ##############################################

    @property
    def dvi_machine(self):
        return self._dvi_machine

    ##############################################
    
    def _post_init(self):
         
        # QtCore.QTimer.singleShot(0, self._open_dvi)
        self.show_message('Welcome to PyDvi')
        self._open_dvi()
        # return to main and then enter to event loop

    ##############################################
    
    def _open_dvi(self):

        self._main_window.open_dvi(self.args.dvi_file)

    ##############################################

    def process_dvi_stream(self, dvi_path):

        dvi_stream = FileStream(dvi_path)
        dvi_program = self._dvi_parser.process_stream(dvi_stream)
        dvi_program.print_summary()
        self.number_of_pages = len(dvi_program.pages)

        self._dvi_machine.load_dvi_program(dvi_program)

    ##############################################

    def run_page(self, page_index=0):

        self._logger.info('Run page {}'.format(page_index))
        if page_index >= 0 and page_index < self.number_of_pages:
            self._logger.info("Run page: {}".format(page_index))
            # page_bounding_box = self._dvi_machine.compute_page_bounding_box(page_index)
            program_page = self._dvi_machine.dvi_program.get_page(page_index) # Fixme: simplify
            self._dvi_machine.process_page_xxx_opcodes(program_page)
            self._dvi_machine.run_page(page_index)
            return self._dvi_machine
        else:
            return None

####################################################################################################
# 
# End
# 
####################################################################################################
