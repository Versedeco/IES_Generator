# 项目结构

## 模块架构

项目采用模块化设计，分为以下核心模块：

```
kiro_ies_generator/
├── input_manager.py       # 输入模块：处理 OBJ/FBX 导入，检查 Mesh 有效性
├── scene_builder.py       # 场景构建：设置光源、材质节点、相机/传感器路径
├── simulation_engine.py   # 物理模拟：控制 Cycles 渲染参数、采样率、去噪
├── data_collector.py      # 数据采集：执行球面采样循环，读取辐射度/亮度数据
├── ies_formatter.py       # IES 生成：单位转换、格式化文本输出
├── output_manager.py      # 输出模块：文件写入和验证
├── kiro_core.py          # 核心脚本：MVP 版本，无 UI
├── kiro_addon.py         # Blender 插件：带 UI 的完整版本
└── config/
    └── materials.json     # 材质预设配置
```

## 数据流

```
用户输入 (3D 模型 + 参数)
    ↓
输入模块 (导入模型，验证几何)
    ↓
场景构建模块 (设置光源、材质、相机)
    ↓
物理模拟模块 (Cycles 渲染配置)
    ↓
数据采集模块 (球面采样，测量光强)
    ↓
IES 生成模块 (单位转换，格式化)
    ↓
输出模块 (写入 .ies 文件)
```

## 关键文件说明

### 核心脚本
- **kiro_core.py**: MVP 版本，纯 Python 脚本，无 UI，用于命令行运行
- **kiro_addon.py**: Blender 插件版本，包含用户界面和交互功能

### 配置文件
- **config/materials.json**: 材质预设数据库
  ```json
  {
    "frosted_glass": {
      "transmission": 0.85,
      "roughness": 0.4,
      "ior": 1.5,
      "subsurface_weight": 0.3,
      "sss_radius": [5.0, 5.0, 5.0]
    },
    "opal_acrylic": { ... }
  }
  ```

### 测试文件
```
tests/
├── test_sphere.py         # 基准测试：球体各向同性验证
├── test_occlusion.py      # 遮挡测试：半球遮罩验证
└── test_calibration.py    # 校准测试：单位转换验证
```

## 代码组织规范

### 模块职责

1. **输入模块 (input_manager.py)**
   - 导入 3D 模型（OBJ、FBX、STL）
   - 验证 Mesh 完整性（封闭性、法线方向）
   - 执行几何预处理（法线一致性检查）

2. **场景构建模块 (scene_builder.py)**
   - 清空默认场景
   - 创建光源（位置、光通量、半径）
   - 应用材质节点（Principled BSDF）
   - 设置相机/传感器路径

3. **物理模拟模块 (simulation_engine.py)**
   - 配置 Cycles 渲染参数
   - 设置采样率（预览/生产模式）
   - 启用去噪（OIDN/OptiX）
   - 管理渲染队列

4. **数据采集模块 (data_collector.py)**
   - 实现球面采样算法（IESNA LM-63 C-Plane）
   - 计算传感器位置（球面坐标转换）
   - 执行渲染并读取亮度数据
   - 存储数据到 NumPy 数组

5. **IES 生成模块 (ies_formatter.py)**
   - 执行校准（Blender Unit → Candela）
   - 格式化 IES 文件头
   - 输出角度列表和光强数据
   - 验证 LM-63-2002 标准合规性

### 命名约定

- **函数名**: 使用 snake_case（如 `calculate_sensor_position`）
- **类名**: 使用 PascalCase（如 `SceneBuilder`）
- **常量**: 使用 UPPER_CASE（如 `DEFAULT_LUMENS`）
- **私有方法**: 使用前缀下划线（如 `_validate_mesh`）

### 注释规范

- 所有公共函数必须包含 docstring（中文）
- 关键算法必须注释数学公式和坐标系转换
- 复杂逻辑必须添加行内注释说明

## 开发阶段

### Phase 1: MVP（核心脚本）
- 文件: `kiro_core.py`
- 功能: 无 UI，纯脚本运行，生成基础 IES 文件

### Phase 2: 插件化（Blender Add-on）
- 文件: `kiro_addon.py`
- 功能: UI 面板、材质预设、进度条

### Phase 3: 优化与健壮性
- 功能: 自适应采样、错误处理、可视化输出
