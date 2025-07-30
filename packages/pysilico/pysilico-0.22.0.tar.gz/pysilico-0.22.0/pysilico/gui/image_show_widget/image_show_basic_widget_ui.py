# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'image_show_basic_widget.ui',
# licensing of 'image_show_basic_widget.ui' applies.
#
# Created: Wed Sep 12 00:04:59 2018
#      by: pyside2-uic  running on PySide2 5.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication as QtCompat

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(502, 359)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = GraphicsView(Form)
        self.graphicsView.setEnabled(True)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.labelInfo = QtWidgets.QLabel(Form)
        self.labelInfo.setText("")
        self.labelInfo.setObjectName("labelInfo")
        self.verticalLayout.addWidget(self.labelInfo)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtCompat.translate("Form", "Form", None, -1))

from pyqtgraph.widgets.GraphicsView import GraphicsView
