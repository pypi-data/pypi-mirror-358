"""A module to replace tomli and tomli_w for simple cases."""
import re
import ast

from ._version import __version__

version = __version__

valid_keys_re = [
    r'^[A-Za-z0-9_-]{1,}$',
    r'^".{1,}"$',
    r"^'.{1,}'$",
]

valid_table_re = [
    r'^\[\w{1,}\]$',
    r'^\["\w{1,}"]$',
    r"^\['\w{1,}']$",
]

valid_equals_re = [
    r'^\w{1,}=\w{1,}$',
    r'^\w{1,}\s{0,}=\s{0,}\w{0,}\s{0,}"\w{0,}\s{0,}=\w{0,}"',
    r"^\w{1,}\s{0,}=\s{0,}\w{0,}\s{0,}'\w{0,}\s{0,}=\w{0,}'",
]

quoted_hash_re = [
    r"\w{0,}'\w{0,}#\w{0,}'\w{0,}",
    r'\w{0,}"\w{0,}#\w{0,}"\w{0,}',
]

valid_number_re = r'^-{0,1}[0-9]{0,}\.{0,1}[0-9]{0,}$'

multi_line_re = r'^\"{3}.{0,}\"{3}$'

list_re = r'^(\[.{0,}\])$'

dict_re = r'^(\{.{0,}\})$'


class TOMLDecodeError(Exception):
    """Exception raised for custom error in the application."""

    def __init__(self, message: str = '') -> None:
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'TOMLDecodeError: {self.message}'


class TomlParser():
    """
    Provide basic functionality for TOML: load, dump, parse.
    """
    def __init__(self):
        self.parsing_list = False
        self.list = []

    def load(self, file_handle) -> list:
        """Read and parse a text file and return a dict."""
        try:
            text = file_handle.read()
            return self.parse(text.split('\n'))
        except Exception as err:
            raise TOMLDecodeError(err.args[0]) from err

    def dump(self, data: dict, file_handle) -> None:
        """Write dict in TOML format."""
        if not isinstance(data, dict):
            raise TOMLDecodeError('Invalid data format')
        try:
            text = self._dict_to_list(data)
            file_handle.write(text)
        except FileNotFoundError as err:
            raise FileNotFoundError(err.args[0]) from err

    def parse(self, data: list) -> dict:
        """Parse the list of text to generate a dict."""
        result = {}
        data = self._combine_lines(data)
        key = ''
        for line, text in enumerate(data):
            try:
                if self.parsing_list:
                    item = data
                else:
                    (key, item) = self._parse(line, text)

                # Handle multi-line list definitions
                if (item and isinstance(item, str)
                        and item[0] == '[' and not self.parsing_list):
                    text = self._start_list(line, item)
                    if isinstance(text, list):
                        item = text
                    else:
                        continue

                if (text and isinstance(text, str)
                        and text[-1] == ']' and self.parsing_list):
                    item = self._end_list(line, text)

                if self.parsing_list:
                    if text:
                        self._process_list_item(line, text)
                    continue

                # Continue with process
                if key:
                    if key in result:
                        raise TOMLDecodeError(
                            f'Key defined multiple times: line {line+1}')
                    result[key] = item

            except TOMLDecodeError as err:
                raise TOMLDecodeError(err.args[0]) from err
        return result

    def _start_list(self, line: int, item: str) -> str:
        if len(item) == 1:
            item = ''
        if item[-1] == ']':
            try:
                return ast.literal_eval(item)
            except SyntaxError as err:
                message = f'Invalid syntax in structure: line {line+1}'
                raise TOMLDecodeError(message) from err

        self.list = []
        self.parsing_list = True
        return item

    def _end_list(self, line: int, item: str) -> list:
        item = item.strip()
        if len(item) > 1:
            item = item[:-1]
            self._process_list_item(line, item)
        item = self.parsing_list
        self.parsing_list = False
        return self.list

    def _process_list_item(self, line: int, text: str) -> None:
        if ',' in text:
            for sub_text in text.split(','):
                if sub_text:
                    sub_text = self._get_item(line, sub_text.strip())
                    self.list.append(sub_text)
        else:
            sub_text = self._get_item(line, text.strip())
            self.list.append(sub_text)

    def _parse(self, line: int, text: str) -> tuple:
        (key, item) = ('', '')
        if not text:
            return (key, item)

        # Comments
        if text[0] == '#':
            return (key, item)
        if '#' in text:
            for test in quoted_hash_re:
                if re.search(test, text):
                    break
            else:  # after or no break
                text = text[:text.index('#')]

        # Tables
        key_portion = text
        if '=' in text:
            key_portion = text[:text.index('=')]
        if '[' in key_portion or ']' in key_portion or '=' not in text:
            self._validate_tables(line, key_portion)

        # Standard items
        if '=' in text:
            if text.count('=') > 1:
                self._validate_equals(line, text)
            index = text.index('=')
            key = self._get_key(line, text[:index])
            item_text = text[index+1:].strip()

            item = self._get_item(line, item_text)
        return (key, item)

    def _get_key(self, line: int, key: str) -> str:
        key = key.strip()
        for test in valid_keys_re:
            if re.search(test, key):
                break
        else:  # after or no break
            raise TOMLDecodeError(f'Invalid key definition: line {line+1}')
        key = key.replace('"', '')
        return key.replace("'", '')

    def _get_item(self, line: int, item: str) -> any:
        if not item:
            raise TOMLDecodeError(f'Invalid value definition: line {line+1}')

        if re.search(list_re, item) or re.search(dict_re, item):
            try:
                item = ast.literal_eval(item)
            except SyntaxError as err:
                message = f'Invalid syntax in structure: line {line+1}'
                raise TOMLDecodeError(message) from err

        elif re.search(multi_line_re, item):
            item = item.replace('"""', '')
        elif (item[0] == '"' and item[-1] == '"'
                or item[0] == "'" and item[-1] == "'"):
            return item[1:-1]
        elif re.search(valid_number_re, item):
            return float(item) if '.' in item else int(item)
        elif item == 'true':
            return True
        elif item == 'false':
            return False
        return item

    def _validate_equals(self, line: int, text: str) -> None:
        for test in valid_equals_re:
            if re.search(test, text):
                break
        else:  # after or no break
            raise TOMLDecodeError(f'Invalid equals definition: line {line+1}')

    def _validate_tables(self, line: int, text: str) -> None:
        for test in valid_table_re:
            if re.search(test, text):
                break
        else:  # after or no break
            raise TOMLDecodeError(f'Invalid table definition: line {line+1}')

    def _dict_to_list(self, dict) -> str:
        toml = []
        for key, item in dict.items():
            if isinstance(item, str):
                item = f'"{item}"'
            elif item is True:
                item = 'true'
            elif item is False:
                item = 'false'
            toml.append(f'{key} = {item}')
        return '\n'.join(toml)

    def _combine_lines(self, data: list[str]) -> list[str]:
        text = []
        nl = '\n'
        for line in data:
            if '\n' not in line:
                text.append(line)
            else:
                new_line = ''
                if text:
                    new_line = text[:-1]
                new_line = f"{new_line} {line.replace(nl, '').strip()}"
                text.append(new_line)
        return text
