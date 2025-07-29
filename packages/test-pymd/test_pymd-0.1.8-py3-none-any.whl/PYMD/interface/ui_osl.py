# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'osl.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QLabel,
    QScrollArea, QSizePolicy, QWidget)
from . import resources_rc

class Ui_dialog_osl(object):
    def setupUi(self, dialog_osl):
        if not dialog_osl.objectName():
            dialog_osl.setObjectName(u"dialog_osl")
        dialog_osl.setWindowModality(Qt.WindowModality.WindowModal)
        dialog_osl.resize(480, 640)
        dialog_osl.setMinimumSize(QSize(480, 640))
        dialog_osl.setMaximumSize(QSize(480, 640))
        font = QFont()
        font.setFamilies([u"Gabriola"])
        font.setPointSize(12)
        dialog_osl.setFont(font)
        dialog_osl.setAcceptDrops(False)
        icon = QIcon()
        icon.addFile(u":/img/logo-pymd-2", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        dialog_osl.setWindowIcon(icon)
        dialog_osl.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        dialog_osl.setSizeGripEnabled(False)
        dialog_osl.setModal(True)
        self.gridLayout_2 = QGridLayout(dialog_osl)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.select_library = QComboBox(dialog_osl)
        self.select_library.addItem("")
        self.select_library.addItem("")
        self.select_library.addItem("")
        self.select_library.setObjectName(u"select_library")
        self.select_library.setMinimumSize(QSize(150, 0))
        font1 = QFont()
        font1.setFamilies([u"Gabriola"])
        font1.setPointSize(14)
        self.select_library.setFont(font1)
        self.select_library.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))

        self.gridLayout_2.addWidget(self.select_library, 0, 1, 1, 1)

        self.frame_container_osl = QFrame(dialog_osl)
        self.frame_container_osl.setObjectName(u"frame_container_osl")
        self.frame_container_osl.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_container_osl.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_container_osl)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea = QScrollArea(self.frame_container_osl)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 442, 515))
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.text_container_license = QLabel(self.scrollAreaWidgetContents)
        self.text_container_license.setObjectName(u"text_container_license")
        self.text_container_license.setMaximumSize(QSize(424, 16777215))
        font2 = QFont()
        font2.setFamilies([u"Times New Roman"])
        font2.setPointSize(12)
        self.text_container_license.setFont(font2)
        self.text_container_license.setTextFormat(Qt.TextFormat.MarkdownText)
        self.text_container_license.setWordWrap(True)
        self.text_container_license.setOpenExternalLinks(True)
        self.text_container_license.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_3.addWidget(self.text_container_license, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 1)

        self.url_osl = QLabel(self.frame_container_osl)
        self.url_osl.setObjectName(u"url_osl")
        self.url_osl.setMinimumSize(QSize(0, 20))
        self.url_osl.setMaximumSize(QSize(444, 20))
        self.url_osl.setTextFormat(Qt.TextFormat.MarkdownText)
        self.url_osl.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft)
        self.url_osl.setOpenExternalLinks(True)

        self.gridLayout.addWidget(self.url_osl, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_container_osl, 1, 0, 1, 2)

        self.info_osl = QLabel(dialog_osl)
        self.info_osl.setObjectName(u"info_osl")
        self.info_osl.setMaximumSize(QSize(300, 16777215))
        self.info_osl.setFont(font1)
        self.info_osl.setTextFormat(Qt.TextFormat.PlainText)
        self.info_osl.setScaledContents(False)
        self.info_osl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.info_osl, 0, 0, 1, 1)

        self.close_dialog_osl = QDialogButtonBox(dialog_osl)
        self.close_dialog_osl.setObjectName(u"close_dialog_osl")
        self.close_dialog_osl.setOrientation(Qt.Orientation.Horizontal)
        self.close_dialog_osl.setStandardButtons(QDialogButtonBox.StandardButton.Close)
        self.close_dialog_osl.setCenterButtons(True)

        self.gridLayout_2.addWidget(self.close_dialog_osl, 2, 0, 1, 2)


        self.retranslateUi(dialog_osl)
        self.close_dialog_osl.accepted.connect(dialog_osl.accept)
        self.close_dialog_osl.rejected.connect(dialog_osl.reject)

        QMetaObject.connectSlotsByName(dialog_osl)
    # setupUi

    def retranslateUi(self, dialog_osl):
        dialog_osl.setWindowTitle(QCoreApplication.translate("dialog_osl", u"Open Source Licenses - Notice", None))
        self.select_library.setItemText(0, QCoreApplication.translate("dialog_osl", u"Select a library", None))
        self.select_library.setItemText(1, QCoreApplication.translate("dialog_osl", u"Markitdown", None))
        self.select_library.setItemText(2, QCoreApplication.translate("dialog_osl", u"PySide6", None))

        self.select_library.setCurrentText(QCoreApplication.translate("dialog_osl", u"Select a library", None))
        self.text_container_license.setText("")
        self.url_osl.setText("")
        self.info_osl.setText(QCoreApplication.translate("dialog_osl", u"CREDITS", None))
    # retranslateUi

