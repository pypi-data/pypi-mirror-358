from chromologger import Logger
from chromolog import Print as Log
from pathlib import Path

log = Logger('./logs/log_file_manager.log')
p:Log = Log()

class FileManager:
    def __init__(self, filename:str | None = None, output:str | None = None, encoding:str='utf-8') -> None:
        self.__fn:Path = Path(filename) # Path to file + extension
        self.__ot:Path = Path(output) # Path to file output + extension
        self.__en:str = encoding # Encoding to write a file .md
        self.__validate()

    def __validate(self) -> bool | None:
        """Validate an extension file, and output existing"""
        __allowed:bool = self.__fn.suffix.lower() in self.extensions()
        __exists:bool = self.__fn.is_file()
        __exists_dir:bool = self.__ot.is_dir()
        if not __allowed:
            raise TypeError(f'File extension ("{self.__fn.suffix.lower()}") not allowed')
        if not __exists:
            raise FileNotFoundError(f'File "{self.__fn.name}" not found')
        if not __exists_dir:
            raise NotADirectoryError(f'"{self.__ot.absolute()}" not found')
        return True

    def save_md(self, content:str) -> bool:
        """Saves content a Markdown file

        :param content: Content to save
        :return: Value indicating whether the file was saved or not
        """
        __return:bool = False
        __file_md:str = f'{self.dir_output}/{self.__fn.stem}.md'
        try:
            if type(content) is not str:
                raise TypeError('The content must be a string')
            with open(__file_md, 'w', encoding=self.__en) as __file:
                __file.write(content)
                log.log(f'File "{__file_md}" saved successfully')
            __return = True
        except Exception as Error:
            log.log_e(Error)
        return __return

    @staticmethod
    def extensions() -> list[str]: return  [".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".msg", ".csv", ".txt", ".text",
                                  ".md", ".markdown", ".json", ".jsonl", ".xml", ".rss", ".atom", ".html", ".mhtml",
                                  ".htm", ".epub", ".zip", ".ipynb"]

    @staticmethod
    def read_file(filename:str = '', encoding:str = 'utf-8') -> str:
        __return:str = ''
        try:
            with open(filename, 'r', encoding=encoding) as file:
                __return = str(file.read())
        except Exception as e:
            log.log_e(e)
        return __return

    @property
    def file(self) -> str: return self.__fn.resolve().__str__()
    @property
    def dir_output(self) -> str: return self.__ot.resolve().__str__()