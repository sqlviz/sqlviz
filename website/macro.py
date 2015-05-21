from datetime import date, timedelta
import re


class Macro:
    def __init__(self, key_pattern=None, replace_value=None):
        self.key_pattern = key_pattern
        self.replace_value = replace_value

    def replace_text(self, text):
        return text.replace(self.key_pattern, self.replace_value)


class DateMacro(Macro):
    def replace_text(self, text):
        pattern = r"<DATEID(-)?(\d+)?>"
        while re.search(pattern, text) is not None:
            re_comp = re.search(pattern, text)
            if re_comp.groups()[1] is None:
                days_delta = 0
            else:
                days_delta = int(re_comp.groups()[1])
            if re_comp.groups()[0] is not None:
                days_delta = -1 * days_delta
            d = timedelta(days=days_delta)
            date_replace = str(date.today() + d)
            text = re.sub(re_comp.group(), date_replace, text)
        return text


class TableMacro(Macro):
    def replace_text(self, text, table_id_dict={}):
        pattern = r"<TABLE-(\d+)>"
        while re.search(pattern, text) is not None:
            re_comp = re.search(pattern, text)
            query_id = int(re_comp.groups()[0])
            replace_text = table_id_dict[query_id]
            text = re.sub(re_comp.group(), replace_text, text)
        return text
