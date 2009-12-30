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
#
#####################################################################################################

#####################################################################################################

__ALL__ = ['MainWindowBase']

#####################################################################################################

import os
import string
import sys

from PyQt4 import QtGui, QtCore, uic

#####################################################################################################

import Config
import Version

#####################################################################################################
#
# Main Window
#

class MainWindowBase(QtGui.QMainWindow):
    
    ###############################################
    
    def __init__(self, application):

        QtGui.QMainWindow.__init__(self)

        self.application = application

    #################################################################################################
    #
    # Actions
    #

    def init_actions(self):

        form = self.main_window_ui

        signal = QtCore.SIGNAL('triggered()')

        self.connect(form.about_qt_action, signal, QtGui.qApp, QtCore.SLOT('aboutQt()'))

        #qt 4.5# form.about_action.triggered.connect(self.about)
        #qt 4.5# form.exit_action.triggered.connect(self.close)
        #qt 4.5# form.help_action.triggered.connect(self.open_help)

        self.connect(form.about_action, signal, self.about)

        # self.connect(form.exit_action, signal, self.close)
        # self.connect(form.about_pydvi_action, signal, self.about_pydvi)
        # self.connect(form.help_action, signal, self.open_help)

    ###############################################

    def open_help(self):

        url = QtCore.QUrl()
        url.setScheme(Config.Help.url_scheme)
        url.setHost(Config.Help.host)
        url.setPath(Config.Help.url_path_pattern % (Version.pydvi_version.to_string()))

        QtGui.QDesktopServices.openUrl(url)

    ###############################################

    def about(self):

        QtGui.QMessageBox.about(self, 'About PyDvi', u'''
<h2>About PyDvi</h2>
<p>PyDvi version is v%(version)s</p>
''' % {'version': Version.pydvi_version.to_string(),
       })

    ###############################################

    def about_pydvi(self):

        url = QtCore.QUrl('http://...')

        QtGui.QDesktopServices.openUrl(url)

    ###############################################

    def update_status_message(self, message = None):

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
