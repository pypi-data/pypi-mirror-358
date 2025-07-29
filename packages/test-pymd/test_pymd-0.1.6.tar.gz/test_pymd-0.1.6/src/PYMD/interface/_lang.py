import os
from typing import Optional

from PySide6.QtCore import Qt, QTranslator, QLocale
from PySide6.QtWidgets import QApplication, QMainWindow
from .ui_dialog_language import Ui_Lang_Dialog
from PySide6.QtWidgets import QDialog
from sqlazo import Database

db = Database(f'{os.path.dirname(os.path.abspath(__file__))}/database/config.db', False)

class LanguageManager(QDialog):
    def __init__(self, app:QApplication=None):
        # es_CO is default
        self.lang_code: str = db.get_data_where('config_ui', 'name == "current_lang_code"').fetchone()[2]
        self.__dir:str = f'{os.path.dirname(os.path.abspath(__file__))}/interface/translations/locale'
        self.lang_file:str = ''
        self.__translator:QTranslator = QTranslator(app)
        self.__app:QApplication = app
        self.parent: Optional[QMainWindow] = None
        self.lang_dialog: Optional[Ui_Lang_Dialog] = None

    def set_super_parent(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.lang_dialog = Ui_Lang_Dialog()
        self.lang_dialog.setupUi(self)

    def show_dialog(self):
        __buttons_dialog = self.lang_dialog.dialog_btn
        __buttons_dialog.setStandardButtons(__buttons_dialog.StandardButton.Ok | __buttons_dialog.StandardButton.Cancel)
        __buttons_dialog.button(__buttons_dialog.StandardButton.Ok).setText(self.tr('Save'))
        __buttons_dialog.button(__buttons_dialog.StandardButton.Cancel).setText(self.tr('Cancel'))
        self.exec()
        if self.result() == 1 and self.lang_dialog.languages.currentItem() is not None:
                self.lang_code:str = self.lang_dialog.languages.currentItem().toolTip()
                # Pending improvement (when 'update_data' is added to 'sqlazo')
                db.delete_data('config_ui', 'name == "current_lang_code"')
                db.insert_data(['current_lang_code', self.lang_code], ['name', 'value'], 'config_ui')
                self.load_lang()

    def load_lang(self, lang_code:str=None):
        __code = lang_code if lang_code is not None else self.lang_code
        self.lang_file = f'pymd_{__code}.qm'
        if self.__translator.load(self.lang_file, self.__dir):
            self.__app.installTranslator(self.__translator)
