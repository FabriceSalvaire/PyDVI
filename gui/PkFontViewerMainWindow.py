# -*- coding: utf-8 -*-

#####################################################################################################

import math

from PyQt4 import QtGui, QtCore, uic

#####################################################################################################

from PyDVI.FontManager import *

#####################################################################################################

from pkfont_viewer_ui import Ui_main_window

#####################################################################################################
#
# Main Window
#

#####################################################################################################

class MainWindow(QtGui.QMainWindow):

    ###############################################

    def __init__(self, font_name = None):

        # Init GUI

        super(MainWindow, self).__init__()

        self.form = form = Ui_main_window()
        self.form.setupUi(self)

        # Graphics View

        self.scene = scene = QtGui.QGraphicsScene(self)
        scene.setSceneRect(0, 0, 100, 100)

        glyph_graphics_view = form.glyph_graphics_view
        glyph_graphics_view.setScene(scene)
        glyph_graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)

        # Signals

        signal = QtCore.SIGNAL('clicked()')

        QtCore.QObject.connect(form.load_font_button, signal, self.load_font)

        signal = QtCore.SIGNAL('valueChanged(int)')

        QtCore.QObject.connect(form.char_code_spin_box, signal, self.show_glyph)

        # 

        if font_name is not None:
            form.font_name_line_edit.setText(font_name)
            # timer: self.load_font()

        self.font_manager = FontManager()

    ###############################################

    def load_font(self):

        form = self.form

        font_name = str(form.font_name_line_edit.text())

        #try:
        self.font = self.font_manager.load_font(font_types.Pk, font_name)
        
        form.char_code_spin_box.setMaximum(len(self.font) -1)
        
        self.font.print_summary()
        
        self.show_glyph(0)

        #except:
            #pass
            #self.font = None
            #form.char_code_spin_box.setMaximum(0)

    ###############################################

    def show_glyph(self, i):

        if self.font is None:
            return

        glyph = self.font[i]
        
        glyph.print_summary()
        glyph.print_glyph()
        
        glyph_bitmap = glyph.get_glyph_bitmap()

        glyph_image = QtGui.QImage(glyph.width, glyph.height, QtGui.QImage.Format_ARGB32) # Format_Mono

        for y in xrange(glyph.height):
            for x in xrange(glyph.width):

                if glyph_bitmap[y, x] == 1:
                    glyph_image.setPixel(x, y, 0xFF000000)
                else:
                    glyph_image.setPixel(x, y, 0xFFFFFFFF)

        self.glyph_bitmap = QtGui.QPixmap.fromImage(glyph_image)

        self.scene.clear()
        self.scene.addPixmap(self.glyph_bitmap)
        self.scene.update()

#    ###############################################
#
#    def keyPressEvent(self, event):
#
#        key = event.key()
#
#        if key == QtCore.Qt.Key_Up:
#            self.translate(0, -2*self.site_radius)
#
#        elif key == QtCore.Qt.Key_Down:
#            self.translate(0, 2*self.site_radius)
#
#        elif key == QtCore.Qt.Key_Left:
#            self.translate(-2*self.site_radius, 0)
#
#        elif key == QtCore.Qt.Key_Right:
#            self.translate(2*self.site_radius, 0)
#
#        elif key == QtCore.Qt.Key_Plus:
#            self.scale_view(1.2)
#
#        elif key == QtCore.Qt.Key_Minus:
#            self.scale_view(1. / 1.2)
#
#        else:
#            QtGui.QGraphicsView.keyPressEvent(self, event)

    ###############################################

    def wheelEvent(self, event):

        self.scale_view(math.pow(2.0, event.delta() / 240.))

    ###############################################

    def scale_view(self, scale_factor):

        glyph_graphics_view = self.form.glyph_graphics_view

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
