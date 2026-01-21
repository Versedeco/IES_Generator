"""
测试多光源场景的支持

验证 scene_validator 模块能够正确处理多光源场景，包括：
- 检测多个光源
- 计算光度中心
- 提供适当的提示信息
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kiro_ies_generator.data_structures import SceneValidation
from kiro_ies_generator.scene_validator import calculate_photometric_center, get_total_lumens


def test_multi_light_detection():
    """
    测试多光源场景的检测
    
    验证点：
    1. is_valid 应该为 True（如果没有其他错误）
    2. has_lights 应该为 True
    3. light_objects 应该包含多个光源
    4. 应该有关于多光源的警告信息
    """
    # 模拟多光源场景的验证结果
    mock_light1 = type('MockLight', (), {'name': 'Light1'})()
    mock_light2 = type('MockLight', (), {'name': 'Light2'})()
    mock_light3 = type('MockLight', (), {'name': 'Light3'})()
    
    validation = SceneValidation.create_valid(
        light_objects=[mock_light1, mock_light2, mock_light3],
        render_engine='CYCLES',
        warnings=[
            "检测到 3 个光源，将进行综合测量\n"
            "光度中心将自动计算为所有光源的几何中心"
        ]
    )
    
    # 验证基本属性
    assert validation.is_valid == True, "多光源场景应该验证通过"
    assert validation.has_lights == True, "has_lights 应该为 True"
    assert len(validation.light_objects) == 3, "应该有 3 个光源"
    assert validation.get_light_count() == 3, "光源数量应该为 3"
    
    # 验证警告消息
    assert validation.has_warnings() == True, "应该有警告信息"
    warning_text = " ".join(validation.warnings)
    assert "检测到 3 个光源" in warning_text, "警告应该提到检测到多个光源"
    assert "综合测量" in warning_text, "警告应该提到综合测量"
    assert "光度中心" in warning_text, "警告应该提到光度中心"
    assert "几何中心" in warning_text, "警告应该提到几何中心"
    
    print("✓ 多光源检测测试通过")


def test_single_vs_multi_light():
    """
    测试单光源和多光源场景的对比
    
    验证单光源场景不应该有多光源警告
    """
    # 单光源场景
    mock_light = type('MockLight', (), {'name': 'Light'})()
    single_validation = SceneValidation.create_valid(
        light_objects=[mock_light],
        render_engine='CYCLES'
    )
    
    # 多光源场景
    mock_light1 = type('MockLight', (), {'name': 'Light1'})()
    mock_light2 = type('MockLight', (), {'name': 'Light2'})()
    multi_validation = SceneValidation.create_valid(
        light_objects=[mock_light1, mock_light2],
        render_engine='CYCLES',
        warnings=[
            "检测到 2 个光源，将进行综合测量\n"
            "光度中心将自动计算为所有光源的几何中心"
        ]
    )
    
    # 验证单光源场景
    assert single_validation.get_light_count() == 1, "单光源场景应该有 1 个光源"
    assert single_validation.has_warnings() == False, "单光源场景不应该有多光源警告"
    
    # 验证多光源场景
    assert multi_validation.get_light_count() == 2, "多光源场景应该有 2 个光源"
    assert multi_validation.has_warnings() == True, "多光源场景应该有警告"
    
    print("✓ 单光源 vs 多光源对比测试通过")


def test_photometric_center_single_light():
    """
    测试单光源的光度中心计算
    
    单光源的光度中心应该就是光源本身的位置
    """
    # 创建模拟光源对象
    mock_light = type('MockLight', (), {
        'name': 'Light',
        'location': type('Vector', (), {'x': 1.0, 'y': 2.0, 'z': 3.0})()
    })()
    
    # 计算光度中心
    center = calculate_photometric_center([mock_light])
    
    # 验证
    assert center == (1.0, 2.0, 3.0), f"单光源的光度中心应该是 (1.0, 2.0, 3.0)，实际是 {center}"
    
    print("✓ 单光源光度中心计算测试通过")


def test_photometric_center_multi_light_symmetric():
    """
    测试多光源的光度中心计算（对称分布）
    
    对称分布的光源，光度中心应该在几何中心
    """
    # 创建 3 个对称分布的光源
    mock_light1 = type('MockLight', (), {
        'name': 'Light1',
        'location': type('Vector', (), {'x': -1.0, 'y': 0.0, 'z': 0.0})()
    })()
    
    mock_light2 = type('MockLight', (), {
        'name': 'Light2',
        'location': type('Vector', (), {'x': 0.0, 'y': 0.0, 'z': 0.0})()
    })()
    
    mock_light3 = type('MockLight', (), {
        'name': 'Light3',
        'location': type('Vector', (), {'x': 1.0, 'y': 0.0, 'z': 0.0})()
    })()
    
    # 计算光度中心
    center = calculate_photometric_center([mock_light1, mock_light2, mock_light3])
    
    # 验证（应该是 (0, 0, 0)）
    assert abs(center[0] - 0.0) < 0.0001, f"X 坐标应该接近 0.0，实际是 {center[0]}"
    assert abs(center[1] - 0.0) < 0.0001, f"Y 坐标应该接近 0.0，实际是 {center[1]}"
    assert abs(center[2] - 0.0) < 0.0001, f"Z 坐标应该接近 0.0，实际是 {center[2]}"
    
    print("✓ 多光源光度中心计算（对称分布）测试通过")


def test_photometric_center_multi_light_asymmetric():
    """
    测试多光源的光度中心计算（不对称分布）
    
    不对称分布的光源，光度中心应该是算术平均值
    """
    # 创建 3 个不对称分布的光源
    mock_light1 = type('MockLight', (), {
        'name': 'Light1',
        'location': type('Vector', (), {'x': 1.0, 'y': 2.0, 'z': 3.0})()
    })()
    
    mock_light2 = type('MockLight', (), {
        'name': 'Light2',
        'location': type('Vector', (), {'x': 4.0, 'y': 5.0, 'z': 6.0})()
    })()
    
    mock_light3 = type('MockLight', (), {
        'name': 'Light3',
        'location': type('Vector', (), {'x': 7.0, 'y': 8.0, 'z': 9.0})()
    })()
    
    # 计算光度中心
    center = calculate_photometric_center([mock_light1, mock_light2, mock_light3])
    
    # 验证（应该是 (4, 5, 6)）
    expected_x = (1.0 + 4.0 + 7.0) / 3
    expected_y = (2.0 + 5.0 + 8.0) / 3
    expected_z = (3.0 + 6.0 + 9.0) / 3
    
    assert abs(center[0] - expected_x) < 0.0001, f"X 坐标应该是 {expected_x}，实际是 {center[0]}"
    assert abs(center[1] - expected_y) < 0.0001, f"Y 坐标应该是 {expected_y}，实际是 {center[1]}"
    assert abs(center[2] - expected_z) < 0.0001, f"Z 坐标应该是 {expected_z}，实际是 {center[2]}"
    
    print("✓ 多光源光度中心计算（不对称分布）测试通过")


def test_photometric_center_two_lights():
    """
    测试两个光源的光度中心计算
    
    两个光源的光度中心应该在中点
    """
    # 创建 2 个光源
    mock_light1 = type('MockLight', (), {
        'name': 'Light1',
        'location': type('Vector', (), {'x': 0.0, 'y': 0.0, 'z': 0.0})()
    })()
    
    mock_light2 = type('MockLight', (), {
        'name': 'Light2',
        'location': type('Vector', (), {'x': 2.0, 'y': 4.0, 'z': 6.0})()
    })()
    
    # 计算光度中心
    center = calculate_photometric_center([mock_light1, mock_light2])
    
    # 验证（应该是 (1, 2, 3)）
    assert abs(center[0] - 1.0) < 0.0001, f"X 坐标应该是 1.0，实际是 {center[0]}"
    assert abs(center[1] - 2.0) < 0.0001, f"Y 坐标应该是 2.0，实际是 {center[1]}"
    assert abs(center[2] - 3.0) < 0.0001, f"Z 坐标应该是 3.0，实际是 {center[2]}"
    
    print("✓ 两个光源光度中心计算测试通过")


def test_total_lumens_calculation():
    """
    测试总流明值计算
    
    多光源场景应该计算所有光源的总流明值
    """
    # 创建模拟光源对象（带有 energy 属性）
    mock_light1 = type('MockLight', (), {
        'name': 'Light1',
        'type': 'LIGHT',
        'data': type('LightData', (), {'energy': 2.64})()  # 1800 lm
    })()
    
    mock_light2 = type('MockLight', (), {
        'name': 'Light2',
        'type': 'LIGHT',
        'data': type('LightData', (), {'energy': 1.32})()  # 900 lm
    })()
    
    mock_light3 = type('MockLight', (), {
        'name': 'Light3',
        'type': 'LIGHT',
        'data': type('LightData', (), {'energy': 0.88})()  # 600 lm
    })()
    
    # 计算总流明值
    total_lumens = get_total_lumens([mock_light1, mock_light2, mock_light3])
    
    # 验证（2.64 + 1.32 + 0.88 = 4.84 W = 3300 lm）
    expected_lumens = (2.64 + 1.32 + 0.88) * 683
    assert abs(total_lumens - expected_lumens) < 1.0, f"总流明应该接近 {expected_lumens}，实际是 {total_lumens}"
    
    print("✓ 总流明值计算测试通过")


def test_multi_light_warning_message():
    """
    测试多光源警告消息的内容
    
    验证警告消息包含所有必要的信息
    """
    mock_light1 = type('MockLight', (), {'name': 'Light1'})()
    mock_light2 = type('MockLight', (), {'name': 'Light2'})()
    
    validation = SceneValidation.create_valid(
        light_objects=[mock_light1, mock_light2],
        render_engine='CYCLES',
        warnings=[
            "检测到 2 个光源，将进行综合测量\n"
            "光度中心将自动计算为所有光源的几何中心"
        ]
    )
    
    warning_message = validation.warnings[0]
    
    # 验证警告消息的关键部分
    required_keywords = [
        "检测到",
        "2 个光源",
        "综合测量",
        "光度中心",
        "自动计算",
        "几何中心"
    ]
    
    for keyword in required_keywords:
        assert keyword in warning_message, f"警告消息应该包含关键词: {keyword}"
    
    print("✓ 多光源警告消息内容测试通过")


def test_photometric_center_empty_list():
    """
    测试空光源列表的错误处理
    
    空列表应该抛出 ValueError
    """
    try:
        calculate_photometric_center([])
        assert False, "空光源列表应该抛出 ValueError"
    except ValueError as e:
        assert "光源列表不能为空" in str(e), f"错误消息应该提到光源列表为空，实际消息: {e}"
    
    print("✓ 空光源列表错误处理测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("测试多光源场景的支持")
    print("=" * 60)
    
    test_multi_light_detection()
    test_single_vs_multi_light()
    test_photometric_center_single_light()
    test_photometric_center_multi_light_symmetric()
    test_photometric_center_multi_light_asymmetric()
    test_photometric_center_two_lights()
    test_total_lumens_calculation()
    test_multi_light_warning_message()
    test_photometric_center_empty_list()
    
    print("=" * 60)
    print("所有测试通过！")
    print("=" * 60)
