"""
测试 SamplingConfig 数据类

验证 SamplingConfig 的功能，包括参数验证、时间估算和预设配置。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kiro_ies_generator.data_structures import SamplingConfig


def test_sampling_config_creation():
    """测试 SamplingConfig 创建"""
    config = SamplingConfig(
        angular_interval=10.0,
        distance=5.0,
        samples=64
    )
    
    assert config.angular_interval == 10.0
    assert config.distance == 5.0
    assert config.samples == 64
    print("✓ SamplingConfig 创建测试通过")


def test_sampling_config_validation():
    """测试参数验证"""
    # 有效配置
    valid_config = SamplingConfig(
        angular_interval=10.0,
        distance=5.0,
        samples=64
    )
    assert valid_config.validate() == True
    print("✓ 有效配置验证通过")
    
    # 无效配置：角度间隔过小
    invalid_config1 = SamplingConfig(
        angular_interval=0.5,
        distance=5.0,
        samples=64
    )
    assert invalid_config1.validate() == False
    print("✓ 无效配置（角度间隔过小）验证通过")
    
    # 无效配置：距离过大
    invalid_config2 = SamplingConfig(
        angular_interval=10.0,
        distance=150.0,
        samples=64
    )
    assert invalid_config2.validate() == False
    print("✓ 无效配置（距离过大）验证通过")
    
    # 无效配置：采样数过大
    invalid_config3 = SamplingConfig(
        angular_interval=10.0,
        distance=5.0,
        samples=5000
    )
    assert invalid_config3.validate() == False
    print("✓ 无效配置（采样数过大）验证通过")


def test_total_sampling_points():
    """测试总采样点数计算"""
    config = SamplingConfig(
        angular_interval=10.0,
        distance=5.0,
        samples=64
    )
    
    # 垂直角度：0° 到 180°，间隔 10° → 19 个点
    # 水平角度：0° 到 360°，间隔 10° → 37 个点
    # 总点数：19 × 37 = 703
    expected_points = 19 * 37
    actual_points = config.get_total_sampling_points()
    
    assert actual_points == expected_points, f"预期 {expected_points}，实际 {actual_points}"
    print(f"✓ 总采样点数计算正确：{actual_points} 点")


def test_estimate_time():
    """测试时间估算"""
    config = SamplingConfig(
        angular_interval=10.0,
        distance=5.0,
        samples=64
    )
    
    time_str = config.estimate_time()
    assert isinstance(time_str, str)
    assert "分钟" in time_str or "小时" in time_str
    print(f"✓ 时间估算：{time_str}")


def test_preview_preset():
    """测试预览模式预设"""
    config = SamplingConfig.preview()
    
    assert config.angular_interval == 10.0
    assert config.distance == 5.0
    assert config.samples == 64
    assert config.validate() == True
    print("✓ 预览模式预设正确")


def test_production_preset():
    """测试生产模式预设"""
    config = SamplingConfig.production()
    
    assert config.angular_interval == 5.0
    assert config.distance == 5.0
    assert config.samples == 256
    assert config.validate() == True
    print("✓ 生产模式预设正确")


def test_string_representation():
    """测试字符串表示"""
    config = SamplingConfig(
        angular_interval=10.0,
        distance=5.0,
        samples=64
    )
    
    str_repr = str(config)
    assert "SamplingConfig" in str_repr
    assert "10.0" in str_repr
    assert "5.0" in str_repr
    assert "64" in str_repr
    print("✓ 字符串表示正确")
    print(f"  {str_repr}")


if __name__ == "__main__":
    print("=" * 60)
    print("测试 SamplingConfig 数据类")
    print("=" * 60)
    
    test_sampling_config_creation()
    test_sampling_config_validation()
    test_total_sampling_points()
    test_estimate_time()
    test_preview_preset()
    test_production_preset()
    test_string_representation()
    
    print("=" * 60)
    print("所有测试通过！")
    print("=" * 60)
