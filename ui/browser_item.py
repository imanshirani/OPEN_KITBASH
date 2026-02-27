from PySide6 import QtWidgets, QtCore, QtGui
from . import style
import os


class ImageLoader(QtCore.QThread):
    finished = QtCore.Signal(QtGui.QImage)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        
        img = QtGui.QImage(self.image_path)    
        if not img.isNull():
            img = img.scaled(120, 110, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.finished.emit(img)

# -------------------------------------------------------------------

class KitbashItem(QtWidgets.QFrame):
    clicked = QtCore.Signal(str) 

    def __init__(self, name, thumb_path, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFixedSize(130, 190) 
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Raised)
        self.setStyleSheet(style.ITEM_STYLE)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)

        
        self.img_label = QtWidgets.QLabel("Loading...")
        self.img_label.setFixedSize(120, 110)
        self.img_label.setAlignment(QtCore.Qt.AlignCenter)
        self.img_label.setStyleSheet("color: #888; background: #222; border-radius: 4px; font-size: 10px;")
        layout.addWidget(self.img_label)

        
        self.loader = ImageLoader(thumb_path)
        self.loader.finished.connect(self.on_image_loaded)
        self.loader.start()

        
        clean_name = os.path.splitext(name)[0]
        self.name_label = QtWidgets.QLabel(clean_name)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 10px; color: #bbb; font-weight: bold;")
        layout.addWidget(self.name_label)

        
        self.btn_insert = QtWidgets.QPushButton("INSERT")
        self.btn_insert.setFixedHeight(24)
        self.btn_insert.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_insert.setStyleSheet(style.BTN_ACTION) 
        self.btn_insert.clicked.connect(lambda: self.clicked.emit(self.file_path))
        layout.addWidget(self.btn_insert)

    def on_image_loaded(self, img):
        """   ‌        ‌"""
        if img.isNull():
            self.img_label.setText("No Preview")
            self.img_label.setStyleSheet("color: #666; background: #222; border-radius: 4px;")
        else:
            self.img_label.clear()
            self.img_label.setStyleSheet("background: transparent;")
            #  QImage  QPixmap   
            self.img_label.setPixmap(QtGui.QPixmap.fromImage(img))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.file_path)

    def contextMenuEvent(self, event):
        from ..core import logic
        main_window = self
        while main_window and not hasattr(main_window, 'log_message'):
            main_window = main_window.parentWidget()
            
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(style.DARK_THEME)
        
        action_fav = menu.addAction("⭐ Add to Favorites")
        menu.addSeparator()
        action_update_thumb = menu.addAction("📸 Update Thumbnail")
        action_rename = menu.addAction("✏ Rename Asset")
        action_delete = menu.addAction("🗑 Delete Asset")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == action_fav: logic.add_to_favorites(self.file_path, main_window)
        elif action == action_update_thumb: logic.update_single_asset_thumbnail(self.file_path, main_window)
        elif action == action_rename: logic.rename_asset(self.file_path, main_window)
        elif action == action_delete: logic.delete_asset(self.file_path, main_window)

    def set_selected(self, is_selected):
        if is_selected:
            self.setStyleSheet(f"background-color: {style.COLOR_ITEM_HOVER}; border: 2px solid {style.COLOR_ACCENT};")
        else:
            self.setStyleSheet(style.ITEM_STYLE)