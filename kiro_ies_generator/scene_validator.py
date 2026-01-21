"""
场景验证器模块 (Scene Validator)

负责验证 Blender 场景配置，确保场景满足 IES 生成的要求。
检查光源、渲染引擎和场景设置，提供详细的错误和警告信息。

重要说明：
- Blender 光源使用瓦特（Watts）作为单位，表示辐射功率
- 转换公式：Blender Watts = Lumens / 683
- 本模块读取瓦特值，由调用者决定是否转换为流明
"""

from typing import List, Dict, Tuple, Optional
import bpy

# 导入数据结构
from .data_structures import SceneValidation, SceneValidationError


# ============================================================================
# 常量定义
# ============================================================================

# 光视效能常数（用于流明和瓦特转换）
LUMINOUS_EFFICACY = 683.0  # lm/W

# 支持的光源类型
SUPPORTED_LIGHT_TYPES = ['POINT', 'AREA']

# 推荐的渲染引擎
RECOMMENDED_RENDER_ENGINE = 'CYCLES'


# ============================================================================
# 主验证函数
# ============================================================================

def validate_scene() -> SceneValidation:
    """
    验证当前 Blender 场景配置
    
    检查项：
    1. 渲染引擎是否为 Cycles
    2. 场景中是否有光源
    3. 光源类型是否支持（点光源或面光源）
    4. 场景单位设置
    
    返回:
        SceneValidation: 验证结果对象
    
    使用示例:
        validation = validate_scene()
        if validation.is_valid:
            print("场景验证通过")
            for light in validation.light_objects:
                print(f"  光源: {light.name}")
        else:
            print("场景验证失败:")
            for error in validation.errors:
                print(f"  - {error}")
    """
    errors = []
    warnings = []
    
    # 检查渲染引擎
    render_engine = check_render_engine()
    
    if render_engine != RECOMMENDED_RENDER_ENGINE:
        errors.append(
            f"渲染引擎必须设置为 Cycles（当前: {render_engine}）\n"
            f"修正方法：Render Properties > Render Engine > Cycles"
        )
    
    # 获取光源
    light_objects = get_light_sources()
    
    if not light_objects:
        errors.append(
            "场景中没有找到光源\n"
            "修正方法：Add > Light > Point Light 或 Area Light"
        )
    
    # 验证每个光源
    unsupported_lights = []
    for light_obj in light_objects:
        if not validate_light_source(light_obj):
            unsupported_lights.append(light_obj.name)
    
    if unsupported_lights:
        warnings.append(
            f"以下光源类型不支持，将被忽略: {', '.join(unsupported_lights)}\n"
            f"仅支持点光源（Point Light）和面光源（Area Light）"
        )
    
    # 过滤掉不支持的光源
    supported_lights = [light for light in light_objects if validate_light_source(light)]
    
    # 多光源场景提示
    if len(supported_lights) > 1:
        warnings.append(
            f"检测到 {len(supported_lights)} 个光源，将进行综合测量\n"
            f"光度中心将自动计算为所有光源的几何中心"
        )
    
    # 检查场景单位
    unit_system = bpy.context.scene.unit_settings.system
    if unit_system != 'METRIC':
        warnings.append(
            f"建议使用公制单位（当前: {unit_system}）\n"
            f"修正方法：Scene Properties > Units > Unit System > Metric"
        )
    
    # 检查 GPU 设置
    if render_engine == 'CYCLES':
        cycles_device = bpy.context.scene.cycles.device
        if cycles_device == 'CPU':
            warnings.append(
                "建议使用 GPU 渲染以提高速度\n"
                "修正方法：Render Properties > Device > GPU Compute"
            )
    
    # 创建验证结果
    if errors:
        return SceneValidation.create_invalid(
            errors=errors,
            light_objects=supported_lights,
            render_engine=render_engine
        )
    else:
        return SceneValidation.create_valid(
            light_objects=supported_lights,
            render_engine=render_engine,
            warnings=warnings if warnings else None
        )


# ============================================================================
# 光源相关函数
# ============================================================================

def get_light_sources() -> List[bpy.types.Object]:
    """
    获取场景中所有光源对象
    
    返回:
        List[bpy.types.Object]: 光源对象列表（包括所有类型的光源）
    
    注意:
        返回所有光源，包括不支持的类型
        使用 validate_light_source() 检查是否支持
    """
    light_objects = []
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'LIGHT':
            light_objects.append(obj)
    
    return light_objects


def validate_light_source(light_obj: bpy.types.Object) -> bool:
    """
    验证光源类型是否支持
    
    参数:
        light_obj: 光源对象
    
    返回:
        bool: True 如果是点光源或面光源，否则 False
    
    支持的光源类型:
        - POINT: 点光源
        - AREA: 面光源
    
    不支持的光源类型:
        - SUN: 太阳光
        - SPOT: 聚光灯
    """
    if light_obj.type != 'LIGHT':
        return False
    
    light_type = light_obj.data.type
    return light_type in SUPPORTED_LIGHT_TYPES


def check_render_engine() -> str:
    """
    检查当前渲染引擎
    
    返回:
        str: 渲染引擎名称
            - 'CYCLES': Cycles 渲染引擎
            - 'BLENDER_EEVEE': Eevee 渲染引擎
            - 其他可能的值
    """
    return bpy.context.scene.render.engine


def get_light_properties(light_obj: bpy.types.Object) -> Dict:
    """
    获取光源属性
    
    参数:
        light_obj: 光源对象
    
    返回:
        dict: 光源属性字典
            {
                'type': str,  # 'POINT' 或 'AREA'
                'location': Tuple[float, float, float],  # 世界坐标
                'power_watts': float,  # 功率（瓦特，Blender 内部单位）
                'power_lumens': float,  # 功率（流明，转换后）
                'color': Tuple[float, float, float],  # RGB 颜色
                'radius': float,  # 点光源半径（仅点光源）
                'size': float,  # 面光源尺寸（仅面光源）
                'shape': str  # 面光源形状（仅面光源）
            }
    
    异常:
        ValueError: 如果对象不是光源
    
    注意:
        - Blender 的 energy 属性是瓦特（辐射功率）
        - 转换为流明：lumens = watts * 683
    """
    if light_obj.type != 'LIGHT':
        raise ValueError(f"对象 '{light_obj.name}' 不是光源")
    
    light_data = light_obj.data
    light_type = light_data.type
    
    # 基本属性
    properties = {
        'type': light_type,
        'location': tuple(light_obj.location),
        'power_watts': light_data.energy,  # Blender 使用瓦特
        'power_lumens': light_data.energy * LUMINOUS_EFFICACY,  # 转换为流明
        'color': tuple(light_data.color)
    }
    
    # 点光源特有属性
    if light_type == 'POINT':
        properties['radius'] = light_data.shadow_soft_size
    
    # 面光源特有属性
    elif light_type == 'AREA':
        properties['size'] = light_data.size
        properties['shape'] = light_data.shape
        if light_data.shape == 'RECTANGLE':
            properties['size_x'] = light_data.size
            properties['size_y'] = light_data.size_y
    
    return properties


# ============================================================================
# 光度中心计算
# ============================================================================

def calculate_photometric_center(light_objects: List[bpy.types.Object]) -> Tuple[float, float, float]:
    """
    计算多个光源的光度中心（几何中心）
    
    对于多光源场景，IES 文件需要一个参考点。
    本函数计算所有光源位置的几何中心作为光度中心。
    
    参数:
        light_objects: 光源对象列表
    
    返回:
        Tuple[float, float, float]: (x, y, z) 光度中心位置（世界坐标）
    
    异常:
        ValueError: 如果光源列表为空
    
    计算方法:
        - 单光源：直接使用光源位置
        - 多光源：计算所有光源位置的算术平均值
    
    使用示例:
        lights = get_light_sources()
        center = calculate_photometric_center(lights)
        print(f"光度中心: {center}")
    """
    if not light_objects:
        raise ValueError("光源列表不能为空")
    
    if len(light_objects) == 1:
        # 单光源：直接使用光源位置
        return tuple(light_objects[0].location)
    
    # 多光源：计算几何中心
    total_x = sum(light.location.x for light in light_objects)
    total_y = sum(light.location.y for light in light_objects)
    total_z = sum(light.location.z for light in light_objects)
    count = len(light_objects)
    
    return (total_x / count, total_y / count, total_z / count)


def calculate_relative_photometric_center(
    light_objects: List[bpy.types.Object],
    fixture_origin: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    """
    计算相对于灯具原点的光度中心
    
    参数:
        light_objects: 光源对象列表
        fixture_origin: 灯具模型原点位置（世界坐标）
    
    返回:
        Tuple[float, float, float]: (x, y, z) 相对坐标
    
    使用示例:
        lights = get_light_sources()
        fixture_origin = get_fixture_origin()
        relative_center = calculate_relative_photometric_center(lights, fixture_origin)
        print(f"相对光度中心: {relative_center}")
    """
    world_center = calculate_photometric_center(light_objects)
    
    return (
        world_center[0] - fixture_origin[0],
        world_center[1] - fixture_origin[1],
        world_center[2] - fixture_origin[2]
    )


def get_fixture_origin() -> Tuple[float, float, float]:
    """
    获取灯具模型的原点位置
    
    返回:
        Tuple[float, float, float]: (x, y, z) 灯具原点位置（世界坐标）
    
    逻辑:
        1. 如果有选中的网格对象，使用第一个对象的位置
        2. 否则返回世界原点 (0, 0, 0)
    
    注意:
        用户应该在运行插件前选择灯具模型
    """
    # 查找选中的网格对象
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if selected_meshes:
        # 使用第一个选中的网格对象的位置
        return tuple(selected_meshes[0].location)
    
    # 如果没有选中对象，返回世界原点
    return (0.0, 0.0, 0.0)


# ============================================================================
# 辅助函数
# ============================================================================

def get_total_lumens(light_objects: List[bpy.types.Object]) -> float:
    """
    计算所有光源的总流明值
    
    参数:
        light_objects: 光源对象列表
    
    返回:
        float: 总流明值
    
    注意:
        Blender 光源使用瓦特，需要转换为流明
    """
    total_lumens = 0.0
    
    for light_obj in light_objects:
        if light_obj.type == 'LIGHT':
            watts = light_obj.data.energy
            lumens = watts * LUMINOUS_EFFICACY
            total_lumens += lumens
    
    return total_lumens


def format_light_info(light_obj: bpy.types.Object) -> str:
    """
    格式化光源信息为可读字符串
    
    参数:
        light_obj: 光源对象
    
    返回:
        str: 格式化的光源信息
    """
    if light_obj.type != 'LIGHT':
        return f"{light_obj.name}: 不是光源"
    
    props = get_light_properties(light_obj)
    
    info = f"{light_obj.name}:\n"
    info += f"  类型: {props['type']}\n"
    info += f"  位置: ({props['location'][0]:.2f}, {props['location'][1]:.2f}, {props['location'][2]:.2f})\n"
    info += f"  功率: {props['power_watts']:.2f} W ({props['power_lumens']:.0f} lm)\n"
    
    if props['type'] == 'POINT':
        info += f"  半径: {props['radius']:.3f} m\n"
    elif props['type'] == 'AREA':
        info += f"  形状: {props['shape']}\n"
        info += f"  尺寸: {props['size']:.3f} m\n"
    
    return info
