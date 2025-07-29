import sys
from typing import Optional

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QMessageBox
from PySide6.QtGui import QIcon, QCloseEvent
from PySide6.QtCore import Qt, QLocale, QSize
from ._lang import LanguageManager
from ._initialHelp import InitialHelp
from ._osl import OSL
from ._about import About
from .. import FileManager, Converter
from .ui_main_window import Ui_MainWindow
from chromologger import Logger as Log
from sqlazo import Database
from pathlib import Path
from . import resources_rc

# Feature: Change focus order (the exit dialog focus is "ok", should be "cancel")

db = Database('PYMD/database/config.db', False)
log:Log = Log('PYMD/logs/log_interface.log')

app = QApplication(sys.argv)
lang_manager:LanguageManager = LanguageManager(app)
lang_manager.load_lang()
# Feature: Allow change style
app.setStyle("windows11")

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__closed_ui:bool = False
        self.current_lang = lang_manager.lang_code
        self.ui: Ui_MainWindow = Ui_MainWindow()
        lang_manager.set_super_parent(self)
        self.ui.setupUi(self)
        self.__listeners()
        # Hide views temporally (to Show initial help)
        self.ui.frame_views.hide()
        self.__init_help: InitialHelp = InitialHelp(self, app)
        self.__icon_window = QIcon()
        self.__icon_window.addFile(u":/img/logo-pymd-2", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.__file_dialog:QFileDialog = QFileDialog()
        self.__filename:Path = Path('')
        self.__dir_output:str = ''

    @property
    def get_app(self) -> QApplication: return app

    def __listeners(self):
        """Catch events and set an action"""
        self.ui.explorer_btn.clicked.connect(self.__open_file)
        self.ui.language_btn.clicked.connect(self.__language)
        self.ui.action_open_file.triggered.connect(self.__open_file)
        self.ui.action_exit.triggered.connect(self.__exit)
        self.ui.action_about.triggered.connect(self.__about)

        self.ui.action_language.triggered.connect(self.__language)
        self.ui.action_theme.triggered.connect(self.__theme)
        self.ui.action_OSL.triggered.connect(self.__osl)
        self.ui.convert_btn.clicked.connect(self.__convert)
        self.ui.text_file_selected.textChanged.connect(self.__update)

    def __open_file(self) -> None:
        __msg:str = self.tr('Select a file')
        __last_dir:str = db.get_data_where('config_ui', 'name == "last_directory_open"').fetchone()[2]
        __file: tuple[str, str] = self.__file_dialog.getOpenFileName(self, self.tr("Open File"), __last_dir, f"{__msg} ({self.__extensions})")
        if __file[0].strip() != '':
            self.__filename = Path(__file[0])
            db.delete_data('config_ui', 'name == "last_directory_open"')
            # Save last directory
            db.insert_data(['last_directory_open', self.__filename.absolute().parent.__str__()], ['name', 'value'], 'config_ui')

            # Feature: Show progress bar
            # => Can be a Label image (hide initialHelp if all ok, continue else show initialHelp again)
            __converter:Converter = Converter(self.__filename.absolute().__str__())
            __content: Optional[str] = __converter.convert_file().data_str

            # File is NOT empty
            if __content is not None:
                # Hide initial "screen" and show file content
                self.__init_help.hide()
                self.ui.frame_views.show()
                self.ui.text_file_selected.setPlainText(__content)
            else:
                # Missing: Feature: Close progress bar
                #self.__progress_bar().close()
                self.__box_dialog(self.tr("Warning"), self.tr('The file does not contain plain text (make sure the file content is not just images)')).exec()

    def __update(self) -> None:
        """Update real-time MarkDown preview"""
        self.ui.text_preview_mode.setMarkdown(self.ui.text_file_selected.toPlainText())

    def __convert(self) -> None:
        """Manage file converter, call methods to convert, open files..."""
        # Feature: New dialog to rename the file (file to save as .md)

        # Before save, validate not empty content
        if self.ui.text_file_selected.toPlainText().strip() == '':
            self.__box_dialog(self.tr('Warning'), self.tr('The file is empty'), {'ok': self.tr('Accept')}).exec()
            return

        # Get the last output directory
        __last_dir:str = db.get_data_where('config_ui', 'name == "last_directory_output"').fetchone()[2]

        # Ask the user for output directory (Remember the previous directory)
        self.__dir_output:str = self.__file_dialog.getExistingDirectory(self, self.tr("Select a directory"), __last_dir)

        try:
            # Output directory was selected
            if self.__dir_output.strip() != '':
                # Update output directory in DB
                db.delete_data('config_ui', 'name == "last_directory_output"')
                db.insert_data(['last_directory_output', self.__dir_output], ['name', 'value'], 'config_ui')

                # Use the same filename input for the output file (Just change the directory)
                __file_manager:FileManager = FileManager(self.__filename.absolute().__str__(), self.__dir_output)

                # Save converted file
                __file_manager.save_md(self.ui.text_file_selected.toPlainText())
        except Exception as e:
            log.log_e(e)

    @property
    def __extensions(self) -> str:
        __allow_extensions:str = ''
        for ex in FileManager.extensions(): __allow_extensions += f'*{ex} '
        return __allow_extensions.strip()

    def __exit(self, event_target: Optional[QCloseEvent] = None) -> None:
        """When event "close" is caught or user press `CTRL + W` shortcut

        Args:
            event_target (Optional[QCloseEvent]): When this method is called from "Title bar" Event (Press title "X")
        """
        __result:int = self.__box_dialog(self.tr('Close Program'),self.tr('Do you want to close this program?'),{'ok': self.tr('Accept')}).exec()

        if __result == 1024:
            # Close via "Dialog" (CTRL + W)
            self.__closed_ui = True
            self.close()
        else:
            # When close via "Window" (Title bar "X")
            if type(event_target) is QCloseEvent: event_target.ignore()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Catch Close Event (Title bar "X")

        Args:
            event (QCloseEvent): Close Event from title bar "X"
        """
        if not self.__closed_ui: self.__exit(event)

    def __about(self):
        """Show about dialog"""
        About(self, self.current_lang)

    def __language(self):
        """Change UI language"""
        __result: int = 0
        if self.ui.text_preview_mode.isVisible():
            # Show a warning dialog before change language
            __result = self.__box_dialog(self.tr('Warning'), self.tr('Extracted content will be deleted once you change the language (unless you have already saved it)'),{'ok': self.tr('Accept')}).exec()

        if not self.ui.text_preview_mode.isVisible() or __result == 1024:
            #Feature: Save content in a temporal file (The content is removed when language change)
            lang_manager.show_dialog()

            #Update UI language (MainWindow > childs and Language Dialog)
            self.ui.retranslateUi(self)
            lang_manager.lang_dialog.retranslateUi(lang_manager)

            # Update lang UI var
            self.current_lang = lang_manager.lang_code

            # When initial info screen is visible
            if self.__init_help.info.isVisible(): self.__init_help.load_info(self.current_lang)

    def __box_dialog(self, title:str = '', text:str = '', buttons_cancel_ok: Optional[dict] = None, icon: Optional[QIcon] = None) -> QMessageBox:
        """Create a Box Dialog (To show warnings, confirms, e.t.c.)

        Args:
            title (str): Dialog title (Example: Warning file size)
            text (str): Dialog message, text
            buttons_cancel_ok (Optional[dict]): Custom text to standard buttons (Cancel | Ok)
            icon (Optional[QIcon]): To set window icon

        Returns:
            QMessageBox: A dialog object ready to use

        Note:
            `show()` method should be executed to use this, not show by default...

        """
        __icon: QIcon = icon if icon is not None else self.__icon_window
        __dialog: QMessageBox = QMessageBox()

        # Standard dialog buttons
        __dialog.setStandardButtons(__dialog.StandardButton.Ok | __dialog.StandardButton.Cancel)

        # If not give buttons labels
        __buttons_txt:list[str] = [self.tr('Ok'), self.tr('Cancel')]

        # Show and set window configs
        __dialog.setWindowIcon(__icon)
        __dialog.setWindowTitle(title)
        __dialog.setText(text)

        # Has been received a dict with buttons
        if buttons_cancel_ok is not None and type(buttons_cancel_ok) is dict:
            if 'ok' in buttons_cancel_ok: __buttons_txt[0] = buttons_cancel_ok['ok']
            if 'cancel' in buttons_cancel_ok: __buttons_txt[1] = buttons_cancel_ok['cancel']

        # Set visible text for each button
        __dialog.button(__dialog.StandardButton.Ok).setText(__buttons_txt[0])
        __dialog.button(__dialog.StandardButton.Cancel).setText(__buttons_txt[1])
        return __dialog


    def __theme(self):
        # Coming Soon
        # Feature: Change theme
        pass

    def __osl(self):
        """Load Open Source Licenses (Information - OSL)"""
        OSL(self, lang_manager)

def run():
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())