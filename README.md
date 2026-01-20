# Kiro IES Generator

**从 Blender 场景生成符合 IESNA LM-63 标准的 IES 光度学文件**

Kiro IES Generator 是一个 Blender Python 插件，利用 Cycles 物理渲染引擎的光线追踪能力，通过球面采样测量光强分布，生成可用于各种渲染引擎的 IES 文件。

---

## 🌟 核心特性

- **物理准确**：基于 Cycles 路径追踪引擎，精确模拟光线传播、透射、折射和次表面散射
- **标准兼容**：生成符合 IESNA LM-63-2002 标准的 IES 文件
- **灵活配置**：支持自定义采样精度，提供预览和生产模式
- **多光源支持**：支持点光源和面光源，可处理多光源场景
- **自动化流程**：从场景验证到 IES 生成的完整自动化工作流
- **元数据输出**：生成配套的 JSON 元数据文件，包含光度中心位置信息

---

## 📋 系统要求

### 必需环境
- **Blender**: 3.6+ 或 4.x
- **Python**: 3.10+（Blender 内置）
- **渲染引擎**: Cycles（必须）
- **操作系统**: Windows / Linux / macOS

### 推荐硬件配置

**最低配置**：
- CPU：4 核心处理器
- 内存：16 GB RAM
- 渲染设备：CPU
- 预期性能：预览模式 20-30 分钟

**推荐配置**（GPU 渲染）：
- CPU：8 核心以上处理器
- GPU：NVIDIA RTX 3060 或更高（8GB+ VRAM）
- 内存：32 GB RAM
- 预期性能：预览模式 3-5 分钟，生产模式 20-40 分钟

**高性能配置**：
- CPU：16 核心以上处理器
- GPU：NVIDIA RTX 4080/4090（16GB+ VRAM）
- 内存：64 GB RAM
- 预期性能：预览模式 1-2 分钟，生产模式 10-20 分钟

> **提示**：使用 GPU 渲染可获得 5-20 倍速度提升，强烈推荐！

---

## 🚀 快速开始

### 安装插件

#### 方法 1：通过 Blender UI（推荐）

1. 下载插件 ZIP 包：`kiro_ies_generator.zip`
2. 打开 Blender
3. 进入 **Edit > Preferences > Add-ons**
4. 点击 **Install** 按钮
5. 选择下载的 ZIP 文件
6. 在插件列表中找到 **Kiro IES Generator** 并勾选启用

#### 方法 2：手动安装

将插件文件夹复制到 Blender 插件目录：

- **Windows**: `%APPDATA%\Blender Foundation\Blender\{version}\scripts\addons\`
- **Linux**: `~/.config/blender/{version}/scripts/addons/`
- **macOS**: `~/Library/Application Support/Blender/{version}/scripts/addons/`

重启 Blender 并在 Preferences > Add-ons 中启用插件。

### 基本使用流程

#### 1. 准备场景

在 Blender 中准备灯具场景：

```
✅ 导入灯具 3D 模型（OBJ、FBX、STL 等）
✅ 设置基于物理的材质参数（Principled BSDF）
   - Transmission（透射率）
   - Roughness（粗糙度）
   - IOR（折射率）
   - Subsurface Scattering（次表面散射）
✅ 在灯具内部正确位置添加光源
   - 点光源（Point Light）：适用于 LED 芯片、灯珠
   - 面光源（Area Light）：适用于灯管、LED 灯带、面板
✅ 设置光源强度为总流明值（例如 1800 lm）
✅ 确保渲染引擎设置为 Cycles
✅ 确保世界背景为黑色（无环境光）
```

**重要**：场景应该是纯净的测量环境——只包含灯具和光源，无其他物体或环境光。

#### 2. 打开插件面板

在 3D 视图中：
- 按 **N** 键打开侧边栏
- 切换到 **IES Generator** 标签页

#### 3. 配置参数

**预设模式**（推荐）：
- **预览模式**：角度间隔 10°，采样数 64（快速验证，2-5 分钟）
- **生产模式**：角度间隔 5°，采样数 256（最终输出，20-40 分钟）
- **自定义**：手动配置参数

**采样参数**：
- **角度间隔**：球面采样的角度间隔（1-45 度）
- **采样数**：Cycles 渲染采样数（1-4096）
- **测量距离**：虚拟传感器距离光源的距离（米）

**光源参数**：
- **总流明**：光源总光通量（流明）

**输出设置**：
- **灯具名称**：用于 IES 文件元数据
- **输出路径**：IES 文件保存位置

#### 4. 生成 IES 文件

1. 点击 **验证场景** 按钮检查配置
2. 点击 **生成 IES** 按钮开始采样
3. 等待进度条完成
4. 获得两个文件：
   - `your_fixture.ies` - IES 光度学数据
   - `your_fixture_metadata.json` - 光度中心和元数据

---

## 📖 详细使用指南

### 场景准备最佳实践

#### 灯具模型要求

**基本要求**：
- ✅ 网格干净（无重叠面、无孤立顶点）
- ✅ 法线方向正确（外法线朝外）
- ✅ 比例正确（使用真实尺寸，单位：米）
- ⚠️ 封闭性：仅对封闭式灯具要求网格封闭

**几何复杂度建议**：
- 简单灯具（推荐）：10K-100K 面
- 中等灯具：100K-500K 面
- 复杂灯具（谨慎使用）：> 500K 面

#### 材质设置

使用 **Principled BSDF** 设置物理准确的材质参数：

**磨砂玻璃灯罩示例**：
```
Principled BSDF:
- Base Color: 白色或浅色
- Transmission: 0.85
- Roughness: 0.4
- IOR: 1.5
- Subsurface Weight: 0.3
- Subsurface Radius: [5.0, 5.0, 5.0] mm
- Normal: Noise Texture（可选，用于表面细节）
```

**压花玻璃灯罩示例**：
```
Principled BSDF:
- Transmission: 0.90
- Roughness: 0.3
- IOR: 1.5
- Normal: Normal Map（压花纹理，Strength: 1.5）
```

**乳白亚克力示例**：
```
Principled BSDF:
- Transmission: 0.80
- Roughness: 0.5
- IOR: 1.49
- Subsurface Weight: 0.5
- Subsurface Radius: [10.0, 10.0, 10.0] mm
```

> **提示**：优先使用程序纹理（Noise、Voronoi）而非 Image Texture，可以避免 UV 拆分，大幅提升渲染速度。

#### 光源设置

**点光源（Point Light）**：
- 适用于：单个 LED 芯片、小型灯珠、球形灯泡
- **Strength**：总流明值（例如 1800 lm）
- **Radius**：光源半径（例如 0.01m = 10mm）

**面光源（Area Light）**：
- 适用于：灯管、LED 灯带、发光面板、灯片
- **Strength**：总流明值（例如 1800 lm）
- **Shape**：Rectangle（矩形）、Square（正方形）、Disk（圆形）
- **Size**：光源尺寸
  - 灯管：Rectangle，Size X = 长度，Size Y = 直径
  - 面板灯：Square，Size = 面板尺寸
  - LED 灯带：Rectangle，Size X = 长度，Size Y = 宽度

**流明值获取方式**：
1. 直接从 LED 规格书查看流明值
2. 或通过计算：功率（W）× 光效（lm/W）= 流明（lm）
   - 例如：15W × 120 lm/W = 1800 lm

### 多光源处理

插件支持多光源场景，会自动计算光度中心（几何中心）：

**示例**：3 个 LED 灯珠排成一排
```
光源配置：
- 光源 A：位置 (-0.2, 0, 0)，600 lm
- 光源 B：位置 (0, 0, 0)，600 lm
- 光源 C：位置 (0.2, 0, 0)，600 lm

计算结果：
- 光度中心：(0, 0, 0)
- 总流明：1800 lm
- IES 文件记录所有 3 个光源的综合光强分布
```

插件会在 UI 中实时显示光度中心位置，并在元数据文件中输出详细信息。

### 性能优化建议

1. **启用 GPU 渲染**（强烈推荐）：
   - Edit > Preferences > System > Cycles Render Devices
   - 选择 CUDA / OptiX / HIP / Metal
   - 速度提升 5-20 倍

2. **使用 Normal 贴图代替 Displacement**：
   - 速度提升 10-100 倍
   - 对于 99% 的项目足够准确

3. **合理设置采样数**：
   - 预览模式：64 采样（快速验证）
   - 生产模式：256 采样（最终输出）
   - 避免过高采样数（> 512 通常无必要）

4. **简化灯具几何**：
   - 使用 Decimate 修改器简化模型
   - 保留主要形状即可

5. **迭代优化**：
   - 先用低采样数（32-64）快速测试
   - 验证光分布形状正确
   - 最后用高采样数生成最终 IES 文件

---

## 🎯 在渲染引擎中使用 IES 文件

### Unreal Engine 5

1. **导入 IES 文件**：
   - Content Browser > 右键 > Import
   - 选择生成的 .ies 文件

2. **读取元数据**：
   - 打开 `your_fixture_metadata.json`
   - 查看 `relative_to_fixture_origin` 字段

3. **创建光源**：
   - 添加 Point Light 或 Spot Light
   - Details 面板 > Light > IES Texture
   - 选择导入的 IES Profile

4. **设置位置**（关键）：
   - 将 IES 光源放在：灯具位置 + 相对偏移
   - 或使用 Socket 附加到灯具模型

5. **设置参数**：
   - Intensity: metadata.json 中的 `total_lumens`
   - Intensity Units: Lumens

### V-Ray

1. 创建 VRayIES 光源
2. 加载生成的 .ies 文件
3. 设置位置：灯具原点 + 相对偏移
4. Power: metadata.json 中的 `total_lumens`
5. Units: Lumens

### Corona Renderer

1. 创建 CoronaLight，类型：IES
2. 加载生成的 .ies 文件
3. 设置位置：灯具原点 + 相对偏移
4. Intensity: metadata.json 中的 `total_lumens`
5. Units: Lumens

---

## 📁 项目结构

```
kiro_ies_generator/
├── __init__.py              # Blender 插件入口，UI 面板
├── scene_validator.py       # 场景验证模块
├── sampler.py              # 球面采样和光强测量
├── ies_generator.py        # IES 文件生成和格式化
├── output_manager.py       # 文件输出和元数据管理
└── config/
    └── materials.json      # 材质预设配置（可选）

tests/
├── test_sphere.py          # 基准测试：球体各向同性验证
├── test_occlusion.py       # 遮挡测试：半球遮罩验证
└── test_calibration.py     # 校准测试：单位转换验证

docs/
└── user_manual.md          # 用户手册（详细）
```

---

## 🔧 开发和测试

### 运行测试

```bash
# 运行基准测试（球体测试）
blender --background --python tests/test_sphere.py

# 运行遮挡测试
blender --background --python tests/test_occlusion.py

# 运行校准测试
blender --background --python tests/test_calibration.py
```

### 调试

```bash
# 启用 Blender 控制台输出
blender --debug-python

# 查看 Cycles 渲染日志
blender --debug-cycles
```

### 命令行运行（无 UI）

```bash
# 在后台模式运行 IES 生成脚本
blender --background --python kiro_core.py -- --input model.obj --output output.ies
```

---

## ❓ 常见问题

### Q: 为什么渲染速度很慢？

**A**: 
1. 确保启用了 GPU 渲染（Edit > Preferences > System）
2. 使用预览模式（64 采样）进行快速验证
3. 简化灯具几何（使用 Decimate 修改器）
4. 使用 Normal 贴图代替 Displacement

### Q: 生成的 IES 文件与预期不符？

**A**:
1. 检查材质参数是否使用真实物理值
2. 确认光源强度设置为流明值（而非瓦特）
3. 验证场景单位设置为米（Scene Properties > Units > Metric）
4. 确保世界背景为黑色，无环境光

### Q: 如何在渲染引擎中正确放置 IES 光源？

**A**:
1. 打开生成的 `your_fixture_metadata.json` 文件
2. 查看 `photometric_center.relative_to_fixture_origin` 字段
3. 将 IES 光源放在：灯具模型原点 + 相对偏移位置
4. 设置流明值为 `total_lumens` 字段的值

### Q: 支持哪些灯具类型？

**A**:
- ✅ 封闭式灯具（球形吊灯、筒灯、台灯）
- ✅ 半封闭式灯具（工业吊灯、装饰灯）
- ✅ 开放式灯具（树状灯、多灯珠灯具、射灯）
- ✅ 单光源和多光源配置

### Q: 需要 UV 拆分吗？

**A**:
- 使用程序纹理（Noise、Voronoi）：❌ 不需要
- 使用 Image Texture（Normal Map）：✅ 需要良好的 UV
- 推荐：优先使用程序纹理，避免 UV 拆分

---

## 📝 版本历史

### v1.0.0（开发中）
- ✅ 基础插件架构
- ✅ UI 面板和参数配置
- ⏳ 场景验证模块
- ⏳ 球面采样算法
- ⏳ IES 文件生成
- ⏳ 元数据输出

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交 Pull Request

### 代码规范

- 函数名：使用 snake_case
- 类名：使用 PascalCase
- 常量：使用 UPPER_CASE
- 所有公共函数必须包含 docstring（中文）

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📧 联系方式

- **项目主页**：https://github.com/kiro-team/kiro-ies-generator
- **问题反馈**：https://github.com/kiro-team/kiro-ies-generator/issues
- **邮箱**：support@kiro-team.com

---

## 🙏 致谢

- Blender Foundation - 提供强大的开源 3D 创作工具
- IESNA - 制定 LM-63 光度学数据标准
- 所有贡献者和用户

---

**Kiro IES Generator** - 让灯具设计更简单，让光照更真实 ✨
