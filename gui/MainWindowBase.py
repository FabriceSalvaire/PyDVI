# -*- coding: utf-8 -*-

#####################################################################################################
#
# PyDVI - Python Library to Process DVI Stream
# Copyright (C) 2009 Salvaire Fabrice
#
#####################################################################################################

#####################################################################################################
#
# Audit
#
# - 10/12/2011
#
#####################################################################################################

#####################################################################################################

__all__ = ['MainWindowBase']

#####################################################################################################

import os
import string
import sys

from PyQt4 import QtGui, QtCore, uic

#####################################################################################################

import Config
import PyDVI.PyDviVersion as Version

#####################################################################################################
#
# Main Window
#

class MainWindowBase(QtGui.QMainWindow):
    
    ###############################################
    
    def __init__(self, application):

        super(MainWindowBase, self).__init__()

        self.application = application

    #################################################################################################

    def init_actions(self):

        form = self.main_window_ui

        form.about_qt_action.triggered.connect(QtGui.qApp.aboutQt)
        # form.about_action.triggered.connect(self.about)
        # form.exit_action.triggered.connect(self.close)
        # form.help_action.triggered.connect(self.open_help)

    ###############################################

    def open_help(self):

        url = QtCore.QUrl()
        url.setScheme(Config.Help.url_scheme)
        url.setHost(Config.Help.host)
        url.setPath(Config.Help.url_path_pattern % (Version.pydvi_version.to_string()))

        QtGui.QDesktopServices.openUrl(url)

    ###############################################

    def about(self):

        message = u'''
<h2>About PyDvi</h2>
<p>PyDvi version is v%(version)s</p>
''' % {'version': Version.pydvi_version.to_string(),
       }

        QtGui.QMessageBox.about(self, 'About PyDvi', message)

    ###############################################

    def about_pydvi(self):

        url = QtCore.QUrl('http://...')
        QtGui.QDesktopServices.openUrl(url)

    ###############################################

    def update_status_message(self, message=None):

        status_bar = self.statusBar()
        if message is None:
            status_bar.clearMessage()
        else:
            status_bar.showMessage(message)

        # self.application.processEvents()

#####################################################################################################
#
# End
#
#####################################################################################################
