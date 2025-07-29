# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_about.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QGridLayout, QLabel, QScrollArea,
    QSizePolicy, QWidget)

class Ui_about_dialog(object):
    def setupUi(self, about_dialog):
        if not about_dialog.objectName():
            about_dialog.setObjectName(u"about_dialog")
        about_dialog.resize(578, 640)
        about_dialog.setMinimumSize(QSize(578, 640))
        about_dialog.setMaximumSize(QSize(578, 640))
        font = QFont()
        font.setFamilies([u"Gabriola"])
        font.setPointSize(20)
        about_dialog.setFont(font)
        about_dialog.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        about_dialog.setModal(True)
        self.gridLayout = QGridLayout(about_dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.close_button = QDialogButtonBox(about_dialog)
        self.close_button.setObjectName(u"close_button")
        font1 = QFont()
        font1.setFamilies([u"Gabriola"])
        font1.setPointSize(12)
        self.close_button.setFont(font1)
        self.close_button.setOrientation(Qt.Orientation.Horizontal)
        self.close_button.setStandardButtons(QDialogButtonBox.StandardButton.Close)
        self.close_button.setCenterButtons(True)

        self.gridLayout.addWidget(self.close_button, 4, 0, 1, 1)

        self.container_label_about = QGridLayout()
        self.container_label_about.setObjectName(u"container_label_about")
        self.container_label_about.setContentsMargins(-1, 0, -1, -1)
        self.about_label = QLabel(about_dialog)
        self.about_label.setObjectName(u"about_label")
        self.about_label.setMinimumSize(QSize(0, 20))
        self.about_label.setMaximumSize(QSize(150, 40))
        font2 = QFont()
        font2.setFamilies([u"Gabriola"])
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setItalic(False)
        font2.setUnderline(False)
        font2.setStrikeOut(False)
        font2.setKerning(True)
        self.about_label.setFont(font2)
        self.about_label.setStyleSheet(u"background-color: rgb(59, 59, 59);\n"
"color: #84CD4F;\n"
"border-radius: 5px;")
        self.about_label.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.about_label.setTextFormat(Qt.TextFormat.RichText)
        self.about_label.setScaledContents(False)
        self.about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.about_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.container_label_about.addWidget(self.about_label, 0, 0, 1, 1)


        self.gridLayout.addLayout(self.container_label_about, 1, 0, 1, 1)

        self.container_scroll_about = QScrollArea(about_dialog)
        self.container_scroll_about.setObjectName(u"container_scroll_about")
        self.container_scroll_about.setWidgetResizable(True)
        self.container_about_text = QWidget()
        self.container_about_text.setObjectName(u"container_about_text")
        self.container_about_text.setGeometry(QRect(0, 0, 558, 562))
        self.formLayout = QFormLayout(self.container_about_text)
        self.formLayout.setObjectName(u"formLayout")
        self.text_about = QLabel(self.container_about_text)
        self.text_about.setObjectName(u"text_about")
        self.text_about.setMaximumSize(QSize(540, 16777215))
        self.text_about.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.text_about.setTextFormat(Qt.TextFormat.RichText)
        self.text_about.setWordWrap(True)
        self.text_about.setOpenExternalLinks(True)
        self.text_about.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.text_about)

        self.container_scroll_about.setWidget(self.container_about_text)

        self.gridLayout.addWidget(self.container_scroll_about, 3, 0, 1, 1)


        self.retranslateUi(about_dialog)
        self.close_button.accepted.connect(about_dialog.accept)
        self.close_button.rejected.connect(about_dialog.reject)

        QMetaObject.connectSlotsByName(about_dialog)
    # setupUi

    def retranslateUi(self, about_dialog):
        about_dialog.setWindowTitle(QCoreApplication.translate("about_dialog", u"About", None))
        self.about_label.setText(QCoreApplication.translate("about_dialog", u"<code>pip install pymd</code>", None))
    # retranslateUi

