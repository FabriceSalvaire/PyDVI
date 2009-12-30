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

__ALL__ = ['InfoTableModel']

#####################################################################################################

from PyQt4 import QtGui, QtCore

from PyQt4.QtCore import Qt, QVariant, QModelIndex

#####################################################################################################

from EnumFactory import EnumFactory

#####################################################################################################

columns_enum = EnumFactory('ColumnsEnum',
                           ('field',
                            'value',
                            ))

#####################################################################################################

class InfoTableModel(QtCore.QAbstractTableModel):

    #############################################################################

    def __init__(self):

        super(InfoTableModel, self).__init__()

        self.fields = []
        self.values = {}

    #############################################################################

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid() or not(0 <= index.row() < len(self.fields)):
            return QVariant()

        field = self.fields[index.row()]

        column = index.column()

        if role == Qt.DisplayRole:
            if column == columns_enum.field:
                return QVariant(field)

            elif column == columns_enum.value:
                return QVariant(self.values[field])

        return QVariant()

    #############################################################################

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))

            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        
        if role != Qt.DisplayRole:
            return QVariant()
        
        if orientation == Qt.Horizontal:
            if section == columns_enum.field:
                return QVariant('Field')

            elif section == columns_enum.value:
                return QVariant('Value')

        return QVariant(int(section + 1))

    #############################################################################

    def columnCount(self, index=QModelIndex()):
        return len(columns_enum)

    #############################################################################

    def rowCount(self, index=QModelIndex()):
        return len(self.fields)

#####################################################################################################
#
# End
#
#####################################################################################################
