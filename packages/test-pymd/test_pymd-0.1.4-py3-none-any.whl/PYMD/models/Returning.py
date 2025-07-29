from typing import Optional

class Returning:
    """To standardize function returns, you can add information in text format (String) or a dictionary (dict)"""
    def __init__(self, ok:bool = True, data_str: Optional[str] = None, data_dict: Optional[str] = None):
        """Class constructor

        :param ok: Successful operation
        :param data_str: String information
        :param data_dict: Dictionary information
        """
        self.ok: bool = ok # Status (operation)
        self.data_str: Optional[str] = data_str # String information
        self.data_dict: Optional[dict] = data_dict # Dictionary information