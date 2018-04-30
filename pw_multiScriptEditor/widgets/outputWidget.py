
from Qt import QtCore, QtGui, QtWidgets


from .. import managers

class outputClass(QtWidgets.QTextBrowser):
    def __init__(self):
        super(outputClass, self).__init__()
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.fs = 14
        self.document().setDefaultFont(QtGui.QFont("monospace", self.fs, QtGui.QFont.Normal))
        metrics = QtGui.QFontMetrics(self.document().defaultFont())
        self.setTabStopWidth(4 * metrics.width(' '))
        self.setMouseTracking(1)

    def showMessage(self, msg):
        self.moveCursor(QtGui.QTextCursor.End)
        cursor = self.textCursor()
        cursor.insertText(str(msg)+'\n')
        self.setTextCursor(cursor)
        self.moveCursor(QtGui.QTextCursor.End)
        self.ensureCursorVisible()

    def setTextEditFontSize(self, size):
        style = '''QTextEdit
    {
        font-size: %spx;
    }''' % size
        self.setStyleSheet(style)


    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.delta() > 0:
                self.changeFontSize(True)
            else:
                self.changeFontSize(False)
        # super(outputClass, self).wheelEvent(event)
        QtWidgets.QTextBrowser.wheelEvent(self, event)

    def changeFontSize(self, up):
        if managers.context == 'hou':
            if up:
                self.fs = min(30, self.fs+1)
            else:
                self.fs = max(8, self.fs - 1)
            self.setTextEditFontSize(self.fs)
        else:
            f = self.font()
            size = f.pointSize()
            if up:
                size = min(30, size+1)
            else:
                size = max(8, size - 1)
            f.setPointSize(size)
            self.setFont(f)


    # def mousePressEvent(self, event):
    #     print context
    #     if context == 'hou':
    #         if event.button() == Qt.LeftButton:
    #             # super(outputClass, self).mousePressEvent(event)
    #             QTextBrowser.mousePressEvent(self, event)
    #     else:
    #     QTextBrowser.mousePressEvent(self, event)
