import os
import pymxs


rt = pymxs.runtime
def get_library_structure(root_path):
    
    structure = {}
    if not root_path or not os.path.exists(root_path): return structure

    valid_extensions = (".max", ".fbx", ".obj")

    for root, dirs, files in os.walk(root_path):
        rel_path = os.path.relpath(root, root_path)
        if rel_path == ".": continue
        
        models = []
        for file in files:
            if file.lower().endswith(valid_extensions):
                full_path = os.path.join(root, file) 
                base_name = os.path.splitext(file)[0]
                thumb_path = os.path.join(root, base_name + ".jpg")
                
                final_thumb = thumb_path if os.path.exists(thumb_path) else get_icon_by_extension(full_path)
                
                models.append({
                    "max": full_path.replace("\\", "/"), 
                    "thumb": final_thumb.replace("\\", "/"),
                    "ext": os.path.splitext(file)[1].lower()
                })
        
        if models or dirs:
            structure[rel_path] = models
    return structure

def get_icon_by_extension(file_path):
    
    ext = os.path.splitext(file_path)[1].lower()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(os.path.dirname(current_dir), "ui", "icons")
    
    icon_map = {
        ".max": "icon_max.jpg",
        ".fbx": "icon_fbx.jpg",
        ".obj": "icon_obj.jpg"
    }
    
    icon_name = icon_map.get(ext, "icon_unknown.jpg")
    return os.path.join(icons_dir, icon_name).replace("\\", "/")

def generate_thumbnail(thumb_output_path):
    
    try:
        
        os.makedirs(os.path.dirname(thumb_output_path), exist_ok=True)
        clean_path = thumb_output_path.replace("\\", "/")

        
        if rt.selection.count > 0:
            rt.execute("max zoomext sel")
        else:
            rt.execute("max zoomext val")
            
        rt.completeRedraw()
        
        
        bmp = rt.gw.getViewportDib()
        bmp.filename = clean_path
        rt.save(bmp)
        
        
        try: 
            rt.free(bmp) 
        except: 
            pass
        
        return True
    except Exception as e:
        print(f"❌ Error generating thumbnail: {e}")
        return False

