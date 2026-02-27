from PySide6 import QtWidgets, QtCore
from . import style

class AddAssetDialog(QtWidgets.QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Asset to Library")
        self.setFixedWidth(350)
        self.setStyleSheet(style.DARK_THEME)   
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        
         
        layout.addWidget(QtWidgets.QLabel("Target Category:"))
        self.cat_combo = QtWidgets.QComboBox()
        self.cat_combo.addItems(categories)
        self.cat_combo.setStyleSheet(style.MAIN_STYLE)
        layout.addWidget(self.cat_combo)
        
         
        layout.addWidget(QtWidgets.QLabel("Asset Name:"))
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Enter name (e.g. Bolt_01)")
        self.name_edit.setStyleSheet(style.MAIN_STYLE)
        layout.addWidget(self.name_edit)
        
        
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_values(self):
        return self.cat_combo.currentText(), self.name_edit.text()