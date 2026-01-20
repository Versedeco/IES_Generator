"""
数据结构模块 (Data Structures)

定义插件使用的核心数据类和错误类。
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


# ============================================================================
# 采样配置数据类
# ============================================================================

@dataclass
class SamplingConfig:
    """
    采样配置数据类
    
    存储球面采样的所有配置参数，包括角度间隔、测量距离和渲染采样数。
    提供参数验证和时间估算功能。
    
    属性:
        angular_interval: 角度间隔（度），范围 1-45
        distance: 采样距离（米），范围 0.1-100
        samples: Cycles 采样数，范围 1-4096
    """
    
    angular_interval: float  # 角度间隔（度）
    distance: float          # 采样距离（米）
    samples: int             # Cycles 采样数
    
    def validate(self) -> bool:
        """
        验证参数范围是否有效
        
        返回:
            bool: 所有参数都在有效范围内返回 True，否则返回 False
        
        验证规则:
            - angular_interval: 1 <= 值 <= 45
            - distance: 0.1 <= 值 <= 100
            - samples: 1 <= 值 <= 4096
        """
        return (1 <= self.angular_interval <= 45 and
                0.1 <= self.distance <= 100 and
                1 <= self.samples <= 4096)
    
    def estimate_time(self, render_time_per_sample: float = 2.0) -> str:
        """
        估计完成时间
        
        参数:
            render_time_per_sample: 每个采样点的平均渲染时间（秒）
                                   默认 2 秒，实际时间取决于硬件和场景复杂度
        
        返回:
            str: 格式化的时间估算字符串（如 "15 分钟" 或 "2.5 小时"）
        
        计算方法:
            1. 计算垂直角度数量: (180 / angular_interval) + 1
            2. 计算水平角度数量: (360 / angular_interval) + 1
            3. 总采样点数 = 垂直数量 × 水平数量
            4. 估算时间 = 总采样点数 × 每点渲染时间
            5. 根据采样数调整时间（采样数越高，渲染越慢）
        """
        num_theta = int(180 / self.angular_interval) + 1
        num_phi = int(360 / self.angular_interval) + 1
        total_samples = num_theta * num_phi
        
        # 根据采样数调整渲染时间
        # 采样数越高，渲染时间越长（近似线性关系）
        adjusted_time = render_time_per_sample * (self.samples / 64)
        
        # 计算总时间（秒）
        seconds = total_samples * adjusted_time
        minutes = seconds / 60
        
        # 格式化输出
        if minutes < 60:
            return f"{int(minutes)} 分钟"
        else:
            hours = minutes / 60
            return f"{hours:.1f} 小时"
    
    def get_total_sampling_points(self) -> int:
        """
        计算总采样点数
        
        返回:
            int: 总采样点数量
        
        计算公式:
            总点数 = (180 / angular_interval + 1) × (360 / angular_interval + 1)
        """
        num_theta = int(180 / self.angular_interval) + 1
        num_phi = int(360 / self.angular_interval) + 1
        return num_theta * num_phi
    
    @staticmethod
    def preview() -> 'SamplingConfig':
        """
        创建预览模式预设配置
        
        返回:
            SamplingConfig: 预览模式配置
                - 角度间隔: 10°
                - 测量距离: 5 米
                - 采样数: 64
        
        用途:
            快速预览和验证光分布，适合迭代设计阶段
            预计时间: 5-10 分钟（取决于硬件）
        """
        return SamplingConfig(
            angular_interval=10.0,
            distance=5.0,
            samples=64
        )
    
    @staticmethod
    def production() -> 'SamplingConfig':
        """
        创建生产模式预设配置
        
        返回:
            SamplingConfig: 生产模式配置
                - 角度间隔: 5°
                - 测量距离: 5 米
                - 采样数: 256
        
        用途:
            高质量最终输出，适合生产环境
            预计时间: 20-60 分钟（取决于硬件）
        """
        return SamplingConfig(
            angular_interval=5.0,
            distance=5.0,
            samples=256
        )
    
    def __str__(self) -> str:
        """
        格式化配置为可读字符串
        
        返回:
            str: 格式化的配置信息
        """
        return (f"SamplingConfig(\n"
                f"  角度间隔: {self.angular_interval}°\n"
                f"  测量距离: {self.distance} m\n"
                f"  采样数: {self.samples}\n"
                f"  总采样点: {self.get_total_sampling_points()}\n"
                f"  预计时间: {self.estimate_time()}\n"
                f")")
    
    def __repr__(self) -> str:
        """
        返回对象的字符串表示
        
        返回:
            str: 对象的字符串表示
        """
        return (f"SamplingConfig(angular_interval={self.angular_interval}, "
                f"distance={self.distance}, samples={self.samples})")


# ============================================================================
# 场景验证结果数据类（占位符，将在后续任务中实现）
# ============================================================================

@dataclass
class SceneValidation:
    """
    场景验证结果数据类
    
    存储场景验证的结果，包括验证状态、光源信息、错误和警告。
    
    属性:
        is_valid: 场景是否有效
        has_lights: 是否包含光源
        light_objects: 光源对象列表
        render_engine: 渲染引擎名称
        errors: 错误消息列表
        warnings: 警告消息列表
    """
    
    is_valid: bool
    has_lights: bool
    light_objects: List  # List[bpy.types.Object]，避免导入 bpy
    render_engine: str
    errors: List[str]
    warnings: List[str]
    
    def __str__(self) -> str:
        """
        格式化验证结果为可读字符串
        
        返回:
            str: 格式化的验证结果
        """
        if self.is_valid:
            result = f"✓ 场景验证通过\n"
            result += f"  - 找到 {len(self.light_objects)} 个光源\n"
            result += f"  - 渲染引擎: {self.render_engine}"
            if self.warnings:
                result += "\n警告:\n" + "\n".join(f"  ⚠ {w}" for w in self.warnings)
            return result
        else:
            return f"✗ 场景验证失败:\n" + "\n".join(f"  - {e}" for e in self.errors)


# ============================================================================
# 采样结果数据类（占位符，将在后续任务中实现）
# ============================================================================

@dataclass
class SamplingResult:
    """
    采样结果数据类
    
    存储球面采样的结果数据，包括角度、亮度数据和元信息。
    
    属性:
        vertical_angles: 垂直角度数组（度）
        horizontal_angles: 水平角度数组（度）
        luminance_data: 亮度数据数组 (N_theta, N_phi)
        light_position: 光源位置 (x, y, z)
        total_samples: 总采样点数
        elapsed_time: 耗时（秒）
    """
    
    vertical_angles: np.ndarray      # 垂直角度数组（度）
    horizontal_angles: np.ndarray    # 水平角度数组（度）
    luminance_data: np.ndarray       # 亮度数据 (N_theta, N_phi)
    light_position: Tuple[float, float, float]
    total_samples: int
    elapsed_time: float              # 耗时（秒）
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        返回:
            dict: 包含所有数据的字典
        """
        return {
            'vertical_angles': self.vertical_angles,
            'horizontal_angles': self.horizontal_angles,
            'luminance_data': self.luminance_data,
            'light_position': self.light_position,
            'total_samples': self.total_samples,
            'elapsed_time': self.elapsed_time
        }


# ============================================================================
# 光度学数据数据类（占位符，将在后续任务中实现）
# ============================================================================

@dataclass
class PhotometricData:
    """
    光度学数据数据类
    
    存储校准后的光度学数据，用于生成 IES 文件。
    
    属性:
        vertical_angles: 垂直角度数组（度）
        horizontal_angles: 水平角度数组（度）
        candela_values: 坎德拉值数组 (N_theta, N_phi)
        lumens: 总光通量（流明）
        distance: 测量距离（米）
        fixture_name: 灯具名称
    """
    
    vertical_angles: np.ndarray      # 垂直角度数组（度）
    horizontal_angles: np.ndarray    # 水平角度数组（度）
    candela_values: np.ndarray       # 坎德拉值数组 (N_theta, N_phi)
    lumens: float                    # 总光通量（流明）
    distance: float                  # 测量距离（米）
    fixture_name: str                # 灯具名称
    
    def to_ies(self) -> str:
        """
        转换为 IES 文件格式
        
        返回:
            str: IES 文件内容字符串
        
        注意:
            此方法将在 IES 生成器模块实现后完成
        """
        # TODO: 在后续任务中实现
        raise NotImplementedError("IES 生成功能将在后续任务中实现")


# ============================================================================
# 错误类（占位符，将在后续任务中实现）
# ============================================================================

class KiroError(Exception):
    """
    基础错误类
    
    所有 Kiro IES Generator 错误的基类。
    
    属性:
        message: 错误消息
        module: 发生错误的模块名称
        recoverable: 错误是否可恢复
    """
    
    def __init__(self, message: str, module: str, recoverable: bool = False):
        self.message = message
        self.module = module
        self.recoverable = recoverable
        super().__init__(self.message)


class SceneValidationError(KiroError):
    """
    场景验证错误
    
    当场景配置不正确时抛出。
    
    属性:
        errors: 错误列表
    """
    
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message, "SceneValidator", recoverable=False)
        self.errors = errors


class SamplingError(KiroError):
    """
    采样错误
    
    当采样过程中发生错误时抛出。
    
    属性:
        position: 发生错误的采样点位置
    """
    
    def __init__(self, message: str, position: Tuple[float, float, float]):
        super().__init__(message, "Sampler", recoverable=True)
        self.position = position


class CalibrationError(KiroError):
    """
    校准错误
    
    当单位校准过程中发生错误时抛出。
    
    属性:
        lumens: 导致错误的流明值
    """
    
    def __init__(self, message: str, lumens: float):
        super().__init__(message, "IESGenerator", recoverable=False)
        self.lumens = lumens
