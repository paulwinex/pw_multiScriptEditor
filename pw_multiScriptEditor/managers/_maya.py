_pyside_ver = 0
try:
    from Qt import QtCore, QtGui, QtWidgets
    _pyside_ver = 1
except:
    _pyside_ver = 2
import maya.OpenMayaUI as omui

import os, sys, re
from ..managers.completeWidget import contextCompleterClass

main = __import__('__main__')
ns = main.__dict__
exec 'import pymel.core as pm' in ns
pm = main.__dict__['pm']

# jedi completion path
compPath = os.path.join(os.environ['MAYA_LOCATION'],'devkit/other/pymel/extras/completion/py').replace('\\','/')
if compPath in sys.path:
    sys.path.remove(compPath)
sys.path.insert(0, compPath)

def getMayaWindow():
    if _pyside_ver == 1:
        from shiboken import wrapInstance
        ptr = omui.MQtUtil.mainWindow()
        if ptr is not None:
            return wrapInstance(long(ptr), QtWidgets.QMainWindow)
    elif _pyside_ver == 2:
        from pymel.core import ui
        return ui.Window('MayaWindow').asQtObject()

def show(dock=False):
    if dock:
        showDickControl()
    else:
        showWindow()

def showWindow():
    from pw_multiScriptEditor import scriptEditor
    reload(scriptEditor)

    editor = scriptEditor.scriptEditorClass(parent=getMayaWindow())
    editor.show()


dockName = 'pw_scriptEditorDock'
name = 'pw_scriptEditor'
def clearDoc():
    if pm.dockControl(dockName, q=1, ex=1):
        pm.deleteUI(dockName)

def showDickControl():
    if pm.window(name, q=1, ex=1):
        pm.deleteUI(name)
    from pw_multiScriptEditor import scriptEditor
    reload(scriptEditor)
    editor = scriptEditor.scriptEditorClass(parent=getMayaWindow())
    clearDoc()
    pm.dockControl(dockName, area='left',
                 content=editor.objectName(),
                 width=700,
                 label='Multi Script Editor',
                 allowedArea=['right', 'left'])


# Shelf button example
# import sys
# path = 'path/to/MultiScriptEditor_module'
# # example c:/maya/python/lib
# if not path in sys.path:
#     sys.path.append(path)
# import pw_multiScriptEditor
# reload(pw_multiScriptEditor)
# pw_multiScriptEditor.showMaya(dock=True)


nodes = pm.allNodeTypes()

def completer(line, ns):
    # create node
    p = r"createNode\(['\"](\w*)$"
    m = re.search(p, line)
    if m:
        name = m.group(1)
        if name:
            auto = [x for x in nodes if x.lower().startswith(name.lower())]
            l = len(name)
            return [contextCompleterClass(x, x[l:], True) for x in auto], None
    # exists nodes
    p = r"PyNode\(['\"](\w*)$"
    m = re.search(p, line)
    if m:
        name = m.group(1)
        existsNodes = sorted(pm.cmds.ls())
        l = len(name)
        if name:
            auto = [x for x in existsNodes if x.lower().startswith(name.lower())]
            return [contextCompleterClass(x, x[l:], True) for x in auto], None
        else:
            return [contextCompleterClass(x, x, True) for x in existsNodes], None
    return None, None

# drop event

def wrapDroppedText(namespace, text, event):
    if event.keyboardModifiers() == QtCore.Qt.AltModifier:
        # pymel with namespace
        for k, m in namespace.items():
            if hasattr(m, '__name__'):
                if m.__name__ == 'pymel.core' and not k == 'm':
                    syntax = []
                    for node in text.split():
                        if namespace[k].objExists(node):
                            syntax.append(k+'.PyNode("%s")' % node)
                        else:
                            syntax.append(node)
                    return '\n'.join(syntax)
        # pymel no namespace
        if 'PyNode' in namespace.keys():
            syntax = []
            for node in text.split():
                if namespace['objExists'](node):
                    syntax.append('PyNode("%s")' % node)
                else:
                    syntax.append(node)
            return '\n'.join(syntax)
                # return 'PyNode("%s")' % text

        # cmds with namespace
        for k, m in namespace.items():
            if hasattr(m, '__name__'):
                if m.__name__ == 'maya.cmds' and not k == 'm':
                    syntax = []
                    for node in text.split():
                        if namespace[k].objExists(node):
                            syntax.append('"%s"' % node)
                        else:
                            syntax.append(node)
                    return '\n'.join(syntax)
        # cmds without namespace
        if 'about' in namespace.keys():
            try:
                syntax = []
                for node in text.split():
                    if namespace['objExists'](node):
                        syntax.append('"%s"' % node)
                    else:
                        syntax.append(node)
                return '\n'.join(syntax)
            except:
                pass
    return text

def contextMenu(parent):
    m = mayaMenuClass(parent)
    return m

class mayaMenuClass(QtWidgets.QMenu):
    def __init__(self, parent):
        super(mayaMenuClass, self).__init__('Maya', parent)
        self.par = parent
        self.setTearOffEnabled(1)
        self.setWindowTitle('MSE %s Maya' % self.par.ver)
        a = QtWidgets.QAction('Save to shelf', parent, triggered=self.saveToShelfDialog)
        self.addAction(a)

    def saveToShelfDialog(self):
        self.dial = saveToShelfClass(self.par)
        # dial.exec_()
        self.dial.show()


class mayaIconsClass(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(mayaIconsClass, self).__init__()
        self.par = parent
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setIconSize(QtCore.QSize(32,32))
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setResizeMode(QtWidgets.QListWidget.ResizeMode.Adjust)
        self.fillIcons()
        self.itemClicked.connect(self.print_name)

    def fillIcons(self):
        res, files = self.getIcons()
        self.par.out.showMessage( "%s icons found" % len(res+files))
        for ico in sorted(res):
            item = QtWidgets.QListWidgetItem(self)
            item.setIcon(QtGui.QIcon(':/'+ico))
            item.setData(32, ':/'+ico)
            item.setToolTip(ico)
            self.addItem(item)
        for f in sorted(files, key=lambda x: os.path.splitext(x)[0]):
            item = QtWidgets.QListWidgetItem(self)
            item.setIcon(QtGui.QIcon(f))
            item.setData(32, f)
            item.setToolTip(f)
            self.addItem(item)


    def getIcons(self):
        res = [ x for x in pm.resourceManager(nameFilter="*") if os.path.splitext(x)[1] in ['.png', '.svg'] ]
        files = []
        for env in 'XBMLANGPATH', 'MAYA_FILE_ICON_PATH':
            if os.getenv(env):
                paths = os.getenv(env).split(os.pathsep)
                for p in paths:
                    files += self.findInPath(p)
        return res, files

    def findInPath(self, path):
        result = []
        for path, dirs, files in os.walk(path):
            for f in files:
                if os.path.splitext(f)[1] in ['.png', '.svg'] :
                    result.append(os.path.join(path, f).replace('\\','/'))
        return result

    def print_name(self, item):
        print item.data(32)

class saveToShelfClass(QtWidgets.QDialog):
    def __init__(self, parent):
        super(saveToShelfClass, self).__init__(parent)
        self.par = parent
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setObjectName('maya_create_shelfButton')
        self.setWindowTitle('Save script to shelf')
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.gridLayout = QtWidgets.QGridLayout()
        self.label = QtWidgets.QLabel('Label')
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.listWidget = mayaIconsClass(parent)
        self.verticalLayout.addWidget(self.listWidget)
        self.pushButton = QtWidgets.QPushButton('Save to shelf')
        self.verticalLayout.addWidget(self.pushButton)

        self.pushButton.clicked.connect(self.createButton)

        center = parent.geometry().center()
        self.resize(450, 400)
        geo = self.geometry()
        geo.moveCenter(self.mapToGlobal(center))
        self.setGeometry(geo)

    def createButton(self):
        # topShelf = pm.mel.eval('$nul = $gShelfTopLevel')
        topShelf = pm.melGlobals['gShelfTopLevel']
        currentShelf = pm.tabLayout(topShelf, q=1, st=1)

        label = self.lineEdit.text()
        sel = self.listWidget.selectedItems()
        if sel:
            icon = sel[0].data(32)
        else:
            icon = 'pythonFamily.png'
        command = self.par.tab.getCurrentText()
        pm.shelfButton (
            parent=currentShelf,
            command=command,
            sourceType="python",
            label=label,
            imageOverlayLabel=label,
            image1=icon,
            style=pm.shelfLayout(currentShelf, query=1, style=1),
            width=pm.shelfLayout(currentShelf,query=1, cellWidth=1),
            height=pm.shelfLayout(currentShelf, query=1, cellHeight=1)
            )
        self.accept()
        self.close()

