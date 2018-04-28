from pw_multiScriptEditor import scriptEditor
from Qt import QtWidgets

app = QtWidgets.QApplication([])
w = scriptEditor.scriptEditorClass()
w.show()
app.exec_()
