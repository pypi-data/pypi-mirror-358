# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_language.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QGridLayout, QLayout, QListView,
    QListWidget, QListWidgetItem, QSizePolicy, QWidget)

from . import resources_rc

class Ui_Lang_Dialog(object):
    def setupUi(self, Lang_Dialog):
        if not Lang_Dialog.objectName():
            Lang_Dialog.setObjectName(u"Lang_Dialog")
        Lang_Dialog.resize(330, 320)
        Lang_Dialog.setMinimumSize(QSize(100, 100))
        Lang_Dialog.setMaximumSize(QSize(330, 320))
        font = QFont()
        font.setFamilies([u"Gabriola"])
        font.setPointSize(12)
        Lang_Dialog.setFont(font)
        icon = QIcon()
        icon.addFile(u":/img/logo-pymd-2", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Lang_Dialog.setWindowIcon(icon)
        Lang_Dialog.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        Lang_Dialog.setAutoFillBackground(False)
        Lang_Dialog.setStyleSheet(u"")
        Lang_Dialog.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.dialog_languages_layout = QGridLayout(Lang_Dialog)
        self.dialog_languages_layout.setObjectName(u"dialog_languages_layout")
        self.dialog_languages_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.dialog_btn = QDialogButtonBox(Lang_Dialog)
        self.dialog_btn.setObjectName(u"dialog_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dialog_btn.sizePolicy().hasHeightForWidth())
        self.dialog_btn.setSizePolicy(sizePolicy)
        self.dialog_btn.setOrientation(Qt.Orientation.Horizontal)
        self.dialog_btn.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)
        self.dialog_btn.setCenterButtons(True)

        self.dialog_languages_layout.addWidget(self.dialog_btn, 3, 0, 1, 1)

        self.languages = QListWidget(Lang_Dialog)
        icon1 = QIcon()
        icon1.addFile(u":/flags/en_GB.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qlistwidgetitem = QListWidgetItem(self.languages)
        __qlistwidgetitem.setFont(font);
        __qlistwidgetitem.setIcon(icon1);
#if QT_CONFIG(tooltip)
        __qlistwidgetitem.setToolTip(u"en_GB");
#endif // QT_CONFIG(tooltip)
        icon2 = QIcon()
        icon2.addFile(u":/flags/es_CO.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qlistwidgetitem1 = QListWidgetItem(self.languages)
        __qlistwidgetitem1.setFont(font);
        __qlistwidgetitem1.setIcon(icon2);
#if QT_CONFIG(tooltip)
        __qlistwidgetitem1.setToolTip(u"es_CO");
#endif // QT_CONFIG(tooltip)
        self.languages.setObjectName(u"languages")
        self.languages.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.languages.sizePolicy().hasHeightForWidth())
        self.languages.setSizePolicy(sizePolicy1)
        self.languages.setMinimumSize(QSize(0, 0))
        self.languages.setMaximumSize(QSize(16777215, 272))
        self.languages.setAutoFillBackground(False)
        self.languages.setStyleSheet(u"QDialog > QListWidget{\n"
"background-image: url(:/img/logo-pymd-2.2);\n"
"background-position: center;\n"
"background-repeat: no-repeat;\n"
"background-attachment: fixed;}")
        self.languages.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.languages.setTabKeyNavigation(True)
        self.languages.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.languages.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.languages.setMovement(QListView.Movement.Static)
        self.languages.setFlow(QListView.Flow.TopToBottom)
        self.languages.setViewMode(QListView.ViewMode.ListMode)
        self.languages.setUniformItemSizes(False)
        self.languages.setSortingEnabled(True)

        self.dialog_languages_layout.addWidget(self.languages, 1, 0, 1, 1)


        self.retranslateUi(Lang_Dialog)
        self.dialog_btn.accepted.connect(Lang_Dialog.accept)
        self.dialog_btn.rejected.connect(Lang_Dialog.reject)

        self.languages.setCurrentRow(0)


        QMetaObject.connectSlotsByName(Lang_Dialog)
    # setupUi

    def retranslateUi(self, Lang_Dialog):
        Lang_Dialog.setWindowTitle(QCoreApplication.translate("Lang_Dialog", u"Select Language", None))

        __sortingEnabled = self.languages.isSortingEnabled()
        self.languages.setSortingEnabled(False)
        ___qlistwidgetitem = self.languages.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Lang_Dialog", u"English - GB", None));
        ___qlistwidgetitem1 = self.languages.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("Lang_Dialog", u"Spanish - CO", None));
        self.languages.setSortingEnabled(__sortingEnabled)

    # retranslateUi

