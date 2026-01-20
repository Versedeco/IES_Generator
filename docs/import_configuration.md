# Python 导入路径和模块依赖配置

## 概述

本文档说明 Kiro IES Generator 插件的 Python 导入路径配置和模块依赖管理。

## 导入路径配置

### 插件目录结构

```
kiro_ies_generator/
├── __init__.py              # 插件入口，包含导入配置
├── scene_validator.py       # 场景验证模块
├── sampler.py              # 球面采样模块
├── ies_generator.py        # IES 文件生成模块
└── output_manager.py       # 输出管理模块
```

### 导入机制

插件使用相对导入来加载核心模块：

```python
from . import scene_validator
from . import sampler
from . import ies_generator
from . import output_manager
```

### 路径设置

在 `__init__.py` 中，我们确保插件目录在 Python 路径中：

```python
import sys
from pathlib import Path

# 确保插件目录在 Python 路径中
addon_dir = Path(__file__).parent
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))
```

这确保了：
1. 相对导入正常工作
2. 模块可以相互引用
3. 在 Blender 环境中正确加载

## 依赖项管理

### 必需依赖项

插件依赖以下 Python 包：

1. **bpy** (Blender Python API)
   - 来源：Blender 内置
   - 版本：随 Blender 版本
   - 用途：访问 Blender 场景、对象、渲染等功能

2. **numpy**
   - 来源：Blender 3.6+ 内置
   - 推荐版本：1.20+
   - 用途：数值计算和数据存储

3. **math**
   - 来源：Python 标准库
   - 用途：数学运算（球面坐标转换）

### 依赖项检查

插件在加载时自动检查依赖项：

```python
def check_dependencies():
    """检查必需的依赖项是否可用"""
    missing_deps = []
    warnings = []
    
    # 检查 bpy
    try:
        import bpy
    except ImportError:
        missing_deps.append("bpy (Blender Python API)")
    
    # 检查 numpy
    try:
        import numpy
        numpy_version = tuple(map(int, numpy.__version__.split('.')[:2]))
        if numpy_version < (1, 20):
            warnings.append(f"NumPy 版本过低 ({numpy.__version__})，推荐 1.20+")
    except ImportError:
        missing_deps.append("numpy")
    
    # 检查 math
    try:
        import math
    except ImportError:
        missing_deps.append("math (Python 标准库)")
    
    is_valid = len(missing_deps) == 0
    return is_valid, missing_deps, warnings
```

### 依赖项状态变量

插件维护以下全局变量来跟踪依赖项状态：

- `DEPENDENCIES_OK`: bool - 所有依赖项是否可用
- `MISSING_DEPENDENCIES`: list - 缺失的依赖项列表
- `DEPENDENCY_WARNINGS`: list - 依赖项警告列表
- `CORE_MODULES_AVAILABLE`: bool - 核心模块是否成功导入

## 错误处理

### 模块导入失败

如果核心模块导入失败，插件会：

1. 设置 `CORE_MODULES_AVAILABLE = False`
2. 打印警告消息到控制台
3. 创建占位符模块变量（避免后续代码出错）
4. 在 UI 中显示错误状态
5. 禁用需要核心模块的功能

示例：

```python
try:
    from . import scene_validator
    from . import sampler
    from . import ies_generator
    from . import output_manager
    
    CORE_MODULES_AVAILABLE = True
    print("Kiro IES Generator: 核心模块已成功导入")
    
except ImportError as e:
    CORE_MODULES_AVAILABLE = False
    print(f"Kiro IES Generator 警告：无法导入核心模块 - {e}")
    
    # 创建占位符模块
    scene_validator = None
    sampler = None
    ies_generator = None
    output_manager = None
```

### 依赖项缺失

如果依赖项缺失，插件会：

1. 在控制台打印详细错误信息
2. 在 UI 面板顶部显示错误框
3. 禁用所有需要依赖项的功能
4. 阻止插件注册（如果在注册阶段检测到）

## UI 集成

### 状态显示

UI 面板会显示依赖项和模块状态：

```python
# 显示依赖项状态（如果有问题）
if not DEPENDENCIES_OK or not CORE_MODULES_AVAILABLE:
    box = layout.box()
    box.alert = True
    box.label(text="插件状态异常", icon='ERROR')
    
    if not DEPENDENCIES_OK:
        box.label(text="缺失依赖项：", icon='CANCEL')
        for dep in MISSING_DEPENDENCIES:
            box.label(text=f"  • {dep}")
    
    if not CORE_MODULES_AVAILABLE:
        box.label(text="核心模块未加载", icon='CANCEL')
```

### 功能禁用

当依赖项或模块不可用时，相关功能会被禁用：

```python
# 禁用生成按钮
if not CORE_MODULES_AVAILABLE or not DEPENDENCIES_OK:
    row.enabled = False
    row.operator("kiro.generate_ies", text="无法生成（缺少依赖）", icon='CANCEL')
```

## 注册和注销

### 注册流程

```python
def register():
    """注册插件"""
    # 检查依赖项
    if not DEPENDENCIES_OK:
        print("插件将不会注册。请在 Blender 3.6+ 环境中运行")
        return
    
    # 注册所有类
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"注册类 {cls.__name__} 失败: {e}")
    
    # 添加属性组
    bpy.types.Scene.kiro_ies_props = PointerProperty(type=KiroIESProperties)
    
    print("Kiro IES Generator 插件已注册")
```

### 注销流程

```python
def unregister():
    """注销插件"""
    # 删除场景属性
    if hasattr(bpy.types.Scene, 'kiro_ies_props'):
        del bpy.types.Scene.kiro_ies_props
    
    # 注销所有类（逆序）
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"注销类 {cls.__name__} 失败: {e}")
```

## 测试

### 导入测试

使用 `tests/test_imports.py` 测试导入配置：

```bash
# 注意：此测试在 Blender 外部运行会失败（预期行为）
python tests/test_imports.py
```

预期结果：
- 在 Blender 外部：检测到 `bpy` 缺失（正常）
- 在 Blender 内部：所有模块成功导入

### 在 Blender 中测试

1. 安装插件到 Blender
2. 启用插件
3. 检查控制台输出：

```
============================================================
Kiro IES Generator 插件已注册
版本: 1.0.0
核心模块状态: ✓ 已加载
依赖项状态: ✓ 正常
============================================================
```

4. 打开 3D 视图侧边栏 > IES Generator
5. 确认没有错误消息显示

## 故障排除

### 问题：核心模块未加载

**症状**：
- UI 显示"核心模块未加载"
- 控制台显示 ImportError

**解决方案**：
1. 确认所有模块文件都在 `kiro_ies_generator/` 目录中
2. 检查文件名是否正确（scene_validator.py, sampler.py 等）
3. 确认没有语法错误阻止模块加载
4. 重启 Blender

### 问题：缺失依赖项

**症状**：
- UI 显示"缺失依赖项"
- 控制台列出缺失的包

**解决方案**：
1. 确认使用 Blender 3.6+ 版本
2. 检查 Blender 是否正确安装
3. 如果缺少 numpy，尝试更新 Blender

### 问题：插件无法注册

**症状**：
- 插件列表中找不到插件
- 控制台显示注册失败

**解决方案**：
1. 检查 `bl_info` 格式是否正确
2. 确认所有类都在 `classes` 元组中
3. 检查是否有语法错误
4. 查看 Blender 控制台的详细错误信息

## 最佳实践

1. **始终使用相对导入**：在插件内部使用 `from . import module`
2. **检查依赖项**：在执行关键操作前检查 `CORE_MODULES_AVAILABLE` 和 `DEPENDENCIES_OK`
3. **优雅降级**：当模块不可用时，禁用功能而不是崩溃
4. **清晰的错误消息**：向用户提供可操作的错误信息
5. **版本检查**：检查 Blender 和依赖项版本，提供警告

## 参考资料

- [Blender Python API 文档](https://docs.blender.org/api/current/)
- [Python 导入系统](https://docs.python.org/3/reference/import.html)
- [Blender 插件开发指南](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
