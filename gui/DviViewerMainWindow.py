# -*- coding: utf-8 -*-

#####################################################################################################

import math

from PyQt4 import QtGui, QtCore, uic

import numpy as np

#####################################################################################################

from DviMachine import DviMachine
from DviParser import DviParser 
from FontManager import *
from PkFont import *
from TeXUnit import *
from Type1Font import *

#####################################################################################################

page_width  = 210
page_height = 297

#####################################################################################################

class QtFtGlyph(object):

    ###############################################

    def __init__(self, font, glyph_index, magnification):

        print 'QtFtGlyph', font.name, glyph_index, magnification

        glyph = font.get_glyph(glyph_index, size = 10, resolution = 100)

        glyph_bitmap = glyph.glyph_bitmap

        np_bitmap = np.fromstring(glyph_bitmap.bitmap, dtype=np.uint8)
        np_bitmap.shape = glyph_bitmap.rows, glyph_bitmap.width

        glyph_image = QtGui.QImage(glyph_bitmap.width, glyph_bitmap.rows, QtGui.QImage.Format_ARGB32)
        
        for y in xrange(glyph_bitmap.rows):
            for x in xrange(glyph_bitmap.width):
                gray_level = np_bitmap[y,x]
                if gray_level == 0:
                    argb = (gray_level << 16) + (gray_level << 8) + gray_level # 0 << 24 + 
                    # argb = 0x00FFFFFF
                else:
                    argb = 0xFF000000
                    # print x, y, gray_level, hex(argb)
                glyph_image.setPixel(x, y, int(argb))
        
        glyph_pixmap = QtGui.QPixmap.fromImage(glyph_image)

        glyph_pixmap.loadFromData(QtCore.QByteArray(glyph_bitmap.bitmap))

        print 'Left:', glyph_bitmap.left
        print 'Top:', glyph_bitmap.top

        self.pixmap = glyph_pixmap

        self.horizontal_offset = glyph_bitmap.left
        self.vertical_offset = - glyph_bitmap.top

#####################################################################################################

class QtPkGlyph(object):

    ###############################################

    def __init__(self, font, glyph_index, magnification):

        print 'QtPkGlyph', font.name, glyph_index, magnification

        glyph = font[glyph_index]

        glyph_bitmap = glyph.get_glyph_bitmap()
        
        glyph_image = QtGui.QImage(glyph.width, glyph.height, QtGui.QImage.Format_ARGB32) # Format_Mono
        
        for y in xrange(glyph.height):
            for x in xrange(glyph.width):
                if glyph_bitmap[y, x] == 1:
                    glyph_image.setPixel(x, y, 0xFF000000)
                else:
                    glyph_image.setPixel(x, y, 0x00FFFFFF)
        
        glyph_pixmap = QtGui.QPixmap.fromImage(glyph_image)

        self.pixmap = glyph_pixmap

        self.horizontal_offset = -glyph.horizontal_offset
        self.vertical_offset   = -glyph.vertical_offset

        self.h_scale = dpi2mm(glyph.pk_font.horizontal_dpi/magnification)
        self.v_scale = dpi2mm(glyph.pk_font.vertical_dpi/magnification)

        print 'Magnification', float(magnification), self.h_scale, self.v_scale

#####################################################################################################

class QtDviMachine(DviMachine):
    
    ###############################################

    def __init__(self, font_manager, scene):

        super(QtDviMachine, self).__init__(font_manager)

        self.scene = scene

        self.glyphs = {}

    ###############################################

    def hash_glyph(self, font, glyph_index, magnification):

        return hex(font.id)[2:] + hex(glyph_index)[1:] # + hex(magnification)[1:]

    ###############################################

    def get_glyph(self, font, glyph_index, magnification):

        glyph_hash_key = self.hash_glyph(font, glyph_index, magnification)

        if self.glyphs.has_key(glyph_hash_key) is True:
            glyph = self.glyphs[glyph_hash_key]
        else:
            if isinstance(font, Type1Font):
                glyph = QtFtGlyph(font, glyph_index, magnification)
            elif isinstance(font, PkFont):
                glyph = QtPkGlyph(font, glyph_index, magnification)

            self.glyphs[glyph_hash_key] = glyph

        return glyph

    ###############################################

    def paint_rule(self, x, y, w, h):

        x_mm, y_mm, w_mm, h_mm = map(sp2mm, (x, y, w, h))

        print 'paint_rule', x_mm, y_mm, w_mm, h_mm

        rule_rect = QtCore.QRectF(x_mm, y_mm, w_mm, h_mm)

        pen = QtGui.QPen(QtCore.Qt.black)
        brush = QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern)

        rule_item = self.scene.addRect(rule_rect, pen, brush)

    ###############################################

    def paint_char(self, xg, yg, char_bounding_box, font, glyph_index, magnification):
        
        # self.paint_char_box(char_bounding_box)

        if isinstance(font, Type1Font):
            self.paint_type1_char(xg, yg, font, glyph_index, magnification)
        elif isinstance(font, PkFont):
            self.paint_pk_char(xg, yg, font, glyph_index, magnification)

    ###############################################

    def paint_char_box(self, char_bounding_box):

        x, y = char_bounding_box.x.inf, char_bounding_box.y.inf

        x_mm, y_mm = map(sp2mm, (x, y))

        box_width  = sp2mm(char_bounding_box.x.length_float())
        box_height = sp2mm(char_bounding_box.y.length_float())

        red_pen = QtGui.QPen(QtCore.Qt.red)

        char_box_rect = QtCore.QRectF(x_mm, y_mm, box_width, box_height)

        char_box_item = self.scene.addRect(char_box_rect, red_pen)

    ###############################################

    def paint_type1_char(self, xg, yg, font, glyph_index, magnification):

        xg_mm, yg_mm = map(sp2mm, (xg, yg))

        qt_glyph = self.get_glyph(font, glyph_index, magnification)

        char_pixmap_item = self.scene.addPixmap(qt_glyph.pixmap)
        char_pixmap_item.setOffset(qt_glyph.horizontal_offset, qt_glyph.vertical_offset)
        char_pixmap_item.translate(xg_mm, yg_mm)
        char_pixmap_item.scale(.25, .25)
        # char_pixmap_item.scale(h_scale, v_scale)

    ###############################################

    def paint_pk_char(self, xg, yg, font, glyph_index, magnification):

        xg_mm, yg_mm = map(sp2mm, (xg, yg))

        qt_glyph = self.get_glyph(font, glyph_index, magnification)

        char_pixmap_item = self.scene.addPixmap(qt_glyph.pixmap)
        char_pixmap_item.setOffset(qt_glyph.horizontal_offset, qt_glyph.vertical_offset)
        char_pixmap_item.translate(xg_mm, yg_mm)
        char_pixmap_item.scale(qt_glyph.h_scale, qt_glyph.v_scale)

        ### box_depth  = max(glyph.height - glyph.vertical_offset, glyph.vertical_offset)
        ### box_height = max(glyph.vertical_offset, box_depth)
        ###
        ### box_scale = 1.5
        ### 
        ### h_line_item = self.scene.addLine(-box_scale*glyph.width, 0, (box_scale+1)*glyph.width, 0, red_pen)
        ### v_line_item = self.scene.addLine(0, box_scale*box_depth, 0, -box_scale*box_height, red_pen)
        ###
        ### for item in (char_pixmap_item, h_line_item, v_line_item, char_box_item):
        ###     item.translate(x_mm, y_mm)
        ###     item.scale(h_scale, v_scale)
        ### 
        ### for item in (h_line_item, v_line_item):
        ###     item.setVisible(False)

#####################################################################################################

from dvi_viewer_ui import Ui_main_window

#####################################################################################################
#
# Main Window
#

class MainWindow(QtGui.QMainWindow):

    ###############################################

    def __init__(self, dvi_file):

        # Init GUI

        super(MainWindow, self).__init__()

        self.form = form = Ui_main_window()
        self.form.setupUi(self)

        # Graphics View

        self.scene = scene = QtGui.QGraphicsScene(self)

        margin = 50
        scene.setSceneRect(-margin, -margin, page_width + margin, page_height + margin)

        dvi_graphics_view = form.dvi_graphics_view

        dvi_graphics_view.setScene(scene)

        dvi_graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)
        dvi_graphics_view.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        dvi_graphics_view.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)

        page_rect = QtCore.QRectF(0, 0, page_width, page_height)

        dvi_graphics_view.ensureVisible(page_rect, 50, 50)

        # DVI

        self.__init_dvi_machine()

        self.process_dvi_stream(dvi_file)

    ###############################################

    def __init_dvi_machine(self):

        self.dvi_parser = DviParser(debug = False)

        self.font_manager = FontManager(font_map = 'pdftex', use_pk = True)

        self.dvi_machine = QtDviMachine(self.font_manager, self.scene)

    ###############################################

    def process_dvi_stream(self, dvi_file):

        dvi_stream = open(dvi_file)

        dvi_program = self.dvi_parser.process_stream(dvi_stream)

        dvi_stream.close()

        dvi_program.print_summary()

        self.scene.clear()

        self.paint_page()

        self.dvi_machine.load_dvi_program(dvi_program)
        
        print 'Run last page:'
        if len(dvi_program.pages) > 0:
            self.dvi_machine.run_page(0)

        self.scene.update()

    ###############################################

    def paint_page(self):

        pen = QtGui.QPen(QtCore.Qt.black)

        page_rect = QtCore.QRectF(0, 0, page_width, page_height)

        self.scene.addRect(page_rect, pen)
        
        grid_spacing = 5

        x = grid_spacing
        while x < page_width:
            self.scene.addRect(QtCore.QRectF(x, 0, 0, page_height), pen)
            x += grid_spacing

        y = grid_spacing
        while y < page_height:
            self.scene.addRect(QtCore.QRectF(0, y, page_width, 0), pen)
            y += grid_spacing
        
    ###############################################

    def keyPressEvent(self, event):

        key = event.key()

        dvi_graphics_view = self.form.dvi_graphics_view

        dx = 10

        print 'keyPressEvent', key

        if key == QtCore.Qt.Key_Up:
            dvi_graphics_view.translate(0, -dx)

        elif key == QtCore.Qt.Key_Down:
            dvi_graphics_view.translate(0, dx)

        elif key == QtCore.Qt.Key_Left:
            dvi_graphics_view.translate(-dx, 0)

        elif key == QtCore.Qt.Key_Right:
            dvi_graphics_view.translate(dx, 0)

        elif key == QtCore.Qt.Key_Plus:
            self.scale_view(2)

        elif key == QtCore.Qt.Key_Minus:
            self.scale_view(.5)

        else:
            QtGui.QGraphicsView.keyPressEvent(dvi_graphics_view, event)

    ###############################################

    def wheelEvent(self, event):

        delta = event.delta()

        if delta > 0:
            self.scale_view(2)
        else:
            self.scale_view(0.5)

    ###############################################

    def scale_view(self, scale_factor):

        dvi_graphics_view = self.form.dvi_graphics_view

        transformation = dvi_graphics_view.matrix().scale(scale_factor, scale_factor)

        factor = transformation.mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.1 or factor > 100:
            return

        dvi_graphics_view.scale(scale_factor, scale_factor)

#####################################################################################################
#
# End
#
#####################################################################################################
