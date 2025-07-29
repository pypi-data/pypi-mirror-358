from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QLabel, QTextEdit, QGridLayout, QFrame, QSizePolicy
from ._lang import LanguageManager

class InitialHelp:
    def __init__(self, window, app):
        self._w = window
        self.__lang: LanguageManager = LanguageManager(app)
        self.__logo = QLabel()
        self.__logo.setMinimumSize(500, 500)
        self.__logo.setTextFormat(Qt.TextFormat.RichText)
        self.__logo.setText('''<style>img{max-width: 100%;max-height: 100%;}</style>
        <img src="interface/assets/img/logo-pymd/logo-pymd-2.1.png"/>''')
        self.info: QLabel= QLabel()
        self._w.ui.container_body.addWidget(self.__logo, 0, 0, 1, 1, alignment=Qt.AlignAbsolute)
        self._w.ui.container_body.addWidget(self.info, 0, 0, 1, 1, alignment=Qt.AlignHCenter)
        self.load_info()

    def load_info(self, lang_code: str=None):
        __lang = self.__lang.lang_code if lang_code is None else lang_code
        __info_md: str = ""
        # This is not a translator, just a file
        with open(f"interface/translations/others/IH_{__lang}.srm", "r", encoding="utf-8") as lang:
            __info_md = lang.read()
        self.info.setTextFormat(Qt.TextFormat.RichText)
        self.info.setText(__info_md)

    def hide(self):
        self.info.hide()
        self.__logo.hide()
