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

from PyDVI.FontManager import *

from MainWindowBase import *
from FontInfoTableModel import *
from GlyphInfoTableModel import *

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
        self.__init_glyph_view()

        # Init Signals

        form = self.main_window_ui

        signal = QtCore.SIGNAL('clicked()')

        QtCore.QObject.connect(form.load_font_button, signal, self.load_font)

        signal = QtCore.SIGNAL('valueChanged(int)')

        QtCore.QObject.connect(form.char_code_spin_box, signal, self.show_glyph)

        # Init Form

        if opt.font_name is not None:
            form.font_name_line_edit.setText(opt.font_name)

        self.font_manager = FontManager(font_map = 'pdftex')

        self.font_information_table_model = FontInfoTableModel()
        self.glyph_information_table_model = GlyphInfoTableModel()

        form.font_information_table_view.setModel(self.font_information_table_model)
        form.glyph_information_table_view.setModel(self.glyph_information_table_model)

        for table_view in (form.font_information_table_view,
                           form.glyph_information_table_view,
                           ):
            table_view.resizeColumnsToContents()

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
    #
    # Glyph View
    #

    def __init_glyph_view(self):

        form = self.main_window_ui

        self.scene = scene = QtGui.QGraphicsScene(self)

        scene.setSceneRect(-100, -100, 100, 100)

        glyph_graphics_view = form.glyph_graphics_view

        glyph_graphics_view.setScene(scene)

        glyph_graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)
        glyph_graphics_view.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        glyph_graphics_view.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)

    ###############################################

    def load_font(self):

        form = self.main_window_ui

        font_name = str(form.font_name_line_edit.text())

        #try:
        self.font = self.font_manager.load_font(font_types.Pk, font_name)

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

    def show_glyph(self, i):

        if self.font is None:
            return

        form = self.main_window_ui

        self.glyph_information_table_model.set_tfm_char(self.font.tfm[i])
        form.glyph_information_table_view.resizeColumnsToContents()

        glyph = self.font[i]
        
        # glyph.print_summary()
        # glyph.print_glyph()
        
        glyph_bitmap = glyph.get_glyph_bitmap()

        glyph_image = QtGui.QImage(glyph.width, glyph.height, QtGui.QImage.Format_ARGB32) # Format_Mono

        for y in xrange(glyph.height):
            for x in xrange(glyph.width):
                if glyph_bitmap[y, x] == 1:
                    glyph_image.setPixel(x, y, 0xFF000000)
                else:
                    glyph_image.setPixel(x, y, 0x00FFFFFF)

        self.glyph_bitmap = QtGui.QPixmap.fromImage(glyph_image)

        self.scene.clear()

        char_pixmap = self.scene.addPixmap(self.glyph_bitmap)
        char_pixmap.setOffset(-glyph.horizontal_offset, -glyph.vertical_offset)

        box_depth  = max(glyph.height - glyph.vertical_offset, glyph.vertical_offset)
        box_height = max(glyph.vertical_offset, box_depth)

        red_pen = QtGui.QPen()
        red_pen.setColor(QtCore.Qt.red)

        box_scale = 1.5

        self.scene.addLine(-box_scale*glyph.width, 0, (box_scale+1)*glyph.width, 0, red_pen)
        self.scene.addLine(0, box_scale*box_depth, 0, -box_scale*box_height, red_pen)

        char_box = QtCore.QRectF(-glyph.horizontal_offset, -glyph.vertical_offset, glyph.width, glyph.height)

        self.scene.addRect(char_box, red_pen)

        self.scene.update()

    ###############################################

    def keyPressEvent(self, event):

        form = self.main_window_ui

        key = event.key()

        glyph_graphics_view = form.glyph_graphics_view

        dx = 10

        print 'keyPressEvent', key

        if key == QtCore.Qt.Key_Up:
            glyph_graphics_view.translate(0, -dx)

        elif key == QtCore.Qt.Key_Down:
            glyph_graphics_view.translate(0, dx)

        elif key == QtCore.Qt.Key_Left:
            glyph_graphics_view.translate(-dx, 0)

        elif key == QtCore.Qt.Key_Right:
            glyph_graphics_view.translate(dx, 0)

        elif key == QtCore.Qt.Key_Plus:
            self.scale_view(2)

        elif key == QtCore.Qt.Key_Minus:
            self.scale_view(.5)

        else:
            QtGui.QGraphicsView.keyPressEvent(glyph_graphics_view, event)

    ###############################################

    def wheelEvent(self, event):

        delta = event.delta()

        if delta > 0:
            self.scale_view(2)
        else:
            self.scale_view(0.5)

    ###############################################

    def scale_view(self, scale_factor):

        form = self.main_window_ui

        glyph_graphics_view = form.glyph_graphics_view

        transformation = glyph_graphics_view.matrix().scale(scale_factor, scale_factor)

        factor = transformation.mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.1 or factor > 100:
            return

        glyph_graphics_view.scale(scale_factor, scale_factor)

#####################################################################################################
#
# End
#
#####################################################################################################
