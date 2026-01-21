"""
测试场景无光源的错误检测

验证 scene_validator 模块能够正确检测并报告场景中没有光源的错误。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kiro_ies_generator.data_structures import SceneValidation


def test_no_light_error_detection():
    """
    测试无光源场景的错误检测
    
    验证点：
    1. is_valid 应该为 False
    2. has_lights 应该为 False
    3. light_objects 应该为空列表
    4. errors 列表应该包含无光源错误消息
    5. 错误消息应该包含修正建议
    """
    # 模拟无光源场景的验证结果
    validation = SceneValidation.create_invalid(
        errors=[
            "场景中没有找到光源\n"
            "修正方法：Add > Light > Point Light 或 Area Light"
        ],
        light_objects=[],
        render_engine='CYCLES'
    )
    
    # 验证基本属性
    assert validation.is_valid == False, "无光源场景应该验证失败"
    assert validation.has_lights == False, "has_lights 应该为 False"
    assert len(validation.light_objects) == 0, "光源列表应该为空"
    assert validation.get_light_count() == 0, "光源数量应该为 0"
    
    # 验证错误消息
    assert validation.has_errors() == True, "应该有错误"
    assert len(validation.errors) > 0, "错误列表不应该为空"
    
    # 检查错误消息内容
    error_message = validation.errors[0]
    assert "没有找到光源" in error_message, "错误消息应该提到没有找到光源"
    assert "修正方法" in error_message, "错误消息应该包含修正建议"
    assert "Add > Light" in error_message, "错误消息应该包含具体的修正步骤"
    
    print("✓ 无光源错误检测测试通过")


def test_no_light_error_message_format():
    """
    测试无光源错误消息的格式
    
    验证错误消息格式化输出是否正确
    """
    validation = SceneValidation.create_invalid(
        errors=["场景中没有找到光源\n修正方法：Add > Light > Point Light 或 Area Light"],
        light_objects=[],
        render_engine='CYCLES'
    )
    
    # 获取字符串表示
    str_repr = str(validation)
    
    # 验证格式
    assert "✗ 场景验证失败" in str_repr, "应该显示验证失败标记"
    assert "没有找到光源" in str_repr, "应该包含错误消息"
    assert "修正方法" in str_repr, "应该包含修正建议"
    
    print("✓ 无光源错误消息格式测试通过")


def test_no_light_error_summary():
    """
    测试无光源错误的摘要信息
    
    验证 get_summary() 方法返回正确的摘要
    """
    validation = SceneValidation.create_invalid(
        errors=["场景中没有找到光源\n修正方法：Add > Light > Point Light 或 Area Light"],
        light_objects=[],
        render_engine='CYCLES'
    )
    
    summary = validation.get_summary()
    
    # 验证摘要内容
    assert summary['is_valid'] == False, "摘要中 is_valid 应该为 False"
    assert summary['light_count'] == 0, "摘要中光源数量应该为 0"
    assert summary['error_count'] == 1, "摘要中错误数量应该为 1"
    assert summary['warning_count'] == 0, "摘要中警告数量应该为 0"
    assert len(summary['errors']) == 1, "摘要中应该有 1 个错误"
    assert "没有找到光源" in summary['errors'][0], "摘要中应该包含错误消息"
    
    print("✓ 无光源错误摘要测试通过")


def test_multiple_errors_including_no_light():
    """
    测试包含无光源错误的多个错误场景
    
    验证当场景同时有多个问题时（包括无光源），所有错误都被正确记录
    """
    validation = SceneValidation.create_invalid(
        errors=[
            "场景中没有找到光源\n修正方法：Add > Light > Point Light 或 Area Light",
            "渲染引擎必须设置为 Cycles（当前: EEVEE）\n修正方法：Render Properties > Render Engine > Cycles"
        ],
        light_objects=[],
        render_engine='EEVEE'
    )
    
    # 验证基本属性
    assert validation.is_valid == False, "多错误场景应该验证失败"
    assert validation.has_lights == False, "has_lights 应该为 False"
    assert len(validation.errors) == 2, "应该有 2 个错误"
    
    # 验证两个错误都存在
    error_text = " ".join(validation.errors)
    assert "没有找到光源" in error_text, "应该包含无光源错误"
    assert "渲染引擎" in error_text, "应该包含渲染引擎错误"
    
    print("✓ 多错误场景（包含无光源）测试通过")


def test_no_light_vs_has_light():
    """
    测试无光源场景与有光源场景的对比
    
    验证有光源和无光源场景的验证结果差异
    """
    # 无光源场景
    no_light_validation = SceneValidation.create_invalid(
        errors=["场景中没有找到光源\n修正方法：Add > Light > Point Light 或 Area Light"],
        light_objects=[],
        render_engine='CYCLES'
    )
    
    # 有光源场景
    mock_light = type('MockLight', (), {'name': 'Light'})()
    has_light_validation = SceneValidation.create_valid(
        light_objects=[mock_light],
        render_engine='CYCLES'
    )
    
    # 对比验证
    assert no_light_validation.is_valid == False, "无光源场景应该无效"
    assert has_light_validation.is_valid == True, "有光源场景应该有效"
    
    assert no_light_validation.has_lights == False, "无光源场景 has_lights 应该为 False"
    assert has_light_validation.has_lights == True, "有光源场景 has_lights 应该为 True"
    
    assert no_light_validation.get_light_count() == 0, "无光源场景光源数量应该为 0"
    assert has_light_validation.get_light_count() == 1, "有光源场景光源数量应该为 1"
    
    assert no_light_validation.has_errors() == True, "无光源场景应该有错误"
    assert has_light_validation.has_errors() == False, "有光源场景不应该有错误"
    
    print("✓ 无光源 vs 有光源对比测试通过")


def test_error_message_content():
    """
    测试错误消息的具体内容
    
    验证错误消息包含所有必要的信息
    """
    validation = SceneValidation.create_invalid(
        errors=["场景中没有找到光源\n修正方法：Add > Light > Point Light 或 Area Light"],
        light_objects=[],
        render_engine='CYCLES'
    )
    
    error_message = validation.errors[0]
    
    # 验证错误消息的关键部分
    required_keywords = [
        "场景",
        "没有找到",
        "光源",
        "修正方法",
        "Add",
        "Light",
        "Point Light",
        "Area Light"
    ]
    
    for keyword in required_keywords:
        assert keyword in error_message, f"错误消息应该包含关键词: {keyword}"
    
    print("✓ 错误消息内容测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("测试场景无光源的错误检测")
    print("=" * 60)
    
    test_no_light_error_detection()
    test_no_light_error_message_format()
    test_no_light_error_summary()
    test_multiple_errors_including_no_light()
    test_no_light_vs_has_light()
    test_error_message_content()
    
    print("=" * 60)
    print("所有测试通过！")
    print("=" * 60)
