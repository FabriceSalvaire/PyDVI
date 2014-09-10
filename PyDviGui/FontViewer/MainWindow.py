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

from PyDvi.Font.FontManager import FontManager

from ..Widgets.MainWindowBase import MainWindowBase
from .FontInfoTableModel import FontInfoTableModel
from .GlyphInfoTableModel import GlyphInfoTableModel

####################################################################################################

from ..ui.font_viewer_ui import Ui_main_window

####################################################################################################

class MainWindow(MainWindowBase):

    ##############################################

    def __init__(self):

        super(MainWindow, self).__init__('Font Viewer')

        self.main_window_ui = Ui_main_window()
        self.main_window_ui.setupUi(self)
        form = self.main_window_ui

        form.load_font_button.clicked.connect(self.load_font)
        form.pk_radio_button.clicked.connect(self.init_font_manager)
        form.type1_radio_button.clicked.connect(self.init_font_manager)
        form.char_code_spin_box.valueChanged.connect(self.show_glyph)

        args = self.application.args
        if args.font_name is not None:
            form.font_name_line_edit.setText(args.font_name)

        self.font_information_table_model = FontInfoTableModel()
        form.font_information_table_view.setModel(self.font_information_table_model)

        self.glyph_information_table_model = GlyphInfoTableModel()
        form.glyph_information_table_view.setModel(self.glyph_information_table_model)

        self.init_font_manager()

    ##############################################

    def init_font_manager(self):

        form = self.main_window_ui

        use_pk = form.pk_radio_button.isChecked()
        self.font_manager = FontManager(font_map='pdftex', use_pk=use_pk)
        form.font_information_table_view.resizeColumnsToContents()
        self.load_font()

    ##############################################

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
        self.show_glyph(form.char_code_spin_box.value())
        form.glyph_graphics_view.fit_view()

        #except:
            #pass
            #self.font = None
            #form.char_code_spin_box.setMaximum(0)

    ##############################################

    def show_glyph(self, glyph_index):

        if self.font is None:
            return

        form = self.main_window_ui

        glyph = form.glyph_graphics_view.show_glyph(self.font, glyph_index)

        # glyph = self.font[glyph_index] # works only for PkFont
        tfm_char = self.font.tfm[glyph_index]
        self.glyph_information_table_model.set_tfm_char(glyph, tfm_char)
        form.glyph_information_table_view.resizeColumnsToContents()

        # glyph.print_summary()
        # glyph.print_glyph()

####################################################################################################
#
# End
#
####################################################################################################
