bl_info = {
    "name" : "Blaze Cutscene",
    "author" : "TΞTRΛ_SKY",
    "version" : (1, 0, 0),
    "blender" : (4, 4, 3),
    "description" : "Complementary addon for Blaze's custom rig"
}

import bpy
from collections import defaultdict

rig_id = "blaze"

def is_limb_selected(rig, bone_names):
    if rig and rig.type == 'ARMATURE':
        selected_bones = [bone.name for bone in rig.data.bones if bone.select]
        return any(bone_name in selected_bones for bone_name in bone_names)
    return False

def is_limb_selected(context, bone_names):
    """Vérifie si un des bones de la liste est sélectionné dans le mode pose"""
    selected_names = [bone.name for bone in context.selected_pose_bones]
    return any(bone_name in selected_names for bone_name in bone_names)

class RigMainPropertiesPanel(bpy.types.Panel):
    bl_label = "Rig Properties"
    bl_idname = "OBJECT_PT_BLAZE_CUTSCENE" + rig_id
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    @classmethod
    def poll(self, context):
        if context.mode != 'POSE':
            return False
        try:
            rig = context.active_object
            if not rig or rig.type != 'ARMATURE' or rig.get("rig_id") != rig_id:
                return False
            
            selected_names = [bone.name for bone in context.selected_pose_bones]
            relevant_bones = [
                "Parent_Arm_L", "IK_Shoulder_L", "IK_Wrist_L",
                "Parent_Arm_R", "IK_Shoulder_R", "IK_Wrist_R",
                "Parent_Thigh_L", "IK_Thigh_L", "FootCTRL_L",
                "Parent_Thigh_R", "IK_Thigh_R", "FootCTRL_R",
                "EyesCTRLMaster", "MouthCTRLMaster", "QuillsCTRLMaster"
            ]
            
            return any(bone_name in selected_names for bone_name in relevant_bones)
        except:
            return False

    def draw(self, context):
        layout = self.layout
        rig = context.active_object

        def is_selected_in_context(bone_names):
            selected_names = [bone.name for bone in context.selected_pose_bones]
            return any(name in selected_names for name in bone_names)

        # LEFT ARM
        left_arm_bones = ["Parent_Arm_L", "IK_Shoulder_L", "IK_Wrist_L"]
        if is_selected_in_context(left_arm_bones):
            self.draw_limb_properties(layout, context, "left_arm", "IK_ArmSwitch_L", "Parent_Arm_L")

        # RIGHT ARM
        right_arm_bones = ["Parent_Arm_R", "IK_Shoulder_R", "IK_Wrist_R"]
        if is_selected_in_context(right_arm_bones):
            self.draw_limb_properties(layout, context, "right_arm", "IK_ArmSwitch_R", "Parent_Arm_R")

        # LEFT LEG
        left_leg_bones = ["Parent_Thigh_L", "IK_Thigh_L", "FootCTRL_L"]
        if is_selected_in_context(left_leg_bones):
            self.draw_limb_properties(layout, context, "left_leg", "IK_LegSwitch_L", "Parent_Thigh_L")

        # RIGHT LEG
        right_leg_bones = ["Parent_Thigh_R", "IK_Thigh_R", "FootCTRL_R"]
        if is_selected_in_context(right_leg_bones):
            self.draw_limb_properties(layout, context, "right_leg", "IK_LegSwitch_R", "Parent_Thigh_R")

        # EYES
        if is_selected_in_context(["EyesCTRLMaster"]):
            self.draw_limit_distance_property(layout, rig, "EyesCTRLMaster")
            
        # MOUTH
        if is_selected_in_context(["MouthCTRLMaster"]):
            self.draw_limit_distance_property(layout, rig, "MouthCTRLMaster")

        # QUILLS
        if is_selected_in_context(["QuillsCTRLMaster"]):
            self.draw_limit_distance_property(layout, rig, "QuillsCTRLMaster")
            self.draw_quills_properties(layout, rig, "QuillsCTRLMaster")
            
        if len(layout._layout.column()._column.children) == 0:
            layout.label(text="Select a control bone to see properties")

    def draw_limb_properties(self, layout, context, limb_prefix, switch_bone_name, parent_bone_name):
        rig = context.active_object
        
        row = layout.row()
        row.operator(f"rig.{limb_prefix}_fk_to_ik_snap", text="FK -> IK Snap", icon='SNAP_ON')
        row.operator(f"rig.{limb_prefix}_ik_to_fk_snap", text="IK -> FK Snap", icon='SNAP_ON')

        switch_bone = rig.pose.bones.get(switch_bone_name)
        if switch_bone:
            row = layout.row()
            switch_prop = switch_bone.get("IK_Switch")
            if switch_prop is not None:
                switch_label = "Switch -> FK" if switch_prop else "Switch -> IK"
                row.prop(switch_bone, '["IK_Switch"]', toggle=True, text=switch_label)
            else:
                row.label(text="IK_Switch property not found!")
        else:
            row.label(text=f"{switch_bone_name} bone not found!")

    def draw_limit_distance_property(self, layout, rig, bone_name):
        bone = rig.pose.bones.get(bone_name)
        if bone:
            limit_distance_constraint = next(
                (constraint for constraint in bone.constraints if constraint.type == "LIMIT_DISTANCE"),
                None
            )
            if limit_distance_constraint:
                row = layout.row()
                row.prop(limit_distance_constraint, 'influence', slider=True, text=f"{bone_name} Limit Distance")
            else:
                layout.label(text=f"No Limit Distance constraint found on {bone_name}.")
        else:
            layout.label(text=f"{bone_name} bone not found!")

    def draw_quills_properties(self, layout, rig, bone_name):
        bone = rig.pose.bones.get(bone_name)
        if bone:
            follow_prop = bone.get("Q - Follow")
            if follow_prop is not None:
                row = layout.row()
                row.prop(bone, '["Q - Follow"]', text="Q - Follow", toggle=True, icon='SNAP_ON')
            else:
                layout.label(text="Q - Follow property not found!")
        else:
            layout.label(text=f"{bone_name} bone not found!")

class RigLayersPanel(bpy.types.Panel):
    bl_label = "Rig Layers"
    bl_idname = "OBJECT_PT_RIG_LAYERS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    
    @classmethod
    def poll(self, context):
        if context.mode != 'POSE':
            return False
        try:
            rig = context.active_object
            return (rig and rig.get("rig_id") == rig_id)
        except:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj and obj.type == 'ARMATURE':
            collections = obj.data.collections

            row_table = defaultdict(list)
            for coll in collections:
                row_id = coll.get('rigify_ui_row', 0)
                if row_id > 0:
                    row_table[row_id].append(coll)

            for row_id in range(min(row_table.keys()), 1 + max(row_table.keys())):
                row = layout.row()
                row_buttons = row_table[row_id]
                if row_buttons:
                    for coll in row_buttons:
                        row2 = row.row()
                        row2.active = coll.is_visible_ancestors
                        row2.prop(coll, 'is_visible', toggle=True, text=coll.name, translate=False)
                else:
                    row.separator()
            
##############
## LEFT ARM ##
##############

class LeftArmFKtoIKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.left_arm_fk_to_ik_snap"
    bl_label = "Left Arm FK to IK Snap"
    bl_description = "Aligns FK to IK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones
        
        fk_shoulder = bones.get("Shoulder_L")
        fk_forearm = bones.get("Forearm_L")
        fk_hand = bones.get("Hand_L")
        ik_shoulder = bones.get("IK_Shoulder_L")
        ik_forearm = bones.get("IK_Forearm_L")
        ik_hand = bones.get("IK_Hand_L")

        if all([fk_shoulder, fk_forearm, fk_hand, ik_shoulder, ik_forearm, ik_hand]):
            for _ in range(3):
                fk_shoulder.matrix = ik_shoulder.matrix
                fk_forearm.matrix = ik_forearm.matrix
                fk_hand.matrix = ik_hand.matrix
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        else:
            self.report({'ERROR'}, "Bones not found!")
        return {'FINISHED'}

class LeftArmIKtoFKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.left_arm_ik_to_fk_snap"
    bl_label = "Left Arm IK to FK Snap"
    bl_description = "Aligns IK to FK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones

        ik_ctrl = bones.get("IK_Wrist_L")
        fk_hand = bones.get("Hand_L")

        if not all([ik_ctrl, fk_hand]):
            self.report({'ERROR'}, "Bones not found!")
            return {'CANCELLED'}
        
        ik_ctrl.matrix = fk_hand.matrix
        return {'FINISHED'}

###############
## RIGHT ARM ##
###############

class RightArmFKtoIKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.right_arm_fk_to_ik_snap"
    bl_label = "Right Arm FK to IK Snap"
    bl_description = "Aligns FK to IK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones

        fk_shoulder = bones.get("Shoulder_R")
        fk_forearm = bones.get("Forearm_R")
        fk_hand = bones.get("Hand_R")
        ik_shoulder = bones.get("IK_Shoulder_R")
        ik_forearm = bones.get("IK_Forearm_R")
        ik_hand = bones.get("IK_Hand_R")

        if all([fk_shoulder, fk_forearm, fk_hand, ik_shoulder, ik_forearm, ik_hand]):
            for _ in range(3):
                fk_shoulder.matrix = ik_shoulder.matrix
                fk_forearm.matrix = ik_forearm.matrix
                fk_hand.matrix = ik_hand.matrix
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        else:
            self.report({'ERROR'}, "Bones not found!")
        return {'FINISHED'}

class RightArmIKtoFKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.right_arm_ik_to_fk_snap"
    bl_label = "Right Arm IK to FK Snap"
    bl_description = "Aligns IK to FK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones

        ik_ctrl = bones.get("IK_Wrist_R")
        fk_hand = bones.get("Hand_R")

        if not all([ik_ctrl, fk_hand]):
            self.report({'ERROR'}, "Bones not found!")
            return {'CANCELLED'}
        
        ik_ctrl.matrix = fk_hand.matrix
        return {'FINISHED'}

##############
## LEFT LEG ##
##############

class LeftLegFKtoIKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.left_leg_fk_to_ik_snap"
    bl_label = "Left Leg FK to IK Snap"
    bl_description = "Aligns FK to IK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones

        fk_thigh = bones.get("Thigh_L")
        fk_knee = bones.get("Knee_L")
        fk_foot = bones.get("Foot_L")
        fk_toe = bones.get("Toe_L")
        ik_thigh = bones.get("IK_Thigh_L")
        ik_knee = bones.get("IK_Knee_L")
        ik_foot = bones.get("IK_Foot_L")
        ik_toe = bones.get("IK_Toe_L")

        if all([fk_thigh, fk_knee, fk_foot, fk_toe, ik_thigh, ik_knee, ik_foot, ik_toe]):
            for _ in range(4):
                fk_thigh.matrix = ik_thigh.matrix
                fk_knee.matrix = ik_knee.matrix
                fk_foot.matrix = ik_foot.matrix
                fk_toe.matrix = ik_toe.matrix
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        else:
            self.report({'ERROR'}, "Bones not found!")
        return {'FINISHED'}

class LeftLegIKtoFKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.left_leg_ik_to_fk_snap"
    bl_label = "Left Leg IK to FK Snap"
    bl_description = "Aligns IK to FK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones

        ik_ctrl = bones.get("FootCTRL_L")
        fk_foot = bones.get("Foot_L")
        
        if not all([ik_ctrl, fk_foot]):
            self.report({'ERROR'}, "Bones not found!")
            return {'CANCELLED'}
        
        ik_ctrl.matrix = fk_foot.matrix
        return {'FINISHED'}

###############
## RIGHT LEG ##
###############

class RightLegFKtoIKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.right_leg_fk_to_ik_snap"
    bl_label = "Right Leg FK to IK Snap"
    bl_description = "Aligns FK to IK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones

        fk_thigh = bones.get("Thigh_R")
        fk_knee = bones.get("Knee_R")
        fk_foot = bones.get("Foot_R")
        fk_toe = bones.get("Toe_R")
        ik_thigh = bones.get("IK_Thigh_R")
        ik_knee = bones.get("IK_Knee_R")
        ik_foot = bones.get("IK_Foot_R")
        ik_toe = bones.get("IK_Toe_R")

        if all([fk_thigh, fk_knee, fk_foot, fk_toe, ik_thigh, ik_knee, ik_foot, ik_toe]):
            for _ in range(4):
                fk_thigh.matrix = ik_thigh.matrix
                fk_knee.matrix = ik_knee.matrix
                fk_foot.matrix = ik_foot.matrix
                fk_toe.matrix = ik_toe.matrix
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        else:
            self.report({'ERROR'}, "Bones not found!")
        return {'FINISHED'}

class RightLegIKtoFKSnapOperator(bpy.types.Operator):
    bl_idname = "rig.right_leg_ik_to_fk_snap"
    bl_label = "Right Leg IK to FK Snap"
    bl_description = "Aligns IK to FK on current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.active_object
        bones = rig.pose.bones

        ik_ctrl = bones.get("FootCTRL_R")
        fk_foot = bones.get("Foot_R")
        
        if not all([ik_ctrl, fk_foot]):
            self.report({'ERROR'}, "Bones not found!")
            return {'CANCELLED'}
        
        ik_ctrl.matrix = fk_foot.matrix
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RigMainPropertiesPanel)
    bpy.utils.register_class(RigLayersPanel)
    bpy.utils.register_class(LeftArmFKtoIKSnapOperator)
    bpy.utils.register_class(LeftArmIKtoFKSnapOperator)
    bpy.utils.register_class(RightArmFKtoIKSnapOperator)
    bpy.utils.register_class(RightArmIKtoFKSnapOperator)
    bpy.utils.register_class(LeftLegFKtoIKSnapOperator)
    bpy.utils.register_class(LeftLegIKtoFKSnapOperator)
    bpy.utils.register_class(RightLegFKtoIKSnapOperator)
    bpy.utils.register_class(RightLegIKtoFKSnapOperator)

def unregister():
    bpy.utils.unregister_class(RigMainPropertiesPanel)
    bpy.utils.unregister_class(RigLayersPanel)
    bpy.utils.unregister_class(LeftArmFKtoIKSnapOperator)
    bpy.utils.unregister_class(LeftArmIKtoFKSnapOperator)
    bpy.utils.unregister_class(RightArmFKtoIKSnapOperator)
    bpy.utils.unregister_class(RightArmIKtoFKSnapOperator)
    bpy.utils.unregister_class(LeftLegFKtoIKSnapOperator)
    bpy.utils.unregister_class(LeftLegIKtoFKSnapOperator)
    bpy.utils.unregister_class(RightLegFKtoIKSnapOperator)
    bpy.utils.unregister_class(RightLegIKtoFKSnapOperator)

if __name__ == "__main__":
    register()