"""
测试 Python 导入路径和模块依赖

这个脚本验证所有核心模块可以正确导入，并且依赖项检查功能正常工作。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_core_module_imports():
    """测试核心模块导入"""
    print("=" * 60)
    print("测试核心模块导入")
    print("=" * 60)
    
    modules_to_test = [
        'kiro_ies_generator.scene_validator',
        'kiro_ies_generator.sampler',
        'kiro_ies_generator.ies_generator',
        'kiro_ies_generator.output_manager',
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name} - 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"✗ {module_name} - 导入失败: {e}")
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"结果: {success_count} 成功, {fail_count} 失败")
    print("=" * 60)
    
    return fail_count == 0


def test_dependency_check():
    """测试依赖项检查功能"""
    print("\n" + "=" * 60)
    print("测试依赖项检查功能")
    print("=" * 60)
    
    try:
        # 导入主模块
        import kiro_ies_generator
        
        # 检查依赖项检查函数是否存在
        if hasattr(kiro_ies_generator, 'check_dependencies'):
            print("✓ check_dependencies 函数存在")
            
            # 执行依赖项检查
            is_valid, missing_deps, warnings = kiro_ies_generator.check_dependencies()
            
            print(f"\n依赖项检查结果:")
            print(f"  状态: {'✓ 正常' if is_valid else '✗ 异常'}")
            
            if missing_deps:
                print(f"  缺失依赖项:")
                for dep in missing_deps:
                    print(f"    - {dep}")
            else:
                print(f"  缺失依赖项: 无")
            
            if warnings:
                print(f"  警告:")
                for warning in warnings:
                    print(f"    ⚠ {warning}")
            else:
                print(f"  警告: 无")
            
            return True
        else:
            print("✗ check_dependencies 函数不存在")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_constants():
    """测试模块常量"""
    print("\n" + "=" * 60)
    print("测试模块常量")
    print("=" * 60)
    
    try:
        import kiro_ies_generator
        
        constants_to_check = [
            'CORE_MODULES_AVAILABLE',
            'DEPENDENCIES_OK',
            'MISSING_DEPENDENCIES',
            'DEPENDENCY_WARNINGS',
        ]
        
        for const_name in constants_to_check:
            if hasattr(kiro_ies_generator, const_name):
                value = getattr(kiro_ies_generator, const_name)
                print(f"✓ {const_name} = {value}")
            else:
                print(f"✗ {const_name} - 不存在")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_bl_info():
    """测试 bl_info 元数据"""
    print("\n" + "=" * 60)
    print("测试 bl_info 元数据")
    print("=" * 60)
    
    try:
        import kiro_ies_generator
        
        if hasattr(kiro_ies_generator, 'bl_info'):
            bl_info = kiro_ies_generator.bl_info
            print(f"✓ bl_info 存在")
            print(f"  名称: {bl_info.get('name', 'N/A')}")
            print(f"  版本: {bl_info.get('version', 'N/A')}")
            print(f"  Blender 版本: {bl_info.get('blender', 'N/A')}")
            print(f"  类别: {bl_info.get('category', 'N/A')}")
            return True
        else:
            print("✗ bl_info 不存在")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Kiro IES Generator - 导入路径和依赖项测试")
    print("=" * 60)
    
    # 运行所有测试
    results = []
    
    results.append(("核心模块导入", test_core_module_imports()))
    results.append(("依赖项检查", test_dependency_check()))
    results.append(("模块常量", test_module_constants()))
    results.append(("bl_info 元数据", test_bl_info()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
