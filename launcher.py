import pymxs
import sys        
import os         
import importlib  
import gc
from PySide6 import QtWidgets, QtCore


def launch_open_kitbash():
          
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    parent_dir = os.path.dirname(current_dir)
    pkg_name = os.path.basename(current_dir)

             
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    elif sys.path[0] != parent_dir:
        sys.path.remove(parent_dir)
        sys.path.insert(0, parent_dir)

        
    prefix = pkg_name + "."
    for mod in list(sys.modules.keys()):
        if mod == pkg_name or mod.startswith(prefix):
            del sys.modules[mod]
    
    gc.collect()

    try:
        
        core_mod = importlib.import_module(f"{pkg_name}.core.constants")
        logic_mod = importlib.import_module(f"{pkg_name}.core.logic")
        ui_mod = importlib.import_module(f"{pkg_name}.ui.main_window")
        
                
        constants = core_mod
        logic = logic_mod
        main_window = ui_mod
        
    except Exception as e:
        print(f"❌ [OPEN KITBASH] Error during loading: {e}")
        import traceback
        traceback.print_exc()
        return

      
    rt = pymxs.runtime
    max_hwnd = rt.windows.getMAXHWND()
    main_window_ptr = QtWidgets.QWidget.find(max_hwnd)

     
    for child in main_window_ptr.findChildren(QtWidgets.QDockWidget):
        if child.objectName() == f"{pkg_name}_dock":
            child.close()
            child.deleteLater()

    window_title = f"{constants.PRODUCT_NAME} v{constants.VERSION}"
    dock_ptr = QtWidgets.QDockWidget(window_title, main_window_ptr)
    dock_ptr.setObjectName(f"{pkg_name}_dock")
    
    ui_content = main_window.OpenKitbashContent()
    dock_ptr.setWidget(ui_content)

    main_window_ptr.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock_ptr)
    
       
    logic.initialize_app(ui_content)
    
    dock_ptr.show()
    print(f"✅ {constants.PRODUCT_NAME} Launched Successfully.")

if __name__ == "__main__":
    launch_open_kitbash()