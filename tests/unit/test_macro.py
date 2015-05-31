from unittest import TestCase
from datetime import date, timedelta
from website.macro import Macro, DateMacro  # , TableMacro


class TestMacro(TestCase):
    def test_replace(self):
        text = "Sample Text ABC"
        macro = Macro('ABC', '123')
        new_text = macro.replace_text(text)
        self.assertEqual(
            new_text,
            "Sample Text 123")

    def test_date(self):
        text = "Sample Text <DATEID> <DATEID-1>"
        macro = DateMacro()
        new_text = macro.replace_text(text)
        self.assertEqual(
            new_text,
            "Sample Text {d1} {d2}".format(
                d1=date.today() + timedelta(days=0),
                d2=date.today() + timedelta(days=-1)
            )
        )
