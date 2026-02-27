import pymxs
rt = pymxs.runtime

def add_conform_modifier(obj, target=None):
    
    if not obj or not rt.isValidNode(obj):
        return False
        
    
    try:
        c_mod = rt.Conformmodifier()
        rt.addModifier(obj, c_mod)
        
        
        if target and rt.isValidNode(target):
            
            c_mod.targets = [target]
            
        print(f"✅ Conform Modifier added to {obj.name}")
        return True
    except:
        print("❌ Error: Conform modifier not found or incompatible.")
        return False

def add_boolean_modifier(obj):
    
    if not obj or not rt.isValidNode(obj):
        return False
        
    try:
        
        b_mod = rt.BooleanMod()
            
        rt.addModifier(obj, b_mod)
        print(f"✅ Boolean Modifier added to {obj.name}")
        return True
    except Exception as e:
        print(f"❌ Error: Boolean modifier could not be added. Details: {e}")
        return False

def apply_mirror(obj, axis="X"):
    
    if not obj or not rt.isValidNode(obj):
        return
        
    if axis == "X":
        obj.scale.x *= -1
    elif axis == "Y":
        obj.scale.y *= -1
    elif axis == "Z":
        obj.scale.z *= -1
        
    rt.redrawViews()

def finalize_and_collapse(obj):
    
    if not obj or not rt.isValidNode(obj):
        return
        
    rt.convertTo(obj, rt.Editable_Poly)
    print(f"✅ History collapsed for {obj.name}")



def add_array_modifier(obj):
    if not obj or not rt.isValidNode(obj): return False
    try:
        mod = rt.ArrayModifier() 
        rt.addModifier(obj, mod)
        print(f"✅ Array Modifier added to {obj.name}")
        return True
    except:
        print("Error: Array modifier not found.")
        return False

def add_symmetry_modifier(obj):
    if not obj or not rt.isValidNode(obj): return False
    try:
        mod = rt.Symmetry()
        rt.addModifier(obj, mod)
        print(f"Symmetry Modifier added to {obj.name}")
        return True
    except: return False

def add_chamfer_modifier(obj):
    if not obj or not rt.isValidNode(obj): return False
    try:
        mod = rt.Chamfer()
        
        try:
            mod.amount = 0.5
            mod.segments = 2
        except: pass
        rt.addModifier(obj, mod)
        print(f"✅ Chamfer Modifier added to {obj.name}")
        return True
    except: return False

def add_bend_modifier(obj):
    if not obj or not rt.isValidNode(obj): return False
    try:
        mod = rt.Bend()
        rt.addModifier(obj, mod)
        print(f"Bend Modifier added to {obj.name}")
        return True
    except: return False

def add_ffd_modifier(obj):
    if not obj or not rt.isValidNode(obj): return False
    try:
        mod = rt.FFD_3x3x3() 
        rt.addModifier(obj, mod)
        print(f"FFD 3x3x3 Modifier added to {obj.name}")
        return True
    except: return False

def add_xform_modifier(obj):
    if not obj or not rt.isValidNode(obj): return False
    try:
        mod = rt.XForm()
        rt.addModifier(obj, mod)
        print(f"XForm Modifier added to {obj.name}")
        return True
    except: return False