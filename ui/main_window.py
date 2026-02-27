from PySide6 import QtWidgets, QtCore, QtGui
import os


from . import style
from .browser_item import KitbashItem 
from ..core import constants, logic


class DraggableDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_mouse_pos = None
        self.setCursor(QtCore.Qt.SizeHorCursor) 
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_custom_menu)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            
            delta = event.pos().x() - self.last_mouse_pos.x()            
            sensitivity = 0.01 if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier else 0.1
            self.setValue(self.value() + (delta * sensitivity))
            self.last_mouse_pos = event.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None
        super().mouseReleaseEvent(event)

    def show_custom_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(style.DARK_THEME) 
        
        reset_action = menu.addAction("Reset")
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste") 
        
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == reset_action: self.setValue(0.0 if self.minimum() <= 0 else 1.0)
            
        elif action == copy_action:
            QtWidgets.QApplication.clipboard().setText(str(self.value()))
            
        elif action == paste_action:
            clipboard_text = QtWidgets.QApplication.clipboard().text()
            try:
                val = float(clipboard_text)
                self.setValue(val)
            except ValueError:
                pass

class OpenKitbashContent(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.Window)
        self.setStyleSheet(style.DARK_THEME)
        
        self.current_rotation = 0 
        self.current_models_data = []
        self.preview_node = None
        self.off_x = self.off_y = self.off_z = 0.0
        self.rot_x = self.rot_y = self.rot_z = 0.0
        self.scl_x = self.scl_y = self.scl_z = 1.0
        self.base_pos = None

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)

        
        self.group_info = QtWidgets.QGroupBox("System & Info")
        self.group_info.setStyleSheet(style.GROUP_BOX_HEADER)
        self.group_info.setFixedHeight(75)
        
        self.header_layout = QtWidgets.QHBoxLayout(self.group_info)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        info_v_layout = QtWidgets.QVBoxLayout()
        self.app_title = QtWidgets.QLabel(f"<b>{constants.PRODUCT_NAME}</b>")
        self.app_title.setStyleSheet("font-size: 14px; color: #00aaff;")
        self.app_version = QtWidgets.QLabel(f"Version: {constants.VERSION}")
        self.app_version.setStyleSheet(style.APP_INFO_LABEL)
        
        info_v_layout.addWidget(self.app_title)
        info_v_layout.addWidget(self.app_version)
        self.header_layout.addLayout(info_v_layout)
        self.header_layout.addStretch()

        self.btn_settings = QtWidgets.QPushButton(" ⚙ Settings / About")
        self.btn_settings.setFixedWidth(140)
        self.btn_settings.setStyleSheet(style.BTN_SETTING) 
        self.header_layout.addWidget(self.btn_settings)
        self.main_layout.addWidget(self.group_info)

        
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search Kitbash Assets...")
        self.main_layout.addWidget(self.search_bar)
        
        
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        
        
        self.left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QtWidgets.QScrollArea()
        self.scroll_content = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.scroll_content)
        self.grid_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        left_layout.addWidget(self.scroll)
        self.splitter.addWidget(self.left_panel)

        
        self.right_panel = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(4, 0, 4, 0)
        self.right_layout.setSpacing(10)

        
        self.group_modifiers = QtWidgets.QGroupBox("Quick Modifiers (2026)")
        self.group_modifiers.setStyleSheet(style.GROUP_BOX_HEADER)
        mod_grid = QtWidgets.QGridLayout(self.group_modifiers)
        mod_grid.setSpacing(6)

        self.btn_add_conform = QtWidgets.QPushButton("Conform")
        self.btn_add_conform.setStyleSheet(style.BTN_ACTION)
        self.btn_add_conform.setToolTip("     ")
        mod_grid.addWidget(self.btn_add_conform, 0, 0)

        self.btn_add_boolean = QtWidgets.QPushButton("Boolean")
        self.btn_add_boolean.setStyleSheet(style.BTN_ACTION)
        self.btn_add_boolean.setToolTip("     ")
        mod_grid.addWidget(self.btn_add_boolean, 0, 1)

        
        self.btn_add_Array = QtWidgets.QPushButton("Array")
        self.btn_add_Array.setStyleSheet(style.BTN_ACTION)
        mod_grid.addWidget(self.btn_add_Array, 1, 0)

        self.btn_add_Symmetry = QtWidgets.QPushButton("Symmetry")        
        self.btn_add_Symmetry.setStyleSheet(style.BTN_ACTION)        
        mod_grid.addWidget(self.btn_add_Symmetry, 1, 1)

        self.btn_add_chamfer = QtWidgets.QPushButton("Chamfer")
        self.btn_add_chamfer.setStyleSheet(style.BTN_ACTION)
        mod_grid.addWidget(self.btn_add_chamfer, 2, 0)
        
        self.btn_add_Bend = QtWidgets.QPushButton("Bend")        
        self.btn_add_Bend.setStyleSheet(style.BTN_ACTION)        
        mod_grid.addWidget(self.btn_add_Bend, 2, 1)

        self.btn_add_FFD = QtWidgets.QPushButton("FFD")
        self.btn_add_FFD.setStyleSheet(style.BTN_ACTION)
        mod_grid.addWidget(self.btn_add_FFD, 3, 0)
        
        self.btn_add_xform = QtWidgets.QPushButton("Xform")        
        self.btn_add_xform.setStyleSheet(style.BTN_ACTION)        
        mod_grid.addWidget(self.btn_add_xform, 3, 1)

        self.right_layout.addWidget(self.group_modifiers)

        
        self.group_settings = QtWidgets.QGroupBox("Live Transformation")
        self.group_settings.setStyleSheet(style.GROUP_BOX_HEADER)
        settings_v = QtWidgets.QVBoxLayout(self.group_settings)
        settings_v.setSpacing(10)

        
        rot_row = QtWidgets.QHBoxLayout()
        rot_row.addWidget(QtWidgets.QLabel("Rotation:"))
        
        self.combo_rot_axis = QtWidgets.QComboBox()
        self.combo_rot_axis.addItems(["X", "Y", "Z"])
        self.combo_rot_axis.setCurrentIndex(2) 
        self.combo_rot_axis.setFixedWidth(45)
        self.combo_rot_axis.setStyleSheet(style.SPIN_BOX_STYLE)
        
        self.spin_rotation = DraggableDoubleSpinBox()
        self.spin_rotation.setRange(-360.0, 360.0)
        self.spin_rotation.setStyleSheet(style.SPIN_BOX_STYLE)
        
        rot_row.addWidget(self.combo_rot_axis)
        rot_row.addWidget(self.spin_rotation)
        settings_v.addLayout(rot_row)

         
        scale_xyz_row = QtWidgets.QHBoxLayout()
        scale_xyz_row.addWidget(QtWidgets.QLabel("Axis Scale:"))
        
        self.combo_scale_axis = QtWidgets.QComboBox()
        self.combo_scale_axis.addItems(["X", "Y", "Z"])
        self.combo_scale_axis.setCurrentIndex(0)
        self.combo_scale_axis.setFixedWidth(45)
        self.combo_scale_axis.setStyleSheet(style.SPIN_BOX_STYLE)
        
        self.spin_scale_axis_val = DraggableDoubleSpinBox()
        self.spin_scale_axis_val.setRange(0.01, 100.0)
        self.spin_scale_axis_val.setValue(1.0)
        self.spin_scale_axis_val.setStyleSheet(style.SPIN_BOX_STYLE)
        
        scale_xyz_row.addWidget(self.combo_scale_axis)
        scale_xyz_row.addWidget(self.spin_scale_axis_val)
        settings_v.addLayout(scale_xyz_row)

        
        global_scale_row = QtWidgets.QHBoxLayout()
        global_scale_row.addWidget(QtWidgets.QLabel("Global Scale:"))
        self.spin_scale_uniform = DraggableDoubleSpinBox()
        self.spin_scale_uniform.setRange(0.01, 100.0)
        self.spin_scale_uniform.setValue(1.0)
        self.spin_scale_uniform.setStyleSheet(style.SPIN_BOX_STYLE)
        global_scale_row.addWidget(self.spin_scale_uniform)
        settings_v.addLayout(global_scale_row)

        
        pos_row = QtWidgets.QHBoxLayout()
        pos_row.addWidget(QtWidgets.QLabel("Position Offset:"))
        
        self.combo_pos_axis = QtWidgets.QComboBox()
        self.combo_pos_axis.addItems(["X", "Y", "Z"])
        self.combo_pos_axis.setCurrentIndex(2) 
        self.combo_pos_axis.setFixedWidth(45)
        self.combo_pos_axis.setStyleSheet(style.SPIN_BOX_STYLE)
        
        self.spin_pos_offset = DraggableDoubleSpinBox()
        self.spin_pos_offset.setRange(-1000.0, 1000.0)
        self.spin_pos_offset.setValue(0.0)
        self.spin_pos_offset.setStyleSheet(style.SPIN_BOX_STYLE)
        
        pos_row.addWidget(self.combo_pos_axis)
        pos_row.addWidget(self.spin_pos_offset)
        settings_v.addLayout(pos_row)

        
        quick_tools = QtWidgets.QHBoxLayout()
        self.btn_mirror = QtWidgets.QPushButton("↔ Mirror")
        self.btn_reset_tm = QtWidgets.QPushButton("🔄 Reset All")
        self.btn_mirror.setStyleSheet(style.BTN_ACTION)
        self.btn_reset_tm.setStyleSheet(style.BTN_ACTION)
        quick_tools.addWidget(self.btn_mirror)
        quick_tools.addWidget(self.btn_reset_tm)
        settings_v.addLayout(quick_tools)

        self.right_layout.addWidget(self.group_settings)

        
        self.group_final = QtWidgets.QGroupBox("Finalize")
        self.group_final.setStyleSheet(style.GROUP_BOX_HEADER)
        final_v = QtWidgets.QVBoxLayout(self.group_final)

        self.btn_commit = QtWidgets.QPushButton("✅ APPLY && COMMIT")
        self.btn_commit.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; height: 35px;")
        
        self.btn_add_to_lib = QtWidgets.QPushButton("➕ Add Selection to Library")
        self.btn_add_to_lib.setStyleSheet(style.BTN_ACTION)
        self.btn_add_to_lib.setFixedHeight(30)

        final_v.addWidget(self.btn_commit)
        final_v.addWidget(self.btn_add_to_lib)
        self.right_layout.addWidget(self.group_final)

        
        self.group_tree = QtWidgets.QGroupBox("Library Explorer")
        self.group_tree.setStyleSheet(style.GROUP_BOX_HEADER)
        tree_v = QtWidgets.QVBoxLayout(self.group_tree)
        self.library_tree = QtWidgets.QTreeWidget()
        self.library_tree.setHeaderHidden(True)
        self.library_tree.setMinimumHeight(300)
        self.library_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.library_tree.customContextMenuRequested.connect(self.open_tree_menu)
        self.fav_root = QtWidgets.QTreeWidgetItem(self.library_tree, ["⭐ Favorites"])
        self.folder_root = QtWidgets.QTreeWidgetItem(self.library_tree, ["📂 All Folders"])
        self.btn_refresh = QtWidgets.QPushButton("🔄 Refresh Library")
        self.btn_refresh.setStyleSheet(style.BTN_ACTION)
        
        tree_v.addWidget(self.btn_refresh)
        tree_v.addWidget(self.library_tree)
        self.right_layout.addWidget(self.group_tree)


        
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([700, 300])
        self.main_layout.addWidget(self.splitter)

        
        self.log_area = QtWidgets.QLabel("Ready.")
        self.log_area.setFixedHeight(30) 
        self.log_area.setStyleSheet(f"color: {constants.LOGGER_INFO_COLOR}; font-size: 10px; padding: 2px;")
        self.main_layout.addWidget(self.log_area)
        self.main_layout.setStretchFactor(self.splitter, 1)

    

    def log_message(self, message, msg_type="info"):
        color = constants.LOGGER_INFO_COLOR
        if msg_type == "error": color = constants.LOGGER_ERROR_COLOR
        elif msg_type == "warn": color = constants.LOGGER_WARN_COLOR
        self.log_area.setStyleSheet(f"color: {color}; font-size: 10px; padding: 2px;")
        self.log_area.setText(message)

    def refresh_categories(self, library_data):
        self.category_list.clear()
        for cat_name in library_data.keys():
            item = QtWidgets.QTreeWidgetItem(self.category_list, [cat_name])
            self.category_list.addTopLevelItem(item)

    def display_models(self, models_list):
        self.current_models_data = models_list
        self.render_grid(models_list)

    def render_grid(self, models_list=None):
        if models_list is not None:
            self.current_models_data = models_list

        
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget(): 
                child.widget().deleteLater()
        
        if not self.current_models_data:
            return

           
        available_width = self.scroll.viewport().width()
        item_width = 145 
        
        
        columns = max(1, available_width // item_width)

         
        for i, model in enumerate(self.current_models_data):
            name = os.path.basename(model["max"])
            item = KitbashItem(name, model["thumb"], model["max"])
            
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(item, row, col)

    def resizeEvent(self, event):
        
        super().resizeEvent(event)
             
        if hasattr(self, 'current_models_data') and self.current_models_data:
            QtCore.QTimer.singleShot(50, lambda: self.render_grid())

    

    def open_tree_menu(self, position):
        
        item = self.library_tree.itemAt(position)
        
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(style.DARK_THEME)

        
        if item == self.folder_root:
            action_new = menu.addAction("➕ Create New Category")
            action = menu.exec_(self.library_tree.mapToGlobal(position))
            if action == action_new: 
                from ..core import logic
                logic.create_new_category(self)

        
        elif item and item.parent() == self.folder_root:
            
            cat_name = item.text(0).strip()
            
            from ..core import logic
            action_rename = menu.addAction("✏ Rename Folder")
            action_delete = menu.addAction("❌ Delete Folder")
            menu.addSeparator()
            action_explore = menu.addAction("📂 Open in Explorer")
            
            action = menu.exec_(self.library_tree.mapToGlobal(position))
            
            if action == action_rename:
                logic.rename_category(self, cat_name)
            elif action == action_delete:
                logic.delete_category(self, cat_name)
            elif action == action_explore:
                self.open_in_explorer(cat_name)

    def open_in_explorer(self, category_name):
        
        from ..core import config_manager
        config = config_manager.load_config()
        
        
        clean_name = category_name.strip()
        path = os.path.join(config.get("library_path", ""), clean_name)
        
        
        path = os.path.normpath(path)
        
        if os.path.exists(path):
            os.startfile(path)
        else:
            self.log_message(f"Path not found: {path}", "error")

    def filter_models(self, text):
        search_text = text.lower()
        filtered_list = [m for m in self.current_models_data if search_text in os.path.basename(m["max"]).lower()]
        self.render_grid(filtered_list)

    

    
        

    def open_in_explorer(self, category_name):
        """      """
        from ..core import config_manager
        config = config_manager.load_config()
        path = os.path.join(config.get("library_path", ""), category_name)
        if os.path.exists(path):
            os.startfile(path)
        else:
            self.log_message(f"❌ Path not found: {path}", "error")

    