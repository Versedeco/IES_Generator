"""
采样器模块 (Sampler)

负责球面采样、虚拟传感器创建和光强测量。
"""

from typing import List, Dict, Tuple, Callable, Optional
import bpy
import math
import numpy as np


class SamplingError(Exception):
    """采样错误"""
    pass


def calculate_sampling_points(angular_interval: float, 
                             distance: float,
                             light_position: Tuple[float, float, float]) -> List[Dict]:
    """
    计算球面采样点位置和角度
    
    参数:
        angular_interval: 角度间隔（度）
        distance: 传感器距离光源的距离（米）
        light_position: 光源位置 (x, y, z)
    
    返回:
        采样点列表，每个元素为:
        {
            'position': (x, y, z),
            'theta': float,  # 垂直角度（度）
            'phi': float     # 水平角度（度）
        }
    """
    sampling_points = []
    
    # 垂直角度：0° (正下方) 到 180° (正上方)
    theta_values = np.arange(0, 181, angular_interval)
    
    # 水平角度：0° 到 360°
    phi_values = np.arange(0, 360, angular_interval)
    
    for theta in theta_values:
        for phi in phi_values:
            # 球面坐标转笛卡尔坐标
            position = spherical_to_cartesian(theta, phi, distance, light_position)
            
            sampling_points.append({
                'position': position,
                'theta': float(theta),
                'phi': float(phi)
            })
    
    return sampling_points


def spherical_to_cartesian(theta: float, phi: float, r: float,
                          center: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    球面坐标转笛卡尔坐标（Blender Z-up）
    
    参数:
        theta: 垂直角度（度），0° = 正下方，90° = 水平，180° = 正上方
        phi: 水平角度（度），0° = +X 轴
        r: 半径（距离）
        center: 球心位置 (x, y, z)
    
    返回:
        (x, y, z) 笛卡尔坐标
    
    坐标系说明：
        Blender Z-up 坐标系
        - X 轴：右
        - Y 轴：前
        - Z 轴：上
    """
    # 转换为弧度
    theta_rad = math.radians(theta)
    phi_rad = math.radians(phi)
    
    # 球面坐标转换公式（Z-up）
    # theta = 0° 时在 -Z 方向（正下方）
    # theta = 90° 时在 XY 平面（水平）
    # theta = 180° 时在 +Z 方向（正上方）
    x = r * math.sin(theta_rad) * math.cos(phi_rad) + center[0]
    y = r * math.sin(theta_rad) * math.sin(phi_rad) + center[1]
    z = -r * math.cos(theta_rad) + center[2]  # 注意负号，因为 theta=0 在下方
    
    return (x, y, z)


def create_virtual_sensor(position: Tuple[float, float, float],
                         target: Tuple[float, float, float],
                         name: str = "VirtualSensor") -> bpy.types.Object:
    """
    创建虚拟传感器（相机）
    
    参数:
        position: 传感器位置 (x, y, z)
        target: 传感器朝向目标 (x, y, z)
        name: 传感器对象名称
    
    返回:
        相机对象
    """
    # 创建相机
    bpy.ops.object.camera_add(location=position)
    camera = bpy.context.object
    camera.name = name
    
    # 计算朝向
    direction = (
        target[0] - position[0],
        target[1] - position[1],
        target[2] - position[2]
    )
    
    # 使用 Track To 约束或手动设置旋转
    # 这里使用简单的方法：让相机朝向目标
    camera.rotation_mode = 'QUATERNION'
    
    # 计算旋转（简化版本，实际可能需要更复杂的计算）
    import mathutils
    direction_vec = mathutils.Vector(direction).normalized()
    camera.rotation_quaternion = direction_vec.to_track_quat('-Z', 'Y')
    
    return camera


def render_at_sensor(camera: bpy.types.Object,
                    samples: int = 64) -> float:
    """
    在传感器位置执行 Cycles 渲染并提取亮度值
    
    参数:
        camera: 相机对象
        samples: Cycles 采样数
    
    返回:
        中心像素的亮度值
    """
    # 设置当前相机
    bpy.context.scene.camera = camera
    
    # 配置 Cycles 渲染参数
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    
    # 设置渲染分辨率（小尺寸以提高速度）
    scene.render.resolution_x = 64
    scene.render.resolution_y = 64
    scene.render.resolution_percentage = 100
    
    # 执行渲染
    bpy.ops.render.render(write_still=False)
    
    # 提取中心像素亮度值
    # 注意：这里需要访问渲染结果，实际实现可能需要更复杂的方法
    # 暂时返回占位值
    brightness = 0.0
    
    # TODO: 实现从渲染结果中提取亮度值的逻辑
    # 可能需要使用 bpy.data.images['Render Result'] 访问渲染结果
    
    return brightness


def collect_spherical_data(light_position: Tuple[float, float, float],
                          angular_interval: float,
                          distance: float,
                          samples: int,
                          progress_callback: Optional[Callable[[int, int], None]] = None) -> np.ndarray:
    """
    完整的球面采样流程
    
    参数:
        light_position: 光源位置 (x, y, z)
        angular_interval: 角度间隔（度）
        distance: 测量距离（米）
        samples: Cycles 采样数
        progress_callback: 进度回调函数 callback(current, total)
    
    返回:
        NumPy 数组，形状为 (n_points, 3)，每行为 [theta, phi, brightness]
    """
    # 计算采样点
    sampling_points = calculate_sampling_points(angular_interval, distance, light_position)
    total_points = len(sampling_points)
    
    # 初始化数据数组
    data = np.zeros((total_points, 3))
    
    # 创建虚拟传感器（复用）
    camera = None
    
    try:
        for i, point in enumerate(sampling_points):
            # 创建或更新虚拟传感器
            if camera is None:
                camera = create_virtual_sensor(
                    point['position'],
                    light_position,
                    "VirtualSensor"
                )
            else:
                # 更新位置和朝向
                camera.location = point['position']
                # TODO: 更新朝向
            
            # 渲染并测量
            brightness = render_at_sensor(camera, samples)
            
            # 存储数据
            data[i] = [point['theta'], point['phi'], brightness]
            
            # 进度回调
            if progress_callback:
                progress_callback(i + 1, total_points)
        
        return data
    
    finally:
        # 清理虚拟传感器
        if camera:
            bpy.data.objects.remove(camera, do_unlink=True)


def cleanup_virtual_sensor(camera: bpy.types.Object):
    """
    清理虚拟传感器对象
    
    参数:
        camera: 要删除的相机对象
    """
    if camera and camera.name in bpy.data.objects:
        bpy.data.objects.remove(camera, do_unlink=True)
