"""
验证 bl_info 元数据配置（不依赖 Blender）

通过直接解析 __init__.py 文件来验证 bl_info 配置
"""

import ast
import os


def extract_bl_info(file_path):
    """从 Python 文件中提取 bl_info 字典"""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'bl_info':
                    # 将 AST 节点转换为字典
                    return ast.literal_eval(node.value)
    
    return None


def validate_bl_info(bl_info):
    """验证 bl_info 配置"""
    errors = []
    warnings = []
    
    # 检查必需字段
    required_fields = {
        "name": str,
        "author": str,
        "version": tuple,
        "blender": tuple,
        "location": str,
        "description": str,
        "category": str,
    }
    
    for field, expected_type in required_fields.items():
        if field not in bl_info:
            errors.append(f"缺少必需字段: {field}")
        elif not isinstance(bl_info[field], expected_type):
            errors.append(f"字段 {field} 类型错误，期望 {expected_type.__name__}")
        elif not bl_info[field]:
            errors.append(f"字段 {field} 不能为空")
    
    # 验证版本号格式
    if "version" in bl_info:
        version = bl_info["version"]
        if not isinstance(version, tuple) or len(version) != 3:
            errors.append("version 必须是包含 3 个整数的元组 (major, minor, patch)")
        elif not all(isinstance(v, int) for v in version):
            errors.append("version 的所有元素必须是整数")
    
    # 验证 Blender 版本
    if "blender" in bl_info:
        blender_version = bl_info["blender"]
        if not isinstance(blender_version, tuple) or len(blender_version) != 3:
            errors.append("blender 版本必须是包含 3 个整数的元组")
        elif blender_version < (3, 6, 0):
            warnings.append(f"Blender 版本 {blender_version} 低于推荐的 3.6.0")
    
    # 验证分类
    valid_categories = [
        "3D View", "Add Curve", "Add Mesh", "Animation", "Compositing",
        "Development", "Game Engine", "Import-Export", "Lighting", "Material",
        "Mesh", "Node", "Object", "Paint", "Physics", "Render", "Rigging",
        "Scene", "Sequencer", "System", "Text Editor", "UV", "User Interface"
    ]
    
    if "category" in bl_info:
        if bl_info["category"] not in valid_categories:
            errors.append(f"分类 '{bl_info['category']}' 不在有效分类列表中")
    
    # 验证可选字段
    if "support" in bl_info:
        valid_support = ["OFFICIAL", "COMMUNITY", "TESTING"]
        if bl_info["support"] not in valid_support:
            errors.append(f"support 必须是 {valid_support} 之一")
    
    # 内容验证
    if "name" in bl_info:
        if "Kiro IES Generator" not in bl_info["name"]:
            warnings.append("插件名称应包含 'Kiro IES Generator'")
    
    if "description" in bl_info:
        if "IES" not in bl_info["description"]:
            warnings.append("描述应包含 'IES'")
        if "IESNA" not in bl_info["description"] and "LM-63" not in bl_info["description"]:
            warnings.append("描述应提及 IESNA 或 LM-63 标准")
    
    if "location" in bl_info:
        if "View3D" not in bl_info["location"]:
            warnings.append("位置应包含 'View3D'")
    
    return errors, warnings


def print_bl_info(bl_info):
    """打印 bl_info 内容"""
    print("\nbl_info 内容:")
    print("-" * 60)
    for key, value in bl_info.items():
        print(f"  {key:15s}: {value}")
    print("-" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("验证 Blender 插件元数据 (bl_info)")
    print("=" * 60)
    
    # 获取 __init__.py 路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    init_file = os.path.join(project_root, "kiro_ies_generator", "__init__.py")
    
    if not os.path.exists(init_file):
        print(f"✗ 错误: 找不到文件 {init_file}")
        return False
    
    print(f"\n检查文件: {init_file}")
    
    # 提取 bl_info
    try:
        bl_info = extract_bl_info(init_file)
    except Exception as e:
        print(f"✗ 错误: 无法解析 bl_info - {e}")
        return False
    
    if bl_info is None:
        print("✗ 错误: 文件中未找到 bl_info")
        return False
    
    print("✓ 成功提取 bl_info")
    
    # 打印 bl_info
    print_bl_info(bl_info)
    
    # 验证 bl_info
    errors, warnings = validate_bl_info(bl_info)
    
    # 显示结果
    print("\n验证结果:")
    print("-" * 60)
    
    if errors:
        print("\n错误:")
        for error in errors:
            print(f"  ✗ {error}")
    
    if warnings:
        print("\n警告:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
    
    if not errors and not warnings:
        print("  ✓ 所有检查通过！")
    
    print("\n" + "=" * 60)
    
    if errors:
        print(f"验证失败: {len(errors)} 个错误, {len(warnings)} 个警告")
        return False
    else:
        print(f"验证成功: 0 个错误, {len(warnings)} 个警告")
        return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
