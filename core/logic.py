import pymxs
import os
from PySide6 import QtWidgets, QtCore

from . import io_manager, mesh_ops, config_manager, constants

try:
    from ..ui import style, browser_item, settings_dialog, add_asset_dialog
except ImportError:
    import ui.style as style
    import ui.browser_item as browser_item
    import ui.settings_dialog as settings_dialog
    import ui.add_asset_dialog as add_asset_dialog

rt = pymxs.runtime

def initialize_app(window):
    
    config = config_manager.load_config()
    path = config.get("library_path")
    library_structure = io_manager.get_library_structure(path)
    
    
    window.selected_asset_path = None
    window.current_selected_widget = None
    if hasattr(window, 'preview_node'):
        window.preview_node = None

    
    interactive_widgets = [
        window.spin_rotation,
        window.spin_scale_uniform,
        window.spin_scale_axis_val,
        window.spin_pos_offset
    ]

    
    def safe_disconnect(signal):
        try: signal.disconnect()
        except: pass

    
    for btn in [window.btn_refresh, window.btn_settings, window.btn_add_to_lib, window.btn_commit]:
        safe_disconnect(btn.clicked)
    
    safe_disconnect(window.library_tree.itemClicked)
    
    
    safe_disconnect(window.btn_add_conform.clicked)
    safe_disconnect(window.btn_add_boolean.clicked)
    safe_disconnect(window.btn_add_Array.clicked)
    safe_disconnect(window.btn_add_Symmetry.clicked)
    safe_disconnect(window.btn_add_chamfer.clicked)
    safe_disconnect(window.btn_add_Bend.clicked)
    safe_disconnect(window.btn_add_FFD.clicked)
    safe_disconnect(window.btn_add_xform.clicked)
    safe_disconnect(window.btn_mirror.clicked)
    safe_disconnect(window.btn_reset_tm.clicked)

    
    for widget in interactive_widgets:
        safe_disconnect(widget.valueChanged)
    safe_disconnect(window.combo_rot_axis.currentIndexChanged)
    safe_disconnect(window.combo_scale_axis.currentIndexChanged)

    
    
    
    window.spin_scale_uniform.valueChanged.connect(lambda: apply_transforms_to_max(window))
    window.spin_rotation.valueChanged.connect(lambda: on_spinbox_changed(window, "rotation"))
    window.spin_scale_axis_val.valueChanged.connect(lambda: on_spinbox_changed(window, "scale"))
    window.spin_pos_offset.valueChanged.connect(lambda: on_spinbox_changed(window, "position"))
    
    
    window.combo_rot_axis.currentIndexChanged.connect(lambda: sync_ui_to_axis(window, "rotation"))
    window.combo_scale_axis.currentIndexChanged.connect(lambda: sync_ui_to_axis(window, "scale"))
    window.combo_pos_axis.currentIndexChanged.connect(lambda: sync_ui_to_axis(window, "position"))
    
    
    window.btn_add_conform.clicked.connect(lambda: apply_conform_to_selection(window))
    window.btn_add_boolean.clicked.connect(lambda: apply_boolean_to_selection(window))
    window.btn_add_Array.clicked.connect(lambda: apply_array_to_selection(window))
    window.btn_add_Symmetry.clicked.connect(lambda: apply_symmetry_to_selection(window))
    window.btn_add_chamfer.clicked.connect(lambda: apply_chamfer_to_selection(window))
    window.btn_add_Bend.clicked.connect(lambda: apply_bend_to_selection(window))
    window.btn_add_FFD.clicked.connect(lambda: apply_ffd_to_selection(window))
    window.btn_add_xform.clicked.connect(lambda: apply_xform_to_selection(window))
    window.btn_mirror.clicked.connect(lambda: mirror_asset(window))
    window.btn_reset_tm.clicked.connect(lambda: reset_all_transforms(window))

    
    window.btn_commit.clicked.connect(lambda: commit_kitbash(window))
    window.btn_refresh.clicked.connect(lambda: initialize_app(window))
    window.btn_settings.clicked.connect(lambda: open_settings(window))
    window.btn_add_to_lib.clicked.connect(lambda: add_selection_to_library(window))

    
    
    if not hasattr(window, '_original_display_func'):
        window._original_display_func = window.display_models

    def on_asset_selected(widget):
        
        if window.current_selected_widget:
            try:
                
                window.current_selected_widget.set_selected(False)
            except RuntimeError:
                pass 
        
        widget.set_selected(True)
        window.current_selected_widget = widget
        window.selected_asset_path = widget.file_path

    def wrapped_display(models):
        window._original_display_func(models)
        for i in range(window.grid_layout.count()):
            item = window.grid_layout.itemAt(i)
            if not item: continue
            widget = item.widget()
            if widget:
                try: widget.clicked.disconnect()
                except: pass
                try: widget.btn_insert.clicked.disconnect()
                except: pass
                
                path = widget.file_path.replace("\\", "/")
                def connect_widget(w, p):
                    w.clicked.connect(lambda: (on_asset_selected(w), execute_kitbash_process(p, window)))
                    w.btn_insert.clicked.connect(lambda: (on_asset_selected(w), execute_kitbash_process(p, window)))
                connect_widget(widget, path)

    window.display_models = wrapped_display

    
    def on_tree_item_clicked(item, column):
        rel_path = item.data(0, QtCore.Qt.UserRole)
        if rel_path == "fav_folder":
            rel_path = item.data(1, QtCore.Qt.UserRole)
        
        if rel_path and rel_path in library_structure:
            models = library_structure.get(rel_path, [])
            window.display_models(models)
            window.log_message(f"Folder Loaded: {rel_path}", "info")

    window.library_tree.itemClicked.connect(on_tree_item_clicked)

   
    _refresh_library_tree(window)
    load_favorites_to_tree(window)
    
    if window.folder_root.childCount() > 0:
        first_item = window.folder_root.child(0)
        on_tree_item_clicked(first_item, 0)
        window.folder_root.setExpanded(True)   


# --- Folder Management ---

def create_new_category(window):
    config = config_manager.load_config()
    lib_path = config.get("library_path")
    name, ok = QtWidgets.QInputDialog.getText(window, "New Category", "Folder Name:")
    if ok and name:
        new_dir = os.path.join(lib_path, name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            initialize_app(window)
        else: window.log_message("Exists!", "warn")

def rename_category(window, old_name):
    new_name, ok = QtWidgets.QInputDialog.getText(window, "Rename Folder", "New Name:", text=old_name)
    if ok and new_name:
        config = config_manager.load_config()
        lib = config.get("library_path")
        os.rename(os.path.join(lib, old_name), os.path.join(lib, new_name))
        initialize_app(window)

def delete_category(window, category_name):
    res = QtWidgets.QMessageBox.question(window, "Delete", f"Delete '{category_name}'?")
    if res == QtWidgets.QMessageBox.Yes:
        path = os.path.join(config_manager.load_config().get("library_path"), category_name)
        import shutil
        shutil.rmtree(path)
        initialize_app(window)


# --- Assets ---

def update_single_asset_thumbnail(file_path, window):
    
    base_path = os.path.splitext(file_path)[0]
    thumb_path = base_path + ".jpg"
    
    
    if io_manager.generate_thumbnail(thumb_path):
        window.log_message(f"Thumbnail updated: {os.path.basename(thumb_path)}", "info")
        initialize_app(window) 
    else:
        window.log_message("Failed to update thumbnail.", "error")



def rename_asset(file_path, window):
    old_name = os.path.basename(file_path).replace(".max", "")
    new_name, ok = QtWidgets.QInputDialog.getText(window, "Rename Asset", "New Name:", text=old_name)
    
    if ok and new_name and new_name != old_name:
        new_path = os.path.join(os.path.dirname(file_path), new_name + ".max")
        
        try:
            
            os.rename(file_path, new_path)
            
            
            old_thumb = file_path.replace(".max", ".jpg")
            new_thumb = new_path.replace(".max", ".jpg")
            if os.path.exists(old_thumb):
                os.rename(old_thumb, new_thumb)
            
            window.log_message(f"Renamed to: {new_name}", "info")
            
            
            initialize_app(window) 
            
        except Exception as e:
            window.log_message(f"Rename failed: {e}", "error")

def delete_asset(file_path, window):
    
    asset_name = os.path.basename(file_path)
    msg = f"Are you sure you want to delete '{asset_name}' permanently?"
    
    res = QtWidgets.QMessageBox.question(window, "Confirm Delete", msg)
    
    if res == QtWidgets.QMessageBox.Yes:
        try:
            
            if os.path.exists(file_path): 
                os.remove(file_path)
            
            
            thumb_path = file_path.replace(".max", ".jpg")
            if os.path.exists(thumb_path): 
                os.remove(thumb_path)
            
            window.log_message(f"Asset '{asset_name}' deleted.", "info")
            
            
            initialize_app(window) 
            
        except Exception as e:
            window.log_message(f"Delete failed: {e}", "error")

# --- favorites ---

def add_to_favorites(file_path, window): 
    config = config_manager.load_config()
    favorites = config.get("favorites", [])
    if file_path not in favorites:
        favorites.append(file_path)
        config["favorites"] = favorites
        config_manager.save_config(config)
        load_favorites_to_tree(window)

def load_favorites_to_tree(window):
    window.fav_root.takeChildren()
    config = config_manager.load_config()
    lib_path = config.get("library_path", "")
    favorites = config.get("favorites", [])
    
    fav_folders = set()
    for fav_path in favorites:
        if os.path.exists(fav_path):
            rel_folder = os.path.relpath(os.path.dirname(fav_path), lib_path)
            fav_folders.add(rel_folder)

    nodes = {"": window.fav_root}
    for rel_path in sorted(list(fav_folders)):
        if rel_path == ".": continue
        
        parent_rel = os.path.dirname(rel_path)
        parent_node = nodes.get(parent_rel, window.fav_root)
        
        name = os.path.basename(rel_path)
        item = QtWidgets.QTreeWidgetItem(parent_node, [f"  {name}"])
        item.setIcon(0, window.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        
        
        item.setData(0, QtCore.Qt.UserRole, "fav_folder") 
        item.setData(1, QtCore.Qt.UserRole, rel_path)
        nodes[rel_path] = item


def add_selection_to_library(window):
    if rt.selection.count == 0:
        window.log_message("Error: Select something in Max first!", "error")
        return

    config = config_manager.load_config()
    lib_path = config.get("library_path")
    
    
    categories = [f for f in os.listdir(lib_path) if os.path.isdir(os.path.join(lib_path, f))]
    
    
    dialog = add_asset_dialog.AddAssetDialog(categories, window) 
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        cat_name, model_name = dialog.get_values()
        
        if not model_name.strip():
            window.log_message("Save cancelled: Asset name is empty.", "warn")
            return

       
        save_dir = os.path.join(lib_path, cat_name)
        max_file = os.path.join(save_dir, f"{model_name}.max")
        thumb_file = os.path.join(save_dir, f"{model_name}.jpg")

        try:
            rt.saveNodes(rt.selection, max_file)
            from ..core import io_manager
            io_manager.generate_thumbnail(thumb_file)
            window.log_message(f"Asset '{model_name}' added to {cat_name}.", "info")
            initialize_app(window)
        except Exception as e:
            window.log_message(f"Save Error: {e}", "error")

def _refresh_library_tree(window):
    window.folder_root.takeChildren()
    lib_path = config_manager.load_config().get("library_path")
    if not os.path.exists(lib_path): return

    
    nodes = {"": window.folder_root}
    
    
    all_paths = sorted([f for f in os.walk(lib_path)])
    
    for root, dirs, files in all_paths:
        rel_path = os.path.relpath(root, lib_path)
        if rel_path == ".": continue
        
        parent_rel = os.path.dirname(rel_path)
        parent_node = nodes.get(parent_rel, window.folder_root)
        
        name = os.path.basename(rel_path)
        item = QtWidgets.QTreeWidgetItem(parent_node, [f"  {name}"])
        item.setIcon(0, window.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        
        
        item.setData(0, QtCore.Qt.UserRole, rel_path)
        nodes[rel_path] = item

def open_settings(window):
    config = config_manager.load_config()
    
    dialog = settings_dialog.SettingsDialog(window, config.get("library_path", "")) 
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        config["library_path"] = dialog.get_path()
        config_manager.save_config(config)
        initialize_app(window)

# --- select Polygon

def enter_polygon_mode(window):
    
    if rt.selection.count > 0:
        target_obj = rt.selection[0]
        if rt.classOf(target_obj) != rt.Editable_Poly:
            rt.convertTo(target_obj, rt.Editable_Poly)
        
        rt.select(target_obj)
        rt.execute("max modify mode") 
        rt.subObjectLevel = 4 
        window.log_message("Select Target Polygons.", "info")
    else: 
        window.log_message("Select an object first!", "warn")




def on_spinbox_changed(window, transform_type):
    
    if not window.preview_node or not rt.isValidNode(window.preview_node):
        return

    if transform_type == "position":
        axis_idx = window.combo_pos_axis.currentIndex()
        val = window.spin_pos_offset.value()
        if axis_idx == 0: window.off_x = val
        elif axis_idx == 1: window.off_y = val
        else: window.off_z = val
        
    elif transform_type == "rotation":
        axis_idx = window.combo_rot_axis.currentIndex()
        val = window.spin_rotation.value()
        if axis_idx == 0: window.rot_x = val
        elif axis_idx == 1: window.rot_y = val
        else: window.rot_z = val
        
    elif transform_type == "scale":
        axis_idx = window.combo_scale_axis.currentIndex()
        val = window.spin_scale_axis_val.value()
        if axis_idx == 0: window.scl_x = val
        elif axis_idx == 1: window.scl_y = val
        else: window.scl_z = val
        
    
    apply_transforms_to_max(window)

def sync_ui_to_axis(window, transform_type):
    
    if transform_type == "position":
        axis_idx = window.combo_pos_axis.currentIndex()
        val = [window.off_x, window.off_y, window.off_z][axis_idx]
        window.spin_pos_offset.blockSignals(True)
        window.spin_pos_offset.setValue(val)
        window.spin_pos_offset.blockSignals(False)
        
    elif transform_type == "rotation":
        axis_idx = window.combo_rot_axis.currentIndex()
        val = [window.rot_x, window.rot_y, window.rot_z][axis_idx]
        window.spin_rotation.blockSignals(True)
        window.spin_rotation.setValue(val)
        window.spin_rotation.blockSignals(False)
        
    elif transform_type == "scale":
        axis_idx = window.combo_scale_axis.currentIndex()
        val = [window.scl_x, window.scl_y, window.scl_z][axis_idx]
        window.spin_scale_axis_val.blockSignals(True)
        window.spin_scale_axis_val.setValue(val)
        window.spin_scale_axis_val.blockSignals(False)

def apply_transforms_to_max(window):
    
    if not window.preview_node or not rt.isValidNode(window.preview_node):
        return

   
    if hasattr(window, 'base_pos'):
        new_pos = rt.Point3(
            window.base_pos.x + window.off_x,
            window.base_pos.y + window.off_y,
            window.base_pos.z + window.off_z
        )
        window.preview_node.pos = new_pos

    
    euler_angles = rt.eulerAngles(window.rot_x, window.rot_y, window.rot_z)
    window.preview_node.rotation = rt.eulerToQuat(euler_angles)

    
    g_scale = window.spin_scale_uniform.value() 
    final_scale = rt.Point3(
        g_scale * window.scl_x,
        g_scale * window.scl_y,
        g_scale * window.scl_z
    )
    window.preview_node.scale = final_scale

    rt.redrawViews()




def update_rotation(window, angle):
    
    window.current_rotation = (window.current_rotation + angle) % 360
    window.log_message(f"Rotation set to: {window.current_rotation}°", "info")
    
    if window.preview_node:
        update_kitbash_preview(window)

def reset_all_transforms(window):
    
    window.rot_x = 0.0
    window.rot_y = 0.0
    window.rot_z = 0.0
    
    
    window.spin_rotation.setValue(0.0)
    window.spin_scale_uniform.setValue(1.0)
    window.spin_scale_axis_val.setValue(1.0)
    window.spin_pos_offset.setValue(0.0)
    
    
    window.combo_rot_axis.setCurrentIndex(2) # Z-Axis
    window.combo_scale_axis.setCurrentIndex(0) # X-Axis
    window.combo_pos_axis.setCurrentIndex(2) # Z-Axis
    
    
    if window.preview_node and rt.isValidNode(window.preview_node):
       
        if hasattr(window, 'base_pos'):
            window.preview_node.pos = rt.Point3(window.base_pos.x, window.base_pos.y, window.base_pos.z)
        
       
        window.preview_node.rotation = rt.eulerToQuat(rt.eulerAngles(0, 0, 0))
        window.preview_node.scale = rt.Point3(1, 1, 1)
        
    window.log_message("🔄 All Transforms & Internal Data Reset. ", "info")
    rt.redrawViews()

# UPDATE CATEGORY THUMBNAILS
def update_category_thumbnails(window, category_name):
    
    msg = "This will open each file in the folder to take a new screenshot.\nUnsaved changes in your current scene will be lost.\n\nDo you want to continue?"
    res = QtWidgets.QMessageBox.warning(window, "Warning: Scene Reset", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    
    if res != QtWidgets.QMessageBox.Yes:
        window.log_message("Thumbnail update cancelled.", "warn")
        return

    config = config_manager.load_config()
    lib_path = config.get("library_path")
    cat_path = os.path.join(lib_path, category_name)
    
    if os.path.exists(cat_path):
        max_files = [f for f in os.listdir(cat_path) if f.endswith(".max")]
        success_count = 0
        
        for f in max_files:
            file_path = os.path.join(cat_path, f).replace("\\", "/")
            thumb_path = os.path.join(cat_path, f.replace(".max", ".jpg")).replace("\\", "/")
            
            try:
                
                rt.loadMaxFile(file_path, quiet=True)
                
                
                rt.execute("select objects")
                
                
                if io_manager.generate_thumbnail(thumb_path):
                    success_count += 1
            except Exception as e:
                print(f"Failed to process {f}: {e}")
        
        
        rt.resetMaxFile(noPrompt=True)
        window.log_message(f"✅ Updated {success_count}/{len(max_files)} thumbnails for '{category_name}'.", "info")
        initialize_app(window)
    else:
        window.log_message(f"❌ Folder not found: {category_name}", "error")


# UPDAT KITBASH PREVIEW
def update_kitbash_preview(window):
    
    if not window.preview_node or not rt.isValidNode(window.preview_node):
        return

    print("\n" + "="*40)
    print("🔄 --- UPDATE PREVIEW CALLED ---")

    # ---------------------------------------------------------
    # Position
    # ---------------------------------------------------------
    pos_axis = window.combo_pos_axis.currentIndex()
    pos_val = window.spin_pos_offset.value()
    
    if pos_axis == 0: window.off_x = pos_val
    elif pos_axis == 1: window.off_y = pos_val
    else: window.off_z = pos_val

    if hasattr(window, 'base_pos'):
        new_pos = rt.Point3(
            window.base_pos.x + window.off_x,
            window.base_pos.y + window.off_y,
            window.base_pos.z + window.off_z
        )
        window.preview_node.pos = new_pos
        print(f"📍 POSITION:")
        print(f"   -> Base Pos: [{window.base_pos.x:.2f}, {window.base_pos.y:.2f}, {window.base_pos.z:.2f}]")
        print(f"   -> Memory Offset: X:{window.off_x:.2f} | Y:{window.off_y:.2f} | Z:{window.off_z:.2f}")
        print(f"   -> Final Pos Applied: [{new_pos.x:.2f}, {new_pos.y:.2f}, {new_pos.z:.2f}]")

    # ---------------------------------------------------------
    # Rotation
    # ---------------------------------------------------------
    rot_axis = window.combo_rot_axis.currentIndex()
    rot_val = window.spin_rotation.value()
    
    if rot_axis == 0: window.rot_x = rot_val
    elif rot_axis == 1: window.rot_y = rot_val
    else: window.rot_z = rot_val
    
    euler_angles = rt.eulerAngles(window.rot_x, window.rot_y, window.rot_z)
    window.preview_node.rotation = rt.eulerToQuat(euler_angles)
    
    print(f"🌪 ROTATION:")
    print(f"   -> Active UI Axis: {'X' if rot_axis==0 else 'Y' if rot_axis==1 else 'Z'} = {rot_val:.2f}°")
    print(f"   -> Memory Euler: X:{window.rot_x:.2f}° | Y:{window.rot_y:.2f}° | Z:{window.rot_z:.2f}°")

    # ---------------------------------------------------------
    # Scale
    # ---------------------------------------------------------
    g_scale = window.spin_scale_uniform.value()
    scl_axis = window.combo_scale_axis.currentIndex()
    scl_val = window.spin_scale_axis_val.value()
    
    if scl_axis == 0: window.scl_x = scl_val
    elif scl_axis == 1: window.scl_y = scl_val
    else: window.scl_z = scl_val
    
    final_scale = rt.Point3(
        g_scale * window.scl_x,
        g_scale * window.scl_y,
        g_scale * window.scl_z
    )
    window.preview_node.scale = final_scale
    
    print(f"📏 SCALE:")
    print(f"   -> Global Scale Multiplier: {g_scale:.2f}")
    print(f"   -> Memory Factors: X:{window.scl_x:.2f} | Y:{window.scl_y:.2f} | Z:{window.scl_z:.2f}")
    print(f"   -> Final Scale Applied: [{final_scale.x:.2f}, {final_scale.y:.2f}, {final_scale.z:.2f}]")
    print("="*40 + "\n")

    rt.redrawViews()




# commit and cancle kitbash
def commit_kitbash(window):
    
    if not window.preview_node or not rt.isValidNode(window.preview_node):
        window.log_message("❌ Error: Nothing to commit! ", "error")
        return

    #Editable Poly 
    mesh_ops.finalize_and_collapse(window.preview_node)
    
   
    window.preview_node = None
    window.log_message("✅ Committed! Ready for next asset. ", "info")
    rt.redrawViews()

def cancel_kitbash(window):
    
    if window.preview_node and rt.isValidNode(window.preview_node):
        rt.delete(window.preview_node)
        window.preview_node = None
        window.log_message("Preview Cancelled.", "warn")
        rt.redrawViews()


# MIRRORS
def mirror_asset(window):
    
    if window.preview_node and rt.isValidNode(window.preview_node):
        axis_idx = window.combo_scale_axis.currentIndex()
        axis_map = {0: "X", 1: "Y", 2: "Z"}
        mesh_ops.apply_mirror(window.preview_node, axis_map[axis_idx])
        window.log_message(f"↔ Mirrored on {axis_map[axis_idx]}", "info")


# --- Execute kitbash Process
def execute_kitbash_process(file_path, window):
    """MAX, FBX  OBJ"""
    file_path = file_path.replace("\\", "/")
    ext = os.path.splitext(file_path)[1].lower() 
    
    
    target_obj = rt.selection[0] if rt.selection.count > 0 else None
    
    
    if hasattr(window, 'preview_node') and window.preview_node and rt.isValidNode(window.preview_node):
        rt.delete(window.preview_node)

    
    objs_before = set(rt.objects)
    import_success = False

    
    if ext == ".max":
        import_success = rt.mergeMAXFile(file_path, noPrompt=True, select=True)
    elif ext in [".fbx", ".obj"]:
        
        import_success = rt.importFile(file_path, rt.name('noPrompt'))
    else:
        window.log_message(f"❌ Unsupported format: {ext}", "error")
        return

    
    if import_success:
        new_objs = list(set(rt.objects) - objs_before)
        if new_objs:
            window.preview_node = new_objs[0] 
            rt.convertTo(window.preview_node, rt.Editable_Poly)
            
            
            if target_obj:
                window.preview_node.pos = target_obj.pos
                window.log_message(f"✅ {ext.upper()} placed on {target_obj.name}.", "info")
            else:
                window.preview_node.pos = rt.Point3(0, 0, 0)
                window.log_message(f"✅ {ext.upper()} imported at center.", "info")
            
            
            window.base_pos = rt.Point3(window.preview_node.pos.x, 
                                       window.preview_node.pos.y, 
                                       window.preview_node.pos.z)
            
            
            apply_transforms_to_max(window)


# ==========================================
# MODIFIERS & QUICK ACTIONS
# ==========================================

def _get_active_target(window):
    """تشخیص هوشمند آبجکت: اولویت با پیش‌نمایش، در غیر این‌صورت آبجکت انتخاب شده در صحنه"""
    if window.preview_node and rt.isValidNode(window.preview_node):
        return window.preview_node
    if rt.selection.count > 0:
        return rt.selection[0]
    return None

def apply_conform_to_selection(window):
    target = _get_active_target(window)
    if target:
        surface = None
        # پیدا کردن آبجکت زیرین به عنوان تارگت کانفرم
        for obj in rt.selection:
            if obj != target:
                surface = obj
                break
        mesh_ops.add_conform_modifier(target, surface)
        window.log_message(f"✅ Conform Modifier Added to {target.name}.", "info")
        rt.redrawViews()

def apply_boolean_to_selection(window):
    target = _get_active_target(window)
    if target:
        mesh_ops.add_boolean_modifier(target)
        window.log_message(f"✂ Boolean Modifier Added to {target.name}.", "info")
        rt.redrawViews()

def apply_array_to_selection(window):
    target = _get_active_target(window)
    if target:
        mesh_ops.add_array_modifier(target)
        window.log_message(f"💠 Array Modifier Added to {target.name}.", "info")
        rt.redrawViews()

def apply_symmetry_to_selection(window):
    target = _get_active_target(window)
    if target:
        mesh_ops.add_symmetry_modifier(target)
        window.log_message(f"🦋 Symmetry Modifier Added to {target.name}.", "info")
        rt.redrawViews()

def apply_chamfer_to_selection(window):
    target = _get_active_target(window)
    if target:
        mesh_ops.add_chamfer_modifier(target)
        window.log_message(f"✨ Chamfer Modifier Added to {target.name}.", "info")
        rt.redrawViews()

def apply_bend_to_selection(window):
    target = _get_active_target(window)
    if target:
        mesh_ops.add_bend_modifier(target)
        window.log_message(f"↪ Bend Modifier Added to {target.name}.", "info")
        rt.redrawViews()

def apply_ffd_to_selection(window):
    target = _get_active_target(window)
    if target:
        mesh_ops.add_ffd_modifier(target)
        window.log_message(f"📦 FFD Modifier Added to {target.name}.", "info")
        rt.redrawViews()

def apply_xform_to_selection(window):
    target = _get_active_target(window)
    if target:
        mesh_ops.add_xform_modifier(target)
        window.log_message(f"📐 XForm Modifier Added to {target.name}.", "info")
        rt.redrawViews()