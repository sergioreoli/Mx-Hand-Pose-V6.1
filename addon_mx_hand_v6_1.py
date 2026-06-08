bl_info = {
    "name": "Mx Hand Pose V6.1 - Mixamo Compatible",
    "author": "Sergio ReOli Paypal:sergioreoli@hotmail.com",
    "version": (6, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Hand Pose",
    "description": "Control hand poses with dedicated buttons for thumb bones - Native Mixamo compatible",
    "category": "Animation",
}

import bpy
from math import radians, degrees

# ============================================
# AUXILIARY FUNCTIONS - MIXAMO COMPATIBLE
# ============================================

def get_bone_by_name(armature, bone_name):
    """Get bone by name, trying different naming conventions"""
    bone = armature.pose.bones.get(bone_name)
    if bone:
        return bone
    
    bone = armature.pose.bones.get(f"mixamorig:{bone_name}")
    if bone:
        return bone
    
    bone = armature.pose.bones.get(f"Ctrl_{bone_name}")
    if bone:
        return bone
    
    return None


def get_bone_by_pattern(armature, patterns):
    """Get bone by trying multiple naming patterns"""
    for pattern in patterns:
        bone = armature.pose.bones.get(pattern)
        if bone:
            return bone
    return None


def get_finger_bone(armature, side, finger, index):
    """
    Get finger bone with flexible naming convention
    side: 'Left' or 'Right'
    finger: 'Thumb', 'Index', 'Middle', 'Ring', 'Pinky'
    index: 1, 2, 3 (bone number)
    """
    side_short = 'L' if side == 'Left' else 'R'
    side_full = side
    finger_map = {
        "Thumb": "Thumb",
        "Index": "Index",
        "Middle": "Middle",
        "Ring": "Ring",
        "Pinky": "Pinky"
    }
    
    finger_name = finger_map[finger]
    finger_lower = finger_name.lower()
    
    patterns = []
    
    # Mixamo Control Rig pattern: Ctrl_Thumb1_L, Ctrl_Thumb_01_L
    patterns.append(f"Ctrl_{finger_name}{index}_{side_short}")
    patterns.append(f"Ctrl_{finger_name}_{index:02d}_{side_short}")
    patterns.append(f"Ctrl_{finger_lower}{index}_{side_short.lower()}")
    patterns.append(f"Ctrl_{finger_name}{index}_{side_full}")
    
    # Mixamo standard pattern: mixamorig:LeftHandThumb1
    patterns.append(f"mixamorig:{side_full}Hand{finger_name}{index}")
    patterns.append(f"mixamorig:{side_full}Hand{finger_name}")
    patterns.append(f"mixamorig:{side_full}Hand{finger_lower}{index}")
    
    # Standard naming: Thumb.01.L
    patterns.append(f"{finger_name}.{index:02d}.{side_short}")
    patterns.append(f"{finger_name}.{index}.{side_short}")
    
    # Alternative: Thumb_01_L
    patterns.append(f"{finger_name}_{index:02d}_{side_short}")
    patterns.append(f"{finger_lower}_{index:02d}_{side_short.lower()}")
    
    # Lowercase variant: thumb.01.l
    patterns.append(f"{finger_lower}.{index:02d}.{side_short.lower()}")
    
    return get_bone_by_pattern(armature, patterns)


def get_hand_bone(armature, side):
    """Get wrist/hand bone"""
    side_short = 'L' if side == 'Left' else 'R'
    side_full = side
    
    patterns = [
        f"Ctrl_Hand_{side_short}",
        f"Ctrl_Hand_{side_full}",
        f"Ctrl_Hand_IK_{side_full}",
        f"Ctrl_Hand_IK_{side_short}",
        f"Ctrl_Wrist_{side_short}",
        f"Ctrl_Arm_{side_short}",
        f"Ctrl_Arm_{side_full}",
        f"mixamorig:{side_full}Hand",
        f"mixamorig:{side_full}Wrist",
        f"Hand_{side_full}",
        f"Hand_{side_short}",
        f"Wrist_{side_full}",
        f"Wrist_{side_short}",
    ]
    
    return get_bone_by_pattern(armature, patterns)


def set_finger_rotation(armature, side, finger, f1x=0, f1y=0, f1z=0, f2=0, f3=0):
    """Set rotation for all three finger joints"""
    bone1 = get_finger_bone(armature, side, finger, 1)
    if bone1:
        bone1.rotation_mode = 'XYZ'
        if finger == "Thumb":
            bone1.rotation_euler = (radians(f1x), radians(f1y), radians(f1z))
        else:
            bone1.rotation_euler.x = radians(f1x)
    
    bone2 = get_finger_bone(armature, side, finger, 2)
    if bone2:
        bone2.rotation_mode = 'XYZ'
        bone2.rotation_euler.x = radians(f2)
    
    bone3 = get_finger_bone(armature, side, finger, 3)
    if bone3:
        bone3.rotation_mode = 'XYZ'
        bone3.rotation_euler.x = radians(f3)


# ============================================
# CLOSURE FUNCTION
# ============================================

def apply_closure(armature, side, percentage):
    """Apply hand closure based on percentage (0-100)"""
    p = percentage / 100

    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 90*p, 50*p, -10*p, 110*p, 50*p)
    else:
        set_finger_rotation(armature, side, "Thumb", 50*p, -50*p, -15*p, 110*p, 50*p)

    for finger in ["Index", "Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 90*p, 0, 0, 90*p, 70*p)


# ============================================
# COMPLETE POSES
# ============================================

def pose_reset(armature, side):
    """Reset all fingers to zero rotation"""
    for finger in ["Thumb", "Index", "Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 0, 0, 0, 0, 0)


def pose_relaxed(armature, side):
    """Relaxed hand pose"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 0, 0, 0, 0, 0)
    else:
        set_finger_rotation(armature, side, "Thumb", 5, -25, -15, 10, 5)
    set_finger_rotation(armature, side, "Index", 15, 0, 0, 10, 5)
    set_finger_rotation(armature, side, "Middle", 20, 0, 0, 15, 8)
    set_finger_rotation(armature, side, "Ring", 15, 0, 0, 10, 5)
    set_finger_rotation(armature, side, "Pinky", 25, 0, 0, 15, 10)


def pose_closed(armature, side):
    """Closed fist"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 50, 50, -10, 110, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 50, -50, -15, 110, 50)
    set_finger_rotation(armature, side, "Index", 80, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Middle", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Ring", 80, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Pinky", 70, 0, 0, 90, 70)


def pose_point(armature, side):
    """Pointing pose"""
    set_finger_rotation(armature, side, "Thumb", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Index", 0, 0, 0, 0, 0)
    for finger in ["Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 90, 0, 0, 90, 70)


def pose_shoot(armature, side):
    """Shooting pose (finger gun)"""
    set_finger_rotation(armature, side, "Thumb", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Index", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Middle", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Ring", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Pinky", 90, 0, 0, 90, 70)


def pose_gun(armature, side):
    """Gun pose"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 40, 30, -15, 80, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 40, -30, -15, 80, 50)
    set_finger_rotation(armature, side, "Index", 20, -15, 10, 10, 0)
    set_finger_rotation(armature, side, "Middle", 20, 15, -10, 10, 0)
    set_finger_rotation(armature, side, "Ring", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Pinky", 90, 0, 0, 90, 70)


def pose_rock(armature, side):
    """Rock on pose"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 50, 50, -10, 110, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 50, -50, -15, 110, 50)
    set_finger_rotation(armature, side, "Index", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Middle", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Ring", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Pinky", 0, 0, 0, 0, 0)


def pose_ok(armature, side):
    """OK sign pose"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 25, 20, -15, 40, 25)
        set_finger_rotation(armature, side, "Index", 45, -5, 5, 35, 20)
    else:
        set_finger_rotation(armature, side, "Thumb", 25, -20, -15, 40, 25)
        set_finger_rotation(armature, side, "Index", 45, 5, -5, 35, 20)
    for finger in ["Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 0, 0, 0, 0, 0)


def pose_peace(armature, side):
    """Peace/Victory sign"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 40, 40, -10, 80, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 40, -40, -10, 80, 50)
    set_finger_rotation(armature, side, "Index", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Middle", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Ring", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Pinky", 90, 0, 0, 90, 70)


def pose_hold(armature, side):
    """Hold pose"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 30, 25, -30, 30, 15)
    else:
        set_finger_rotation(armature, side, "Thumb", 30, -25, -30, 30, 15)
    for finger in ["Index", "Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 50, 0, 0, 60, 40)


def pose_like(armature, side):
    """Like/Thumbs up pose"""
    set_finger_rotation(armature, side, "Thumb", 0, 0, 0, 0, 0)
    for finger in ["Index", "Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 90, 0, 0, 90, 70)


def pose_hang_loose(armature, side):
    """Hang loose pose"""
    set_finger_rotation(armature, side, "Thumb", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Index", 80, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Middle", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Ring", 80, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Pinky", 0, 0, 0, 0, 0)


def pose_hold_cup(armature, side):
    """Hold cup pose"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 25, 35, -15, 20, 15)
    else:
        set_finger_rotation(armature, side, "Thumb", 25, -35, -15, 20, 15)
    set_finger_rotation(armature, side, "Index", 10, 10, 0, 60, 40)
    set_finger_rotation(armature, side, "Middle", 18, 0, 0, 60, 40)
    set_finger_rotation(armature, side, "Ring", 20, 0, 0, 60, 40)
    set_finger_rotation(armature, side, "Pinky", 20, 0, 0, 60, 40)


def pose_hold_phone(armature, side):
    """Hold phone pose"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 5, 35, -20, 0, 0)
    else:
        set_finger_rotation(armature, side, "Thumb", 5, -35, -20, 0, 0)
    set_finger_rotation(armature, side, "Index", 40, -5, 5, 30, 15)
    set_finger_rotation(armature, side, "Middle", 45, 0, 5, 35, 20)
    set_finger_rotation(armature, side, "Ring", 50, 5, 0, 40, 25)
    set_finger_rotation(armature, side, "Pinky", 60, 15, -10, 50, 35)


def pose_fuck_you(armature, side):
    """Fuck you pose (middle finger)"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 40, 40, -10, 80, 50)
        set_finger_rotation(armature, side, "Index", 90, 0, 0, 90, 70)
        set_finger_rotation(armature, side, "Middle", 0, 0, 0, 0, 0)
        set_finger_rotation(armature, side, "Ring", 90, 0, 0, 90, 70)
        set_finger_rotation(armature, side, "Pinky", 90, 0, 0, 90, 70)
    else:
        set_finger_rotation(armature, side, "Thumb", 40, -40, -10, 80, 50)
        set_finger_rotation(armature, side, "Index", 90, 0, 0, 90, 70)
        set_finger_rotation(armature, side, "Middle", 0, 0, 0, 0, 0)
        set_finger_rotation(armature, side, "Ring", 90, 0, 0, 90, 70)
        set_finger_rotation(armature, side, "Pinky", 90, 0, 0, 90, 70)


def pose_number_1(armature, side):
    """Number 1 gesture"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 40, 40, -10, 80, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 40, -40, -10, 80, 50)
    set_finger_rotation(armature, side, "Index", 0, 0, 0, 0, 0)
    for finger in ["Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 90, 0, 0, 90, 70)


def pose_number_2(armature, side):
    """Number 2 gesture"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 40, 40, -10, 80, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 40, -40, -10, 80, 50)
    set_finger_rotation(armature, side, "Index", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Middle", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Ring", 90, 0, 0, 90, 70)
    set_finger_rotation(armature, side, "Pinky", 90, 0, 0, 90, 70)


def pose_number_3(armature, side):
    """Number 3 gesture"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 40, 40, -10, 80, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 40, -40, -10, 80, 50)
    set_finger_rotation(armature, side, "Index", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Middle", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Ring", 0, 0, 0, 0, 0)
    set_finger_rotation(armature, side, "Pinky", 90, 0, 0, 90, 70)


def pose_number_4(armature, side):
    """Number 4 gesture"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 50, 30, -15, 80, 50)
    else:
        set_finger_rotation(armature, side, "Thumb", 50, -30, -15, 80, 50)
    for finger in ["Index", "Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 0, 0, 0, 0, 0)


def pose_number_5(armature, side):
    """Number 5 gesture"""
    if side == 'Left':
        set_finger_rotation(armature, side, "Thumb", 0, 35, -25, 0, 0)
    else:
        set_finger_rotation(armature, side, "Thumb", 0, -35, -25, 0, 0)
    for finger in ["Index", "Middle", "Ring", "Pinky"]:
        set_finger_rotation(armature, side, finger, 0, 0, 0, 0, 0)


# ============================================
# POSES DICTIONARY
# ============================================

POSES_DICT = {
    "reset": ("Reset", pose_reset),
    "relaxed": ("Relaxed", pose_relaxed),
    "closed": ("Closed", pose_closed),
    "point": ("Point", pose_point),
    "shoot": ("Shoot", pose_shoot),
    "gun": ("Gun", pose_gun),
    "rock": ("Rock", pose_rock),
    "ok": ("OK", pose_ok),
    "peace": ("Peace", pose_peace),
    "hold": ("Hold", pose_hold),
    "like": ("Like", pose_like),
    "hang_loose": ("Hang Loose", pose_hang_loose),
    "hold_cup": ("Hold Cup", pose_hold_cup),
    "hold_phone": ("Hold Phone", pose_hold_phone),
    "fuck_you": ("Fuck You", pose_fuck_you),
    "number_1": ("Number 1", pose_number_1),
    "number_2": ("Number 2", pose_number_2),
    "number_3": ("Number 3", pose_number_3),
    "number_4": ("Number 4", pose_number_4),
    "number_5": ("Number 5", pose_number_5),
}


# ============================================
# ARMATURE CHECK FUNCTIONS
# ============================================

def check_armature_ready(self, armature):
    """Check if armature is ready for use"""
    if not armature:
        self.report({'ERROR'}, "No armature selected!")
        return False
    
    if armature.hide_viewport or armature.hide_get():
        self.report({'ERROR'}, f"Armature '{armature.name}' is HIDDEN!")
        return False
    
    return True


def safe_mode_set(self, armature, mode):
    """Safely change mode with error message"""
    if not check_armature_ready(self, armature):
        return False
    
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    
    try:
        bpy.ops.object.mode_set(mode=mode)
        return True
    except RuntimeError:
        self.report({'ERROR'}, f"Unable to enter {mode} mode.")
        return False


# ============================================
# SELECTION OPERATORS
# ============================================

class HAND_POSE_OT_select_left(bpy.types.Operator):
    bl_idname = "hand_pose.select_left"
    bl_label = "LEFT"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.hand_pose_props
        props.hand_side = 'Left'
        self.report({'INFO'}, "Left hand selected")
        return {'FINISHED'}


class HAND_POSE_OT_select_right(bpy.types.Operator):
    bl_idname = "hand_pose.select_right"
    bl_label = "RIGHT"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.hand_pose_props
        props.hand_side = 'Right'
        self.report({'INFO'}, "Right hand selected")
        return {'FINISHED'}


# ============================================
# WRIST ROTATION OPERATORS
# ============================================

class HAND_POSE_OT_rotate_hand_left(bpy.types.Operator):
    bl_idname = "hand_pose.rotate_hand_left"
    bl_label = "-5° ←"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_hand_bone(armature, props.hand_side)
        if bone:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler.z -= radians(5)
        return {'FINISHED'}


class HAND_POSE_OT_rotate_hand_right(bpy.types.Operator):
    bl_idname = "hand_pose.rotate_hand_right"
    bl_label = "+5° →"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_hand_bone(armature, props.hand_side)
        if bone:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler.z += radians(5)
        return {'FINISHED'}


class HAND_POSE_OT_rotate_hand_up(bpy.types.Operator):
    bl_idname = "hand_pose.rotate_hand_up"
    bl_label = "↑ +5°"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_hand_bone(armature, props.hand_side)

        if bone:
            bone.rotation_mode = 'XYZ'
            if props.hand_side == 'Right':
                bone.rotation_euler.x -= radians(5)
            else:
                bone.rotation_euler.x += radians(5)
        return {'FINISHED'}


class HAND_POSE_OT_rotate_hand_down(bpy.types.Operator):
    bl_idname = "hand_pose.rotate_hand_down"
    bl_label = "↓ -5°"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_hand_bone(armature, props.hand_side)

        if bone:
            bone.rotation_mode = 'XYZ'
            if props.hand_side == 'Right':
                bone.rotation_euler.x += radians(5)
            else:
                bone.rotation_euler.x -= radians(5)
        return {'FINISHED'}


class HAND_POSE_OT_rotate_hand_roll_left(bpy.types.Operator):
    bl_idname = "hand_pose.rotate_hand_roll_left"
    bl_label = "↺ -5°"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_hand_bone(armature, props.hand_side)
        if bone:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler.y -= radians(5)
        return {'FINISHED'}


class HAND_POSE_OT_rotate_hand_roll_right(bpy.types.Operator):
    bl_idname = "hand_pose.rotate_hand_roll_right"
    bl_label = "↻ +5°"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_hand_bone(armature, props.hand_side)
        if bone:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler.y += radians(5)
        return {'FINISHED'}


# ============================================
# THUMB CONTROL OPERATORS
# ============================================

class HAND_POSE_OT_thumb_bone_rotate(bpy.types.Operator):
    bl_idname = "hand_pose.thumb_bone_rotate"
    bl_label = "Rotate Thumb Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    bone_index: bpy.props.IntProperty(default=2)
    axis: bpy.props.StringProperty(default="x")
    direction: bpy.props.FloatProperty(default=5)
    
    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_finger_bone(armature, props.hand_side, "Thumb", self.bone_index)
        if bone:
            bone.rotation_mode = 'XYZ'
            if self.axis == "x":
                bone.rotation_euler.x += radians(self.direction)
            elif self.axis == "y":
                bone.rotation_euler.y += radians(self.direction)
            elif self.axis == "z":
                bone.rotation_euler.z += radians(self.direction)
        
        return {'FINISHED'}


class HAND_POSE_OT_thumb_bone_reset(bpy.types.Operator):
    bl_idname = "hand_pose.thumb_bone_reset"
    bl_label = "Reset Thumb Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    bone_index: bpy.props.IntProperty(default=2)
    
    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        bone = get_finger_bone(armature, props.hand_side, "Thumb", self.bone_index)
        if bone:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler.x = 0
            bone.rotation_euler.y = 0
            bone.rotation_euler.z = 0
        
        return {'FINISHED'}


class HAND_POSE_OT_thumb_reset_all(bpy.types.Operator):
    bl_idname = "hand_pose.thumb_reset_all"
    bl_label = "Reset All Thumb"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}
        
        for i in range(1, 4):
            bone = get_finger_bone(armature, props.hand_side, "Thumb", i)
            if bone:
                bone.rotation_mode = 'XYZ'
                bone.rotation_euler.x = 0
                bone.rotation_euler.y = 0
                bone.rotation_euler.z = 0
        
        return {'FINISHED'}


# ============================================
# ACTION OPERATORS
# ============================================

class HAND_POSE_OT_apply_pose(bpy.types.Operator):
    bl_idname = "hand_pose.apply_pose"
    bl_label = "APPLY POSE"
    bl_options = {'REGISTER', 'UNDO'}

    pose_name: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}

        if self.pose_name in POSES_DICT:
            POSES_DICT[self.pose_name][1](armature, props.hand_side)
            self.report({'INFO'}, f"Pose '{POSES_DICT[self.pose_name][0]}' applied")

        return {'FINISHED'}


class HAND_POSE_OT_insert_keyframe(bpy.types.Operator):
    bl_idname = "hand_pose.insert_keyframe"
    bl_label = "INSERT KEYFRAME"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}

        side = props.hand_side
        fingers = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        
        count = 0
        
        for finger in fingers:
            for i in range(1, 4):
                bone = get_finger_bone(armature, side, finger, i)
                if bone:
                    bone.keyframe_insert("rotation_euler", index=-1)
                    count += 1

        hand_bone = get_hand_bone(armature, side)
        if hand_bone:
            hand_bone.keyframe_insert("rotation_euler", index=-1)
            count += 1

        self.report({'INFO'}, f"Keyframes inserted on {count} bones")
        return {'FINISHED'}


class HAND_POSE_OT_mirror_pose(bpy.types.Operator):
    bl_idname = "hand_pose.mirror_pose"
    bl_label = "MIRROR POSE"
    bl_options = {'REGISTER', 'UNDO'}

    def get_rotation_from_bone(self, armature, side, finger, index):
        bone = get_finger_bone(armature, side, finger, index)
        if bone:
            return bone.rotation_euler.copy()
        return None

    def set_rotation_to_bone(self, armature, side, finger, index, rot):
        bone = get_finger_bone(armature, side, finger, index)
        if bone:
            bone.rotation_euler = rot
            bone.rotation_mode = 'XYZ'

    def execute(self, context):
        props = context.scene.hand_pose_props
        armature = props.armature_object
        
        if not check_armature_ready(self, armature):
            return {'CANCELLED'}
        
        if not safe_mode_set(self, armature, 'POSE'):
            return {'CANCELLED'}

        source = props.hand_side
        target = "Right" if source == "Left" else "Left"

        fingers = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

        for finger in fingers:
            for i in range(1, 4):
                rot = self.get_rotation_from_bone(armature, source, finger, i)
                if rot:
                    if finger == "Thumb":
                        mirrored_rot = (rot.x, -rot.y, rot.z)
                    else:
                        mirrored_rot = (rot.x, -rot.y, -rot.z)
                    self.set_rotation_to_bone(armature, target, finger, i, mirrored_rot)

        hand_source = get_hand_bone(armature, source)
        hand_target = get_hand_bone(armature, target)

        if hand_source and hand_target:
            rot = hand_source.rotation_euler
            hand_target.rotation_euler = (rot.x, -rot.y, -rot.z)
            hand_target.rotation_mode = 'XYZ'

        self.report({'INFO'}, f"Pose mirrored: {source} → {target}")
        bpy.context.view_layer.update()
        return {'FINISHED'}


# ============================================
# PROPERTIES
# ============================================

def update_armature(self, context):
    """When selecting an armature, ensure Object Mode"""
    if not context or not hasattr(context, 'scene') or context.scene is None:
        return
    if self.armature_object:
        if bpy.context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except RuntimeError:
                pass


class HandPoseProperties(bpy.types.PropertyGroup):
    armature_object: bpy.props.PointerProperty(
        name="Armature",
        type=bpy.types.Object,
        poll=lambda self, obj: obj and obj.type == 'ARMATURE',
        update=update_armature
    )
    hand_side: bpy.props.EnumProperty(
        name="Hand",
        items=[('Left', "Left", ""), ('Right', "Right", "")],
        default='Left'
    )
    pose_type: bpy.props.EnumProperty(
        name="Pose",
        items=[(key, value[0], "") for key, value in POSES_DICT.items()],
        default='relaxed'
    )
    closure: bpy.props.FloatProperty(
        name="CLOSURE",
        description="0% = Open hand | 100% = Closed fist",
        default=0,
        min=0,
        max=100,
        step=1,
        subtype='PERCENTAGE',
        update=lambda self, ctx: update_closure(ctx, self)
    )
    thumb_bone_selection: bpy.props.EnumProperty(
        name="Thumb Bone",
        description="Select which thumb bone to control",
        items=[
            ('1', "Bone 1 (Base)", "First thumb bone (closest to wrist)"),
            ('2', "Bone 2 (Middle)", "Middle thumb bone"),
            ('3', "Bone 3 (Tip)", "Tip thumb bone (closest to nail)")
        ],
        default='2'
    )


def update_closure(context, props):
    """Update hand closure when slider changes"""
    if not context or not hasattr(context, 'scene') or context.scene is None:
        return

    armature = props.armature_object
    
    if not armature:
        print("Hand Pose: No armature selected")
        return
    
    if armature.hide_viewport or armature.hide_get():
        print(f"Hand Pose: Armature '{armature.name}' is HIDDEN")
        return

    previous_mode = bpy.context.mode
    if previous_mode != 'POSE':
        try:
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
        except RuntimeError as e:
            print(f"Hand Pose: Error entering Pose Mode - {e}")
            return

    apply_closure(armature, props.hand_side, props.closure)

    if previous_mode != 'POSE' and previous_mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode=previous_mode)
        except RuntimeError:
            pass


# ============================================
# MAIN PANEL
# ============================================

class HAND_POSE_PT_main_panel(bpy.types.Panel):
    bl_label = "Mx Hand Pose V6.1"
    bl_idname = "HAND_POSE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mx Hand Pose"

    def draw(self, context):
        layout = self.layout
        props = context.scene.hand_pose_props

        # Armature selector
        box = layout.box()
        box.label(text="Armature:", icon='ARMATURE_DATA')
        box.prop(props, "armature_object", text="")

        if props.armature_object and (props.armature_object.hide_viewport or props.armature_object.hide_get()):
            box = layout.box()
            box.label(text="ARMATURE IS HIDDEN!", icon='ERROR')

        # Hand selector
        box = layout.box()
        box.label(text="Hand:", icon='HAND')
        row = box.row(align=True)
        row.operator("hand_pose.select_left", text="LEFT", icon='TRIA_LEFT')
        row.operator("hand_pose.select_right", text="RIGHT", icon='TRIA_RIGHT')

        # Main control - Closure
        box = layout.box()
        box.label(text="Main Control:", icon='MODIFIER')
        
        if props.armature_object and (props.armature_object.hide_viewport or props.armature_object.hide_get()):
            box.label(text="Unhide armature to use slider", icon='ERROR')
        else:
            box.prop(props, "closure", slider=True)

        # Thumb control section
        box = layout.box()
        box.label(text="Thumb Control:", icon='BONE_DATA')
        
        box.prop(props, "thumb_bone_selection", text="")
        
        bone_idx = int(props.thumb_bone_selection)
        
        col = box.column(align=True)
        
        row = col.row(align=True)
        op = row.operator("hand_pose.thumb_bone_rotate", text="X+")
        op.bone_index = bone_idx
        op.axis = "x"
        op.direction = 5
        
        op = row.operator("hand_pose.thumb_bone_rotate", text="X-")
        op.bone_index = bone_idx
        op.axis = "x"
        op.direction = -5
        
        row = col.row(align=True)
        op = row.operator("hand_pose.thumb_bone_rotate", text="Y+")
        op.bone_index = bone_idx
        op.axis = "y"
        op.direction = 5
        
        op = row.operator("hand_pose.thumb_bone_rotate", text="Y-")
        op.bone_index = bone_idx
        op.axis = "y"
        op.direction = -5
        
        row = col.row(align=True)
        op = row.operator("hand_pose.thumb_bone_rotate", text="Z+")
        op.bone_index = bone_idx
        op.axis = "z"
        op.direction = 5
        
        op = row.operator("hand_pose.thumb_bone_rotate", text="Z-")
        op.bone_index = bone_idx
        op.axis = "z"
        op.direction = -5
        
        row = col.row(align=True)
        op = row.operator("hand_pose.thumb_bone_reset", text=f"Reset Bone {bone_idx}")
        op.bone_index = bone_idx
        row.operator("hand_pose.thumb_reset_all", text="Reset All")

        # Special poses
        box = layout.box()
        box.label(text="Special Poses:", icon='POSE_HLT')
        box.prop(props, "pose_type", text="")
        op = box.operator("hand_pose.apply_pose", icon='CHECKMARK', text="APPLY POSE")
        op.pose_name = props.pose_type

        # Wrist rotation
        box = layout.box()
        box.label(text="Wrist Rotation:", icon='ARROW_LEFTRIGHT')

        row = box.row(align=True)
        row.operator("hand_pose.rotate_hand_left", icon='TRIA_LEFT')
        row.operator("hand_pose.rotate_hand_right", icon='TRIA_RIGHT')

        row = box.row(align=True)
        row.operator("hand_pose.rotate_hand_down", icon='TRIA_DOWN')
        row.operator("hand_pose.rotate_hand_up", icon='TRIA_UP')

        row = box.row(align=True)
        row.operator("hand_pose.rotate_hand_roll_left", icon='LOOP_BACK')
        row.operator("hand_pose.rotate_hand_roll_right", icon='LOOP_FORWARDS')

        # Actions
        box = layout.box()
        box.label(text="Actions:", icon='TOOL_SETTINGS')
        box.operator("hand_pose.insert_keyframe", icon='KEYFRAME')
        box.operator("hand_pose.mirror_pose", icon='ARROW_LEFTRIGHT')


# ============================================
# REGISTRATION
# ============================================

classes = [
    HandPoseProperties,
    HAND_POSE_OT_select_left,
    HAND_POSE_OT_select_right,
    HAND_POSE_OT_rotate_hand_left,
    HAND_POSE_OT_rotate_hand_right,
    HAND_POSE_OT_rotate_hand_up,
    HAND_POSE_OT_rotate_hand_down,
    HAND_POSE_OT_rotate_hand_roll_left,
    HAND_POSE_OT_rotate_hand_roll_right,
    HAND_POSE_OT_thumb_bone_rotate,
    HAND_POSE_OT_thumb_bone_reset,
    HAND_POSE_OT_thumb_reset_all,
    HAND_POSE_OT_apply_pose,
    HAND_POSE_OT_insert_keyframe,
    HAND_POSE_OT_mirror_pose,
    HAND_POSE_PT_main_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hand_pose_props = bpy.props.PointerProperty(type=HandPoseProperties)
    print("Mx Hand Pose V6.1: Registered successfully")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, 'hand_pose_props'):
        del bpy.types.Scene.hand_pose_props
    print("Mx Hand Pose V6.1: Unregistered successfully")

if __name__ == "__main__":
    register()