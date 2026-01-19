# 设计文档

## 概述

Kiro IES Generator 是一个 Blender Python 插件，专注于从用户手动准备的场景生成符合 IESNA LM-63 标准的 IES 光度学文件。插件采用简化的模块化架构，将核心功能分解为四个主要模块。

### 设计理念

**数字化仿真实验室测量**：本插件通过 Blender 的 Cycles 物理渲染引擎，数字化仿真了传统实验室的 IES 测量过程。

```
物理实验室测量流程              数字仿真流程（本插件）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 暗室环境                  ⟹  全黑虚空场景（无环境光）
2. 放置真实灯具              ⟹  导入 3D 模型 + 设置材质
3. 安装真实光源              ⟹  添加 Blender 光源
4. 机械臂 + 光度计            ⟹  虚拟相机 + Cycles 渲染
5. 球面旋转测量（5-10m）      ⟹  球面采样算法（5-10m）
6. 光度计读数                ⟹  渲染图像亮度值
7. 数据处理 + 单位转换        ⟹  校准算法（坎德拉转换）
8. 输出 IES 文件             ⟹  输出 IES 文件
```

**核心优势**：
- **物理精确**：Cycles 路径追踪 + 次表面散射模拟真实光学特性
- **成本低廉**：无需昂贵的实验室设备和专业场地
- **快速迭代**：5-60 分钟完成测量，支持设计快速迭代
- **灵活性高**：可测试未制造的设计，快速尝试不同材质参数

**人工准备 + 插件辅助**：用户在 Blender 中完成场景准备工作（导入模型、设置材质、放置光源），插件专注于核心功能：球面采样、光强测量和 IES 文件生成。

### 核心工作流程

**阶段 1：用户手动准备**（在 Blender 中）

**重要原则**：场景应该是纯净的测量环境——只包含灯具和光源，无其他物体或环境光。这确保测量的是灯具本身的光分布特性，不受环境干扰。

**物理准确性要求**：为确保仿真结果与实验室测量一致，必须使用真实的物理参数。

准备步骤：
1. 清空默认场景（删除默认立方体、灯光）
2. 导入灯具 3D 模型（OBJ、FBX、STL 等）
3. 将灯具放置在世界原点附近（便于计算，但非强制）
4. 检查模型质量（封闭性、法线方向）
5. **设置物理准确的材质参数**：
   - 使用 Principled BSDF
   - 根据材料规格书设置透射率（Transmission）
   - 根据材料规格书设置折射率（IOR）
   - 根据雾度设置粗糙度（Roughness）
   - 设置次表面散射参数（Subsurface Weight、Radius）
   - 必须使用 Random Walk SSS 方法（最物理准确）
6. **设置真实的光源参数**：
   - 在灯具内部正确位置添加点光源或面光源
   - **设置光源强度（Strength）为总流明值**（例如 1800 lm）
   - 设置光源尺寸/半径接近实际 LED 芯片尺寸（例如 0.01m = 10mm）
   - 可选：设置色温（开尔文 K）或颜色（影响颜色但不影响光强分布）
7. 确认世界背景为黑色（World > Surface > Background，强度 0）
8. 确保渲染引擎设置为 Cycles
9. 确保场景单位设置为米（Scene Properties > Units > Metric）

**参数来源**：
- **总光通量（流明）**：LED 规格书中的流明值，或通过功率 × 光效计算（例如：15W × 120 lm/W = 1800 lm）
- **光源尺寸**：LED 芯片实际尺寸（通常 5-15mm）
- **材质参数**：材料供应商数据（透射率、折射率、雾度）

**注意**：IES 文件只关心光通量（流明）和光强分布（坎德拉），不需要电功率（瓦特）参数。

**场景要求**：
- ✅ 只有灯具模型和内部光源
- ✅ 黑色背景，无环境光照
- ✅ 无地面、墙壁等环境元素
- ✅ 使用真实物理参数
- ✅ 使用 Cycles + Random Walk SSS
- ❌ 不要添加 HDRI 或天光
- ❌ 不要添加其他物体
- ❌ 不要使用 Eevee 渲染引擎
- ❌ 不要随意调整参数"看起来好看"

**阶段 2：插件执行**（自动化）
1. 验证场景配置（检查光源、渲染引擎）
2. 基于 IESNA LM-63 C-Plane 坐标系进行球面采样
3. 使用 Cycles 渲染引擎测量每个采样点的光强
4. 将测量数据转换为坎德拉单位
5. 格式化为 IES 文件并输出

### 模型准备与 UV 拆分

#### 模型质量要求

**基本要求**：
- ✅ 网格干净（无重叠面、无孤立顶点）
- ✅ 法线方向正确（外法线朝外）
- ✅ 比例正确（使用真实尺寸，单位：米）
- ⚠️ 封闭性：仅对封闭式灯具要求网格封闭

**几何复杂度建议**：
```
简单灯具（推荐）：
- 面数：10K-100K
- 渲染速度：快
- 适用场景：大多数 IES 生成

中等灯具：
- 面数：100K-500K
- 渲染速度：中等
- 适用场景：需要一定细节

复杂灯具（谨慎使用）：
- 面数：> 500K
- 渲染速度：慢
- 适用场景：高精度要求
- 建议：使用 Decimate 修改器简化
```

**模型检查清单**：
1. 打开 Blender > 导入模型
2. 选择模型 > Edit Mode (Tab)
3. 检查法线：Viewport Overlays > Face Orientation
   - 蓝色 = 正确（外法线）
   - 红色 = 错误（内法线）
   - 修复：选择红色面 > Alt+N > Flip
4. 检查重叠面：Select > Select All by Trait > Non-Manifold
5. 检查比例：View > Properties (N) > Item > Dimensions

#### 多材质灯具处理

真实灯具通常包含多种材质，需要正确分配材质以获得准确的 IES 数据。

**典型灯具材质组成**：

```
灯具结构分析：
┌─────────────────────────────────────┐
│  1. 金属外壳（不透光）              │
│     - 材质：金属、塑料              │
│     - 作用：遮挡光线                │
│     - 对 IES 影响：产生阴影         │
│     - UV 需求：不重要               │
├─────────────────────────────────────┤
│  2. 半透明灯罩（透光，核心部分）    │
│     - 材质：磨砂玻璃、亚克力        │
│     - 作用：散射和透射光线          │
│     - 对 IES 影响：决定光分布       │
│     - UV 需求：如使用贴图则重要     │
├─────────────────────────────────────┤
│  3. 透明玻璃（透光）                │
│     - 材质：透明玻璃                │
│     - 作用：透射光线，轻微折射      │
│     - 对 IES 影响：影响光线方向     │
│     - UV 需求：通常不重要           │
├─────────────────────────────────────┤
│  4. 内部支撑结构（遮挡）            │
│     - 材质：任意                    │
│     - 作用：产生遮挡和阴影          │
│     - 对 IES 影响：局部遮挡         │
│     - UV 需求：不重要               │
└─────────────────────────────────────┘
```

**材质分配策略**：

**1. 金属外壳（不透光部分）**：
```
Principled BSDF 设置：
- Base Color: 金属颜色（如 RGB 0.8, 0.8, 0.8）
- Metallic: 1.0（金属）或 0.0（塑料）
- Roughness: 0.2-0.5（根据表面光洁度）
- Transmission: 0.0（完全不透光）

UV 需求：❌ 不需要（除非用于视觉展示）
重要性：★☆☆☆☆（只影响遮挡，不影响散射）

注意：
- 可以使用纯色材质
- 如需视觉效果，可添加 Image Texture
- 对 IES 生成影响很小
```

**2. 半透明灯罩（核心透光部分）**：
```
Principled BSDF 设置：
- Base Color: 白色或浅色
- Transmission: 0.80-0.95（根据材料透明度）
- Roughness: 0.3-0.6（根据雾度）
- IOR: 1.5（玻璃）或 1.49（亚克力）
- Subsurface Weight: 0.2-0.5（增强散射）
- Subsurface Radius: [5.0, 5.0, 5.0] mm
- Normal: 连接 Normal Map（如需纹理）

UV 需求：
- 使用程序纹理：❌ 不需要
- 使用 Image Texture：✅ 必须有良好 UV

重要性：★★★★★（最重要，直接决定光分布）

注意：
- 这是最关键的部分
- 材质参数直接影响 IES 准确性
- 如使用 Normal 贴图，UV 质量至关重要
```

**3. 透明玻璃（装饰或保护）**：
```
Principled BSDF 设置：
- Transmission: 0.95-0.98
- Roughness: 0.0-0.1（高度透明）
- IOR: 1.5
- Normal: 可选（轻微 Bump）

UV 需求：❌ 通常不需要
重要性：★★★☆☆（影响折射，但通常影响较小）

注意：
- 通常使用统一的透明材质
- 除非有特殊压花或纹理
```

**4. 内部支撑结构**：
```
任意材质：
- 可以使用简单的漫反射材质
- 或直接使用金属材质

UV 需求：❌ 不需要
重要性：★★☆☆☆（只产生遮挡）

注意：
- 主要作用是产生阴影和遮挡
- 材质类型对 IES 影响很小
```

**材质分配工作流程**：

```
步骤 1：识别材质区域
- 在 Blender 中选择模型
- Edit Mode > 按材质选择面
- 或使用 Material Properties 查看现有材质

步骤 2：创建材质槽
- Material Properties > + 添加材质槽
- 为每种材质类型创建独立材质
- 命名清晰（如 "Metal_Shell", "Frosted_Glass", "Clear_Glass"）

步骤 3：分配材质
- Edit Mode > 选择对应的面
- 在材质列表中选择材质
- 点击 "Assign" 分配

步骤 4：设置材质参数
- 按照上述建议设置每个材质的参数
- 重点关注半透明灯罩的参数

步骤 5：测试渲染
- 渲染几个角度检查效果
- 确认透光部分正确散射光线
- 确认不透光部分正确遮挡
```

#### UV 拆分指南

**何时需要 UV**：

```
不需要 UV 的情况（推荐）：
✅ 使用程序纹理（Noise、Voronoi、Wave）
✅ 纯色材质
✅ 简单的 Principled BSDF 参数设置
✅ 快速原型和迭代

需要 UV 的情况：
⚠️ 使用 Normal Map（Image Texture）
⚠️ 使用 Image Texture（颜色、粗糙度等）
⚠️ 使用 Displacement Map
⚠️ 需要特定的压花图案
```

**UV 质量对 IES 的影响**：

```
好的 UV（无拉伸）：
✅ Normal 贴图均匀分布
✅ 凹凸效果一致
✅ 光线散射均匀
✅ IES 数据准确

差的 UV（有拉伸）：
❌ Normal 贴图变形
❌ 某些区域凹凸过度/不足
❌ 光线散射不均匀
❌ IES 数据可能不准确
❌ 需要重新拆 UV 并重新生成
```

**UV 拆分步骤**（仅针对透光部分）：

```
步骤 1：准备模型
1. 选择灯罩部分（透光材质）
2. 进入编辑模式（Tab）
3. 确保只选择了需要 UV 的部分

步骤 2：标记接缝（Seam）
1. 选择边缘模式（Edge Mode, 2）
2. 选择关键边缘（通常是不显眼的位置）
3. Ctrl+E > Mark Seam（标记为红色）
4. 接缝位置建议：
   - 灯罩底部边缘
   - 对称轴位置
   - 避免正面显眼位置

步骤 3：展开 UV
1. 全选（A）
2. U > Unwrap
3. 或使用 Smart UV Project（自动）

步骤 4：检查拉伸
1. 打开 UV Editor
2. 启用 Overlay > Stretch
3. 查看颜色：
   - 蓝色/绿色 = 良好（无拉伸）
   - 黄色 = 轻微拉伸（可接受）
   - 红色 = 严重拉伸（需要修复）

步骤 5：调整 UV 岛屿
1. 选择拉伸严重的岛屿
2. 使用 Minimize Stretch（Ctrl+V）
3. 或重新标记接缝并 Unwrap

步骤 6：打包 UV
1. 全选 UV 岛屿（A）
2. UV > Pack Islands
3. 调整 Margin（边距，建议 0.01-0.02）

步骤 7：验证
1. 应用 Normal Map 或 Image Texture
2. 渲染测试
3. 检查纹理是否均匀、无明显变形
```

**UV 质量检查清单**：

```
✅ 无明显拉伸（Stretch Overlay 大部分为蓝色/绿色）
✅ 纹理密度均匀（整个表面纹理大小一致）
✅ 接缝位置合理（不在显眼位置）
✅ UV 岛屿方向正确（与模型方向一致）
✅ 无重叠的 UV 岛屿
✅ UV 在 0-1 范围内（或合理的平铺）
```

#### 程序纹理 vs Image Texture

**程序纹理（推荐用于 IES 生成）**：

```
优点：
✅ 不需要 UV
✅ 无缝衔接
✅ 可以实时调整参数
✅ 文件体积小
✅ 适合快速迭代
✅ 渲染速度快

常用程序纹理：
- Noise Texture: 磨砂效果、随机粗糙
- Voronoi Texture: 蜂窝纹理、有机图案
- Wave Texture: 波纹、条纹
- Musgrave Texture: 复杂有机纹理

设置示例（磨砂玻璃）：
Principled BSDF > Normal > Normal Map > Color:
└── Noise Texture
    - Scale: 50-100
    - Detail: 2-4
    - Roughness: 0.5
Normal Map:
    - Strength: 0.5-1.5
```

**Image Texture（特殊需求）**：

```
优点：
✅ 可以使用特定的压花图案
✅ 可以从实物扫描获得
✅ 精确控制纹理细节
✅ 可以复制真实产品

缺点：
❌ 必须有良好的 UV
❌ UV 拉伸会导致变形
❌ 需要准备贴图文件
❌ 文件体积大
❌ 调整不灵活

适用场景：
- 特定的品牌压花图案
- 从实物扫描的纹理
- 需要精确复制真实灯具
- 高端产品展示

设置示例（压花玻璃）：
Principled BSDF > Normal > Normal Map > Color:
└── Image Texture
    - 加载 Normal Map 图片
    - Color Space: Non-Color
    - Interpolation: Linear
Normal Map:
    - Space: Tangent
    - Strength: 1.0-2.0
```

**选择建议**：

```
快速原型阶段：
→ 使用程序纹理
→ 不需要 UV
→ 快速验证光分布

精细调整阶段：
→ 如需特定纹理，准备 UV 和贴图
→ 或继续使用程序纹理（通常足够）

最终输出：
→ 大多数情况：程序纹理
→ 特殊需求：Image Texture + 良好 UV
```

#### 实际工作流程建议

**推荐流程（平衡效率和质量）**：

```
阶段 1：模型准备（5-15 分钟）
1. 导入灯具模型
2. 检查几何质量（法线、比例）
3. 简化模型（如需要，使用 Decimate）
4. 分配材质区域（金属、玻璃、灯罩等）

阶段 2：材质设置（10-20 分钟）
1. 为每个材质区域创建材质
2. 设置基本参数（Transmission、Roughness、IOR）
3. 使用程序纹理添加表面细节（推荐）
4. 或准备 UV 并使用 Image Texture（如需要）

阶段 3：快速验证（5-10 分钟）
1. 使用低采样数（32-64）渲染几个角度
2. 检查光分布是否符合预期
3. 调整材质参数（如需要）

阶段 4：生成 IES（根据硬件）
1. 运行插件
2. 等待完成（GPU: 几分钟到半小时）
3. 验证 IES 文件

阶段 5：视觉优化（可选）
1. 仅当需要渲染展示图时
2. 精心拆分 UV（如使用 Image Texture）
3. 添加高质量贴图
4. 此时 IES 已经生成完毕
```

**常见问题和解决方案**：

```
问题 1：Normal 贴图效果不均匀
原因：UV 拉伸
解决：重新拆分 UV，确保无拉伸

问题 2：某些方向光线过强/过弱
原因：材质参数不正确或 UV 变形
解决：检查材质参数，检查 UV 质量

问题 3：渲染速度太慢
原因：模型过于复杂
解决：使用 Decimate 修改器简化模型

问题 4：IES 文件与预期不符
原因：材质参数不准确
解决：使用真实的物理参数（从规格书获取）

问题 5：不知道是否需要 UV
原因：不确定使用程序纹理还是 Image Texture
解决：优先使用程序纹理（99% 的情况足够）
```

#### 最佳实践总结

**模型准备**：
- ✅ 使用干净的几何（10K-100K 面）
- ✅ 确保法线方向正确
- ✅ 使用真实尺寸（米）

**多材质处理**：
- ✅ 正确识别透光和不透光部分
- ✅ 重点关注半透明灯罩的材质设置
- ✅ 金属外壳可以使用简单材质

**UV 策略**：
- ✅ 优先使用程序纹理（不需要 UV）
- ✅ 仅在必要时使用 Image Texture
- ✅ 如使用 Image Texture，确保 UV 质量良好
- ✅ 只为透光部分精心拆 UV

**效率优化**：
- ✅ 快速原型阶段使用程序纹理
- ✅ 使用低采样数快速验证
- ✅ 最后才考虑高质量贴图和 UV

### 灯具类型支持

插件设计支持各种灯具类型，用户在准备场景时需要考虑：

1. **封闭式灯具**：完全封闭的灯罩（球形吊灯、筒灯）
   - 用户需确保网格封闭
   - 光线通过半透明材质散射

2. **半封闭式灯具**：带内部支撑结构
   - Cycles 自动处理遮挡效果
   - 无需特殊配置

3. **开放式灯具**：无灯罩（树状灯、多灯珠）
   - 网格可以不封闭
   - 支持多个光源

4. **多光源配置**：
   - 用户可放置多个点光源或面光源
   - 插件会测量所有光源的综合效果

### 多光源处理与光度中心

#### IES 文件的核心概念

**IES 文件描述的是：从一个参考点（光度中心）向各个方向发出的光强分布。**

```
关键点：
- IES 文件只有一个参考点（光度中心）
- 所有角度和距离都相对于这个点测量
- 这个点通常是灯具的"光学中心"
- IES 文件记录的是"综合光强分布"，不区分光来自哪个光源
```

#### 单光源 vs 多光源

**单光源情况（简单）**：

```
场景：一个灯泡在灯罩中心

┌─────────────────┐
│                 │
│    灯罩         │
│                 │
│       💡        │ ← 光源位置 (0, 0, 0)
│                 │
│                 │
└─────────────────┘

IES 参考点：光源位置 (0, 0, 0)
采样球心：光源位置 (0, 0, 0)
测量距离：5 米（从光源中心）

结果：
- IES 文件的光度中心 = 光源位置
- 在渲染引擎中使用时，IES 光源放在这个位置
```

**多光源情况（复杂）**：

```
场景：3 个 LED 灯珠排成一排

┌─────────────────────────┐
│                         │
│    灯罩                 │
│                         │
│   💡    💡    💡        │ ← 3 个光源
│   A     B     C         │
│                         │
└─────────────────────────┘

问题：IES 文件只能有一个参考点，但有 3 个光源！

解决方案：计算"等效光度中心"
```

#### 光度中心的计算方法

**方法：几何中心（插件采用）**

```python
def calculate_photometric_center(light_objects):
    """
    计算多个光源的光度中心（几何中心）
    
    参数:
        light_objects: 光源对象列表
    
    返回:
        (x, y, z) 光度中心位置
    """
    if len(light_objects) == 1:
        # 单光源：直接使用光源位置
        return light_objects[0].location
    
    # 多光源：计算几何中心
    total_x = sum(light.location.x for light in light_objects)
    total_y = sum(light.location.y for light in light_objects)
    total_z = sum(light.location.z for light in light_objects)
    count = len(light_objects)
    
    return (total_x / count, total_y / count, total_z / count)
```

**计算示例**：

```
光源配置：
- 光源 A：位置 (-0.2, 0, 0)，600 lm
- 光源 B：位置 (0, 0, 0)，600 lm
- 光源 C：位置 (0.2, 0, 0)，600 lm

计算：
光度中心 = ((-0.2 + 0 + 0.2) / 3, 0, 0) = (0, 0, 0)

采样：
- 球心：(0, 0, 0)
- 半径：5 米
- 测量：所有 3 个光源的综合效果

IES 文件：
- 参考点：(0, 0, 0)
- 总流明：1800 lm
- 光强分布：3 个光源的叠加效果
```

#### 光度中心的输出

**IES 文件标准不包含位置信息**，因此插件需要额外输出光度中心数据。

**输出方案：生成配套的元数据文件**

```
输出文件：
1. my_fixture.ies          ← IES 光度学数据
2. my_fixture_metadata.json ← 光度中心和其他元数据

metadata.json 内容示例：
{
  "fixture_name": "三 LED 吊灯",
  "generated_date": "2024-01-19T10:30:00Z",
  
  "photometric_center": {
    "world_coordinates": {
      "x": 0.0,
      "y": 0.0,
      "z": 1.5,
      "unit": "meters"
    },
    "relative_to_fixture_origin": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.1,
      "unit": "meters",
      "note": "相对于灯具模型的原点（Pivot）"
    }
  },
  
  "light_sources": [
    {
      "name": "LED_A",
      "type": "POINT",
      "location": [-0.2, 0.0, 1.5],
      "power": 600,
      "unit": "lumens"
    },
    {
      "name": "LED_B",
      "type": "POINT",
      "location": [0.0, 0.0, 1.5],
      "power": 600,
      "unit": "lumens"
    },
    {
      "name": "LED_C",
      "type": "POINT",
      "location": [0.2, 0.0, 1.5],
      "power": 600,
      "unit": "lumens"
    }
  ],
  
  "total_lumens": 1800,
  
  "usage_instructions": {
    "unreal_engine": "在灯具模型原点偏移 (0, 0, 0.1) 处放置 IES 光源",
    "vray": "使用 VRayIES 光源，位置偏移 (0, 0, 0.1)",
    "corona": "使用 CoronaLight，位置偏移 (0, 0, 0.1)"
  }
}
```

**UI 显示**：

插件在 Blender UI 中实时显示光度中心：

```
IES Generator 面板：
┌─────────────────────────────────┐
│ 光源选择：                      │
│ ☑ LED_A  ☑ LED_B  ☑ LED_C      │
│                                 │
│ 计算的光度中心：                │
│ 世界坐标：(0.0, 0.0, 1.5)      │
│ 相对坐标：(0.0, 0.0, 0.1)      │
│ [复制世界坐标] [复制相对坐标]  │
│                                 │
│ 总流明：1800 lm                 │
└─────────────────────────────────┘
```

#### 多光源的综合效果

**重要概念**：

```
IES 文件记录的是"综合光强分布"：
- 不区分光来自哪个光源
- 就像实验室测量一样，只测量最终结果

示例：
- 3 个光源在某方向的光强：200 cd, 300 cd, 250 cd
- IES 记录：750 cd（总和）

在渲染引擎中使用时：
- 只需要一个 IES 光源
- 设置总流明值（所有光源之和）
- IES 文件会正确分布光线
```

### 在渲染引擎中使用 IES 文件

#### 核心原则

**在任何渲染引擎中使用 IES 文件时，都需要：**
1. 创建一个单独的 IES 光源（即使 Blender 中有多个光源）
2. 将光源放置在光度中心位置
3. 设置总流明值（所有 Blender 光源的流明总和）

#### Unreal Engine 5 使用指南

**完整工作流程**：

```
步骤 1：导入 IES 文件
1. 在 UE5 中打开项目
2. Content Browser > 右键 > Import
3. 选择生成的 .ies 文件
4. UE5 会创建一个 IES Profile 资产

步骤 2：导入灯具模型（可选）
1. 导入灯具的 3D 模型（FBX）
2. 注意模型的 Pivot 位置

步骤 3：读取元数据
1. 打开 my_fixture_metadata.json
2. 查看 "relative_to_fixture_origin" 字段
3. 记录偏移值，例如：(0, 0, 0.1)

步骤 4：创建光源
1. 在场景中添加 Point Light 或 Spot Light
2. Details 面板 > Light > IES Texture
3. 选择导入的 IES Profile

步骤 5：设置光源位置（关键！）
方法 A - 使用 Socket（推荐）：
  1. 在灯具模型的 Static Mesh Editor 中
  2. 添加 Socket，命名为 "LightSocket"
  3. 位置：metadata.json 中的 relative_to_fixture_origin
  4. 将 IES 光源附加到这个 Socket

方法 B - 手动定位：
  1. 放置灯具模型，例如位置 (100, 200, 300)
  2. 计算 IES 光源位置：
     灯具位置 + 相对偏移
     = (100, 200, 300) + (0, 0, 0.1)
     = (100, 200, 300.1)
  3. 将 IES 光源放在 (100, 200, 300.1)

步骤 6：设置光源参数
Details 面板：
- Intensity: 1800 lm（metadata.json 中的 total_lumens）
- Intensity Units: Lumens
- Attenuation Radius: 根据需要调整
- IES Brightness Scale: 1.0
```

**坐标系转换**：

```
Blender 坐标系（Z-up）：
- X: 右
- Y: 前
- Z: 上

UE5 坐标系（Z-up）：
- X: 前
- Y: 右
- Z: 上

转换：
Blender (X, Y, Z) → UE5 (Y, X, Z)

示例：
Blender 相对偏移：(0.1, 0.2, 0.3)
UE5 相对偏移：(0.2, 0.1, 0.3)

注意：
- 使用 FBX 导出时，Blender 通常会自动处理转换
- 建议在 Blender 导出时勾选 "Forward: -Y Forward"
```

**验证方法**：

```
方法 1：视觉对比
1. 在 Blender 中渲染一个角度
2. 在 UE5 中从相同角度渲染
3. 对比光分布是否一致

方法 2：使用调试可视化
1. 在 UE5 中启用 "Show > Lighting > Light Radius"
2. 检查 IES 光源是否在灯具的正确位置
3. 使用 "Show > Lighting > IES Light Profiles" 查看光分布

方法 3：测量光强
1. 在 UE5 中放置一个测试平面
2. 测量特定位置的照度
3. 与 Blender 中的预期值对比
```

#### V-Ray 使用指南

```
步骤 1：创建 VRayIES 光源
1. 在 3ds Max/Maya 中创建 VRayIES 光源
2. 加载生成的 .ies 文件

步骤 2：设置位置
1. 读取 metadata.json 中的 relative_to_fixture_origin
2. 将 VRayIES 光源放在灯具原点 + 相对偏移位置

步骤 3：设置参数
- Power: metadata.json 中的 total_lumens
- Units: Lumens
- Color: 根据需要调整色温

注意：
- V-Ray 会自动处理 IES 文件的光分布
- 确保使用流明单位而非瓦特
```

#### Corona Renderer 使用指南

```
步骤 1：创建 CoronaLight
1. 在 3ds Max 中创建 CoronaLight
2. 类型：IES
3. 加载生成的 .ies 文件

步骤 2：设置位置
1. 读取 metadata.json 中的 relative_to_fixture_origin
2. 将 CoronaLight 放在灯具原点 + 相对偏移位置

步骤 3：设置参数
- Intensity: metadata.json 中的 total_lumens
- Units: Lumens
- Include/Exclude: 根据需要设置

注意：
- Corona 对 IES 文件的支持非常好
- 可以实时预览 IES 光分布
```

#### Blender 中使用（验证）

```
在 Blender 中使用生成的 IES 文件进行验证：

步骤 1：创建新场景
1. 打开新的 Blender 文件
2. 删除默认立方体和灯光

步骤 2：导入灯具模型
1. 导入原始灯具模型
2. 确保位置和原始场景一致

步骤 3：添加 IES 光源
1. 添加 Point Light
2. Light Properties > Nodes > Use Nodes
3. 添加 IES Texture 节点
4. 加载生成的 .ies 文件
5. 连接到 Strength

步骤 4：设置位置
1. 读取 metadata.json 中的 photometric_center.world_coordinates
2. 将 Point Light 放在这个位置

步骤 5：渲染对比
1. 从相同角度渲染
2. 对比与原始场景的光分布
3. 应该非常接近（验证 IES 文件正确性）
```

#### 通用最佳实践

**1. 使用 Socket/Attachment（推荐）**：

```
优点：
✅ 光源自动跟随灯具
✅ 位置始终正确
✅ 易于管理和复制
✅ 支持动态灯具（旋转、移动）

实现：
1. 在灯具模型上创建 Socket/Locator
2. Socket 位置 = 光度中心（相对于模型 Pivot）
3. 将 IES 光源附加到 Socket
```

**2. 创建灯具资产/预制件**：

```
封装完整的灯具：
1. 灯具模型（Mesh）
2. IES 光源（Light）
3. 自动设置正确的相对位置
4. 可以添加其他功能（开关、调光等）

优点：
✅ 一次设置，多次复用
✅ 确保位置始终正确
✅ 易于团队协作
```

**3. 文档化光度中心**：

```
在项目中保存元数据：
- 将 metadata.json 与 IES 文件放在一起
- 在资产管理系统中记录光度中心信息
- 创建使用说明文档

示例文档：
---
灯具名称：三 LED 吊灯
IES 文件：my_fixture.ies
光度中心（相对于模型底部中心）：
  X: 0.0 m
  Y: 0.0 m
  Z: 0.1 m
总流明：1800 lm
使用说明：在灯具模型中心上方 0.1m 处放置 IES 光源
---
```

**4. 自动化工作流（高级）**：

```
使用脚本自动化 IES 光源放置：

Python 示例（UE5）：
import unreal
import json

# 读取元数据
with open('my_fixture_metadata.json') as f:
    metadata = json.load(f)

# 获取相对偏移
offset = metadata['photometric_center']['relative_to_fixture_origin']

# 创建光源
light = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.PointLight,
    unreal.Vector(0, 0, 0)
)

# 设置 IES
ies_profile = unreal.load_asset('/Game/IES/my_fixture')
light.set_editor_property('ies_texture', ies_profile)

# 设置流明
light.set_editor_property('intensity', metadata['total_lumens'])

# 附加到灯具
fixture = unreal.EditorLevelLibrary.get_selected_level_actors()[0]
light.attach_to_actor(
    fixture,
    unreal.AttachmentRule.KEEP_RELATIVE,
    ''
)
light.set_actor_relative_location(
    unreal.Vector(offset['x'], offset['y'], offset['z'])
)
```

#### 常见问题和解决方案

**问题 1：光分布与 Blender 不一致**

```
原因：IES 光源位置不正确
解决：
1. 检查 metadata.json 中的光度中心位置
2. 确认 IES 光源是否在正确位置
3. 注意坐标系转换（Blender Z-up → 目标引擎）
```

**问题 2：亮度不正确**

```
原因：流明值设置错误
解决：
1. 使用 metadata.json 中的 total_lumens
2. 确认渲染引擎使用流明单位（而非瓦特）
3. 检查 IES Brightness Scale 是否为 1.0
```

**问题 3：不知道光度中心位置**

```
原因：metadata.json 文件丢失或未生成
解决：
1. 重新在 Blender 中生成 IES 文件
2. 确保插件生成了 metadata.json
3. 或在 Blender 插件 UI 中查看并记录光度中心
```

**问题 4：多个灯具实例位置混乱**

```
原因：手动管理位置容易出错
解决：
1. 使用 Socket/Attachment 方法
2. 或创建灯具预制件/Blueprint
3. 自动化脚本批量处理
```

### 高级光学效果

插件采用"黑盒测量"原则，完全依赖 Cycles 渲染引擎计算光学效果。这意味着插件不读取或判断材质参数，只测量 Cycles 渲染的最终结果。

#### 支持的光学效果

**基础效果（推荐，性能良好）**：
- ✅ **透射**（Transmission）：光线穿透半透明材质
- ✅ **折射**（IOR）：光线在材质界面改变方向
- ✅ **粗糙度散射**（Roughness）：表面粗糙度导致的光线散射
- ✅ **次表面散射**（SSS）：光在材质内部的穿透和散射
- ✅ **多次反射/透射**：光线在灯具内部的多次弹射

**高级效果（支持但有性能成本）**：
- ⚠️ **焦散**（Caustics）：光线聚焦产生的明亮图案
- ⚠️ **复杂几何细节**：使用位移贴图（Displacement）的精细表面

#### 焦散效果的技术说明

**Cycles 焦散计算能力**：

Cycles 理论上可以计算焦散效果，但需要：
- 极高的采样数（1000-4000+）
- 启用焦散设置（Render Properties > Light Paths > Caustics）
- 真实的几何细节（Displacement 或高精度建模）

**时间成本估算**：

渲染时间高度依赖于硬件配置。Cycles 支持 CPU 和 GPU 渲染，**GPU 渲染速度通常是 CPU 的 5-20 倍**。

**硬件配置说明**：
- **CPU 示例**：AMD Ryzen 9 5950X（16 核）或 Intel i9-12900K
- **GPU 示例**：NVIDIA RTX 3080（推荐）或 RTX 4090（最快）
- **推荐配置**：使用 GPU 渲染以获得最佳性能

**标准配置（无焦散，Normal 贴图）**：

预览模式（角度间隔 10°，采样数 64，703 个采样点）：
```
CPU 渲染：
- 每点渲染时间：1-2 秒
- 总时间：12-23 分钟

GPU (RTX 3080) 渲染：
- 每点渲染时间：0.2-0.3 秒
- 总时间：2.4-3.5 分钟

GPU (RTX 4090) 渲染：
- 每点渲染时间：0.1-0.15 秒
- 总时间：1.2-1.8 分钟
```

生产模式（角度间隔 5°，采样数 256，2701 个采样点）：
```
CPU 渲染：
- 每点渲染时间：3-5 秒
- 总时间：2.3-3.8 小时

GPU (RTX 3080) 渲染：
- 每点渲染时间：0.5-0.8 秒
- 总时间：23-36 分钟

GPU (RTX 4090) 渲染：
- 每点渲染时间：0.25-0.4 秒
- 总时间：11-18 分钟
```

**焦散配置（真实几何 + Displacement）**：

焦散模式（角度间隔 10°，采样数 2000，703 个采样点）：
```
CPU 渲染：
- 每点渲染时间：5-10 分钟
- 总时间：58-117 小时（2.4-4.9 天）
- 实用性：❌ 不推荐

GPU (RTX 3080) 渲染：
- 每点渲染时间：0.8-1.5 分钟
- 总时间：9.4-17.6 小时
- 实用性：⚠️ 仅限特殊需求

GPU (RTX 4090) 渲染：
- 每点渲染时间：0.4-0.8 分钟
- 总时间：4.7-9.4 小时
- 实用性：⚠️ 仅限特殊需求
```

**关键结论**：
- ✅ **强烈推荐使用 GPU 渲染**（速度提升 5-20 倍）
- ✅ **使用 Normal 贴图**：即使在 GPU 上，也只需几分钟到半小时
- ⚠️ **焦散效果**：即使使用顶级 GPU，仍需 5-18 小时
- ❌ **CPU 焦散渲染**：需要数天时间，不实用

#### 压花/纹理玻璃的实用方法

**推荐方法：Normal 贴图 + 粗糙度（实用平衡）**

对于压花玻璃、磨砂玻璃、纹理玻璃等材质，**强烈推荐**使用 Normal 贴图而非真实几何建模：

**优点**：
- ✅ 渲染速度快（与普通材质相同）
- ✅ 可以模拟表面细节和光线散射
- ✅ 适合 99% 的建筑可视化和产品展示场景
- ✅ 生成时间在可接受范围内（10-60 分钟）

**实现步骤**：
```
1. 准备 Normal 贴图：
   - 从材料供应商获取
   - 或使用程序纹理生成（Noise、Voronoi 等）
   - 或从高精度模型烘焙

2. 设置 Principled BSDF：
   - Base Color: 白色或浅色
   - Transmission: 0.85-0.95（根据材料透明度）
   - Roughness: 0.3-0.6（根据雾度调整）
   - IOR: 1.5（玻璃）或 1.49（亚克力）
   - Normal: 连接 Normal Map 节点
   - Subsurface Weight: 0.2-0.4（可选，增强散射）

3. Normal Map 节点设置：
   - Space: Tangent
   - Strength: 0.5-2.0（根据压花深度调整）
```

**效果对比**：

```
真实几何（Displacement）：
- 物理准确度：★★★★★
- 视觉效果：★★★★★（包含真实焦散）
- 渲染时间（GPU）：★☆☆☆☆（5-18 小时）
- 渲染时间（CPU）：☆☆☆☆☆（2-5 天）
- 实用性：★☆☆☆☆
- 适用场景：科研、极致准确性要求

Normal 贴图：
- 物理准确度：★★★★☆（足够准确）
- 视觉效果：★★★★☆（无焦散，但整体光分布准确）
- 渲染时间（GPU）：★★★★★（几分钟到半小时）
- 渲染时间（CPU）：★★★☆☆（10 分钟到 4 小时）
- 实用性：★★★★★
- 适用场景：建筑可视化、产品展示、快速迭代
```

**为什么 Normal 贴图足够好**：

1. **IES 文件的用途**：
   - IES 文件主要用于建筑可视化和照明设计
   - 关注的是整体光分布，而非微观焦散细节
   - 渲染引擎（V-Ray、Unreal）会根据 IES 数据重新计算光照

2. **视觉效果**：
   - Normal 贴图可以准确模拟表面粗糙度导致的光线散射
   - 配合 Roughness 和 SSS，可以达到视觉上非常接近真实的效果
   - 对于大多数观察距离，与真实几何难以区分

3. **工程实践**：
   - 专业灯具厂商的 IES 文件也是基于测量，而非完美的光学模拟
   - 实验室测量本身也有误差和近似
   - Normal 贴图方法在工程精度范围内

#### 材质配置示例

**示例 1：磨砂玻璃灯罩**
```
Principled BSDF:
- Transmission: 0.85
- Roughness: 0.4
- IOR: 1.5
- Subsurface Weight: 0.3
- Subsurface Radius: [5.0, 5.0, 5.0] mm
- Normal: Noise Texture (Scale: 50, Strength: 1.0)

预期效果：柔和、均匀的光分布
渲染时间（GPU RTX 3080）：2-4 分钟（预览模式）
渲染时间（CPU）：12-20 分钟（预览模式）
```

**示例 2：压花玻璃灯罩**
```
Principled BSDF:
- Transmission: 0.90
- Roughness: 0.3
- IOR: 1.5
- Normal: Normal Map（压花纹理，Strength: 1.5）

预期效果：带有纹理特征的光分布
渲染时间（GPU RTX 3080）：2-4 分钟（预览模式）
渲染时间（CPU）：12-20 分钟（预览模式）
```

**示例 3：乳白亚克力**
```
Principled BSDF:
- Transmission: 0.80
- Roughness: 0.5
- IOR: 1.49
- Subsurface Weight: 0.5
- Subsurface Radius: [10.0, 10.0, 10.0] mm
- Normal: 可选（轻微 Noise）

预期效果：高度散射、柔和的光分布
渲染时间（GPU RTX 3080）：3-5 分钟（预览模式）
渲染时间（CPU）：15-30 分钟（预览模式）
```

#### 何时使用真实几何

**仅在以下情况考虑使用 Displacement**：
- 科研项目，需要发表论文
- 需要验证光学设计的极端情况
- 有充足的计算时间（数天）
- 需要捕捉微观焦散效果

**对于 99% 的实际项目，Normal 贴图是最佳选择。**

#### 插件的"黑盒测量"原则

**核心理念**：

插件不关心光学效果是如何产生的，只测量最终结果：

```
用户准备场景：
- 设置材质（Normal 贴图、Roughness、SSS 等）
- Cycles 根据材质参数计算光线传播

插件执行测量：
- 在各采样点"拍照"（渲染）
- 读取渲染图像的亮度值
- 不读取、不判断材质参数

生成 IES 文件：
- 记录各方向的光强分布
- 不关心光强是直射、散射还是焦散
```

**类比实验室测量**：

```
物理实验室                     数字仿真（本插件）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
光度计不分析材质成分          插件不读取材质参数
↓                            ↓
只测量最终的光输出            只测量 Cycles 渲染结果
↓                            ↓
记录各方向的光强              记录各采样点的亮度值
↓                            ↓
生成 IES 文件                生成 IES 文件
```

**优势**：
- ✅ 简单可靠：不需要解析复杂的材质节点树
- ✅ 通用性强：支持任何材质配置，包括复杂的节点组合
- ✅ 物理准确：完全依赖 Cycles 的物理计算
- ✅ 符合实验室流程：模拟真实测量过程

#### 最佳实践建议

1. **优先使用 Normal 贴图**：
   - 对于所有纹理、压花、磨砂表面
   - 配合 Roughness 和 SSS 参数
   - 可以达到视觉上足够准确的效果

2. **合理设置采样数**：
   - 预览模式：64 采样（快速验证）
   - 生产模式：256 采样（最终输出）
   - 避免过高采样数（除非真的需要焦散）

3. **使用真实物理参数**：
   - 从材料供应商获取透射率、IOR、雾度数据
   - 使用 LED 规格书中的流明值
   - 确保场景单位设置正确（米）

4. **迭代优化**：
   - 先用低采样数（32-64）快速测试
   - 验证光分布形状正确
   - 最后用高采样数生成最终 IES 文件

### 硬件配置与性能优化

#### 推荐硬件配置

**最低配置**：
- CPU：4 核心处理器（Intel i5 或 AMD Ryzen 5）
- 内存：16 GB RAM
- 渲染设备：CPU
- 预期性能：预览模式 20-30 分钟，生产模式 3-5 小时

**推荐配置**：
- CPU：8 核心以上处理器（Intel i7/i9 或 AMD Ryzen 7/9）
- GPU：NVIDIA RTX 3060 或更高（8GB+ VRAM）
- 内存：32 GB RAM
- 渲染设备：GPU (CUDA/OptiX)
- 预期性能：预览模式 3-5 分钟，生产模式 20-40 分钟

**高性能配置**：
- CPU：16 核心以上处理器（AMD Threadripper 或 Intel i9-13900K）
- GPU：NVIDIA RTX 4080/4090（16GB+ VRAM）
- 内存：64 GB RAM
- 渲染设备：GPU (OptiX)
- 预期性能：预览模式 1-2 分钟，生产模式 10-20 分钟

#### Cycles 渲染设备配置

**启用 GPU 渲染**（强烈推荐）：

1. 打开 Blender 偏好设置：
   - Edit > Preferences > System

2. 选择 Cycles 渲染设备：
   - Cycles Render Devices: CUDA / OptiX / HIP / Metal
   - 勾选可用的 GPU 设备

3. 在渲染属性中选择设备：
   - Render Properties > Device: GPU Compute

**GPU 类型说明**：
- **OptiX**（推荐）：NVIDIA RTX 系列专用，最快，支持硬件加速光线追踪
- **CUDA**：所有 NVIDIA GPU，兼容性好
- **HIP**：AMD GPU
- **Metal**：Apple Silicon (M1/M2/M3)

#### 性能对比表

**预览模式（角度间隔 10°，采样数 64，703 个采样点）**：

| 硬件配置 | 每点时间 | 总时间 | 性能评级 |
|---------|---------|--------|---------|
| CPU (i5-12400) | 2-3 秒 | 23-35 分钟 | ★★☆☆☆ |
| CPU (Ryzen 9 5950X) | 1-2 秒 | 12-23 分钟 | ★★★☆☆ |
| GPU (RTX 3060) | 0.3-0.5 秒 | 3.5-5.8 分钟 | ★★★★☆ |
| GPU (RTX 3080) | 0.2-0.3 秒 | 2.4-3.5 分钟 | ★★★★★ |
| GPU (RTX 4090) | 0.1-0.15 秒 | 1.2-1.8 分钟 | ★★★★★ |

**生产模式（角度间隔 5°，采样数 256，2701 个采样点）**：

| 硬件配置 | 每点时间 | 总时间 | 性能评级 |
|---------|---------|--------|---------|
| CPU (i5-12400) | 5-8 秒 | 3.8-6 小时 | ★☆☆☆☆ |
| CPU (Ryzen 9 5950X) | 3-5 秒 | 2.3-3.8 小时 | ★★☆☆☆ |
| GPU (RTX 3060) | 0.8-1.2 秒 | 36-54 分钟 | ★★★☆☆ |
| GPU (RTX 3080) | 0.5-0.8 秒 | 23-36 分钟 | ★★★★☆ |
| GPU (RTX 4090) | 0.25-0.4 秒 | 11-18 分钟 | ★★★★★ |

#### 性能优化建议

**1. 渲染设备优化**：
- ✅ 优先使用 GPU 渲染（速度提升 5-20 倍）
- ✅ NVIDIA RTX 系列使用 OptiX（比 CUDA 快 20-30%）
- ✅ 确保 GPU 驱动程序为最新版本

**2. 场景优化**：
- ✅ 使用 Normal 贴图代替 Displacement（速度提升 10-100 倍）
- ✅ 避免过于复杂的材质节点树
- ✅ 使用简化的灯具几何（保留主要形状即可）
- ⚠️ 避免使用体积雾（Volume）效果（极慢）

**3. Cycles 设置优化**：
- ✅ 启用去噪（Denoising）：减少所需采样数
- ✅ 使用自适应采样（Adaptive Sampling）：自动优化采样
- ✅ 设置合理的 Max Bounces：
  - 透明材质：Transmission Bounces = 8-12
  - 一般场景：Total Bounces = 12
  - 避免过高设置（> 20）

**4. 采样策略**：
- ✅ 预览阶段使用低采样数（32-64）快速验证
- ✅ 最终输出使用中等采样数（256）
- ⚠️ 避免盲目提高采样数（> 512 通常无必要）

**5. 批量处理**：
- ✅ 如需生成多个 IES 文件，使用夜间批量处理
- ✅ 利用 Blender 命令行模式自动化处理
- ✅ 考虑使用渲染农场（Render Farm）处理大批量任务

#### 内存管理

**VRAM 需求估算**：
- 简单灯具（< 100K 面）：2-4 GB VRAM
- 中等灯具（100K-500K 面）：4-8 GB VRAM
- 复杂灯具（> 500K 面）：8-16 GB VRAM

**内存不足时的解决方案**：
1. 简化灯具几何（使用 Decimate 修改器）
2. 降低纹理分辨率
3. 使用 CPU 渲染（速度慢但无 VRAM 限制）
4. 分批处理采样点（修改插件代码）

#### 时间成本总结

**关键结论**：
- 🚀 **GPU 渲染是必须的**：速度提升 5-20 倍
- ✅ **Normal 贴图 + GPU**：几分钟到半小时（最佳选择）
- ⚠️ **真实几何 + GPU**：5-18 小时（仅限特殊需求）
- ❌ **真实几何 + CPU**：2-5 天（不实用）

**实际建议**：
- 对于 99% 的项目：使用 GPU + Normal 贴图
- 预算有限：至少使用 RTX 3060 级别 GPU
- 追求速度：使用 RTX 4080/4090
- 无 GPU：使用 CPU 但接受较长等待时间

## 架构

### 模块依赖关系

```
用户手动准备场景（Blender）
    ↓
插件启动
    ↓
场景验证器 (scene_validator.py)
    ↓
采样器 (sampler.py)
    ↓
IES生成器 (ies_generator.py)
    ↓
输出管理器 (output_manager.py)
    ↓
IES 文件输出
```

### 模块职责

**场景验证器（Scene Validator）**
- 检查当前场景是否包含光源
- 验证渲染引擎是否为 Cycles
- 提示用户选择要测量的光源（如有多个）
- 验证光源类型（点光源或面光源）

**采样器（Sampler）**
- 实现 IESNA LM-63 C-Plane 球面采样算法
- 计算采样点位置（球面坐标转换）
- 在每个采样点创建虚拟传感器（相机）
- 执行 Cycles 渲染并提取亮度数据
- 存储测量结果到 NumPy 数组
- 提供进度反馈

**IES生成器（IES Generator）**
- 执行单位校准（Blender 单位 → 坎德拉）
- 生成 LM-63-2002 标准文件头
- 格式化角度和光强数据
- 验证输出合规性

**输出管理器（Output Manager）**
- 处理文件路径和目录创建
- 写入 IES 文件到磁盘
- 验证文件完整性
- 处理覆盖确认

**UI 面板（UI Panel）**
- 在 3D 视图侧边栏显示插件面板
- 提供参数配置界面（角度间隔、采样数、测量距离）
- 显示光源选择下拉菜单
- 显示进度条和状态信息
- 提供"生成 IES"按钮和"取消"按钮

### 坐标系约定

系统需要处理两个坐标系之间的转换：

**Blender 坐标系（Z-up 右手系）**
- X 轴：右
- Y 轴：前
- Z 轴：上

**IES 坐标系（Y-up）**
- X 轴：右
- Y 轴：上
- Z 轴：前

转换公式：
```
IES_X = Blender_X
IES_Y = Blender_Z
IES_Z = Blender_Y
```

## 组件和接口

### 场景验证器（scene_validator.py）

#### 主要函数

```python
def validate_scene() -> dict:
    """
    验证当前 Blender 场景配置
    
    返回:
        验证结果字典:
        {
            'is_valid': bool,
            'has_lights': bool,
            'light_objects': List[bpy.types.Object],
            'render_engine': str,
            'errors': List[str],
            'warnings': List[str]
        }
    """
    pass

def get_light_sources() -> List[bpy.types.Object]:
    """
    获取场景中所有光源对象
    
    返回:
        光源对象列表（点光源和面光源）
    """
    pass

def validate_light_source(light_obj: bpy.types.Object) -> bool:
    """
    验证光源类型是否支持
    
    参数:
        light_obj: 光源对象
    
    返回:
        True 如果是点光源或面光源
    """
    pass

def check_render_engine() -> str:
    """
    检查当前渲染引擎
    
    返回:
        渲染引擎名称 ('CYCLES', 'EEVEE', 等)
    """
    pass

def get_light_properties(light_obj: bpy.types.Object) -> dict:
    """
    获取光源属性
    
    返回:
        {
            'type': str,  # 'POINT' 或 'AREA'
            'location': Tuple[float, float, float],
            'power': float,  # 瓦特
            'color': Tuple[float, float, float]
        }
    """
    pass
```

#### 接口规范

- **输入**：当前 Blender 场景上下文
- **输出**：验证结果字典，光源对象列表
- **错误处理**：返回错误和警告列表，不抛出异常

### 采样器（sampler.py）

#### 球面采样原理

**测量距离与灯具包裹性**：

IES 测量使用球面采样方法，虚拟传感器在以光源为球心、用户指定距离为半径的球面上移动。这个球面会自动"包裹"整个灯具，无需人工调整。

```
关键参数：
- 光源位置：用户在 Blender 中设置（例如 0, 0, 0）
- 测量距离：用户在插件中配置（默认 5 米）
- 采样球面：插件自动计算，半径 = 测量距离

测量距离选择建议：
- 测量距离应为灯具最大尺寸的 5-10 倍
- 例如：直径 0.5m 的灯具 → 使用 2.5-5m 测量距离
- 距离越远，越接近"远场"条件，符合 IES 标准
```

**自动包裹机制**：
1. 插件读取用户选择的光源位置（例如 x=0, y=0, z=0）
2. 以该位置为球心，测量距离为半径创建虚拟球面
3. 在球面上按角度间隔计算采样点位置
4. 每个采样点的传感器朝向球心（光源）
5. 只要测量距离 > 灯具尺寸，球面就完全包裹灯具

用户**不需要**手动调整采样点位置，算法自动处理。

**光源参数说明**：
- **必需参数**：
  - 光源强度（Strength）：总流明值（例如 1800 lm）
  - 光源尺寸：
    - 点光源：Radius（半径，例如 0.01m）
    - 面光源：Size X 和 Size Y（长度和宽度，例如 1.0m × 0.03m）
- **可选参数**：
  - 色温或颜色：影响渲染颜色但不影响 IES 光强分布
- **不需要的参数**：
  - 功率（瓦特）：IES 计算不需要电功率

**光源类型选择**：
- **点光源（Point Light）**：
  - 适用于：单个 LED 芯片、小型灯珠、球形灯泡
  - 参数：Strength + Radius
  
- **面光源（Area Light）**：
  - 适用于：灯管、LED 灯带、发光面板、灯片
  - 参数：Strength + Shape + Size
  - 形状：Rectangle（矩形）、Square（正方形）、Disk（圆形）
  - 示例：
    - 灯管：Rectangle，Size X = 长度，Size Y = 直径
    - 面板灯：Square，Size = 面板尺寸
    - LED 灯带：Rectangle，Size X = 长度，Size Y = 宽度

**流明值获取方式**：
1. 直接从 LED 规格书查看流明值
2. 或通过计算：功率（W）× 光效（lm/W）= 流明（lm）
   - 例如：15W × 120 lm/W = 1800 lm

#### 主要函数

```python
def calculate_sampling_points(angular_interval: float, 
                             distance: float,
                             light_position: Tuple[float, float, float]) -> List[dict]:
    """
    计算球面采样点位置和角度
    
    参数:
        angular_interval: 角度间隔（度）
        distance: 传感器距离光源的距离（米）
        light_position: 光源位置 (x, y, z)
    
    返回:
        采样点列表，每个元素为:
        {
            'position': (x, y, z),
            'theta': float,  # 垂直角度
            'phi': float     # 水平角度
        }
    """
    pass

def spherical_to_cartesian(theta: float, phi: float, r: float,
                          center: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    球面坐标转笛卡尔坐标（Blender Z-up）
    
    参数:
        theta: 垂直角（0° = 天顶/正上方，90° = 水平，180° = 天底/正下方）
        phi: 水平角（0° = X 轴正方向）
        r: 半径
        center: 球心位置（光源位置）
    
    返回:
        (x, y, z) 笛卡尔坐标
    """
    pass

def create_virtual_sensor(position: Tuple[float, float, float],
                         target: Tuple[float, float, float]) -> bpy.types.Object:
    """
    在指定位置创建虚拟传感器（相机）
    
    参数:
        position: 相机位置
        target: 相机朝向目标（光源位置）
    
    返回:
        相机对象
    """
    pass

def render_at_sensor(camera: bpy.types.Object, samples: int) -> float:
    """
    在传感器位置渲染并提取亮度
    
    参数:
        camera: 相机对象
        samples: Cycles 采样数
    
    返回:
        测量的亮度值（Blender 内部单位）
    """
    pass

def collect_spherical_data(light_obj: bpy.types.Object,
                          angular_interval: float,
                          distance: float,
                          samples: int,
                          progress_callback=None) -> dict:
    """
    执行完整的球面采样
    
    参数:
        light_obj: 要测量的光源对象
        angular_interval: 角度间隔（度）
        distance: 采样距离（米）
        samples: Cycles 采样数
        progress_callback: 进度回调函数 callback(current, total, message)
    
    返回:
        {
            'vertical_angles': np.ndarray,    # 垂直角度数组
            'horizontal_angles': np.ndarray,  # 水平角度数组
            'luminance_data': np.ndarray,     # 亮度数据 (N_theta, N_phi)
            'light_position': Tuple[float, float, float],
            'total_samples': int
        }
    """
    pass
```

#### 球面采样算法

IESNA LM-63 C-Plane 坐标系定义：
- **垂直角（Theta）**：0° 到 180°
  - 0° = 天顶（正上方，+Z）
  - 90° = 水平面
  - 180° = 天底（正下方，-Z）
- **水平角（Phi）**：0° 到 360°
  - 0° = 参考方向（+X 轴）
  - 逆时针旋转

采样点计算（Blender Z-up 坐标系）：
```python
对于每个 theta 从 0° 到 180°（步长 = angular_interval）:
    对于每个 phi 从 0° 到 360°（步长 = angular_interval）:
        # 球面坐标转笛卡尔坐标
        x = light_x + distance * sin(theta) * cos(phi)
        y = light_y + distance * sin(theta) * sin(phi)
        z = light_z + distance * cos(theta)
        
        # 在位置 (x, y, z) 创建虚拟传感器
        camera = create_virtual_sensor((x, y, z), light_position)
        
        # 执行渲染
        luminance = render_at_sensor(camera, samples)
        
        # 存储到数组
        data[theta_index, phi_index] = luminance
        
        # 更新进度
        if progress_callback:
            progress_callback(current, total, f"θ={theta}°, φ={phi}°")
```

### IES生成器（ies_generator.py）

#### 主要函数

```python
def calibrate_to_candela(luminance_data: np.ndarray,
                        lumens: float,
                        distance: float,
                        angular_interval: float) -> np.ndarray:
    """
    将 Blender 亮度单位校准为坎德拉
    
    参数:
        luminance_data: 原始亮度数据数组 (N_theta, N_phi)
        lumens: 光源总光通量（流明）
        distance: 采样距离（米）
        angular_interval: 角度间隔（度）
    
    返回:
        校准后的坎德拉值数组
    
    校准原理:
        1. 计算所有采样点的总亮度
        2. 根据立体角计算校准因子
        3. 应用因子将亮度转换为坎德拉
    """
    pass

def generate_ies_header(lumens: float,
                       num_vertical: int,
                       num_horizontal: int,
                       fixture_name: str = "Kiro Generated") -> str:
    """
    生成 IESNA LM-63-2002 文件头
    
    参数:
        lumens: 总光通量
        num_vertical: 垂直角度数量
        num_horizontal: 水平角度数量
        fixture_name: 灯具名称
    
    返回:
        格式化的文件头字符串
    """
    pass

def format_ies_data(candela_data: np.ndarray,
                   vertical_angles: np.ndarray,
                   horizontal_angles: np.ndarray) -> str:
    """
    格式化 IES 数据部分
    
    参数:
        candela_data: 坎德拉值数组 (N_theta, N_phi)
        vertical_angles: 垂直角度数组
        horizontal_angles: 水平角度数组
    
    返回:
        格式化的数据字符串
    """
    pass

def blender_to_ies_coordinates(vertical_angles: np.ndarray,
                               horizontal_angles: np.ndarray,
                               candela_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    将 Blender Z-up 坐标系转换为 IES Y-up 坐标系
    
    参数:
        vertical_angles: Blender 垂直角度
        horizontal_angles: Blender 水平角度
        candela_data: 坎德拉数据
    
    返回:
        (ies_vertical, ies_horizontal, ies_candela)
    """
    pass

def validate_ies_compliance(ies_content: str) -> Tuple[bool, List[str]]:
    """
    验证 IES 文件是否符合 LM-63-2002 标准
    
    返回:
        (is_valid, error_messages)
    """
    pass

def generate_ies_file(sampling_result: dict,
                     lumens: float,
                     fixture_name: str = "Kiro Generated") -> str:
    """
    从采样结果生成完整的 IES 文件内容
    
    参数:
        sampling_result: collect_spherical_data() 的返回值
        lumens: 光源总光通量
        fixture_name: 灯具名称
    
    返回:
        完整的 IES 文件内容字符串
    """
    pass
```

#### IES 文件格式

```
IESNA:LM-63-2002
[MANUFAC] Kiro IES Generator
[LUMCAT] {fixture_name}
[LUMINAIRE] Generated from Blender scene
[LAMPCAT] Virtual Light Source
[LAMP] 1
[BALLAST] None
[TILT] NONE
1 {lumens} 1 {num_vertical_angles} {num_horizontal_angles} 1 1 0 0 0
1.0 1.0 0.0
{vertical_angles}
{horizontal_angles}
{candela_values}
```

### 输出管理器（output_manager.py）

#### 主要函数

```python
def write_ies_file(ies_content: str, output_path: str, overwrite: bool = False) -> dict:
    """
    写入 IES 文件到磁盘
    
    参数:
        ies_content: IES 文件内容字符串
        output_path: 输出文件路径
        overwrite: 是否覆盖现有文件
    
    返回:
        {
            'success': bool,
            'path': str,
            'size': int
        }
    
    异常:
        FileExistsError: 文件已存在且 overwrite=False
        IOError: 写入失败
    """
    pass

def ensure_directory_exists(path: str):
    """确保目录存在，如不存在则创建"""
    pass

def verify_file_written(path: str) -> dict:
    """
    验证文件已成功写入
    
    返回:
        {
            'exists': bool,
            'size': int,
            'path': str,
            'readable': bool
        }
    """
    pass

def get_default_output_path(light_name: str) -> str:
    """
    生成默认输出路径
    
    参数:
        light_name: 光源对象名称
    
    返回:
        默认输出路径（当前 .blend 文件目录 + 光源名称.ies）
    """
    pass
```

## 数据模型

### 采样配置

```python
@dataclass
class SamplingConfig:
    """采样配置数据类"""
    angular_interval: float  # 角度间隔（度）
    distance: float          # 采样距离（米）
    samples: int             # Cycles 采样数
    
    def validate(self) -> bool:
        """验证参数范围"""
        return (1 <= self.angular_interval <= 45 and
                0.1 <= self.distance <= 100 and
                1 <= self.samples <= 4096)
    
    def estimate_time(self) -> str:
        """估计完成时间"""
        num_theta = int(180 / self.angular_interval) + 1
        num_phi = int(360 / self.angular_interval) + 1
        total_samples = num_theta * num_phi
        
        # 假设每个采样点 1-3 秒
        seconds = total_samples * (1 + self.samples / 64)
        minutes = seconds / 60
        
        if minutes < 60:
            return f"{int(minutes)} 分钟"
        else:
            hours = minutes / 60
            return f"{hours:.1f} 小时"
    
    @staticmethod
    def preview() -> 'SamplingConfig':
        """预览模式预设"""
        return SamplingConfig(
            angular_interval=10.0,
            distance=5.0,
            samples=64
        )
    
    @staticmethod
    def production() -> 'SamplingConfig':
        """生产模式预设"""
        return SamplingConfig(
            angular_interval=5.0,
            distance=5.0,
            samples=256
        )
```

### 场景验证结果

```python
@dataclass
class SceneValidation:
    """场景验证结果数据类"""
    is_valid: bool
    has_lights: bool
    light_objects: List[bpy.types.Object]
    render_engine: str
    errors: List[str]
    warnings: List[str]
    
    def __str__(self) -> str:
        """格式化验证结果为可读字符串"""
        if self.is_valid:
            result = f"✓ 场景验证通过\n"
            result += f"  - 找到 {len(self.light_objects)} 个光源\n"
            result += f"  - 渲染引擎: {self.render_engine}"
            if self.warnings:
                result += "\n警告:\n" + "\n".join(f"  ⚠ {w}" for w in self.warnings)
            return result
        else:
            return f"✗ 场景验证失败:\n" + "\n".join(f"  - {e}" for e in self.errors)
```

### 采样结果

```python
@dataclass
class SamplingResult:
    """采样结果数据类"""
    vertical_angles: np.ndarray      # 垂直角度数组（度）
    horizontal_angles: np.ndarray    # 水平角度数组（度）
    luminance_data: np.ndarray       # 亮度数据 (N_theta, N_phi)
    light_position: Tuple[float, float, float]
    total_samples: int
    elapsed_time: float              # 耗时（秒）
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'vertical_angles': self.vertical_angles,
            'horizontal_angles': self.horizontal_angles,
            'luminance_data': self.luminance_data,
            'light_position': self.light_position,
            'total_samples': self.total_samples,
            'elapsed_time': self.elapsed_time
        }
```

### 光度学数据

```python
@dataclass
class PhotometricData:
    """光度学数据数据类"""
    vertical_angles: np.ndarray      # 垂直角度数组（度）
    horizontal_angles: np.ndarray    # 水平角度数组（度）
    candela_values: np.ndarray       # 坎德拉值数组 (N_theta, N_phi)
    lumens: float                    # 总光通量（流明）
    distance: float                  # 测量距离（米）
    fixture_name: str                # 灯具名称
    
    def to_ies(self) -> str:
        """转换为 IES 文件格式"""
        from ies_generator import generate_ies_file
        return generate_ies_file(
            {
                'vertical_angles': self.vertical_angles,
                'horizontal_angles': self.horizontal_angles,
                'luminance_data': self.candela_values
            },
            self.lumens,
            self.fixture_name
        )
```


## 正确性属性

属性是关于系统行为的特征或规则，应该在所有有效执行中保持为真。以下属性将通过基于属性的测试来验证，每个属性将在至少 100 次随机生成的输入上进行测试。

### 属性 1：场景光源检测

*对于任何*包含至少一个点光源或面光源的 Blender 场景，场景验证器应该正确识别所有光源对象。

**验证需求：1.1**

### 属性 2：光源类型验证

*对于任何*光源对象，验证函数应该正确判断其类型是否为支持的类型（点光源或面光源）。

**验证需求：1.4**

### 属性 3：渲染引擎检测

*对于任何*Blender 场景，场景验证器应该正确识别当前渲染引擎类型。

**验证需求：1.5**

### 属性 4：采样参数验证

*对于任何*采样配置参数，系统应该验证参数是否在有效范围内（角度间隔 1-45°，距离 0.1-100m，采样数 1-4096）。

**验证需求：2.5**

### 属性 5：采样点数量计算

*对于任何*角度间隔值，计算的采样点总数应该等于 (180/间隔 + 1) × (360/间隔 + 1)。

**验收需求：2.4**

### 属性 6：球面坐标距离不变性

*对于任何*角度对（theta, phi）和距离 r，球面到笛卡尔坐标转换应该产生一个点，该点到球心的距离等于 r（在浮点精度范围内）。

**验证需求：3.5**

### 属性 7：坐标系转换往返

*对于任何*在 Blender Z-up 坐标系中的 3D 点，转换到 IES Y-up 坐标系然后再转换回来，应该得到原始点（在浮点精度范围内）。

**验证需求：3.4**

### 属性 8：虚拟传感器朝向

*对于任何*传感器位置和光源位置，创建的虚拟传感器（相机）应该精确朝向光源中心。

**验证需求：4.2**

### 属性 9：传感器清理

*对于任何*渲染操作，完成后临时相机对象应该被删除，场景中不应残留临时对象。

**验证需求：4.5**

### 属性 10：数据存储格式

*对于任何*采样操作，存储的测量数据应该是 NumPy 数组类型，并且数组维度应该与采样点数量匹配。

**验证需求：5.1, 5.2**

### 属性 11：渲染错误恢复

*对于任何*包含部分失败渲染的采样序列，采样器应该记录错误但继续处理剩余的采样点。

**验证需求：5.3**

### 属性 12：数据完整性验证

*对于任何*完成的采样操作，系统应该验证数据数组中没有缺失值（NaN 或 None）。

**验证需求：5.4**

### 属性 13：单位校准一致性

*对于任何*亮度数据数组和校准参数，校准函数应该对所有数据点应用相同的转换因子。

**验证需求：6.5**

### 属性 14：校准参数验证

*对于任何*无效的校准参数（零或负流明值），校准函数应该检测并报告错误。

**验证需求：6.4**

### 属性 15：IES 文件头合规性

*对于任何*生成的 IES 文件头，它应该包含所有 IESNA LM-63-2002 标准要求的字段。

**验证需求：7.1, 7.2**

### 属性 16：角度数据排序

*对于任何*角度数据集（垂直和水平），格式化后的输出应该以严格升序排列。

**验证需求：7.3**

### 属性 17：坎德拉值格式化

*对于任何*坎德拉值数组，格式化输出应该符合 LM-63-2002 规范的数值格式要求。

**验证需求：7.4, 7.5**

### 属性 18：文件写入验证

*对于任何*有效的输出路径和 IES 内容，写入操作成功后，文件应该存在于指定位置。

**验证需求：8.1, 8.4**

### 属性 19：目录自动创建

*对于任何*不存在的目录路径，输出管理器应该创建所有必要的父目录。

**验证需求：8.2**

### 属性 20：文件覆盖保护

*对于任何*已存在的文件路径，如果 overwrite=False，系统应该拒绝写入并提示用户。

**验证需求：8.3**

### 属性 21：进度报告完整性

*对于任何*采样操作，进度回调应该在每个采样点完成时被调用，并提供当前进度信息。

**验证需求：9.1, 9.2, 9.3**

### 属性 22：取消操作安全性

*对于任何*正在进行的采样操作，用户取消时系统应该安全停止并清理所有临时对象。

**验证需求：9.4**

### 属性 23：错误日志完整性

*对于任何*模块中发生的错误，日志条目应该包含时间戳、模块名称和错误描述。

**验证需求：10.1, 10.2**

### 属性 24：错误恢复建议

*对于任何*场景配置错误，错误消息应该包含具体的修正建议。

**验证需求：10.3**

### 属性 25：异常堆栈跟踪

*对于任何*未预期的异常，系统应该记录完整的堆栈跟踪信息。

**验证需求：10.5**

## 错误处理

### 错误分类

系统将错误分为三类：

1. **可恢复错误**：系统可以继续运行
   - 单个采样点渲染失败
   - 部分场景验证警告

2. **用户错误**：需要用户纠正
   - 场景中没有光源
   - 渲染引擎不是 Cycles
   - 无效的参数值
   - 无效的输出路径

3. **致命错误**：系统无法继续
   - Blender API 初始化失败
   - 内存不足
   - 关键文件写入失败

### 错误处理策略

```python
class KiroError(Exception):
    """基础错误类"""
    def __init__(self, message: str, module: str, recoverable: bool = False):
        self.message = message
        self.module = module
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        super().__init__(self.message)

class SceneValidationError(KiroError):
    """场景验证错误"""
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message, "SceneValidator", recoverable=False)
        self.errors = errors

class SamplingError(KiroError):
    """采样错误"""
    def __init__(self, message: str, position: Tuple[float, float, float]):
        super().__init__(message, "Sampler", recoverable=True)
        self.position = position

class CalibrationError(KiroError):
    """校准错误"""
    def __init__(self, message: str, lumens: float):
        super().__init__(message, "IESGenerator", recoverable=False)
        self.lumens = lumens
```

### 错误日志格式

```
[2024-01-15 14:32:45] [ERROR] [scene_validator] 场景验证失败
  - 未找到光源对象
  建议：在场景中添加至少一个点光源或面光源

[2024-01-15 14:35:12] [WARNING] [sampler] 采样点渲染失败
  - 位置: (5.0, 0.0, 0.0)
  - 角度: θ=90°, φ=0°
  继续处理剩余采样点...

[2024-01-15 14:40:33] [INFO] [sampler] 采样完成
  - 总采样点: 666
  - 成功: 665
  - 失败: 1
  - 耗时: 8.5 分钟
```

### 资源清理

所有模块应该确保资源正确清理：

```python
class Sampler:
    def __init__(self):
        self.temp_camera = None
    
    def sample(self, ...):
        try:
            # 执行采样
            pass
        finally:
            # 清理临时对象
            if self.temp_camera:
                bpy.data.objects.remove(self.temp_camera)
                self.temp_camera = None
```

## 测试策略

### 双重测试方法

系统将使用单元测试和基于属性的测试的组合：

**单元测试**：
- 验证特定示例和边缘情况
- 测试错误条件和异常处理
- 验证模块交互
- 测试具体的采样配置（预览、生产模式）
- 测试 UI 组件行为

**基于属性的测试**：
- 验证跨所有输入的通用属性
- 通过随机化提供全面的输入覆盖
- 每个属性测试最少 100 次迭代
- 使用 Python 的 `hypothesis` 库进行属性测试

### 测试配置

```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(
    theta=st.floats(min_value=0, max_value=180),
    phi=st.floats(min_value=0, max_value=360),
    distance=st.floats(min_value=0.1, max_value=100)
)
def test_spherical_coordinate_distance(theta, phi, distance):
    """
    属性 6：球面坐标距离不变性
    Feature: kiro-ies-generator, Property 6: 对于任何角度对和距离，
    球面到笛卡尔转换应该产生距球心指定距离的点
    """
    center = (0, 0, 0)
    x, y, z = spherical_to_cartesian(theta, phi, distance, center)
    calculated_distance = math.sqrt(x**2 + y**2 + z**2)
    assert math.isclose(calculated_distance, distance, rel_tol=1e-6)
```

### 测试标签格式

每个基于属性的测试必须使用以下格式标记：

```python
"""
Feature: kiro-ies-generator, Property {number}: {property_text}
"""
```

### 人工测试阶段

#### 测试阶段 1：场景准备验证

**测试时机**：完成场景验证器模块后

**测试目标**：验证插件能正确识别场景配置

**测试用例 1.1：单光源场景**
- **测试步骤**：
  1. 打开 Blender，创建新场景
  2. 删除默认立方体
  3. 添加点光源（Add > Light > Point Light）
  4. 设置光源功率为 1000W
  5. 切换渲染引擎为 Cycles（Render Properties > Render Engine > Cycles）
  6. 运行插件的场景验证功能
- **预期结果**：
  - 插件显示"✓ 场景验证通过"
  - 显示找到 1 个光源
  - 显示渲染引擎为 Cycles
- **验证要点**：
  - 光源被正确识别
  - 光源类型正确（POINT）
  - 光源位置和功率被正确读取

**测试用例 1.2：多光源场景**
- **测试步骤**：
  1. 在场景中添加 3 个点光源
  2. 运行插件验证
- **预期结果**：
  - 插件提示用户选择要测量的光源
  - 显示光源列表供选择
- **验证要点**：
  - 所有光源都被列出
  - 可以选择任意一个光源

**测试用例 1.3：错误场景检测**
- **测试步骤**：
  1. 创建场景但不添加光源
  2. 运行插件验证
- **预期结果**：
  - 显示错误："未找到光源对象"
  - 提供建议："在场景中添加至少一个点光源或面光源"
- **验证要点**：
  - 错误消息清晰
  - 提供可操作的建议

**测试数据**：无需特殊文件，使用 Blender 默认场景

---

#### 测试阶段 2：球面采样功能

**测试时机**：完成采样器模块后

**测试目标**：验证球面采样算法和渲染功能

**测试用例 2.1：简单球体测试**
- **测试步骤**：
  1. 创建 UV 球体（Add > Mesh > UV Sphere）
  2. 缩放到半径 0.5m
  3. 在球心添加点光源（位置 0, 0, 0）
  4. 设置光源功率 1000W
  5. 给球体添加发光材质（Emission shader）
  6. 配置采样参数：角度间隔 10°，距离 5m，采样数 64
  7. 运行采样
- **预期结果**：
  - 进度条正常显示
  - 采样点总数：19 × 37 = 703
  - 所有采样点成功渲染
  - 耗时约 5-10 分钟
- **验证要点**：
  - 进度更新流畅
  - 无渲染错误
  - 临时相机被正确清理

**测试用例 2.2：半球遮挡测试**
- **测试步骤**：
  1. 创建 UV 球体
  2. 在编辑模式删除下半球
  3. 在球心添加点光源
  4. 运行采样（角度间隔 10°）
- **预期结果**：
  - 上半球（θ=0°-90°）有光强数据
  - 下半球（θ=90°-180°）光强接近零
- **验证要点**：
  - 遮挡效果正确
  - 数据分布符合预期

**测试用例 2.3：取消操作**
- **测试步骤**：
  1. 开始采样
  2. 等待 10 秒后点击"取消"按钮
- **预期结果**：
  - 采样立即停止
  - 显示"已取消"消息
  - 场景中无残留临时对象
- **验证要点**：
  - 取消响应及时
  - 资源正确清理

**测试数据**：
- 简单球体模型（Blender 内置）
- 采样参数：角度间隔 10°，距离 5m，采样数 64

---

#### 测试阶段 3：IES 文件生成

**测试时机**：完成 IES 生成器和输出管理器后

**测试目标**：验证 IES 文件格式正确性和可用性

**测试用例 3.1：IES 文件格式验证**
- **测试步骤**：
  1. 完成一次完整采样
  2. 指定输出路径（如 C:\temp\test.ies）
  3. 设置光源流明值 1000lm
  4. 生成 IES 文件
  5. 用文本编辑器打开 IES 文件
- **预期结果**：
  - 文件第一行为 "IESNA:LM-63-2002"
  - 包含必要的元数据标签
  - 角度数据按升序排列
  - 坎德拉值为正数
- **验证要点**：
  - 文件头格式正确
  - 数据格式符合标准
  - 数值精度合理

**测试用例 3.2：IES 文件导入测试**
- **测试步骤**：
  1. 生成 IES 文件
  2. 在 Blender 中导入该 IES 文件作为光源
     - 添加点光源
     - Light Properties > Nodes > Use Nodes
     - 添加 IES Texture 节点
     - 加载生成的 IES 文件
  3. 渲染场景观察光分布
- **预期结果**：
  - IES 文件成功加载
  - 光分布与原始灯具相似
  - 无错误或警告
- **验证要点**：
  - IES 文件可被 Blender 识别
  - 光分布数据有效

**测试用例 3.3：第三方工具验证**
- **测试步骤**：
  1. 生成 IES 文件
  2. 使用在线 IES 查看器验证（如 https://www.photometricviewer.com/）
  3. 上传 IES 文件
  4. 查看光分布图
- **预期结果**：
  - 文件成功解析
  - 显示光分布曲线
  - 无格式错误
- **验证要点**：
  - 与行业工具兼容
  - 数据可视化正常

**测试数据**：
- 采样结果数据
- 输出路径：可写入的文件系统位置

---

#### 测试阶段 4：完整工作流

**测试时机**：所有模块完成后

**测试目标**：验证端到端工作流

**测试用例 4.1：简单灯具完整流程**
- **测试步骤**：
  1. 导入简单灯具模型（如圆柱形灯罩）
  2. 设置半透明材质（Principled BSDF）：
     - Transmission: 0.8
     - Roughness: 0.4
     - Subsurface Weight: 0.3
  3. 在灯罩中心添加点光源（1000W）
  4. 切换到 Cycles 渲染引擎
  5. 打开插件面板
  6. 配置参数：角度间隔 10°，采样数 64
  7. 点击"生成 IES"
  8. 等待完成
  9. 验证输出文件
- **预期结果**：
  - 整个流程无错误
  - 生成有效的 IES 文件
  - 耗时在预期范围内
- **验证要点**：
  - 所有步骤顺利执行
  - 用户体验流畅
  - 输出文件质量良好

**测试数据**：
- 简单灯具 3D 模型（OBJ 或 FBX 格式）
- 建议尺寸：直径 0.2-0.5m

---

### IES 文件验证工具

推荐使用以下工具验证生成的 IES 文件：

1. **Blender 内置 IES 导入**
   - 最直接的验证方法
   - 路径：Light Properties > Nodes > IES Texture

2. **在线 IES 查看器**
   - Photometric Viewer: https://www.photometricviewer.com/
   - IES Viewer: https://iesviewer.com/

3. **专业照明软件**
   - DIALux（免费）
   - Relux（免费）
   - AGi32（商业）

### 基准测试

系统包含两个关键基准测试：

1. **球体测试（test_sphere.py）**
   - 验证各向同性光源（裸灯泡）
   - 预期结果：所有方向的光强度相等（±5%）
   - 用于校准基线

2. **半球测试（test_hemisphere.py）**
   - 验证半球遮罩的光分布
   - 预期结果：一半球面为零，另一半为均匀分布
   - 验证几何遮挡正确性

### 测试覆盖目标

- 单元测试代码覆盖率：> 80%
- 属性测试：所有 25 个属性
- 人工测试：4 个测试阶段，12 个测试用例
- 基准测试：2 个基准场景

### 持续集成

测试应该在以下情况下运行：
- 每次代码提交（单元测试 + 属性测试）
- 每次拉取请求（完整测试套件）
- 每周构建（包括人工测试验证）

CI 环境要求：
- Blender 3.6+ 或 4.x
- Python 3.10+
- hypothesis 库
- numpy 库
