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

####################################################################################################

from PyQt4 import QtGui

####################################################################################################

class ApplicationStatusBar(object):

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def __init__(self, parent):

        self._application = QtGui.QApplication.instance()

        self._status_bar = parent.statusBar()

        label_definitions = (('message_label', 'Message'),
                             ('coordinate_label', 'Coordinate of the pointer'),
                             ('zoom_label', 'Zoom'),
                             )

        for attribute_name, tool_tip in label_definitions:
            widget = QtGui.QLabel(toolTip=tool_tip)
            setattr(self, attribute_name, widget)

        coordinate_max = 10**5
        self.update_coordinate_status(coordinate_max, coordinate_max)
        self.update_status_message('W'*30)
        self.update_zoom_status(1)

        for widget in (self.message_label,
                       self.coordinate_label,
                       self.zoom_label,
                       ):
            # Permanently means that the widget may not be obscured by temporary messages. It is is
            # located at the far right of the status bar.
            self._status_bar.addPermanentWidget(widget)
            widget.setMinimumSize(widget.sizeHint())
            widget.clear()

        self.update_coordinate_status(0, 0)

    ##############################################

    def update_status_message(self, message):

        self.message_label.setText(message)

    ##############################################

    def update_coordinate_status(self, x, y):

        text = '({:.1f}, {:.1f}) mm'.format(x, y)
        self.coordinate_label.setText(text)

    ##############################################

    def update_zoom_status(self, zoom):

        text = '{:.1f} %'.format(zoom*100)
        self.zoom_label.setText(text)

####################################################################################################
#
# End
#
####################################################################################################
