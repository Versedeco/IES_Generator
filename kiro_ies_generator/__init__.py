"""
Kiro IES Generator - Blender 插件入口

这是一个 Blender Python 插件，用于从灯具场景生成符合 IESNA LM-63 标准的 IES 光度学文件。
插件利用 Cycles 物理渲染引擎进行球面采样，测量光强分布。

作者：Kiro Team
版本：1.0.0
Blender 版本：3.6+, 4.x
"""

bl_info = {
    "name": "Kiro IES Generator",
    "author": "Kiro Team",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > IES Generator",
    "description": "从 Blender 场景生成 IESNA LM-63 标准的 IES 光度学文件",
    "warning": "",
    "doc_url": "https://github.com/kiro-team/kiro-ies-generator",
    "category": "Lighting",
}

import bpy
from bpy.props import (
    FloatProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
)
from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
    AddonPreferences,
)

# 导入核心模块（将在后续任务中实现）
try:
    from . import scene_validator
    from . import sampler
    from . import ies_generator
    from . import output_manager
except ImportError as e:
    print(f"警告：无法导入核心模块 - {e}")
    print("插件将以有限功能运行")


# ============================================================================
# 属性组：存储插件设置
# ============================================================================

class KiroIESProperties(PropertyGroup):
    """插件属性组，存储用户配置"""
    
    # 采样参数
    angular_interval: FloatProperty(
        name="角度间隔",
        description="球面采样的角度间隔（度）",
        default=10.0,
        min=1.0,
        max=45.0,
        step=100,
        precision=1,
    )
    
    samples: IntProperty(
        name="采样数",
        description="Cycles 渲染采样数",
        default=64,
        min=1,
        max=4096,
    )
    
    distance: FloatProperty(
        name="测量距离",
        description="虚拟传感器距离光源的距离（米）",
        default=5.0,
        min=0.1,
        max=100.0,
        step=10,
        precision=2,
    )
    
    # 光源参数
    lumens: FloatProperty(
        name="总流明",
        description="光源总光通量（流明）",
        default=1800.0,
        min=1.0,
        max=1000000.0,
        step=100,
        precision=1,
    )
    
    # 输出参数
    output_path: StringProperty(
        name="输出路径",
        description="IES 文件输出路径",
        default="",
        subtype='FILE_PATH',
    )
    
    fixture_name: StringProperty(
        name="灯具名称",
        description="灯具名称（用于 IES 文件元数据）",
        default="Kiro Generated Fixture",
        maxlen=128,
    )
    
    # 预设模式
    preset_mode: EnumProperty(
        name="预设模式",
        description="快速选择采样参数预设",
        items=[
            ('CUSTOM', "自定义", "手动配置参数"),
            ('PREVIEW', "预览模式", "快速预览（10°间隔，64采样）"),
            ('PRODUCTION', "生产模式", "高质量输出（5°间隔，256采样）"),
        ],
        default='PREVIEW',
    )
    
    # 运行状态
    is_running: BoolProperty(
        name="运行中",
        description="采样是否正在运行",
        default=False,
    )
    
    progress: FloatProperty(
        name="进度",
        description="当前进度（0-100）",
        default=0.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE',
    )
    
    status_message: StringProperty(
        name="状态消息",
        description="当前状态信息",
        default="就绪",
    )


# ============================================================================
# 操作符：生成 IES 文件
# ============================================================================

class KIRO_OT_GenerateIES(Operator):
    """生成 IES 文件操作符"""
    bl_idname = "kiro.generate_ies"
    bl_label = "生成 IES"
    bl_description = "从当前场景生成 IES 光度学文件"
    bl_options = {'REGISTER', 'UNDO'}
    
    # 用于模态操作的计时器
    _timer = None
    _is_running = False
    
    def execute(self, context):
        """执行 IES 生成"""
        props = context.scene.kiro_ies_props
        
        # 验证场景
        self.report({'INFO'}, "开始场景验证...")
        
        # TODO: 调用 scene_validator.validate_scene()
        # 这将在后续任务中实现
        
        # 临时占位符逻辑
        self.report({'WARNING'}, "核心模块尚未实现，这是占位符执行")
        props.status_message = "等待核心模块实现"
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        """调用操作符（显示文件选择对话框）"""
        props = context.scene.kiro_ies_props
        
        # 如果输出路径为空，打开文件选择对话框
        if not props.output_path:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        
        return self.execute(context)
    
    def modal(self, context, event):
        """模态操作（用于进度更新）"""
        if event.type == 'TIMER':
            # TODO: 更新进度
            pass
        
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def cancel(self, context):
        """取消操作"""
        props = context.scene.kiro_ies_props
        props.is_running = False
        props.status_message = "已取消"
        
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)


# ============================================================================
# 操作符：应用预设
# ============================================================================

class KIRO_OT_ApplyPreset(Operator):
    """应用采样参数预设"""
    bl_idname = "kiro.apply_preset"
    bl_label = "应用预设"
    bl_description = "应用预设的采样参数"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.kiro_ies_props
        
        if props.preset_mode == 'PREVIEW':
            props.angular_interval = 10.0
            props.samples = 64
            props.distance = 5.0
            self.report({'INFO'}, "已应用预览模式预设")
        
        elif props.preset_mode == 'PRODUCTION':
            props.angular_interval = 5.0
            props.samples = 256
            props.distance = 5.0
            self.report({'INFO'}, "已应用生产模式预设")
        
        return {'FINISHED'}


# ============================================================================
# 操作符：验证场景
# ============================================================================

class KIRO_OT_ValidateScene(Operator):
    """验证场景配置"""
    bl_idname = "kiro.validate_scene"
    bl_label = "验证场景"
    bl_description = "检查场景配置是否正确"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """执行场景验证"""
        
        # TODO: 调用 scene_validator.validate_scene()
        # 这将在后续任务中实现
        
        # 临时占位符逻辑
        self.report({'INFO'}, "场景验证功能将在后续任务中实现")
        
        return {'FINISHED'}


# ============================================================================
# 面板：主 UI 面板
# ============================================================================

class KIRO_PT_IESGenerator(Panel):
    """IES Generator 主面板"""
    bl_label = "IES Generator"
    bl_idname = "KIRO_PT_ies_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IES Generator'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.kiro_ies_props
        
        # 场景验证部分
        box = layout.box()
        box.label(text="场景验证", icon='CHECKMARK')
        box.operator("kiro.validate_scene", text="验证场景")
        
        # 采样参数部分
        box = layout.box()
        box.label(text="采样参数", icon='SETTINGS')
        
        # 预设模式
        row = box.row()
        row.prop(props, "preset_mode", text="预设")
        row.operator("kiro.apply_preset", text="", icon='FILE_REFRESH')
        
        # 参数设置
        col = box.column(align=True)
        col.prop(props, "angular_interval")
        col.prop(props, "samples")
        col.prop(props, "distance")
        
        # 显示预计采样点数
        num_theta = int(180 / props.angular_interval) + 1
        num_phi = int(360 / props.angular_interval) + 1
        total_points = num_theta * num_phi
        box.label(text=f"预计采样点数: {total_points}", icon='INFO')
        
        # 光源参数部分
        box = layout.box()
        box.label(text="光源参数", icon='LIGHT')
        box.prop(props, "lumens")
        
        # 输出设置部分
        box = layout.box()
        box.label(text="输出设置", icon='FILE')
        box.prop(props, "fixture_name")
        box.prop(props, "output_path")
        
        # 生成按钮
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.5
        
        if props.is_running:
            row.enabled = False
            row.operator("kiro.generate_ies", text="生成中...", icon='TIME')
        else:
            row.operator("kiro.generate_ies", text="生成 IES", icon='EXPORT')
        
        # 进度显示
        if props.is_running:
            layout.separator()
            box = layout.box()
            box.label(text="进度", icon='TIME')
            box.prop(props, "progress", text="", slider=True)
            box.label(text=props.status_message)
        
        # 状态信息
        if not props.is_running and props.status_message != "就绪":
            layout.separator()
            box = layout.box()
            box.label(text=props.status_message, icon='INFO')


# ============================================================================
# 注册和注销
# ============================================================================

# 要注册的类列表
classes = (
    KiroIESProperties,
    KIRO_OT_GenerateIES,
    KIRO_OT_ApplyPreset,
    KIRO_OT_ValidateScene,
    KIRO_PT_IESGenerator,
)


def register():
    """注册插件"""
    # 注册所有类
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # 将属性组添加到场景
    bpy.types.Scene.kiro_ies_props = PointerProperty(type=KiroIESProperties)
    
    print("Kiro IES Generator 插件已注册")


def unregister():
    """注销插件"""
    # 删除场景属性
    del bpy.types.Scene.kiro_ies_props
    
    # 注销所有类（逆序）
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("Kiro IES Generator 插件已注销")


# 用于在 Blender 文本编辑器中直接运行
if __name__ == "__main__":
    register()
