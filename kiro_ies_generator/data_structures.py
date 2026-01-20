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
# 场景验证结果数据类
# ============================================================================

@dataclass
class SceneValidation:
    """
    场景验证结果数据类
    
    存储场景验证的结果，包括验证状态、光源信息、错误和警告。
    用于在采样前检查场景配置是否正确。
    
    属性:
        is_valid: 场景是否有效（所有必需条件都满足）
        has_lights: 是否包含光源
        light_objects: 光源对象列表
        render_engine: 渲染引擎名称（如 'CYCLES', 'EEVEE'）
        errors: 错误消息列表（阻止采样的问题）
        warnings: 警告消息列表（不阻止采样但需要注意的问题）
    
    使用示例:
        validation = SceneValidation(
            is_valid=True,
            has_lights=True,
            light_objects=[light1, light2],
            render_engine='CYCLES',
            errors=[],
            warnings=['建议使用 GPU 渲染以提高速度']
        )
        print(validation)
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
            str: 格式化的验证结果，包含状态、光源数量、渲染引擎和所有错误/警告
        
        格式:
            成功时：
                ✓ 场景验证通过
                  - 找到 N 个光源
                  - 渲染引擎: CYCLES
                警告:
                  ⚠ 警告消息1
                  ⚠ 警告消息2
            
            失败时：
                ✗ 场景验证失败:
                  - 错误消息1
                  - 错误消息2
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
    
    def __repr__(self) -> str:
        """
        返回对象的字符串表示
        
        返回:
            str: 对象的字符串表示
        """
        return (f"SceneValidation(is_valid={self.is_valid}, "
                f"has_lights={self.has_lights}, "
                f"light_count={len(self.light_objects)}, "
                f"render_engine='{self.render_engine}', "
                f"errors={len(self.errors)}, "
                f"warnings={len(self.warnings)})")
    
    def get_light_count(self) -> int:
        """
        获取光源数量
        
        返回:
            int: 光源对象的数量
        """
        return len(self.light_objects)
    
    def has_errors(self) -> bool:
        """
        检查是否有错误
        
        返回:
            bool: 如果有错误返回 True，否则返回 False
        """
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """
        检查是否有警告
        
        返回:
            bool: 如果有警告返回 True，否则返回 False
        """
        return len(self.warnings) > 0
    
    def get_summary(self) -> dict:
        """
        获取验证结果摘要
        
        返回:
            dict: 包含验证结果关键信息的字典
                {
                    'is_valid': bool,
                    'light_count': int,
                    'render_engine': str,
                    'error_count': int,
                    'warning_count': int,
                    'errors': List[str],
                    'warnings': List[str]
                }
        """
        return {
            'is_valid': self.is_valid,
            'light_count': len(self.light_objects),
            'render_engine': self.render_engine,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy()
        }
    
    @staticmethod
    def create_valid(light_objects: List, render_engine: str = 'CYCLES', 
                    warnings: List[str] = None) -> 'SceneValidation':
        """
        创建一个有效的场景验证结果
        
        参数:
            light_objects: 光源对象列表
            render_engine: 渲染引擎名称
            warnings: 警告消息列表（可选）
        
        返回:
            SceneValidation: 有效的验证结果对象
        """
        return SceneValidation(
            is_valid=True,
            has_lights=len(light_objects) > 0,
            light_objects=light_objects,
            render_engine=render_engine,
            errors=[],
            warnings=warnings or []
        )
    
    @staticmethod
    def create_invalid(errors: List[str], light_objects: List = None,
                      render_engine: str = 'UNKNOWN') -> 'SceneValidation':
        """
        创建一个无效的场景验证结果
        
        参数:
            errors: 错误消息列表
            light_objects: 光源对象列表（可选）
            render_engine: 渲染引擎名称（可选）
        
        返回:
            SceneValidation: 无效的验证结果对象
        """
        return SceneValidation(
            is_valid=False,
            has_lights=len(light_objects) > 0 if light_objects else False,
            light_objects=light_objects or [],
            render_engine=render_engine,
            errors=errors,
            warnings=[]
        )


# ============================================================================
# 采样结果数据类
# ============================================================================

@dataclass
class SamplingResult:
    """
    采样结果数据类
    
    存储球面采样的结果数据，包括角度、亮度数据和元信息。
    这是采样器模块的输出，将被传递给 IES 生成器进行单位转换和格式化。
    
    属性:
        vertical_angles: 垂直角度数组（度），范围 0-180
        horizontal_angles: 水平角度数组（度），范围 0-360
        luminance_data: 亮度数据数组 (N_theta, N_phi)，Blender 内部单位
        light_position: 光源位置 (x, y, z)，世界坐标系
        total_samples: 总采样点数
        elapsed_time: 耗时（秒）
    
    使用示例:
        result = SamplingResult(
            vertical_angles=np.array([0, 10, 20, ..., 180]),
            horizontal_angles=np.array([0, 10, 20, ..., 350]),
            luminance_data=np.random.rand(19, 36),
            light_position=(0.0, 0.0, 0.0),
            total_samples=684,
            elapsed_time=125.5
        )
        print(result)
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
                {
                    'vertical_angles': np.ndarray,
                    'horizontal_angles': np.ndarray,
                    'luminance_data': np.ndarray,
                    'light_position': tuple,
                    'total_samples': int,
                    'elapsed_time': float
                }
        """
        return {
            'vertical_angles': self.vertical_angles,
            'horizontal_angles': self.horizontal_angles,
            'luminance_data': self.luminance_data,
            'light_position': self.light_position,
            'total_samples': self.total_samples,
            'elapsed_time': self.elapsed_time
        }
    
    def get_data_shape(self) -> Tuple[int, int]:
        """
        获取亮度数据的形状
        
        返回:
            Tuple[int, int]: (垂直角度数量, 水平角度数量)
        """
        return self.luminance_data.shape
    
    def get_elapsed_time_formatted(self) -> str:
        """
        获取格式化的耗时字符串
        
        返回:
            str: 格式化的耗时（如 "2 分钟 5 秒" 或 "1.5 小时"）
        """
        seconds = self.elapsed_time
        
        if seconds < 60:
            return f"{int(seconds)} 秒"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes} 分钟 {remaining_seconds} 秒"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} 小时"
    
    def validate_data_integrity(self) -> Tuple[bool, List[str]]:
        """
        验证数据完整性
        
        检查：
        1. 数组形状是否匹配
        2. 是否有 NaN 或无穷值
        3. 角度范围是否正确
        
        返回:
            Tuple[bool, List[str]]: (是否有效, 错误消息列表)
        """
        errors = []
        
        # 检查数组形状
        n_theta = len(self.vertical_angles)
        n_phi = len(self.horizontal_angles)
        data_shape = self.luminance_data.shape
        
        if data_shape != (n_theta, n_phi):
            errors.append(
                f"数据形状不匹配：预期 ({n_theta}, {n_phi})，实际 {data_shape}"
            )
        
        # 检查 NaN 值
        if np.isnan(self.luminance_data).any():
            nan_count = np.isnan(self.luminance_data).sum()
            errors.append(f"亮度数据包含 {nan_count} 个 NaN 值")
        
        # 检查无穷值
        if np.isinf(self.luminance_data).any():
            inf_count = np.isinf(self.luminance_data).sum()
            errors.append(f"亮度数据包含 {inf_count} 个无穷值")
        
        # 检查垂直角度范围
        if self.vertical_angles.min() < 0 or self.vertical_angles.max() > 180:
            errors.append(
                f"垂直角度超出范围 [0, 180]：[{self.vertical_angles.min()}, "
                f"{self.vertical_angles.max()}]"
            )
        
        # 检查水平角度范围
        if self.horizontal_angles.min() < 0 or self.horizontal_angles.max() >= 360:
            errors.append(
                f"水平角度超出范围 [0, 360)：[{self.horizontal_angles.min()}, "
                f"{self.horizontal_angles.max()}]"
            )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def get_statistics(self) -> dict:
        """
        获取亮度数据的统计信息
        
        返回:
            dict: 统计信息
                {
                    'min': float,
                    'max': float,
                    'mean': float,
                    'std': float,
                    'median': float
                }
        """
        return {
            'min': float(np.min(self.luminance_data)),
            'max': float(np.max(self.luminance_data)),
            'mean': float(np.mean(self.luminance_data)),
            'std': float(np.std(self.luminance_data)),
            'median': float(np.median(self.luminance_data))
        }
    
    def __str__(self) -> str:
        """
        格式化采样结果为可读字符串
        
        返回:
            str: 格式化的采样结果信息
        """
        is_valid, errors = self.validate_data_integrity()
        status = "✓ 有效" if is_valid else "✗ 无效"
        
        result = f"SamplingResult {status}\n"
        result += f"  光源位置: {self.light_position}\n"
        result += f"  采样点数: {self.total_samples}\n"
        result += f"  数据形状: {self.get_data_shape()}\n"
        result += f"  耗时: {self.get_elapsed_time_formatted()}\n"
        
        stats = self.get_statistics()
        result += f"  亮度统计:\n"
        result += f"    - 最小值: {stats['min']:.6f}\n"
        result += f"    - 最大值: {stats['max']:.6f}\n"
        result += f"    - 平均值: {stats['mean']:.6f}\n"
        result += f"    - 中位数: {stats['median']:.6f}\n"
        
        if not is_valid:
            result += f"  错误:\n"
            for error in errors:
                result += f"    - {error}\n"
        
        return result
    
    def __repr__(self) -> str:
        """
        返回对象的字符串表示
        
        返回:
            str: 对象的字符串表示
        """
        return (f"SamplingResult(total_samples={self.total_samples}, "
                f"shape={self.get_data_shape()}, "
                f"elapsed_time={self.elapsed_time:.1f}s)")


# ============================================================================
# 光度学数据数据类
# ============================================================================

@dataclass
class PhotometricData:
    """
    光度学数据数据类
    
    存储校准后的光度学数据，用于生成 IES 文件。
    这是 IES 生成器的输出，包含已转换为坎德拉单位的光强数据。
    
    属性:
        vertical_angles: 垂直角度数组（度），IES 坐标系
        horizontal_angles: 水平角度数组（度），IES 坐标系
        candela_values: 坎德拉值数组 (N_theta, N_phi)
        lumens: 总光通量（流明）
        distance: 测量距离（米）
        fixture_name: 灯具名称
    
    使用示例:
        data = PhotometricData(
            vertical_angles=np.array([0, 10, 20, ..., 180]),
            horizontal_angles=np.array([0, 10, 20, ..., 350]),
            candela_values=np.random.rand(19, 36) * 1000,
            lumens=1800.0,
            distance=5.0,
            fixture_name="三 LED 吊灯"
        )
        ies_content = data.to_ies()
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
            当前抛出 NotImplementedError
        """
        # TODO: 在后续任务中实现
        raise NotImplementedError("IES 生成功能将在后续任务中实现")
    
    def get_data_shape(self) -> Tuple[int, int]:
        """
        获取坎德拉数据的形状
        
        返回:
            Tuple[int, int]: (垂直角度数量, 水平角度数量)
        """
        return self.candela_values.shape
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """
        验证光度学数据的有效性
        
        检查：
        1. 数组形状是否匹配
        2. 坎德拉值是否为非负数
        3. 流明值是否为正数
        4. 角度范围是否正确
        
        返回:
            Tuple[bool, List[str]]: (是否有效, 错误消息列表)
        """
        errors = []
        
        # 检查数组形状
        n_theta = len(self.vertical_angles)
        n_phi = len(self.horizontal_angles)
        data_shape = self.candela_values.shape
        
        if data_shape != (n_theta, n_phi):
            errors.append(
                f"数据形状不匹配：预期 ({n_theta}, {n_phi})，实际 {data_shape}"
            )
        
        # 检查坎德拉值（应该非负）
        if (self.candela_values < 0).any():
            negative_count = (self.candela_values < 0).sum()
            errors.append(f"坎德拉值包含 {negative_count} 个负值")
        
        # 检查流明值
        if self.lumens <= 0:
            errors.append(f"流明值必须为正数，当前值: {self.lumens}")
        
        # 检查距离
        if self.distance <= 0:
            errors.append(f"测量距离必须为正数，当前值: {self.distance}")
        
        # 检查垂直角度范围
        if self.vertical_angles.min() < 0 or self.vertical_angles.max() > 180:
            errors.append(
                f"垂直角度超出范围 [0, 180]：[{self.vertical_angles.min()}, "
                f"{self.vertical_angles.max()}]"
            )
        
        # 检查水平角度范围
        if self.horizontal_angles.min() < 0 or self.horizontal_angles.max() >= 360:
            errors.append(
                f"水平角度超出范围 [0, 360)：[{self.horizontal_angles.min()}, "
                f"{self.horizontal_angles.max()}]"
            )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def get_statistics(self) -> dict:
        """
        获取坎德拉数据的统计信息
        
        返回:
            dict: 统计信息
                {
                    'min': float,
                    'max': float,
                    'mean': float,
                    'std': float,
                    'median': float,
                    'total_flux_estimate': float  # 估算的总光通量
                }
        """
        return {
            'min': float(np.min(self.candela_values)),
            'max': float(np.max(self.candela_values)),
            'mean': float(np.mean(self.candela_values)),
            'std': float(np.std(self.candela_values)),
            'median': float(np.median(self.candela_values)),
            'total_flux_estimate': float(np.sum(self.candela_values))
        }
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        返回:
            dict: 包含所有数据的字典
        """
        return {
            'vertical_angles': self.vertical_angles,
            'horizontal_angles': self.horizontal_angles,
            'candela_values': self.candela_values,
            'lumens': self.lumens,
            'distance': self.distance,
            'fixture_name': self.fixture_name
        }
    
    def __str__(self) -> str:
        """
        格式化光度学数据为可读字符串
        
        返回:
            str: 格式化的光度学数据信息
        """
        is_valid, errors = self.validate_data()
        status = "✓ 有效" if is_valid else "✗ 无效"
        
        result = f"PhotometricData {status}\n"
        result += f"  灯具名称: {self.fixture_name}\n"
        result += f"  总流明: {self.lumens} lm\n"
        result += f"  测量距离: {self.distance} m\n"
        result += f"  数据形状: {self.get_data_shape()}\n"
        
        stats = self.get_statistics()
        result += f"  坎德拉统计:\n"
        result += f"    - 最小值: {stats['min']:.2f} cd\n"
        result += f"    - 最大值: {stats['max']:.2f} cd\n"
        result += f"    - 平均值: {stats['mean']:.2f} cd\n"
        result += f"    - 中位数: {stats['median']:.2f} cd\n"
        
        if not is_valid:
            result += f"  错误:\n"
            for error in errors:
                result += f"    - {error}\n"
        
        return result
    
    def __repr__(self) -> str:
        """
        返回对象的字符串表示
        
        返回:
            str: 对象的字符串表示
        """
        return (f"PhotometricData(fixture_name='{self.fixture_name}', "
                f"lumens={self.lumens}, "
                f"shape={self.get_data_shape()})")


# ============================================================================
# 错误类
# ============================================================================

class KiroError(Exception):
    """
    基础错误类
    
    所有 Kiro IES Generator 错误的基类。
    提供统一的错误处理接口和日志记录功能。
    
    属性:
        message: 错误消息
        module: 发生错误的模块名称
        recoverable: 错误是否可恢复
        timestamp: 错误发生的时间戳
    
    使用示例:
        raise KiroError(
            "发生了一个错误",
            module="Sampler",
            recoverable=True
        )
    """
    
    def __init__(self, message: str, module: str, recoverable: bool = False):
        self.message = message
        self.module = module
        self.recoverable = recoverable
        
        # 添加时间戳
        from datetime import datetime
        self.timestamp = datetime.now()
        
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        格式化错误消息
        
        返回:
            str: 格式化的错误消息
        """
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        recoverable_str = "可恢复" if self.recoverable else "不可恢复"
        
        return (f"[{timestamp_str}] [{self.module}] {recoverable_str}\n"
                f"错误: {self.message}")
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        返回:
            dict: 包含错误信息的字典
        """
        return {
            'message': self.message,
            'module': self.module,
            'recoverable': self.recoverable,
            'timestamp': self.timestamp.isoformat(),
            'type': self.__class__.__name__
        }


class SceneValidationError(KiroError):
    """
    场景验证错误
    
    当场景配置不正确时抛出。
    这是一个不可恢复的错误，需要用户修正场景配置后重试。
    
    属性:
        errors: 错误列表（具体的验证失败项）
    
    使用示例:
        raise SceneValidationError(
            "场景验证失败",
            errors=["未找到光源", "渲染引擎不是 Cycles"]
        )
    """
    
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message, "SceneValidator", recoverable=False)
        self.errors = errors
    
    def __str__(self) -> str:
        """
        格式化错误消息
        
        返回:
            str: 格式化的错误消息，包含所有验证错误
        """
        base_str = super().__str__()
        if self.errors:
            error_list = "\n".join(f"  - {e}" for e in self.errors)
            return f"{base_str}\n详细错误:\n{error_list}"
        return base_str
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        返回:
            dict: 包含错误信息的字典
        """
        data = super().to_dict()
        data['errors'] = self.errors.copy()
        return data


class SamplingError(KiroError):
    """
    采样错误
    
    当采样过程中发生错误时抛出。
    这通常是一个可恢复的错误，系统可以跳过失败的采样点继续处理。
    
    属性:
        position: 发生错误的采样点位置 (x, y, z)
        theta: 垂直角度（可选）
        phi: 水平角度（可选）
    
    使用示例:
        raise SamplingError(
            "渲染失败",
            position=(5.0, 0.0, 0.0),
            theta=90.0,
            phi=0.0
        )
    """
    
    def __init__(self, message: str, position: Tuple[float, float, float],
                 theta: float = None, phi: float = None):
        super().__init__(message, "Sampler", recoverable=True)
        self.position = position
        self.theta = theta
        self.phi = phi
    
    def __str__(self) -> str:
        """
        格式化错误消息
        
        返回:
            str: 格式化的错误消息，包含采样点位置和角度
        """
        base_str = super().__str__()
        location_info = f"\n采样点位置: {self.position}"
        
        if self.theta is not None and self.phi is not None:
            location_info += f"\n角度: θ={self.theta}°, φ={self.phi}°"
        
        return base_str + location_info
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        返回:
            dict: 包含错误信息的字典
        """
        data = super().to_dict()
        data['position'] = self.position
        if self.theta is not None:
            data['theta'] = self.theta
        if self.phi is not None:
            data['phi'] = self.phi
        return data


class CalibrationError(KiroError):
    """
    校准错误
    
    当单位校准过程中发生错误时抛出。
    这是一个不可恢复的错误，通常由无效的输入参数引起。
    
    属性:
        lumens: 导致错误的流明值
        calibration_factor: 计算的校准因子（如果有）
    
    使用示例:
        raise CalibrationError(
            "流明值必须为正数",
            lumens=-100.0
        )
    """
    
    def __init__(self, message: str, lumens: float, 
                 calibration_factor: float = None):
        super().__init__(message, "IESGenerator", recoverable=False)
        self.lumens = lumens
        self.calibration_factor = calibration_factor
    
    def __str__(self) -> str:
        """
        格式化错误消息
        
        返回:
            str: 格式化的错误消息，包含流明值和校准因子
        """
        base_str = super().__str__()
        param_info = f"\n流明值: {self.lumens} lm"
        
        if self.calibration_factor is not None:
            param_info += f"\n校准因子: {self.calibration_factor}"
        
        return base_str + param_info
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        返回:
            dict: 包含错误信息的字典
        """
        data = super().to_dict()
        data['lumens'] = self.lumens
        if self.calibration_factor is not None:
            data['calibration_factor'] = self.calibration_factor
        return data
