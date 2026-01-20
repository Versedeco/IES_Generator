"""
测试 bl_info 元数据配置

验证 Blender 插件元数据是否正确配置
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_bl_info_exists():
    """测试 bl_info 是否存在"""
    from kiro_ies_generator import bl_info
    assert bl_info is not None, "bl_info 不存在"
    print("✓ bl_info 存在")


def test_bl_info_required_fields():
    """测试 bl_info 必需字段"""
    from kiro_ies_generator import bl_info
    
    required_fields = [
        "name",
        "author",
        "version",
        "blender",
        "location",
        "description",
        "category",
    ]
    
    for field in required_fields:
        assert field in bl_info, f"缺少必需字段: {field}"
        assert bl_info[field], f"字段 {field} 不能为空"
    
    print("✓ 所有必需字段存在")


def test_bl_info_version_format():
    """测试版本号格式"""
    from kiro_ies_generator import bl_info
    
    version = bl_info["version"]
    assert isinstance(version, tuple), "version 必须是元组"
    assert len(version) == 3, "version 必须包含 3 个元素 (major, minor, patch)"
    assert all(isinstance(v, int) for v in version), "version 元素必须是整数"
    
    print(f"✓ 版本号格式正确: {version}")


def test_bl_info_blender_version():
    """测试 Blender 版本要求"""
    from kiro_ies_generator import bl_info
    
    blender_version = bl_info["blender"]
    assert isinstance(blender_version, tuple), "blender 版本必须是元组"
    assert len(blender_version) == 3, "blender 版本必须包含 3 个元素"
    assert blender_version >= (3, 6, 0), "最低 Blender 版本应为 3.6.0"
    
    print(f"✓ Blender 版本要求正确: {blender_version}")


def test_bl_info_category():
    """测试分类"""
    from kiro_ies_generator import bl_info
    
    valid_categories = [
        "3D View", "Add Curve", "Add Mesh", "Animation", "Compositing",
        "Development", "Game Engine", "Import-Export", "Lighting", "Material",
        "Mesh", "Node", "Object", "Paint", "Physics", "Render", "Rigging",
        "Scene", "Sequencer", "System", "Text Editor", "UV", "User Interface"
    ]
    
    category = bl_info["category"]
    assert category in valid_categories, f"分类 '{category}' 不在有效分类列表中"
    
    print(f"✓ 分类正确: {category}")


def test_bl_info_content():
    """测试 bl_info 内容"""
    from kiro_ies_generator import bl_info
    
    # 验证名称
    assert bl_info["name"] == "Kiro IES Generator", "插件名称不正确"
    
    # 验证作者
    assert bl_info["author"] == "Kiro Team", "作者信息不正确"
    
    # 验证位置
    assert "View3D" in bl_info["location"], "位置信息应包含 View3D"
    assert "IES Generator" in bl_info["location"], "位置信息应包含 IES Generator"
    
    # 验证描述
    assert "IES" in bl_info["description"], "描述应包含 IES"
    assert "IESNA" in bl_info["description"] or "LM-63" in bl_info["description"], \
        "描述应提及 IESNA 或 LM-63 标准"
    
    print("✓ bl_info 内容正确")


def test_bl_info_optional_fields():
    """测试可选字段"""
    from kiro_ies_generator import bl_info
    
    # 检查可选字段
    if "warning" in bl_info:
        print(f"  警告信息: {bl_info['warning']}")
    
    if "doc_url" in bl_info:
        print(f"  文档 URL: {bl_info['doc_url']}")
    
    if "support" in bl_info:
        valid_support = ["OFFICIAL", "COMMUNITY", "TESTING"]
        assert bl_info["support"] in valid_support, \
            f"support 必须是 {valid_support} 之一"
        print(f"  支持级别: {bl_info['support']}")
    
    print("✓ 可选字段检查完成")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("测试 bl_info 元数据配置")
    print("=" * 60)
    
    tests = [
        test_bl_info_exists,
        test_bl_info_required_fields,
        test_bl_info_version_format,
        test_bl_info_blender_version,
        test_bl_info_category,
        test_bl_info_content,
        test_bl_info_optional_fields,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n运行测试: {test.__name__}")
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ 测试错误: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
