import pymxs
import sys        
import os         
import gc
from PySide6 import QtWidgets, QtCore

def main(): 
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    
    
    if current_dir in sys.path:
        sys.path.remove(current_dir)
    sys.path.insert(0, current_dir)

    
    keys_to_clear = [k for k in list(sys.modules.keys()) if k == "ui" or k.startswith("ui.") or k == "core" or k.startswith("core.")]
    for k in keys_to_clear:
        del sys.modules[k]
    
    gc.collect()

    try:
        
        import core.constants as constants
        import core.logic as logic
        import ui.main_window as ui_mod
        
    except Exception as e:
        print(f"❌ [OPEN KITBASH] Error during loading: {e}")
        import traceback
        traceback.print_exc()
        return

    rt = pymxs.runtime
    max_hwnd = rt.windows.getMAXHWND()
    main_window_ptr = QtWidgets.QWidget.find(max_hwnd)

    pkg_id = "MAB_OPENKITBASH" 
    for child in main_window_ptr.findChildren(QtWidgets.QDockWidget):
        if child.objectName() == f"{pkg_id}_dock":
            child.close()
            child.deleteLater()

    window_title = f"{constants.PRODUCT_NAME} v{constants.VERSION}"
    dock_ptr = QtWidgets.QDockWidget(window_title, main_window_ptr)
    dock_ptr.setObjectName(f"{pkg_id}_dock")
    
    ui_content = ui_mod.OpenKitbashContent()
    dock_ptr.setWidget(ui_content)

    main_window_ptr.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock_ptr)
    
    logic.initialize_app(ui_content)
    
    dock_ptr.show()
    print(f"✅ {constants.PRODUCT_NAME} Launched Successfully.")

if __name__ == "__main__":
    main()