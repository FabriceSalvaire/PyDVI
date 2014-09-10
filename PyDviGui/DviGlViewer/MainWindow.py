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

from ..Widgets.IconLoader import IconLoader
from ..Widgets.MainWindowBase import MainWindowBase
from .GlWidgetV4 import GlWidget

####################################################################################################

_module_logger = logging.getLogger(__name__)

class MainWindow(MainWindowBase):

    _logger = _module_logger.getChild('MainWindow')

    ##############################################

    def __init__(self):

        super(MainWindow, self).__init__('Dvi Viewer')

        self.resize(1000, 800) # else Ortho2D fails ...

        self._init_ui()

    ##############################################

    def _init_ui(self):

        from .ApplicationStatusBar import ApplicationStatusBar

        self.status_bar = ApplicationStatusBar(self)

        self.central_widget = QtGui.QWidget(self)
        self.horizontal_layout = QtGui.QHBoxLayout(self.central_widget)

        self.graphics_view = GlWidget(self.central_widget, self)
        self.graphics_view.setFocusPolicy(QtCore.Qt.ClickFocus|QtCore.Qt.WheelFocus)

        self.horizontal_layout.addWidget(self.graphics_view)
        self.setCentralWidget(self.central_widget)

        self._create_actions()
        self._create_toolbar()

    ##############################################
    
    def _create_actions(self):

        icon_loader = IconLoader()

        self._previous_page_action = \
            QtGui.QAction(icon_loader['arrow-left'],
                          'Previous document',
                          self,
                          toolTip='Previous Document',
                          triggered=lambda: self.previous_page(),
                          shortcut='Backspace',
                          shortcutContext=QtCore.Qt.ApplicationShortcut,
                          )

        self._next_page_action = \
            QtGui.QAction(icon_loader['arrow-right'],
                          'Next document',
                          self,
                          toolTip='Next Document',
                          triggered=lambda: self.next_page(),
                          shortcut='Space',
                          shortcutContext=QtCore.Qt.ApplicationShortcut,
                          )

    ##############################################
    
    def _create_toolbar(self):

        self._page_index_line_edit = QtGui.QLineEdit()
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self._page_index_line_edit.setSizePolicy(size_policy)
        self._last_page_index_label = QtGui.QLabel()

        self._page_tool_bar = self.addToolBar('Navigation')
        for item in (self._previous_page_action,
                     self._page_index_line_edit,
                     self._last_page_index_label,
                     self._next_page_action,
                    ):
            if isinstance(item,QtGui.QAction):
                self._page_tool_bar.addAction(item)
            else:
                self._page_tool_bar.addWidget(item)

    ##############################################
    
    def open_dvi(self, dvi_path):

        self._application.process_dvi_stream(dvi_path)
        self._page_index = 0
        self._last_page_index_label.setText('of {}'.format(self._application.number_of_pages))
        self._run_page()

    ##############################################

    def _run_page(self):

        self._page_index_line_edit.setText(str(self._page_index +1))
        dvi_machine = self._application.run_page(self._page_index)
        if dvi_machine is not None:
            self.graphics_view.update_dvi(dvi_machine)
            
    ##############################################

    def previous_page(self):

        if self._page_index > 0:
            self._page_index -= 1
            self._run_page()

    ##############################################

    def next_page(self):

        if self._page_index < (self._application.number_of_pages - 1):
            self._page_index += 1
            self._run_page()

####################################################################################################
#
# End
#
####################################################################################################
