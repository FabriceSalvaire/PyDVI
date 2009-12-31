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
from PyDVI.PkFont import *
from PyDVI.TeXUnit import *
from PyDVI.Type1Font import *

from FontInfoTableModel import *
from GlyphInfoTableModel import *
from MainWindowBase import *
from QtGlyph import *

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

        self.font_manager = FontManager(font_map = 'pdftex', use_pk = True)

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

    def show_glyph(self, i):

        if self.font is None:
            return

        form = self.main_window_ui

        self.tfm_char = self.font.tfm[i]
        self.glyph_information_table_model.set_tfm_char(self.tfm_char)
        form.glyph_information_table_view.resizeColumnsToContents()

        # glyph.print_summary()
        # glyph.print_glyph()
      
        self.scene.clear()

        if isinstance(self.font, Type1Font):
            self.paint_type1_char(i)
        elif isinstance(self.font, PkFont):
            self.paint_pk_char(i)

        self.paint_glyph_box()

        self.scene.update()

    ###############################################

    def paint_glyph_box(self):

        qt_glyph = self.qt_glyph

        red_pen = QtGui.QPen(QtCore.Qt.red)

        char_box = QtCore.QRectF(qt_glyph.horizontal_offset, qt_glyph.vertical_offset,
                                 qt_glyph.width, qt_glyph.height)

        self.scene.addRect(char_box, red_pen)

        width = qt_glyph.width - qt_glyph.horizontal_offset
        depth = qt_glyph.height + qt_glyph.vertical_offset
        height = qt_glyph.height

        print width, depth, height

        box_scale = 1.25

        # Base line
        self.scene.addLine(-(box_scale-1)*width, 0, box_scale*width, 0, red_pen)

        # Vertical Line
        self.scene.addLine(0, box_scale*(depth+.25*height), 0, -box_scale*height, red_pen)

        ## box_depth  = max(glyph.height - glyph.vertical_offset, glyph.vertical_offset)
        ## box_height = max(glyph.vertical_offset, box_depth)
        ## 
        ## self.scene.addLine(-box_scale*glyph.width, 0, (box_scale+1)*glyph.width, 0, red_pen)
        ## self.scene.addLine(0, box_scale*box_depth, 0, -box_scale*box_height, red_pen)

    ###############################################

    def paint_type1_char(self, i):

        self.qt_glyph = qt_glyph = QtFtGlyph(self.font, i, magnification = 1)

        char_pixmap_item = self.scene.addPixmap(qt_glyph.pixmap)
        char_pixmap_item.setOffset(qt_glyph.horizontal_offset, qt_glyph.vertical_offset)

    ###############################################

    def paint_pk_char(self, i):

        self.qt_glyph = qt_glyph = QtPkGlyph(self.font, i, magnification = 1)

        char_pixmap_item = self.scene.addPixmap(qt_glyph.pixmap)
        char_pixmap_item.setOffset(qt_glyph.horizontal_offset, qt_glyph.vertical_offset)

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
