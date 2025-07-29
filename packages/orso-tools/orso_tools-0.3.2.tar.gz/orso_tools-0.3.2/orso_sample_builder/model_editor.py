from dataclasses import fields

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit


class OrsoSampleHighlighter(QSyntaxHighlighter):
    _orso_special = ["stack"]

    def __init__(self, parent=None):
        super(OrsoSampleHighlighter, self).__init__(parent)
        self.dict_key_format = QTextCharFormat()
        self.dict_key_format.setFontWeight(QFont.Bold)
        self.dict_key_format.setForeground(Qt.GlobalColor.darkMagenta)
        self.special_key_format = QTextCharFormat()
        self.special_key_format.setFontWeight(QFont.Bold)
        self.special_key_format.setForeground(Qt.GlobalColor.darkGreen)
        self.stack_format = QTextCharFormat()
        self.stack_format.setFontWeight(QFont.Bold)
        self.stack_format.setForeground(Qt.GlobalColor.black)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(Qt.GlobalColor.gray)
        self.inline_dict_format = QTextCharFormat()
        self.inline_dict_format.setBackground(QColor(240, 240, 255))

    def highlightBlock(self, text):
        expression = QRegularExpression("\\b[a-zA-Z_0-9]*:")
        i = expression.globalMatch(text)
        while i.hasNext():
            match = i.next()
            name = match.capturedTexts()[0][:-1]
            if name in self._orso_special:
                self.setFormat(match.capturedStart(), match.capturedLength(), self.special_key_format)
            else:
                self.setFormat(match.capturedStart(), match.capturedLength(), self.dict_key_format)

        expression = QRegularExpression("(?<=stack:).*")
        i = expression.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.stack_format)

        expression = QRegularExpression("# .*$")
        i = expression.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.comment_format)

        expression = QRegularExpression("\\{.*\\}")
        i = expression.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.inline_dict_format)


class ModelEditor(QTextEdit):

    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.highlighter = OrsoSampleHighlighter(self.document())

    def keyPressEvent(self, event):
        tab_char = "  "  # could be anything including spaces
        if event.key() == Qt.Key_Backtab:
            # get current cursor
            cur = self.textCursor()
            cur.clearSelection()

            # move to begining of line and select text to first word
            cur.movePosition(QTextCursor.StartOfLine)
            cur.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
            sel_text = cur.selectedText()

            # if the text starts with the tab_char, replace it
            if sel_text.startswith(tab_char):
                text = sel_text.replace(tab_char, "", 1)
                cur.insertText(text)
        elif event.key() == Qt.Key_Tab:
            # get current cursor
            cur = self.textCursor()
            cur.clearSelection()

            # move to begining of line and select text to first word
            cur.movePosition(QTextCursor.StartOfLine)
            cur.insertText(tab_char)
            cur.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)

        else:
            return QTextEdit.keyPressEvent(self, event)

    def insert_class(self, cls_name, **initial_values):
        from orsopy.fileio import model_language as ml

        try:
            from orsopy.fileio import model_complex as mc
        except ImportError:
            mc = ml

        namespace = {**ml.__dict__, **mc.__dict__}

        cls = namespace[cls_name]

        c = self.textCursor()
        pre_c_line = self.toPlainText()[: int(c.anchor())].rsplit("\n", 1)[-1]
        expression = QRegularExpression("^ *")
        i = expression.globalMatch(pre_c_line)
        if i.hasNext():
            indent = " " * i.next().capturedLength()
        else:
            indent = ""
        if pre_c_line.strip().endswith(":"):
            insert_txt = "\n"
        else:
            insert_txt = ""

        if cls_name == "Value":
            insert_txt = "{magnitude: 0., unit: ''}"
        elif cls_name == "ComplexValue":
            insert_txt = "{real: 0., imag: 0., unit: ''}"
        else:
            for field in fields(cls):
                if field.name in ["comment"]:
                    continue
                type_str = f"{field.type}"
                type_str = type_str.replace("typing.", "")
                type_str = type_str.replace("orsopy.fileio.base.", "")
                type_str = type_str.replace("orsopy.fileio.model_language.", "")
                type_str = type_str.replace("orsopy.fileio.model_building_blocks.", "")
                type_str = type_str.replace("orsopy.fileio.model_complex.", "")
                if field.name in initial_values:
                    insert_txt += f"{field.name}: {initial_values[field.name]}\n"
                elif field.name in ["sub_stack_class"]:
                    insert_txt += f"{field.name}: {field.default}\n"
                else:
                    insert_txt += f"{field.name}: null # {type_str}\n"
        if cls_name != "SampleModel":
            insert_txt = insert_txt.replace("\n", "\n  " + indent)
        c.insertText(insert_txt)
