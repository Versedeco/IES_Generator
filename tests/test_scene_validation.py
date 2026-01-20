"""
测试 SceneValidation 数据类

验证 SceneValidation 的功能，包括验证结果创建、格式化和辅助方法。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kiro_ies_generator.data_structures import SceneValidation


def test_scene_validation_creation():
    """测试 SceneValidation 创建"""
    # 模拟光源对象（使用简单对象代替 bpy.types.Object）
    mock_light1 = type('MockLight', (), {'name': 'Light1'})()
    mock_light2 = type('MockLight', (), {'name': 'Light2'})()
    
    validation = SceneValidation(
        is_valid=True,
        has_lights=True,
        light_objects=[mock_light1, mock_light2],
        render_engine='CYCLES',
        errors=[],
        warnings=[]
    )
    
    assert validation.is_valid == True
    assert validation.has_lights == True
    assert len(validation.light_objects) == 2
    assert validation.render_engine == 'CYCLES'
    assert len(validation.errors) == 0
    assert len(validation.warnings) == 0
    print("✓ SceneValidation 创建测试通过")


def test_valid_scene_validation():
    """测试有效场景验证"""
    mock_light = type('MockLight', (), {'name': 'Light'})()
    
    validation = SceneValidation(
        is_valid=True,
        has_lights=True,
        light_objects=[mock_light],
        render_engine='CYCLES',
        errors=[],
        warnings=['建议使用 GPU 渲染']
    )
    
    assert validation.is_valid == True
    assert validation.has_warnings() == True
    assert validation.has_errors() == False
    assert validation.get_light_count() == 1
    
    # 测试字符串表示
    str_repr = str(validation)
    assert "✓ 场景验证通过" in str_repr
    assert "找到 1 个光源" in str_repr
    assert "CYCLES" in str_repr
    assert "建议使用 GPU 渲染" in str_repr
    
    print("✓ 有效场景验证测试通过")


def test_invalid_scene_validation():
    """测试无效场景验证"""
    validation = SceneValidation(
        is_valid=False,
        has_lights=False,
        light_objects=[],
        render_engine='EEVEE',
        errors=['未找到光源对象', '渲染引擎不是 Cycles'],
        warnings=[]
    )
    
    assert validation.is_valid == False
    assert validation.has_lights == False
    assert validation.has_errors() == True
    assert validation.has_warnings() == False
    assert validation.get_light_count() == 0
    
    # 测试字符串表示
    str_repr = str(validation)
    assert "✗ 场景验证失败" in str_repr
    assert "未找到光源对象" in str_repr
    assert "渲染引擎不是 Cycles" in str_repr
    
    print("✓ 无效场景验证测试通过")


def test_get_summary():
    """测试获取验证摘要"""
    mock_light = type('MockLight', (), {'name': 'Light'})()
    
    validation = SceneValidation(
        is_valid=True,
        has_lights=True,
        light_objects=[mock_light],
        render_engine='CYCLES',
        errors=[],
        warnings=['警告1', '警告2']
    )
    
    summary = validation.get_summary()
    
    assert summary['is_valid'] == True
    assert summary['light_count'] == 1
    assert summary['render_engine'] == 'CYCLES'
    assert summary['error_count'] == 0
    assert summary['warning_count'] == 2
    assert '警告1' in summary['warnings']
    assert '警告2' in summary['warnings']
    
    print("✓ 获取验证摘要测试通过")


def test_create_valid_factory():
    """测试创建有效验证结果的工厂方法"""
    mock_light1 = type('MockLight', (), {'name': 'Light1'})()
    mock_light2 = type('MockLight', (), {'name': 'Light2'})()
    
    # 不带警告
    validation1 = SceneValidation.create_valid(
        light_objects=[mock_light1, mock_light2],
        render_engine='CYCLES'
    )
    
    assert validation1.is_valid == True
    assert validation1.has_lights == True
    assert len(validation1.light_objects) == 2
    assert len(validation1.errors) == 0
    assert len(validation1.warnings) == 0
    
    # 带警告
    validation2 = SceneValidation.create_valid(
        light_objects=[mock_light1],
        render_engine='CYCLES',
        warnings=['建议使用 GPU']
    )
    
    assert validation2.is_valid == True
    assert len(validation2.warnings) == 1
    
    print("✓ 创建有效验证结果工厂方法测试通过")


def test_create_invalid_factory():
    """测试创建无效验证结果的工厂方法"""
    # 无光源
    validation1 = SceneValidation.create_invalid(
        errors=['未找到光源']
    )
    
    assert validation1.is_valid == False
    assert validation1.has_lights == False
    assert len(validation1.light_objects) == 0
    assert len(validation1.errors) == 1
    assert validation1.render_engine == 'UNKNOWN'
    
    # 有光源但有其他错误
    mock_light = type('MockLight', (), {'name': 'Light'})()
    validation2 = SceneValidation.create_invalid(
        errors=['渲染引擎不正确'],
        light_objects=[mock_light],
        render_engine='EEVEE'
    )
    
    assert validation2.is_valid == False
    assert validation2.has_lights == True
    assert len(validation2.light_objects) == 1
    assert validation2.render_engine == 'EEVEE'
    
    print("✓ 创建无效验证结果工厂方法测试通过")


def test_repr():
    """测试对象字符串表示"""
    mock_light = type('MockLight', (), {'name': 'Light'})()
    
    validation = SceneValidation(
        is_valid=True,
        has_lights=True,
        light_objects=[mock_light],
        render_engine='CYCLES',
        errors=[],
        warnings=['警告1']
    )
    
    repr_str = repr(validation)
    assert "SceneValidation" in repr_str
    assert "is_valid=True" in repr_str
    assert "light_count=1" in repr_str
    assert "render_engine='CYCLES'" in repr_str
    assert "errors=0" in repr_str
    assert "warnings=1" in repr_str
    
    print("✓ 对象字符串表示测试通过")


def test_multiple_errors_and_warnings():
    """测试多个错误和警告"""
    validation = SceneValidation(
        is_valid=False,
        has_lights=False,
        light_objects=[],
        render_engine='EEVEE',
        errors=['错误1', '错误2', '错误3'],
        warnings=['警告1', '警告2']
    )
    
    assert len(validation.errors) == 3
    assert len(validation.warnings) == 2
    assert validation.has_errors() == True
    assert validation.has_warnings() == True
    
    summary = validation.get_summary()
    assert summary['error_count'] == 3
    assert summary['warning_count'] == 2
    
    print("✓ 多个错误和警告测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("测试 SceneValidation 数据类")
    print("=" * 60)
    
    test_scene_validation_creation()
    test_valid_scene_validation()
    test_invalid_scene_validation()
    test_get_summary()
    test_create_valid_factory()
    test_create_invalid_factory()
    test_repr()
    test_multiple_errors_and_warnings()
    
    print("=" * 60)
    print("所有测试通过！")
    print("=" * 60)
