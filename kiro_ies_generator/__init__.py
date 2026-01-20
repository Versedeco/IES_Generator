"""
Kiro IES Generator - Blender 插件入口

这是一个 Blender Python 插件，用于从灯具场景生成符合 IESNA LM-63 标准的 IES 光度学文件。
插件利用 Cycles 物理渲染引擎进行球面采样，测量光强分布。

作者：Kiro Team
版本：1.0.0
Blender 版本：3.6+, 4.x

依赖项：
- bpy (Blender Python API) - 内置
- numpy - 内置于 Blender 3.6+
- math - Python 标准库
"""

# ============================================================================
# 插件元数据
# ============================================================================

bl_info = {
    "name": "Kiro IES Generator",
    "author": "Kiro Team",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > IES Generator",
    "description": "从 Blender 场景生成 IESNA LM-63 标准的 IES 光度学文件。支持 Cycles 物理渲染，模拟半透明材质的光学特性",
    "warning": "需要 Cycles 渲染引擎。推荐使用 GPU 渲染以获得最佳性能",
    "doc_url": "https://github.com/kiro-team/kiro-ies-generator",
    "support": "COMMUNITY",
    "category": "Lighting",
}

# ============================================================================
# 依赖项检查
# ============================================================================

def check_dependencies():
    """
    检查必需的依赖项是否可用
    
    返回:
        tuple: (is_valid, missing_deps, warnings)
            - is_valid: bool, 所有必需依赖是否可用
            - missing_deps: list, 缺失的依赖项列表
            - warnings: list, 警告信息列表
    """
    missing_deps = []
    warnings = []
    
    # 检查 bpy (Blender Python API)
    try:
        import bpy
    except ImportError:
        missing_deps.append("bpy (Blender Python API)")
    
    # 检查 numpy
    try:
        import numpy
        # 检查 numpy 版本
        numpy_version = tuple(map(int, numpy.__version__.split('.')[:2]))
        if numpy_version < (1, 20):
            warnings.append(f"NumPy 版本过低 ({numpy.__version__})，推荐 1.20+")
    except ImportError:
        missing_deps.append("numpy")
    
    # 检查 math (Python 标准库，应该总是可用)
    try:
        import math
    except ImportError:
        missing_deps.append("math (Python 标准库)")
    
    # 检查 Blender 版本
    try:
        import bpy
        blender_version = bpy.app.version
        if blender_version < (3, 6, 0):
            warnings.append(
                f"Blender 版本 {blender_version[0]}.{blender_version[1]}.{blender_version[2]} "
                f"低于推荐版本 3.6.0，部分功能可能不可用"
            )
    except:
        pass
    
    is_valid = len(missing_deps) == 0
    return is_valid, missing_deps, warnings


# 执行依赖项检查
DEPENDENCIES_OK, MISSING_DEPENDENCIES, DEPENDENCY_WARNINGS = check_dependencies()

if not DEPENDENCIES_OK:
    print("=" * 60)
    print("Kiro IES Generator - 依赖项检查失败")
    print("=" * 60)
    print("缺失的依赖项：")
    for dep in MISSING_DEPENDENCIES:
        print(f"  - {dep}")
    print("\n请确保在 Blender 3.6+ 环境中运行此插件")
    print("=" * 60)

if DEPENDENCY_WARNINGS:
    print("Kiro IES Generator - 依赖项警告：")
    for warning in DEPENDENCY_WARNINGS:
        print(f"  ⚠ {warning}")

# ============================================================================
# Blender API 导入
# ============================================================================

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

# ============================================================================
# 模块导入配置
# ============================================================================

# 导入 Python 标准库
import sys
import os
from pathlib import Path

# 确保插件目录在 Python 路径中
# 这对于 Blender 插件开发很重要，确保相对导入正常工作
addon_dir = Path(__file__).parent
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))

# 导入核心模块
# 使用 try-except 确保插件在模块未完全实现时也能加载
try:
    from . import scene_validator
    from . import sampler
    from . import ies_generator
    from . import output_manager
    
    # 标记核心模块已成功导入
    CORE_MODULES_AVAILABLE = True
    print("Kiro IES Generator: 核心模块已成功导入")
    
except ImportError as e:
    CORE_MODULES_AVAILABLE = False
    print(f"Kiro IES Generator 警告：无法导入核心模块 - {e}")
    print("插件将以有限功能运行，部分功能可能不可用")
    print("请确保所有模块文件都已正确放置在插件目录中")
    
    # 创建占位符模块，避免后续代码出错
    scene_validator = None
    sampler = None
    ies_generator = None
    output_manager = None


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
        
        # 检查核心模块是否可用
        if not CORE_MODULES_AVAILABLE:
            self.report({'ERROR'}, "核心模块未加载，无法执行 IES 生成")
            self.report({'ERROR'}, "请检查插件安装是否完整")
            return {'CANCELLED'}
        
        # 检查依赖项
        if not DEPENDENCIES_OK:
            self.report({'ERROR'}, "依赖项检查失败")
            for dep in MISSING_DEPENDENCIES:
                self.report({'ERROR'}, f"缺失依赖: {dep}")
            return {'CANCELLED'}
        
        # 验证场景
        self.report({'INFO'}, "开始场景验证...")
        
        # TODO: 调用 scene_validator.validate_scene()
        # 这将在后续任务中实现
        
        # 临时占位符逻辑
        self.report({'WARNING'}, "核心功能尚未实现，这是占位符执行")
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
        
        # 检查核心模块是否可用
        if not CORE_MODULES_AVAILABLE:
            self.report({'ERROR'}, "核心模块未加载，无法执行场景验证")
            return {'CANCELLED'}
        
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
        
        # 显示依赖项状态（如果有问题）
        if not DEPENDENCIES_OK or not CORE_MODULES_AVAILABLE:
            box = layout.box()
            box.alert = True
            box.label(text="插件状态异常", icon='ERROR')
            
            if not DEPENDENCIES_OK:
                box.label(text="缺失依赖项：", icon='CANCEL')
                for dep in MISSING_DEPENDENCIES:
                    box.label(text=f"  • {dep}")
            
            if not CORE_MODULES_AVAILABLE:
                box.label(text="核心模块未加载", icon='CANCEL')
                box.label(text="请检查插件安装")
            
            layout.separator()
        
        # 显示依赖项警告
        if DEPENDENCY_WARNINGS:
            box = layout.box()
            box.label(text="警告", icon='ERROR')
            for warning in DEPENDENCY_WARNINGS:
                row = box.row()
                row.label(text=warning, icon='INFO')
            layout.separator()
        
        # 场景验证部分
        box = layout.box()
        box.label(text="场景验证", icon='CHECKMARK')
        row = box.row()
        row.enabled = CORE_MODULES_AVAILABLE
        row.operator("kiro.validate_scene", text="验证场景")
        
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
        
        # 如果核心模块或依赖项不可用，禁用按钮
        if not CORE_MODULES_AVAILABLE or not DEPENDENCIES_OK:
            row.enabled = False
            row.operator("kiro.generate_ies", text="无法生成（缺少依赖）", icon='CANCEL')
        elif props.is_running:
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
    # 检查依赖项
    if not DEPENDENCIES_OK:
        print("=" * 60)
        print("Kiro IES Generator - 注册失败")
        print("=" * 60)
        print("缺失的依赖项：")
        for dep in MISSING_DEPENDENCIES:
            print(f"  - {dep}")
        print("\n插件将不会注册。请在 Blender 3.6+ 环境中运行")
        print("=" * 60)
        return
    
    # 注册所有类
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"注册类 {cls.__name__} 失败: {e}")
            # 继续注册其他类
    
    # 将属性组添加到场景
    bpy.types.Scene.kiro_ies_props = PointerProperty(type=KiroIESProperties)
    
    print("=" * 60)
    print("Kiro IES Generator 插件已注册")
    print(f"版本: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}")
    print(f"核心模块状态: {'✓ 已加载' if CORE_MODULES_AVAILABLE else '✗ 未加载'}")
    print(f"依赖项状态: {'✓ 正常' if DEPENDENCIES_OK else '✗ 异常'}")
    
    if DEPENDENCY_WARNINGS:
        print("\n警告：")
        for warning in DEPENDENCY_WARNINGS:
            print(f"  ⚠ {warning}")
    
    print("=" * 60)


def unregister():
    """注销插件"""
    # 删除场景属性
    if hasattr(bpy.types.Scene, 'kiro_ies_props'):
        del bpy.types.Scene.kiro_ies_props
    
    # 注销所有类（逆序）
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"注销类 {cls.__name__} 失败: {e}")
            # 继续注销其他类
    
    print("Kiro IES Generator 插件已注销")


# 用于在 Blender 文本编辑器中直接运行
if __name__ == "__main__":
    register()
