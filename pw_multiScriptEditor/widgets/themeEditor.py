try:
    from Qt import QtCore, QtGui, QtWidgets
    qt = 1
except:
    qt = 2
import themeEditor_UIs as ui
from .. import settingsManager
import os
from .pythonSyntax import design
from .pythonSyntax import syntaxHighLighter
from . import inputWidget
from .. import icons_rcs


class themeEditorClass(QtWidgets.QDialog, ui.Ui_themeEditor):
    def __init__(self, parent = None, desk=None):
        super(themeEditorClass, self).__init__(parent)
        self.setupUi(self)
        self.preview_twd = inputWidget.inputClass(self, desk)
        self.preview_ly.addWidget(self.preview_twd)
        self.preview_twd.setPlainText(defaultText)
        self.splitter.setSizes([200,300])
        self.s = settingsManager.scriptEditorClass()
        self.colors_lwd.itemDoubleClicked.connect(self.getNewColor)
        self.save_btn.clicked.connect(self.saveTheme)
        self.del_btn.clicked.connect(self.deleteTheme)
        self.themeList_cbb.currentIndexChanged.connect(self.updateColors)
        self.apply_btn.clicked.connect(self.apply)
        self.apply_btn.setText('Close')
        self.textSize_spb.valueChanged.connect(self.updateExample)

        self.fillUI()
        self.updateUI()
        self.updateColors()
        self.preview_twd.completer.updateCompleteList()
        self.namespace={}


    def fillUI(self, restore=None):
        if restore is None:
            restore = self.themeList_cbb.currentText()
        settings = self.s.readSettings()
        self.themeList_cbb.clear()
        self.themeList_cbb.addItem('default')
        if settings.get('colors'):
            for x in settings.get('colors'):
                self.themeList_cbb.addItem(x)
        if not restore:
            restore = settings.get('theme')
        if restore:
            index = self.themeList_cbb.findText(restore)
            self.themeList_cbb.setCurrentIndex(index)
        self.updateExample()


    def updateColors(self):
        curTheme = self.themeList_cbb.currentText()
        if curTheme == 'default':
            self.del_btn.setEnabled(0)
            colors = design.defaultColors
        else:
            self.del_btn.setEnabled(1)
            settings = self.s.readSettings()
            allThemes = settings.get('colors')
            if allThemes and curTheme in allThemes:
                colors = allThemes.get(curTheme)
                for k, v in design.getColors().items():
                    if not k in colors:
                        colors[k] = v
            else:
                colors = design.getColors()

        self.colors_lwd.clear()
        for x in sorted(colors.keys()):
            if x == 'textsize':
                self.textSize_spb.setValue(colors['textsize'])
            else:
                item = QtWidgets.QListWidgetItem(x)
                pix = QtGui.QPixmap(QtCore.QSize(16,16))
                pix.fill(QtGui.QColor(*colors[x]))
                item.setIcon(QtGui.QIcon(pix))
                item.setData(32, colors[x])
                self.colors_lwd.addItem(item)
        self.updateExample()

    def updateExample(self):
        colors = self.getCurrentColors()
        self.preview_twd.applyPreviewStyle(colors)

    def getCurrentColors(self):
        colors = {}
        for i in range(self.colors_lwd.count()):
            item = self.colors_lwd.item(i)
            colors[item.text()] = item.data(32)
        colors['textsize'] = self.textSize_spb.value()
        return colors

    def getNewColor(self):
        items = self.colors_lwd.selectedItems()
        if items:
            item = items[0]
            init = QtGui.QColor(*item.data(32))
            color = QtWidgets.QColorDialog.getColor(init ,self)
            if color.isValid():
                newColor = (color.red(), color.green(), color.blue())
                item.setData(32, newColor)
                pix = QtGui.QPixmap(QtCore.QSize(16,16))
                pix.fill(QtGui.QColor(*newColor))
                item.setIcon(QtGui.QIcon(pix))
                self.updateExample()

    def saveTheme(self):
        text = self.themeList_cbb.currentText() or 'NewTheme'
        name = QtWidgets.QInputDialog.getText(self, 'Theme name', 'Enter Theme name', QtWidgets.QLineEdit.Normal, text)
        if name[1]:
            name = name[0]
            if name == 'default':
                name = 'Not default'
            settings = self.s.readSettings()
            if 'colors' in settings:
                if name in settings['colors']:
                    if not self.yes_no_question('Replace exists?'):
                        return

            colors = self.getCurrentColors()
            if 'colors' in settings:
                settings['colors'][name] = colors
            else:
                settings['colors'] = {name: colors}
            self.s.writeSettings(settings)
            self.fillUI(name)
            # self.updateUI()

    def deleteTheme(self):
        text = self.themeList_cbb.currentText()
        if text:
            if self.yes_no_question('Remove current theme?'):
                name = self.themeList_cbb.currentText()
                settings = self.s.readSettings()
                if 'colors' in settings:
                    if name in settings['colors']:
                        del settings['colors'][name]
                        self.s.writeSettings(settings)
                        self.fillUI(False)
                        self.updateUI()

    def updateUI(self):
        if not self.themeList_cbb.count():
            self.apply_btn.setEnabled(0)
        else:
            self.apply_btn.setEnabled(1)

    def apply(self):
        name = self.themeList_cbb.currentText()
        if name:
            settings = self.s.readSettings()
            settings['theme'] = name
            self.s.writeSettings(settings)
            self.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            event.ignore()
        else:
            super(themeEditorClass, self).keyPressEvent(event)

    def current(self):
        pass
        # print self.colors_lwd.selectedItems()[0].data(32)

    def yes_no_question(self, question):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setText(question)
        yes_button = msg_box.addButton("Yes", QtWidgets.QMessageBox.YesRole)
        no_button = msg_box.addButton("No", QtWidgets.QMessageBox.NoRole)
        msg_box.exec_()
        return msg_box.clickedButton() == yes_button

defaultText = r'''@decorator(param=1)
def f(x):
    """ Syntax Highlighting Demo
        @param x Parameter"""
    s = ("Test", 2+3, {'a': 'b'}, x)   # Comment
    print s[0].lower()

class Foo:
    def __init__(self):
        string = 'newline'
        self.makeSense(whatever=1)

    def makeSense(self, whatever):
        self.sense = whatever

x = len('abc')
print(f.__doc__)
'''




if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = themeEditorClass()
    w.show()
    qss = os.path.join(os.path.dirname(os.path.dirname(__file__)),'style', 'style.css')
    if os.path.exists(qss):
        w.setStyleSheet(open(qss).read())
    app.exec_()


