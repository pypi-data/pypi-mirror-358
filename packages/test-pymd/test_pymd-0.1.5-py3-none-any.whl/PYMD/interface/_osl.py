from PySide6.QtWidgets import QDialog
from .ui_osl import Ui_dialog_osl
from .. import FileManager
import json

class OSL(QDialog):
    def __init__(self, parent=None, lang_manager=None):
        super().__init__(parent)
        self.__lang = lang_manager
        self.__osl: Ui_dialog_osl = Ui_dialog_osl()
        self.__osl.setupUi(self)
        self.__load_initial_content()
        self.show()
        self.__osl.select_library.currentTextChanged.connect(self.__load_library_osl)

    def __load_initial_content(self):
        __notice:str = FileManager.read_file(f'interface/translations/others/NOTICE_{self.__lang.lang_code}.srm')
        self.__osl.text_container_license.setText(__notice)

    def __load_library_osl(self):
        if self.__osl.select_library.currentIndex() > 0:
            __name_library:str = self.__osl.select_library.currentText()
            __license_file:str = f'OSL/LICENSE_{__name_library.upper()}'
            __links:dict = json.loads(FileManager.read_file('OSL/url_licenses.srm'))
            self.__osl.url_osl.setText(self.tr(f'{__name_library.capitalize()} - original: {__links[__name_library.lower()]}'))
            self.__osl.text_container_license.setText(FileManager.read_file(__license_file))
        else:
            self.__load_initial_content()
            self.__osl.url_osl.clear()