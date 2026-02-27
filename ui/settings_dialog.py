from PySide6 import QtWidgets, QtCore
import webbrowser
from . import style
from ..core import constants

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, current_path=""):
        super().__init__(parent)
        self.setWindowTitle(f"About & Settings - {constants.PRODUCT_NAME}")
        self.setFixedWidth(420)
        self.setStyleSheet(style.DARK_THEME)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(15)

        
        self.group_about = QtWidgets.QGroupBox("Product Information")
        self.group_about.setStyleSheet(style.GROUP_BOX_HEADER)
        about_layout = QtWidgets.QVBoxLayout(self.group_about)
        about_layout.setContentsMargins(15, 20, 15, 15)
        
        
        title = QtWidgets.QLabel(f"🚀 {constants.PRODUCT_NAME}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00AAFF; margin-bottom: 5px;")
        
        
        info_text = (
            f"<b>Version:</b> {constants.VERSION}<br>"            
            f"<span style='color:#ddd;'>{constants.DEVELOPER_TAG}</span>"
            f"Professional Kitbash Manager for 3ds Max."
        )
        info = QtWidgets.QLabel(info_text)
        info.setStyleSheet("color: #bbb; font-size: 11px; line-height: 150%;")
        
        
        link_layout = QtWidgets.QHBoxLayout()
        link_layout.setSpacing(10)
        
        self.btn_git = QtWidgets.QPushButton("GitHub Repository")
        self.btn_git.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_git.setStyleSheet(style.BTN_GITHUB)
        
        self.btn_pay = QtWidgets.QPushButton("Support (PayPal)")
        self.btn_pay.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_pay.setStyleSheet(style.BTN_PAYPAL)
        
        link_layout.addWidget(self.btn_git)
        link_layout.addWidget(self.btn_pay)
        
        about_layout.addWidget(title)
        about_layout.addWidget(info)
        about_layout.addLayout(link_layout)
        self.layout.addWidget(self.group_about)

        
        self.group_path = QtWidgets.QGroupBox("Library Configuration")
        self.group_path.setStyleSheet(style.GROUP_BOX_HEADER)
        path_v_layout = QtWidgets.QVBoxLayout(self.group_path)
        path_v_layout.setContentsMargins(15, 20, 15, 15)
        
        path_label = QtWidgets.QLabel("Root Library Path:")
        path_label.setStyleSheet("color: #888; font-weight: bold;")
        
        self.path_layout = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit(current_path)
        self.path_edit.setPlaceholderText("Select your Kitbash folder...")
        
        self.btn_browse = QtWidgets.QPushButton("Browse...")
        self.btn_browse.setFixedWidth(80)
        self.btn_browse.setStyleSheet(style.BTN_GITHUB) 
        
        self.path_layout.addWidget(self.path_edit)
        self.path_layout.addWidget(self.btn_browse)
        
        path_v_layout.addWidget(path_label)
        path_v_layout.addLayout(self.path_layout)
        self.layout.addWidget(self.group_path)
        
        
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.layout.addWidget(self.button_box)

        
        self.btn_browse.clicked.connect(self.browse_folder)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        
        self.btn_git.clicked.connect(lambda: webbrowser.open(constants.GITHUB_URL))
        self.btn_pay.clicked.connect(lambda: webbrowser.open(constants.DONATION_LINK))

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Kitbash Library Folder", self.path_edit.text()
        )
        if folder:
            self.path_edit.setText(folder)

    def get_path(self):
        return self.path_edit.text()