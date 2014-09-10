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
import sys

from PyQt4 import QtGui

####################################################################################################

from PyDviGui.Tools.Platform import Platform
import PyDvi.Version as Version
import PyDviGui.Config.Messages as Messages

# import PyDviGui.Config.Config as Config

####################################################################################################

class ApplicationBase(QtGui.QApplication):

    _logger = logging.getLogger(__name__)
    
    ##############################################
    
    def __init__(self, args, **kwargs):

        super(ApplicationBase, self).__init__(sys.argv)

        self._args = args
        self._platform = Platform()

        self._main_window = None
        self._init_actions()

    ##############################################

    @property
    def args(self):
        return self._args

    @property
    def platform(self):
        return self._platform

    @property
    def main_window(self):
        return self._main_window

    ##############################################
    
    def exit(self):

        sys.exit(0)

    ##############################################

    def _init_actions(self):

        self.about_action = \
            QtGui.QAction('About PyDvi',
                          self,
                          triggered=self.about)

        self.exit_action = \
            QtGui.QAction('Exit',
                          self,
                          triggered=self.exit)

        self.help_action = \
            QtGui.QAction('Help',
                          self,
                          triggered=self.open_help)

        self.show_system_information_action = \
            QtGui.QAction('System Information',
                          self,
                          triggered=self.show_system_information)

    ##############################################

    def show_message(self, message=None, echo=False, timeout=0):

        if self._main_window is not None:
            self._main_window.show_message(message, echo, timeout)
        else:
            self._logger.info(message)

    ##############################################

    def open_help(self):

        pass
        # url = QtCore.QUrl()
        # url.setScheme(Config.Help.url_scheme)
        # url.setHost(Config.Help.host)
        # url.setPath(Config.Help.url_path_pattern)
        # QtGui.QDesktopServices.openUrl(url)

    ##############################################

    def about(self):
        
        message = Messages.about_pydvi % {'version':str(Version.pydvi)}
        QtGui.QMessageBox.about(self.main_window, 'About PyDvi', message)

    ##############################################

    def show_system_information(self):

        fields = dict(self._platform.__dict__)
        fields.update({
                'pydvi_version': str(Version.pydvi),
                })  
        message = Messages.system_information_message_pattern % fields
        QtGui.QMessageBox.about(self.main_window, 'System Information', message)
        
####################################################################################################
#
# End
#
####################################################################################################
