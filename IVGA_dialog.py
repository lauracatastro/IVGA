# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Plugin\IVGA_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IVGA_dialog(object):
    def setupUi(self, IVGA_dialog):
        IVGA_dialog.setObjectName("IVGA_dialog")
        IVGA_dialog.resize(550, 466)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        IVGA_dialog.setFont(font)
        IVGA_dialog.setWindowTitle("Exportación parcelas a GML")
        self.verticalLayout = QtWidgets.QVBoxLayout(IVGA_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Logo = QtWidgets.QLabel(IVGA_dialog)
        self.Logo.setMinimumSize(QtCore.QSize(48, 48))
        self.Logo.setMaximumSize(QtCore.QSize(48, 48))
        self.Logo.setText("")
        self.Logo.setPixmap(QtGui.QPixmap("IVGA.png"))
        self.Logo.setScaledContents(True)
        self.Logo.setObjectName("Logo")
        self.horizontalLayout_2.addWidget(self.Logo)
        self.label = QtWidgets.QLabel(IVGA_dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.label.setOpenExternalLinks(True)
        self.label.setText('<a href="https://www.catastro.minhafp.es/asistente_catreg/img/IVGA.pdf">Exportación parcelas catastrales<br/>(formato INSPIRE GML CP)</a>')
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(IVGA_dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.Selec = QtWidgets.QTableWidget(IVGA_dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Selec.setFont(font)
        self.Selec.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.Selec.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.Selec.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.Selec.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.Selec.setWordWrap(False)
        self.Selec.setObjectName("Selec")
        self.Selec.setColumnCount(0)
        self.Selec.setRowCount(0)
        self.Selec.horizontalHeader().setDefaultSectionSize(20)
        self.Selec.horizontalHeader().setHighlightSections(False)
        self.Selec.horizontalHeader().setMinimumSectionSize(20)
        self.Selec.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.Selec, 0, 1, 1, 1)

        self.check_lbl = QtWidgets.QLabel(IVGA_dialog)
        self.check_lbl.setObjectName("check_lbl")
        self.gridLayout.addWidget(self.check_lbl, 1, 0, 1, 1)
        self.check = QtWidgets.QCheckBox(IVGA_dialog)
        self.check.setObjectName("check")
        self.gridLayout.addWidget(self.check, 1, 1, 1, 1)

        self.fileName_lbl = QtWidgets.QLabel(IVGA_dialog)
        self.fileName_lbl.setObjectName("fileName_lbl")
        self.gridLayout.addWidget(self.fileName_lbl, 2, 0, 1, 1)
        self.fileName = QtWidgets.QLineEdit(IVGA_dialog)
        self.fileName.setObjectName("fileName")
        self.gridLayout.addWidget(self.fileName, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(IVGA_dialog)
        self.label_3.setMinimumSize(QtCore.QSize(116, 0))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.data = QtWidgets.QDateTimeEdit(IVGA_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data.sizePolicy().hasHeightForWidth())
        self.data.setSizePolicy(sizePolicy)
        self.data.setMinimumSize(QtCore.QSize(157, 25))
        self.data.setMaximumSize(QtCore.QSize(157, 25))
        self.data.setCalendarPopup(True)
        self.data.setObjectName("data")
        self.horizontalLayout_3.addWidget(self.data)
        self.label_5 = QtWidgets.QLabel(IVGA_dialog)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.Inspire3 = QtWidgets.QRadioButton(IVGA_dialog)
        self.Inspire3.setObjectName("Inspire3")
        self.horizontalLayout_3.addWidget(self.Inspire3)
        self.Inspire4 = QtWidgets.QRadioButton(IVGA_dialog)
        self.Inspire4.setObjectName("Inspire4")
        self.horizontalLayout_3.addWidget(self.Inspire4)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(IVGA_dialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.desti = QtWidgets.QLineEdit(IVGA_dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.desti.setFont(font)
        self.desti.setObjectName("desti")
        self.horizontalLayout_5.addWidget(self.desti)
        self.Carpeta = QtWidgets.QPushButton(IVGA_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Carpeta.sizePolicy().hasHeightForWidth())
        self.Carpeta.setSizePolicy(sizePolicy)
        self.Carpeta.setMinimumSize(QtCore.QSize(33, 29))
        self.Carpeta.setMaximumSize(QtCore.QSize(33, 29))
        self.Carpeta.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Carpeta.setIcon(icon1)
        self.Carpeta.setAutoDefault(False)
        self.Carpeta.setObjectName("Carpeta")
        self.horizontalLayout_5.addWidget(self.Carpeta)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.Crear = QtWidgets.QPushButton(IVGA_dialog)
        self.Crear.setObjectName("Crear")
        self.horizontalLayout.addWidget(self.Crear)
        self.Tancar = QtWidgets.QPushButton(IVGA_dialog)
        self.Tancar.setObjectName("Tancar")
        self.horizontalLayout.addWidget(self.Tancar)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(IVGA_dialog)
        self.Tancar.clicked.connect(IVGA_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(IVGA_dialog)

    def retranslateUi(self, IVGA_dialog):
        _translate = QtCore.QCoreApplication.translate
        #self.label.setText(_translate("IVGA_dialog", "Exportación parcelas catastrales\n(formato INSPIRE GML CP)"))
        self.label_2.setText(_translate("IVGA_dialog", "Parcelas\nseleccionadas"))

        self.check_lbl.setText(_translate("IVGA_dialog", "Comprobar Ref. Cat."))
        self.fileName_lbl.setText(_translate("IVGA_dialog", "Nombre del fichero"))
        self.label_3.setText(_translate("IVGA_dialog", "Fecha y hora"))
        self.data.setDisplayFormat(_translate("IVGA_dialog", "dd-MM-yyyy H:mm"))
        self.label_5.setText(_translate("IVGA_dialog", "   INSPIRE:"))
        self.Inspire3.setText(_translate("IVGA_dialog", "v3"))
        self.Inspire4.setText(_translate("IVGA_dialog", "v4"))
        self.label_4.setText(_translate("IVGA_dialog", "Carpeta destino"))
        self.Crear.setText(_translate("IVGA_dialog", "Crear GML"))
        self.Tancar.setText(_translate("IVGA_dialog", "Salir"))
