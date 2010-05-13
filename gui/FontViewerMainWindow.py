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

import math

from PyQt4 import QtGui, QtCore

#####################################################################################################

from PyDVI.FontManager import FontManager

from FontInfoTableModel import FontInfoTableModel
from GlyphInfoTableModel import GlyphInfoTableModel
from MainWindowBase import MainWindowBase

#####################################################################################################

from font_viewer_ui import Ui_main_window

#####################################################################################################
#
# Main Window
#

class MainWindow(MainWindowBase):

    ###############################################

    def __init__(self, application, opt):

        super(MainWindow, self).__init__(application)

        self.opt = opt

        self.main_window_ui = Ui_main_window()
        self.main_window_ui.setupUi(self)

        super(MainWindow, self).init_actions()
        self.__init_actions()
        self.__init_menu()

        # Init Signals

        form = self.main_window_ui

        signal = QtCore.SIGNAL('clicked()')

        QtCore.QObject.connect(form.load_font_button, signal, self.load_font)
        QtCore.QObject.connect(form.pk_radio_button, signal, self.init_font_manager)
        QtCore.QObject.connect(form.type1_radio_button, signal, self.init_font_manager)

        signal = QtCore.SIGNAL('valueChanged(int)')

        QtCore.QObject.connect(form.char_code_spin_box, signal, self.show_glyph)

        # Init Form

        if opt.font_name is not None:
            form.font_name_line_edit.setText(opt.font_name)

        self.font_information_table_model = FontInfoTableModel()
        form.font_information_table_view.setModel(self.font_information_table_model)

        self.glyph_information_table_model = GlyphInfoTableModel()
        form.glyph_information_table_view.setModel(self.glyph_information_table_model)

        self.init_font_manager()

    ###############################################
    #
    # Menu
    #

    def __init_menu(self):

        form = self.main_window_ui

    ###############################################
    #
    # Actions
    #

    def __init_actions(self):

        form = self.main_window_ui

    ###############################################

    def init_font_manager(self):

        form = self.main_window_ui

        self.font_manager = FontManager(font_map = 'pdftex', use_pk = form.pk_radio_button.isChecked())

        form.font_information_table_view.resizeColumnsToContents()

        self.load_font()

    ###############################################

    def load_font(self):

        form = self.main_window_ui

        font_name = str(form.font_name_line_edit.text())

        if not font_name:
            return

        #try:
        # self.font = self.font_manager.load_font(font_types.Pk, font_name)
        self.font = self.font_manager[font_name]

        self.font_information_table_model.set_font(self.font)
        form.font_information_table_view.resizeColumnsToContents()
        
        form.char_code_spin_box.setMaximum(len(self.font) -1)
        
        # self.font.print_summary()
        
        self.show_glyph(0)

        #except:
            #pass
            #self.font = None
            #form.char_code_spin_box.setMaximum(0)

    ###############################################

    def show_glyph(self, glyph_index):

        if self.font is None:
            return

        form = self.main_window_ui

        self.tfm_char = self.font.tfm[glyph_index]
        self.glyph_information_table_model.set_tfm_char(self.tfm_char)
        form.glyph_information_table_view.resizeColumnsToContents()

        # glyph.print_summary()
        # glyph.print_glyph()

        form.glyph_graphics_view.show_glyph(self.font, glyph_index)

#####################################################################################################
#
# End
#
#####################################################################################################
