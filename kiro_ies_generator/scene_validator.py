"""
场景验证器模块 (Scene Validator)

负责验证 Blender 场景配置，确保场景满足 IES 生成的要求。
"""

from typing import List, Dict, Tuple, Optional
import bpy


class SceneValidationError(Exception):
    """场景验证错误"""
    pass


def validate_scene() -> Dict:
    """
    验证当前 Blender 场景配置
    
    返回:
        验证结果字典:
        {
            'is_valid': bool,
            'has_lights': bool,
            'light_objects': List[bpy.types.Object],
            'render_engine': str,
            'errors': List[str],
            'warnings': List[str]
        }
    """
    result = {
        'is_valid': True,
        'has_lights': False,
        'light_objects': [],
        'render_engine': '',
        'errors': [],
        'warnings': []
    }
    
    # 检查渲染引擎
    render_engine = check_render_engine()
    result['render_engine'] = render_engine
    
    if render_engine != 'CYCLES':
        result['errors'].append("渲染引擎必须设置为 Cycles")
        result['is_valid'] = False
    
    # 获取光源
    light_objects = get_light_sources()
    result['light_objects'] = light_objects
    result['has_lights'] = len(light_objects) > 0
    
    if not result['has_lights']:
        result['errors'].append("场景中没有找到光源，请添加至少一个点光源或面光源")
        result['is_valid'] = False
    
    # 验证每个光源
    for light_obj in light_objects:
        if not validate_light_source(light_obj):
            result['warnings'].append(f"光源 '{light_obj.name}' 类型不支持，仅支持点光源和面光源")
    
    return result


def get_light_sources() -> List[bpy.types.Object]:
    """
    获取场景中所有光源对象
    
    返回:
        光源对象列表（点光源和面光源）
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
        True 如果是点光源或面光源
    """
    if light_obj.type != 'LIGHT':
        return False
    
    light_type = light_obj.data.type
    return light_type in ['POINT', 'AREA']


def check_render_engine() -> str:
    """
    检查当前渲染引擎
    
    返回:
        渲染引擎名称 ('CYCLES', 'EEVEE', 等)
    """
    return bpy.context.scene.render.engine


def get_light_properties(light_obj: bpy.types.Object) -> Dict:
    """
    获取光源属性
    
    参数:
        light_obj: 光源对象
    
    返回:
        {
            'type': str,  # 'POINT' 或 'AREA'
            'location': Tuple[float, float, float],
            'power': float,  # 流明
            'color': Tuple[float, float, float]
        }
    """
    if light_obj.type != 'LIGHT':
        raise ValueError(f"对象 '{light_obj.name}' 不是光源")
    
    light_data = light_obj.data
    
    properties = {
        'type': light_data.type,
        'location': tuple(light_obj.location),
        'power': light_data.energy,  # Blender 中的 energy 对应流明值
        'color': tuple(light_data.color)
    }
    
    return properties


def calculate_photometric_center(light_objects: List[bpy.types.Object]) -> Tuple[float, float, float]:
    """
    计算多个光源的光度中心（几何中心）
    
    参数:
        light_objects: 光源对象列表
    
    返回:
        (x, y, z) 光度中心位置
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


def get_fixture_origin() -> Tuple[float, float, float]:
    """
    获取灯具模型的原点位置
    
    返回:
        (x, y, z) 灯具原点位置（世界坐标）
    """
    # 假设灯具模型是选中的网格对象
    selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if not selected_objects:
        # 如果没有选中对象，返回世界原点
        return (0.0, 0.0, 0.0)
    
    # 使用第一个选中的网格对象的位置
    return tuple(selected_objects[0].location)
