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

__all__ = ['MainWindowBase']

####################################################################################################

from PyQt4 import QtGui, QtCore

####################################################################################################

import PyDvi.PyDviVersion as Version

####################################################################################################

class MainWindowBase(QtGui.QMainWindow):
    
    ##############################################
    
    def __init__(self, application):

        super(MainWindowBase, self).__init__()

        self.application = application

    ################################################################################################

    def init_actions(self):

        form = self.main_window_ui

        form.about_qt_action.triggered.connect(QtGui.qApp.aboutQt)
        # form.about_action.triggered.connect(self.about)
        # form.exit_action.triggered.connect(self.close)
        # form.help_action.triggered.connect(self.open_help)

    ##############################################

    def open_help(self):

        url = QtCore.QUrl()
        url.setScheme(Config.Help.url_scheme)
        url.setHost(Config.Help.host)
        url.setPath(Config.Help.url_path_pattern % (Version.pydvi_version.to_string()))

        QtGui.QDesktopServices.openUrl(url)

    ##############################################

    def about(self):

        message = u'''
<h2>About PyDvi</h2>
<p>PyDvi version is v%(version)s</p>
''' % {'version': Version.pydvi_version.to_string(),
       }

        QtGui.QMessageBox.about(self, 'About PyDvi', message)

    ##############################################

    def about_pydvi(self):

        url = QtCore.QUrl('http://...')
        QtGui.QDesktopServices.openUrl(url)

    ##############################################

    def update_status_message(self, message=None):

        status_bar = self.statusBar()
        if message is None:
            status_bar.clearMessage()
        else:
            status_bar.showMessage(message)

        # self.application.processEvents()

####################################################################################################
#
# End
#
####################################################################################################
