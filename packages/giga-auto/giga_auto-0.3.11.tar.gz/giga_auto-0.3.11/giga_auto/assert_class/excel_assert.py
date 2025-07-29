from giga_auto.file_attr.excel_attr import ExcelAttr

class AssertExcel:

    @staticmethod
    def assert_excel_headers(filepath, expected: list, msg=None):
        assert ExcelAttr(
            filepath).headers == expected, f'{msg or "检查文件表头"} \nExcel{filepath} Headers Failed{expected}'

    @staticmethod
    def assert_excel_rows_num(filepath, rows_num, msg=None):
        assert ExcelAttr(
            filepath).row_num == rows_num, f'{msg or "检查文件行的长度"}\n Excel{filepath} rows_num Failed {rows_num}'
