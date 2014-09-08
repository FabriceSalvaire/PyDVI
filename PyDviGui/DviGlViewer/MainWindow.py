# -*- coding: utf-8 -*-

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

from PyQt4 import QtGui, QtCore

####################################################################################################

from PyOpenGLng.Tools.Interval import IntervalInt2D

from PyDvi.Dvi.DviParser import DviParser 
from PyDvi.Font.FontManager import FontManager
from PyDvi.TeXUnit import *
from PyDvi.Tools.Stream import FileStream

from .DviMachine import GlDviMachine
from .GlWidgetV4 import GlWidget

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class MainWindow(QtGui.QMainWindow):

    _logger = _module_logger.getChild('MainWindow')

    ##############################################

    def __init__(self, dvi_file):

        super(MainWindow, self).__init__()

        self.resize(1000, 800)

        self.central_widget = QtGui.QWidget(self)
        self.horizontal_layout = QtGui.QHBoxLayout(self.central_widget)

        self.graphics_view = GlWidget(self.central_widget)
        self.graphics_view.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.horizontal_layout.addWidget(self.graphics_view)
        self.setCentralWidget(self.central_widget)

        self._init_dvi_machine()
        self.process_dvi_stream(dvi_file)

    ##############################################

    def _init_dvi_machine(self):

        self.dvi_parser = DviParser()
        self.font_manager = FontManager(font_map='pdftex', use_pk=False)
        self.dvi_machine = GlDviMachine(self.font_manager)

    ##############################################

    def process_dvi_stream(self, dvi_file):

        dvi_stream = FileStream(dvi_file)
        dvi_program = self.dvi_parser.process_stream(dvi_stream)
        dvi_program.print_summary()

        # scene.clear()
        self.dvi_machine.load_dvi_program(dvi_program)
        page_index = 0
        self._logger.info("Run page: {}".format(page_index))
        if len(dvi_program.pages) > 0:
            page_bounding_box = self.dvi_machine.compute_page_bounding_box(page_index)
            self.dvi_machine.run_page(page_index)
        self.graphics_view.update_dvi(self.dvi_machine) # Fixme:

####################################################################################################
#
# End
#
####################################################################################################
