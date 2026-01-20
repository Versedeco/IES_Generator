"""
测试 bl_info 配置的有效性

这个脚本验证 Blender 插件元数据是否正确配置。
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_bl_info_exists():
    """测试 bl_info 是否存在"""
    try:
        from kiro_ies_generator import bl_info
        assert bl_info is not None, "bl_info 不存在"
        print("✓ bl_info 存在")
        return True
    except ImportError as e:
        print(f"✗ 无法导入 bl_info: {e}")
        return False


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
    
    all_passed = True
    for field in required_fields:
        if field in bl_info:
            print(f"✓ 必需字段 '{field}' 存在: {bl_info[field]}")
        else:
            print(f"✗ 缺少必需字段 '{field}'")
            all_passed = False
    
    return all_passed


def test_bl_info_version_format():
    """测试版本号格式"""
    from kiro_ies_generator import bl_info
    
    version = bl_info.get("version")
    if not isinstance(version, tuple):
        print(f"✗ 版本号必须是元组，当前类型: {type(version)}")
        return False
    
    if len(version) != 3:
        print(f"✗ 版本号必须是三元组 (major, minor, patch)，当前长度: {len(version)}")
        return False
    
    if not all(isinstance(v, int) for v in version):
        print(f"✗ 版本号的所有元素必须是整数")
        return False
    
    print(f"✓ 版本号格式正确: {version}")
    return True


def test_bl_info_blender_version():
    """测试 Blender 版本要求"""
    from kiro_ies_generator import bl_info
    
    blender_version = bl_info.get("blender")
    if not isinstance(blender_version, tuple):
        print(f"✗ Blender 版本必须是元组，当前类型: {type(blender_version)}")
        return False
    
    if len(blender_version) != 3:
        print(f"✗ Blender 版本必须是三元组 (major, minor, patch)，当前长度: {len(blender_version)}")
        return False
    
    # 检查是否支持 Blender 3.6+
    if blender_version < (3, 6, 0):
        print(f"✗ 插件要求 Blender 3.6+，当前设置: {blender_version}")
        return False
    
    print(f"✓ Blender 版本要求正确: {blender_version} (3.6+)")
    return True


def test_bl_info_category():
    """测试分类是否有效"""
    from kiro_ies_generator import bl_info
    
    # Blender 有效的分类列表
    valid_categories = [
        "3D View",
        "Add Curve",
        "Add Mesh",
        "Animation",
        "Compositing",
        "Development",
        "Game Engine",
        "Import-Export",
        "Lighting",
        "Material",
        "Mesh",
        "Node",
        "Object",
        "Paint",
        "Physics",
        "Render",
        "Rigging",
        "Scene",
        "Sequencer",
        "System",
        "Text Editor",
        "UV",
        "User Interface",
    ]
    
    category = bl_info.get("category")
    if category not in valid_categories:
        print(f"⚠ 分类 '{category}' 可能不是标准 Blender 分类")
        print(f"  有效分类: {', '.join(valid_categories)}")
        return True  # 警告但不失败
    
    print(f"✓ 分类有效: {category}")
    return True


def test_bl_info_optional_fields():
    """测试可选字段"""
    from kiro_ies_generator import bl_info
    
    optional_fields = {
        "warning": "警告信息",
        "doc_url": "文档 URL",
        "support": "支持级别",
        "tracker_url": "问题跟踪 URL",
    }
    
    for field, description in optional_fields.items():
        if field in bl_info:
            print(f"✓ 可选字段 '{field}' ({description}): {bl_info[field]}")
        else:
            print(f"  可选字段 '{field}' ({description}) 未设置")
    
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试 Blender 插件元数据 (bl_info)")
    print("=" * 60)
    print()
    
    tests = [
        ("bl_info 存在性", test_bl_info_exists),
        ("必需字段", test_bl_info_required_fields),
        ("版本号格式", test_bl_info_version_format),
        ("Blender 版本要求", test_bl_info_blender_version),
        ("分类有效性", test_bl_info_category),
        ("可选字段", test_bl_info_optional_fields),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n测试: {test_name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ 测试失败，出现异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n✓ 所有测试通过！bl_info 配置正确。")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
