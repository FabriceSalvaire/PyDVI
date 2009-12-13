# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pkfont_viewer.ui'
#
# Created: Sun Dec 13 13:58:22 2009
#      by: PyQt4 UI code generator 4.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(800, 600)
        self.central_widget = QtGui.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.central_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.font_name_label = QtGui.QLabel(self.central_widget)
        self.font_name_label.setObjectName("font_name_label")
        self.horizontalLayout.addWidget(self.font_name_label)
        self.font_name_line_edit = QtGui.QLineEdit(self.central_widget)
        self.font_name_line_edit.setObjectName("font_name_line_edit")
        self.horizontalLayout.addWidget(self.font_name_line_edit)
        self.load_font_button = QtGui.QPushButton(self.central_widget)
        self.load_font_button.setObjectName("load_font_button")
        self.horizontalLayout.addWidget(self.load_font_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.char_code_label = QtGui.QLabel(self.central_widget)
        self.char_code_label.setObjectName("char_code_label")
        self.horizontalLayout_2.addWidget(self.char_code_label)
        self.char_code_spin_box = QtGui.QSpinBox(self.central_widget)
        self.char_code_spin_box.setMaximum(999)
        self.char_code_spin_box.setObjectName("char_code_spin_box")
        self.horizontalLayout_2.addWidget(self.char_code_spin_box)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.glyph_graphics_view = QtGui.QGraphicsView(self.central_widget)
        self.glyph_graphics_view.setObjectName("glyph_graphics_view")
        self.verticalLayout.addWidget(self.glyph_graphics_view)
        main_window.setCentralWidget(self.central_widget)
        self.menubar = QtGui.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        main_window.setWindowTitle(QtGui.QApplication.translate("main_window", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.font_name_label.setText(QtGui.QApplication.translate("main_window", "Font Name", None, QtGui.QApplication.UnicodeUTF8))
        self.load_font_button.setText(QtGui.QApplication.translate("main_window", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.char_code_label.setText(QtGui.QApplication.translate("main_window", "Char Code", None, QtGui.QApplication.UnicodeUTF8))

