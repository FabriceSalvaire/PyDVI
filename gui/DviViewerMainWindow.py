# -*- coding: utf-8 -*-

#####################################################################################################

import math

from PyQt4 import QtGui, QtCore, uic

#####################################################################################################

from TeXUnit import *
from DviParser import DviParser 
from DviMachine import DviMachine

#####################################################################################################

page_width  = 210
page_height = 297

#####################################################################################################

class QtDviMachine(DviMachine):
    
    ###############################################

    def __init__(self, scene):

        super(QtDviMachine, self).__init__(font_map = 'pdftex')

        self.scene = scene

    ###############################################

    def paint_rule(self, x, y, w, h):

        x_mm, y_mm, w_mm, h_mm = map(sp2mm, (x, y, w, h))

        print 'paint_rule', x_mm, y_mm, w_mm, h_mm

        rule_rect = QtCore.QRectF(x_mm, y_mm, w_mm, h_mm)

        pen = QtGui.QPen(QtCore.Qt.black)
        brush = QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern)

        rule_item = self.scene.addRect(rule_rect, pen, brush)

    ###############################################

    def paint_char(self, xg, yg, char_bounding_box, glyph, magnification):

        h_scale = dpi2mm(glyph.pk_font.horizontal_dpi/magnification)
        v_scale = dpi2mm(glyph.pk_font.vertical_dpi/magnification)
        print 'Magnification', float(magnification), h_scale, v_scale

        x, y = char_bounding_box.x.inf, char_bounding_box.y.inf

        x_mm, y_mm = sp2mm(x), sp2mm(y)

        xg_mm, yg_mm = sp2mm(xg), sp2mm(yg)

        print 'paint_char', x, y, x_mm, y_mm

        glyph_bitmap = glyph.get_glyph_bitmap()
        
        glyph_image = QtGui.QImage(glyph.width, glyph.height, QtGui.QImage.Format_ARGB32) # Format_Mono
        
        for y in xrange(glyph.height):
            for x in xrange(glyph.width):
                if glyph_bitmap[y, x] == 1:
                    glyph_image.setPixel(x, y, 0xFF000000)
                else:
                    glyph_image.setPixel(x, y, 0x00FFFFFF)
        
        glyph_bitmap = QtGui.QPixmap.fromImage(glyph_image)

        char_pixmap_item = self.scene.addPixmap(glyph_bitmap)
        char_pixmap_item.setOffset(-glyph.horizontal_offset, -glyph.vertical_offset)
        char_pixmap_item.translate(xg_mm, yg_mm)
        char_pixmap_item.scale(h_scale, v_scale)

        #b# box_depth  = max(glyph.height - glyph.vertical_offset, glyph.vertical_offset)
        #b# box_height = max(glyph.vertical_offset, box_depth)

        box_width  = sp2mm(char_bounding_box.x.length_float())
        box_height = sp2mm(char_bounding_box.y.length_float())

        red_pen = QtGui.QPen(QtCore.Qt.red)
         
        #l# box_scale = 1.5
        #l# 
        #l# h_line_item = self.scene.addLine(-box_scale*glyph.width, 0, (box_scale+1)*glyph.width, 0, red_pen)
        #l# v_line_item = self.scene.addLine(0, box_scale*box_depth, 0, -box_scale*box_height, red_pen)

        #b# char_box_rect = QtCore.QRectF(-glyph.horizontal_offset, -glyph.vertical_offset, glyph.width, glyph.height)

        char_box_rect = QtCore.QRectF(x_mm, y_mm, box_width, box_height)

        char_box_item = self.scene.addRect(char_box_rect, red_pen)
        
        #!# for item in (char_pixmap_item, h_line_item, v_line_item, char_box_item):
        #!#     item.translate(x_mm, y_mm)
        #!#     item.scale(h_scale, v_scale)
        #!# 
        #!# for item in (h_line_item, v_line_item):
        #!#     item.setVisible(False)

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

        self.dvi_machine = QtDviMachine(self.scene)

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
