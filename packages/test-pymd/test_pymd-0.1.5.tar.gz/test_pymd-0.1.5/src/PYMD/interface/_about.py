# This Python file uses the following encoding: utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from .ui_dialog_about import Ui_about_dialog

class About(QDialog):
    def __init__(self, parent=None, lang=None):
        super().__init__(parent)
        self.__lang:str = lang
        self.__dialog = Ui_about_dialog()
        self.__dialog.setupUi(self)
        self.load_content()
        self.show()

    def load_content(self):
        # Load information
        with open(f'interface/translations/others/ABOUT_{self.__lang}.trg', 'r', encoding='utf-8') as __about:
            self.__dialog.text_about.setTextFormat(Qt.TextFormat.RichText)
            self.__dialog.text_about.setText(__about.read())
