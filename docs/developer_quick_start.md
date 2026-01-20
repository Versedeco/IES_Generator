# 开发者快速入门指南

## 环境设置

### 必需软件

1. **Blender 3.6+ 或 4.x**
   - 下载：https://www.blender.org/download/
   - 推荐：最新稳定版

2. **代码编辑器**（可选）
   - VS Code（推荐）
   - PyCharm
   - Sublime Text

### 项目结构

```
kiro_ies_generator/
├── kiro_ies_generator/          # 插件主目录
│   ├── __init__.py             # 插件入口（已配置导入路径）
│   ├── scene_validator.py      # 场景验证模块
│   ├── sampler.py             # 球面采样模块
│   ├── ies_generator.py       # IES 文件生成模块
│   └── output_manager.py      # 输出管理模块
├── tests/                      # 测试脚本
│   ├── test_imports.py        # 导入测试
│   └── ...
├── docs/                       # 文档
│   ├── import_configuration.md
│   └── ...
└── README.md                   # 项目说明
```

## 开发工作流

### 1. 在 Blender 中开发

#### 方法 A：直接编辑（快速迭代）

1. 打开 Blender
2. 切换到 Scripting 工作区
3. 打开插件文件（例如 `__init__.py`）
4. 编辑代码
5. 保存文件
6. 重新加载插件：
   ```python
   import bpy
   import importlib
   import kiro_ies_generator
   importlib.reload(kiro_ies_generator)
   ```

#### 方法 B：外部编辑器（推荐）

1. 使用 VS Code 或其他编辑器编辑代码
2. 保存文件
3. 在 Blender 中重新加载插件（使用上述代码）

### 2. 安装插件到 Blender

#### 开发模式安装

1. 找到 Blender 插件目录：
   - Windows: `%APPDATA%\Blender Foundation\Blender\{version}\scripts\addons\`
   - Linux: `~/.config/blender/{version}/scripts/addons/`
   - macOS: `~/Library/Application Support/Blender/{version}/scripts/addons/`

2. 创建符号链接（推荐）：
   ```bash
   # Windows (以管理员身份运行)
   mklink /D "C:\Users\YourName\AppData\Roaming\Blender Foundation\Blender\4.0\scripts\addons\kiro_ies_generator" "C:\path\to\your\project\kiro_ies_generator"
   
   # Linux/macOS
   ln -s /path/to/your/project/kiro_ies_generator ~/.config/blender/4.0/scripts/addons/kiro_ies_generator
   ```

3. 重启 Blender
4. Edit > Preferences > Add-ons
5. 搜索 "Kiro IES Generator"
6. 勾选启用

#### ZIP 安装（测试发布版本）

1. 创建 ZIP 包：
   ```bash
   cd /path/to/project
   zip -r kiro_ies_generator.zip kiro_ies_generator/
   ```

2. 在 Blender 中安装：
   - Edit > Preferences > Add-ons > Install
   - 选择 ZIP 文件
   - 启用插件

### 3. 调试

#### 查看控制台输出

**Windows**：
- Window > Toggle System Console

**Linux/macOS**：
- 从终端启动 Blender：
  ```bash
  blender
  ```

#### 使用 Python 调试器

在代码中添加断点：
```python
import pdb; pdb.set_trace()
```

#### 打印调试信息

```python
print("调试信息:", variable)
```

### 4. 测试

#### 在 Blender 中测试

1. 打开 Blender
2. 切换到 Scripting 工作区
3. 运行测试脚本：
   ```python
   import sys
   sys.path.append('/path/to/your/project')
   
   import tests.test_imports
   tests.test_imports.main()
   ```

#### 命令行测试（有限）

```bash
# 注意：需要 bpy 的测试会失败（预期行为）
python tests/test_imports.py
```

## 常用代码片段

### 重新加载插件

```python
import bpy
import importlib

# 重新加载主模块
import kiro_ies_generator
importlib.reload(kiro_ies_generator)

# 重新加载子模块
importlib.reload(kiro_ies_generator.scene_validator)
importlib.reload(kiro_ies_generator.sampler)
importlib.reload(kiro_ies_generator.ies_generator)
importlib.reload(kiro_ies_generator.output_manager)

# 重新注册插件
bpy.ops.preferences.addon_disable(module="kiro_ies_generator")
bpy.ops.preferences.addon_enable(module="kiro_ies_generator")
```

### 访问插件属性

```python
import bpy

# 获取插件属性
props = bpy.context.scene.kiro_ies_props

# 读取属性
print(f"角度间隔: {props.angular_interval}")
print(f"采样数: {props.samples}")
print(f"测量距离: {props.distance}")

# 设置属性
props.angular_interval = 10.0
props.samples = 64
```

### 调用操作符

```python
import bpy

# 验证场景
bpy.ops.kiro.validate_scene()

# 生成 IES
bpy.ops.kiro.generate_ies()

# 应用预设
bpy.ops.kiro.apply_preset()
```

### 检查依赖项状态

```python
import kiro_ies_generator

print(f"依赖项状态: {kiro_ies_generator.DEPENDENCIES_OK}")
print(f"核心模块状态: {kiro_ies_generator.CORE_MODULES_AVAILABLE}")

if not kiro_ies_generator.DEPENDENCIES_OK:
    print("缺失的依赖项:")
    for dep in kiro_ies_generator.MISSING_DEPENDENCIES:
        print(f"  - {dep}")

if kiro_ies_generator.DEPENDENCY_WARNINGS:
    print("警告:")
    for warning in kiro_ies_generator.DEPENDENCY_WARNINGS:
        print(f"  ⚠ {warning}")
```

## 开发最佳实践

### 1. 代码组织

- **模块化**：每个功能模块独立文件
- **清晰命名**：使用描述性的函数和变量名
- **中文注释**：所有公共函数必须有中文 docstring

### 2. 错误处理

```python
def my_function():
    """函数说明"""
    try:
        # 主要逻辑
        pass
    except Exception as e:
        print(f"错误: {e}")
        # 返回错误状态或抛出自定义异常
        return {'CANCELLED'}
```

### 3. 依赖项检查

在执行关键操作前检查：
```python
if not CORE_MODULES_AVAILABLE:
    self.report({'ERROR'}, "核心模块未加载")
    return {'CANCELLED'}

if not DEPENDENCIES_OK:
    self.report({'ERROR'}, "依赖项检查失败")
    return {'CANCELLED'}
```

### 4. UI 反馈

```python
# 信息
self.report({'INFO'}, "操作成功")

# 警告
self.report({'WARNING'}, "这是一个警告")

# 错误
self.report({'ERROR'}, "操作失败")
```

### 5. 进度报告

```python
# 更新进度
props.progress = 50.0  # 0-100
props.status_message = "正在处理..."

# 完成
props.progress = 100.0
props.status_message = "完成"
```

## 常见问题

### Q: 修改代码后没有生效？

**A**: 需要重新加载插件：
```python
import bpy
import importlib
import kiro_ies_generator
importlib.reload(kiro_ies_generator)
bpy.ops.preferences.addon_disable(module="kiro_ies_generator")
bpy.ops.preferences.addon_enable(module="kiro_ies_generator")
```

### Q: 如何查看错误信息？

**A**: 
1. 打开 Blender 控制台（Window > Toggle System Console）
2. 查看详细的错误堆栈跟踪

### Q: 插件无法加载？

**A**: 检查：
1. 文件是否在正确的目录
2. `bl_info` 格式是否正确
3. 是否有语法错误
4. 控制台是否有错误消息

### Q: 如何测试特定功能？

**A**: 在 Blender Scripting 工作区运行测试代码：
```python
import bpy

# 测试场景验证
bpy.ops.kiro.validate_scene()

# 测试参数设置
props = bpy.context.scene.kiro_ies_props
props.angular_interval = 10.0
print(f"角度间隔: {props.angular_interval}")
```

## 下一步

1. **实现数据结构**（任务 1.3）
   - 定义 `SamplingConfig`
   - 定义 `SceneValidation`
   - 定义 `SamplingResult`
   - 定义错误类

2. **实现场景验证**（任务 2.1）
   - `validate_scene()`
   - `get_light_sources()`
   - `validate_light_source()`

3. **实现采样器**（任务 3.1）
   - `calculate_sampling_points()`
   - `spherical_to_cartesian()`
   - `create_virtual_sensor()`

## 参考资料

- [Blender Python API 文档](https://docs.blender.org/api/current/)
- [Blender 插件开发教程](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
- [Python 导入系统](https://docs.python.org/3/reference/import.html)
- [项目文档](docs/)
