# 技术栈

## 核心技术

### 宿主环境
- **Blender**: 3.6+ / 4.x（必须支持 Python 3.10+）
- **Python**: 3.10+
- **Blender Python API (bpy)**: 用于场景操作和渲染控制

### 渲染引擎
- **Cycles Render Engine**: 必须支持 Path Tracing 和 Random Walk SSS
- **去噪方案**: OpenImageDenoise (OIDN) 或 OptiX

### 核心库
- `bpy`: Blender Python API
- `numpy`: 数值计算和数据存储
- `math`: 数学运算（球面坐标转换）

## 开发工具链

### 开发环境设置
```bash
# 确保安装 Blender 3.6+ 或 4.x
# Blender 内置 Python 环境，无需单独安装 Python

# 在 Blender 脚本编辑器中测试代码
# 或使用命令行运行脚本
blender --background --python your_script.py
```

### 常用命令

#### 运行核心脚本（无 UI）
```bash
# 在后台模式运行 IES 生成脚本
blender --background --python kiro_core.py -- --input model.obj --output output.ies
```

#### 安装插件
```bash
# 方式 1: 通过 Blender UI
# Edit > Preferences > Add-ons > Install > 选择 kiro_addon.zip

# 方式 2: 手动复制到插件目录
# Windows: %APPDATA%\Blender Foundation\Blender\{version}\scripts\addons\
# Linux: ~/.config/blender/{version}/scripts/addons/
# macOS: ~/Library/Application Support/Blender/{version}/scripts/addons/
```

#### 测试与验证
```bash
# 运行基准测试（球体测试）
blender --background --python tests/test_sphere.py

# 运行遮挡测试
blender --background --python tests/test_occlusion.py
```

#### 调试
```bash
# 启用 Blender 控制台输出
blender --debug-python

# 查看 Cycles 渲染日志
blender --debug-cycles
```

## 技术约束

### 渲染设置要求
- 必须使用 Cycles 渲染引擎（不支持 Eevee）
- 次表面散射方法必须设置为 `RANDOM_WALK`
- 必须启用去噪以减少 SSS 材质噪点
- 场景单位必须设置为 Metric (mm)

### 性能考虑
- **预览模式**: 角度间隔 10°，采样数 64（约 5-10 分钟）
- **生产模式**: 角度间隔 5°，采样数 256+（约 20-60 分钟）
- 使用 NumPy 数组存储数据以提高处理速度

### 坐标系转换
- Blender 使用 Z-up 坐标系
- IES 标准使用 Y-up 坐标系
- 代码中必须处理坐标系转换
