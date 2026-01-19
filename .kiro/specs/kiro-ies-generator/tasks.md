# 实施计划：Kiro IES Generator

## 概述

本实施计划将 Kiro IES Generator 的设计分解为可执行的编码任务。实施将采用增量方式，从核心模块开始，逐步构建完整的 MVP 核心脚本（kiro_core.py）。每个任务都包含具体的实现目标和需求引用。

## 任务

- [ ] 1. 项目结构和配置设置
  - 创建项目目录结构
  - 设置 config/materials.json 材质预设文件
  - 创建基础的 Python 包结构（__init__.py）
  - _需求：13.1_

- [ ] 2. 实现输入管理器模块
  - [ ] 2.1 实现 3D 模型导入功能
    - 实现 import_model() 函数，支持 OBJ、FBX、STL 格式
    - 使用 bpy.ops.import_scene 进行文件导入
    - 处理文件不存在和格式不支持的错误
    - _需求：1.1, 1.2, 1.3, 1.4_
  
  - [ ]* 2.2 为模型导入编写属性测试
    - **属性 1：多格式导入一致性**
    - **验证需求：1.1, 1.2, 1.3**
  
  - [ ] 2.3 实现网格验证功能
    - 实现 validate_mesh() 函数
    - 实现 check_mesh_closed() - 检查边界边
    - 实现 check_mesh_manifold() - 检查非流形顶点
    - 实现 check_normals_consistent() - 检查法线方向
    - 返回 ValidationResult 数据类
    - 对开放式灯具，将非封闭状态作为警告而非错误
    - _需求：2.1, 2.2, 2.3, 2.4_
  
  - [ ]* 2.4 为网格验证编写属性测试
    - **属性 2：网格验证完整性**
    - **验证需求：2.1, 2.2, 2.3, 2.4**
    - **属性 3：无效几何检测**
    - **验证需求：1.4, 1.5, 2.2, 2.3**

- [ ] 3. 实现场景构建器模块
  - [ ] 3.1 实现场景初始化和清理
    - 实现 clear_scene() 函数
    - 实现 setup_scene_units() - 设置为公制毫米
    - _需求：3.1, 3.4_
  
  - [ ] 3.2 实现光源创建功能
    - 实现 create_light_source() - 单光源
    - 实现 create_multiple_light_sources() - 多光源（树状灯、多灯珠）
    - 实现 load_light_positions_from_model() - 从模型读取光源位置
    - 设置光源位置、流明值和半径
    - _需求：3.2, 3.3_
  
  - [ ]* 3.3 为光源创建编写属性测试
    - **属性 4：光源位置精度**
    - **验证需求：3.2, 3.3**
    - **属性 3a：多光源配置一致性**
    - **验证需求：3.2, 3.3**
  
  - [ ] 3.4 实现材质系统
    - 实现 load_material_presets() - 从 JSON 加载预设
    - 实现 apply_material() - 创建 Principled BSDF 节点
    - 设置透射、粗糙度、IOR、SSS 参数
    - 强制 SSS 方法为 RANDOM_WALK
    - 实现材质参数验证
    - _需求：3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 13.1, 13.4_
  
  - [ ]* 3.5 为材质系统编写属性测试
    - **属性 5：材质参数应用**
    - **验证需求：3.5, 4.3**
    - **属性 6：材质预设一致性**
    - **验证需求：4.1, 4.2, 13.3**
    - **属性 7：SSS 方法强制**
    - **验证需求：4.4**
    - **属性 8：材质参数验证**
    - **验证需求：4.5, 15.5**
    - **属性 28：材质预设加载往返**
    - **验证需求：13.1, 13.2**
    - **属性 29：预设回退机制**
    - **验证需求：13.4**
    - **属性 30：自定义预设验证**
    - **验证需求：13.5**

- [ ] 4. 检查点 - 验证场景构建
  - 确保所有测试通过，如有问题请询问用户

- [ ] 4.5 人工测试 - 场景构建验证
  - **测试时机**：完成场景构建器模块后，在实现模拟引擎之前
  - **测试目标**：验证 3D 模型导入、材质应用和光源设置的正确性
  - **需要 Blender**：是，需要在 Blender UI 中进行可视化验证
  
  - [ ] 4.5.1 测试用例 1：基础模型导入和场景设置
    - **测试步骤**：
      1. 准备测试文件：创建或下载一个简单的球体模型（sphere.obj）
      2. 启动 Blender（版本 3.6+ 或 4.x）
      3. 打开 Blender 脚本编辑器（Scripting 工作区）
      4. 运行以下测试脚本：
         ```python
         import sys
         sys.path.append("项目路径")
         from input_manager import import_model, validate_mesh
         from scene_builder import clear_scene, setup_scene_units, create_light_source
         
         # 清空场景
         clear_scene()
         setup_scene_units()
         
         # 导入模型
         model = import_model("path/to/sphere.obj")
         validation = validate_mesh(model)
         print(f"验证结果: {validation}")
         
         # 创建光源
         light = create_light_source(position=(0, 0, 0), lumens=1000, radius=5)
         ```
      5. 在 3D 视口中检查场景（切换到 Layout 工作区）
    - **预期结果**：
      - 控制台输出验证结果显示网格有效
      - 3D 视口中可见球体模型
      - 场景单位显示为毫米（Scene Properties > Units > Unit System: Metric, Length: Millimeters）
      - 可见点光源位于原点
    - **验证要点**：
      - 模型是否正确导入且位置正确
      - 场景单位是否设置为公制毫米
      - 光源是否在正确位置且可见
  
  - [ ] 4.5.2 测试用例 2：材质应用验证
    - **测试步骤**：
      1. 继续上一个测试场景
      2. 在脚本编辑器中运行：
         ```python
         from scene_builder import load_material_presets, apply_material
         
         # 加载材质预设
         presets = load_material_presets()
         print(f"可用材质: {list(presets.keys())}")
         
         # 应用磨砂玻璃材质
         apply_material(model, "frosted_glass")
         ```
      3. 切换到 Shading 工作区
      4. 选中球体模型，查看材质节点
      5. 切换到 Rendered 视图模式（视口右上角，按 Z 键选择 Rendered）
    - **预期结果**：
      - 控制台显示可用材质列表（frosted_glass, opal_acrylic 等）
      - Shader Editor 中显示 Principled BSDF 节点
      - 节点参数正确设置（Transmission > 0, Roughness > 0, Subsurface Weight > 0）
      - Subsurface Method 设置为 Random Walk
      - Rendered 视图中球体显示半透明效果
    - **验证要点**：
      - 材质节点是否正确创建
      - SSS 方法是否强制为 RANDOM_WALK
      - 材质参数值是否与 config/materials.json 一致
      - 视觉效果是否符合预期（半透明、散射）
  
  - [ ] 4.5.3 测试用例 3：多光源配置验证
    - **测试步骤**：
      1. 清空场景并重新导入一个灯具模型（如吊灯模型）
      2. 运行脚本创建多个光源：
         ```python
         from scene_builder import create_multiple_light_sources
         
         # 创建 3 个光源（模拟 3 灯珠吊灯）
         positions = [(0, 0, 0), (50, 0, 0), (-50, 0, 0)]
         lights = create_multiple_light_sources(positions, lumens=800, radius=3)
         print(f"创建了 {len(lights)} 个光源")
         ```
      3. 在 Outliner 中检查光源对象
      4. 在 3D 视口中验证光源位置
    - **预期结果**：
      - 控制台显示创建了 3 个光源
      - Outliner 中显示 3 个 Light 对象
      - 3D 视口中 3 个光源位于指定位置
      - 每个光源的属性面板显示正确的流明值和半径
    - **验证要点**：
      - 光源数量是否正确
      - 光源位置是否精确
      - 光源参数（流明、半径）是否一致
  
  - **测试数据**：
    - 测试模型：sphere.obj（简单球体，半径 50mm）
    - 测试材质：frosted_glass（config/materials.json 中定义）
    - 光源参数：1000 流明，半径 5mm

- [ ] 5. 实现模拟引擎模块
  - [ ] 5.1 实现 Cycles 渲染配置
    - 实现 configure_cycles() 函数
    - 设置渲染引擎为 Cycles
    - 实现 set_sampling() - 配置采样数
    - 实现 enable_denoising() - 配置 OIDN/OptiX
    - 实现 get_render_settings() - 获取预览/生产模式设置
    - 自动为 SSS 材质启用去噪
    - _需求：5.1, 5.2, 5.3, 5.4, 5.5, 15.1, 15.2_
  
  - [ ]* 5.2 为渲染配置编写单元测试
    - 测试预览模式配置（64 采样）
    - 测试生产模式配置（256+ 采样）
    - 测试去噪器配置
    - **属性 9：SSS 自动去噪**
    - **验证需求：5.5**

- [ ] 6. 实现数据采集器模块
  - [ ] 6.1 实现坐标转换功能
    - 实现 spherical_to_cartesian() - 球面到笛卡尔转换
    - 使用 IESNA LM-63 C-Plane 坐标系
    - 处理 Blender Z-up 坐标系
    - _需求：6.1, 6.2, 14.1_
  
  - [ ]* 6.2 为坐标转换编写属性测试
    - **属性 10：球面坐标计算**
    - **验证需求：6.1, 6.5**
    - **属性 11：坐标系转换往返**
    - **验证需求：6.2, 14.2**
    - **属性 31：坐标系约定一致性**
    - **验证需求：14.1, 14.3**
  
  - [ ] 6.3 实现球面采样算法
    - 实现 calculate_sensor_positions() - 计算采样点
    - 根据角度间隔生成 theta（0-180°）和 phi（0-360°）
    - 支持预览模式（10°）和生产模式（5°）
    - 返回传感器位置的 NumPy 数组
    - _需求：6.3, 6.4, 6.5_
  
  - [ ] 6.4 实现渲染和数据采集
    - 实现 render_at_position() - 在指定位置渲染
    - 设置相机位置和朝向（朝向光源）
    - 执行 Cycles 渲染
    - 从渲染输出提取中心像素亮度
    - 实现错误恢复（渲染失败时继续）
    - _需求：7.1, 7.2, 7.4_
  
  - [ ] 6.5 实现完整采样循环
    - 实现 collect_spherical_data() - 执行完整球面采样
    - 遍历所有采样点并渲染
    - 存储数据到 NumPy 数组 (N_theta, N_phi)
    - 实现进度报告
    - _需求：7.3, 7.5, 12.1, 12.2_
  
  - [ ]* 6.6 为数据采集编写属性测试
    - **属性 13：数据存储格式**
    - **验证需求：7.3, 7.5**
    - **属性 14：渲染错误恢复**
    - **验证需求：7.4**

- [ ] 7. 检查点 - 验证数据采集
  - 确保所有测试通过，如有问题请询问用户

- [ ] 7.5 人工测试 - 数据采集和渲染验证
  - **测试时机**：完成数据采集器模块后，在实现 IES 格式化之前
  - **测试目标**：验证球面采样、渲染执行和光强数据采集的正确性
  - **需要 Blender**：是，需要在 Blender 中运行渲染并验证输出
  
  - [ ] 7.5.1 测试用例 1：球面采样点可视化
    - **测试步骤**：
      1. 启动 Blender 并打开脚本编辑器
      2. 运行以下脚本生成采样点可视化：
         ```python
         import bpy
         from data_collector import calculate_sensor_positions
         
         # 生成预览模式采样点（10° 间隔）
         positions = calculate_sensor_positions(
             distance=1000,  # 1 米距离
             theta_step=10,
             phi_step=10
         )
         
         # 在场景中创建小球体标记采样点
         for i, pos in enumerate(positions):
             bpy.ops.mesh.primitive_uv_sphere_add(
                 radius=10,
                 location=pos
             )
             bpy.context.active_object.name = f"Sensor_{i}"
         
         print(f"创建了 {len(positions)} 个采样点")
         ```
      3. 在 3D 视口中查看采样点分布
      4. 切换到不同视角（前视图、侧视图、顶视图）检查对称性
    - **预期结果**：
      - 控制台显示创建的采样点数量（预览模式约 19×37 = 703 个点）
      - 3D 视口中显示均匀分布在球面上的小球体
      - 采样点在各个方向上对称分布
      - 采样点覆盖完整的球面（0-180° 垂直，0-360° 水平）
    - **验证要点**：
      - 采样点数量是否正确（(180/step+1) × (360/step+1)）
      - 采样点是否均匀分布在球面上
      - 是否覆盖所有角度范围
  
  - [ ] 7.5.2 测试用例 2：单点渲染测试
    - **测试步骤**：
      1. 设置一个简单的测试场景：
         ```python
         from scene_builder import clear_scene, setup_scene_units, create_light_source, apply_material
         from input_manager import import_model
         from simulation_engine import configure_cycles
         from data_collector import render_at_position
         
         # 准备场景
         clear_scene()
         setup_scene_units()
         
         # 导入球体模型并应用材质
         model = import_model("path/to/sphere.obj")
         apply_material(model, "frosted_glass")
         
         # 创建光源
         light = create_light_source(position=(0, 0, 0), lumens=1000, radius=5)
         
         # 配置渲染（预览模式）
         configure_cycles(samples=64, use_denoising=True)
         
         # 在一个位置渲染
         intensity = render_at_position(
             position=(1000, 0, 0),  # X 轴正方向 1 米
             look_at=(0, 0, 0)
         )
         print(f"测得光强: {intensity}")
         ```
      2. 等待渲染完成（约 30-60 秒）
      3. 检查 Blender 渲染输出窗口
      4. 查看控制台输出的光强值
    - **预期结果**：
      - 渲染成功完成，无错误
      - 渲染输出窗口显示球体的渲染图像
      - 图像中心显示光源透过材质的效果
      - 控制台输出一个正数光强值（> 0）
    - **验证要点**：
      - 渲染是否成功执行
      - 是否正确提取中心像素亮度
      - 光强值是否在合理范围内（非零、非负）
      - 去噪是否生效（图像相对平滑）
  
  - [ ] 7.5.3 测试用例 3：完整球面采样测试
    - **测试步骤**：
      1. 运行完整的球面采样（使用小角度间隔以缩短测试时间）：
         ```python
         from data_collector import collect_spherical_data
         import numpy as np
         
         # 执行球面采样（使用 30° 间隔快速测试）
         data = collect_spherical_data(
             theta_step=30,  # 7 个垂直角度
             phi_step=30,    # 13 个水平角度
             distance=1000,
             progress_callback=lambda p: print(f"进度: {p:.1f}%")
         )
         
         print(f"数据形状: {data.shape}")
         print(f"最小值: {np.min(data)}, 最大值: {np.max(data)}")
         print(f"平均值: {np.mean(data)}")
         
         # 保存数据用于检查
         np.save("test_spherical_data.npy", data)
         ```
      2. 观察进度输出
      3. 等待采样完成（约 5-10 分钟）
      4. 检查输出的数据统计
    - **预期结果**：
      - 进度从 0% 逐步增加到 100%
      - 数据形状为 (7, 13)（对应 theta 和 phi 的采样点数）
      - 所有数据值为非负数
      - 数据显示合理的分布（不全为零，不全相同）
      - 对于球体+各向同性材质，数据应相对均匀
    - **验证要点**：
      - 采样循环是否正确执行
      - 进度报告是否准确
      - 数据数组形状是否正确
      - 数据值是否在合理范围内
      - 是否有异常值（NaN、Inf、负数）
  
  - [ ] 7.5.4 测试用例 4：渲染错误恢复测试
    - **测试步骤**：
      1. 故意创建一个会导致渲染失败的场景：
         ```python
         # 创建一个无效的相机位置（过近或重叠）
         try:
             intensity = render_at_position(
                 position=(0, 0, 0),  # 与光源重叠
                 look_at=(0, 0, 0)
             )
             print(f"结果: {intensity}")
         except Exception as e:
             print(f"捕获错误: {e}")
         
         # 继续下一个有效位置
         intensity = render_at_position(
             position=(1000, 0, 0),
             look_at=(0, 0, 0)
         )
         print(f"恢复后的结果: {intensity}")
         ```
      2. 观察错误处理和恢复
    - **预期结果**：
      - 第一次渲染失败并输出错误信息
      - 错误被正确捕获，不会导致程序崩溃
      - 第二次渲染成功执行
      - 控制台显示恢复后的有效光强值
    - **验证要点**：
      - 错误是否被正确捕获
      - 错误信息是否清晰
      - 是否能从错误中恢复并继续执行
  
  - **测试数据**：
    - 测试模型：sphere.obj（半径 50mm 的球体）
    - 测试材质：frosted_glass
    - 光源：1000 流明，半径 5mm，位于原点
    - 采样距离：1000mm（1 米）
    - 快速测试角度间隔：30°（生产环境使用 5° 或 10°）

- [ ] 8. 实现 IES 格式化器模块
  - [ ] 8.1 实现单位校准功能
    - 实现 calibrate_to_candela() - Blender 单位转换为坎德拉
    - 使用光通量和距离计算校准因子
    - 对所有数据点应用一致的转换
    - 实现校准参数验证
    - _需求：8.1, 8.2, 8.3, 8.4_
  
  - [ ]* 8.2 为单位校准编写属性测试
    - **属性 15：单位校准一致性**
    - **验证需求：8.1, 8.2, 8.4**
    - **属性 16：校准参数验证**
    - **验证需求：8.3**
  
  - [ ] 8.3 实现 IES 文件生成
    - 实现 generate_ies_header() - 生成 LM-63-2002 文件头
    - 实现 format_ies_data() - 格式化角度和坎德拉数据
    - 确保角度以升序输出
    - 实现坐标系转换（Z-up 到 Y-up）
    - 格式化坎德拉值符合规范
    - _需求：9.1, 9.2, 9.3, 9.4, 14.2_
  
  - [ ] 8.4 实现 IES 验证功能
    - 实现 validate_ies_compliance() - 验证 LM-63-2002 合规性
    - 检查文件头必需字段
    - 验证数据格式
    - _需求：9.5_
  
  - [ ]* 8.5 为 IES 格式化编写属性测试
    - **属性 17：IES 文件头合规性**
    - **验证需求：9.1**
    - **属性 18：角度数据排序**
    - **验证需求：9.2, 9.3**
    - **属性 19：IES 格式验证往返**
    - **验证需求：9.5**
    - **属性 20：坎德拉值格式化**
    - **验证需求：9.4**
    - **属性 12：坐标系几何不变性**
    - **验证需求：14.4**

- [ ] 9. 实现输出管理器模块
  - [ ] 9.1 实现文件输出功能
    - 实现 ensure_directory_exists() - 创建必要目录
    - 实现 write_ies_file() - 写入 IES 文件
    - 处理文件已存在的情况
    - 实现 verify_file_written() - 验证文件写入
    - 实现错误处理和报告
    - _需求：10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 9.2 为文件输出编写属性测试
    - **属性 21：文件写入验证**
    - **验证需求：10.1, 10.5**
    - **属性 22：目录自动创建**
    - **验证需求：10.2**
    - **属性 23：文件写入错误处理**
    - **验证需求：10.4**

- [ ] 10. 实现错误处理和日志系统
  - [ ] 10.1 实现错误类层次结构
    - 创建 KiroError 基类
    - 创建 ValidationError、RenderError 等子类
    - 包含时间戳、模块名称、可恢复标志
    - _需求：11.1, 11.2, 11.3_
  
  - [ ] 10.2 实现日志和进度报告
    - 实现错误日志记录（时间戳、模块、消息）
    - 实现进度报告功能
    - 报告阶段完成和经过时间
    - 实现异常堆栈跟踪记录
    - _需求：11.1, 11.5, 12.1, 12.3, 12.5_
  
  - [ ]* 10.3 为错误处理编写属性测试
    - **属性 24：错误日志完整性**
    - **验证需求：11.1**
    - **属性 25：可恢复错误建议**
    - **验证需求：11.2**
    - **属性 26：异常堆栈跟踪**
    - **验证需求：11.5**
    - **属性 27：进度报告完整性**
    - **验证需求：12.3**

- [ ] 11. 实现核心脚本（kiro_core.py）
  - [ ] 11.1 创建主工作流函数
    - 实现 main() 函数，整合所有模块
    - 实现命令行参数解析（argparse）
    - 参数：--input（模型路径）、--output（IES 路径）、--lumens、--material、--mode
    - 实现完整的数据流：导入 → 场景构建 → 模拟 → 采集 → 格式化 → 输出
    - _需求：所有需求_
  
  - [ ] 11.2 实现资源管理
    - 使用上下文管理器确保资源清理
    - 实现优雅的错误处理和退出
    - _需求：11.3_
  
  - [ ]* 11.3 编写端到端集成测试
    - 测试完整工作流（简单球体模型）
    - 测试多光源灯具
    - 测试开放式灯具（非封闭网格）
    - 测试错误恢复场景

- [ ] 12. 检查点 - 验证核心脚本
  - 确保所有测试通过，如有问题请询问用户

- [ ] 12.5 人工测试 - 核心脚本端到端验证
  - **测试时机**：完成核心脚本（kiro_core.py）后，在进行基准测试之前
  - **测试目标**：验证完整工作流从模型导入到 IES 文件生成的正确性
  - **需要 Blender**：是，需要通过 Blender 命令行运行核心脚本
  
  - [ ] 12.5.1 测试用例 1：简单球体灯具完整流程
    - **测试步骤**：
      1. 准备测试文件：
         - 创建一个简单球体模型 `test_sphere.obj`（半径 50mm）
         - 确保 `config/materials.json` 包含 `frosted_glass` 预设
      2. 在命令行运行核心脚本（预览模式）：
         ```bash
         blender --background --python kiro_core.py -- \
           --input test_sphere.obj \
           --output output/sphere_test.ies \
           --lumens 1000 \
           --material frosted_glass \
           --mode preview
         ```
      3. 等待执行完成（预览模式约 5-10 分钟）
      4. 检查控制台输出的日志信息
      5. 检查生成的 IES 文件
    - **预期结果**：
      - 控制台显示各阶段进度：
        - "导入模型..."
        - "验证网格..."
        - "构建场景..."
        - "配置渲染..."
        - "执行球面采样... 进度: X%"
        - "生成 IES 文件..."
        - "完成！输出文件: output/sphere_test.ies"
      - 无错误或警告信息
      - 生成的 IES 文件存在于 `output/sphere_test.ies`
      - 文件大小合理（几 KB）
    - **验证要点**：
      - 完整流程是否无错误执行
      - 各模块是否正确集成
      - 进度报告是否准确
      - IES 文件是否成功生成
  
  - [ ] 12.5.2 测试用例 2：IES 文件内容验证
    - **测试步骤**：
      1. 使用文本编辑器打开生成的 `sphere_test.ies` 文件
      2. 检查文件头部信息
      3. 检查数据格式
      4. 使用 IES 验证工具（可选）：
         - 在线工具：https://www.photometricviewer.com/
         - 或使用 Dialux、AGi32 等照明设计软件
      5. 如果有验证工具，导入 IES 文件并查看光分布图
    - **预期结果**：
      - 文件头包含必需字段：
        ```
        IESNA:LM-63-2002
        [TEST] Kiro IES Generator
        [MANUFAC] Kiro
        [LUMCAT] test_sphere
        [LUMINAIRE] Test Sphere Fixture
        ...
        TILT=NONE
        1 1000 1 19 37 1 1 0 0 0
        1 1 1
        0 0 0
        0.0 10.0 20.0 ... 180.0
        0.0 10.0 20.0 ... 360.0
        123.4 125.6 ... (坎德拉值)
        ```
      - 角度数据升序排列
      - 坎德拉值为正数
      - 验证工具显示球形光分布（各向同性）
    - **验证要点**：
      - IES 文件格式是否符合 LM-63-2002 标准
      - 文件头信息是否完整
      - 角度和光强数据是否正确格式化
      - 光分布是否符合预期（球体应为各向同性）
  
  - [ ] 12.5.3 测试用例 3：多光源灯具测试
    - **测试步骤**：
      1. 准备一个包含多个光源位置的灯具模型（如吊灯）
      2. 创建光源配置文件 `light_config.json`：
         ```json
         {
           "positions": [
             [0, 0, 0],
             [50, 0, 0],
             [-50, 0, 0]
           ],
           "lumens_per_source": 800
         }
         ```
      3. 运行核心脚本（需要支持多光源参数）：
         ```bash
         blender --background --python kiro_core.py -- \
           --input chandelier.obj \
           --output output/chandelier.ies \
           --light-config light_config.json \
           --material opal_acrylic \
           --mode preview
         ```
      4. 检查输出和生成的 IES 文件
    - **预期结果**：
      - 控制台显示创建了 3 个光源
      - 流程正常完成
      - 生成的 IES 文件显示多光源的综合光分布
      - 光分布不再是各向同性（取决于灯具几何形状）
    - **验证要点**：
      - 多光源是否正确创建
      - 光强是否为所有光源的总和
      - IES 文件是否反映多光源的综合效果
  
  - [ ] 12.5.4 测试用例 4：不同材质对比测试
    - **测试步骤**：
      1. 使用同一个模型，测试不同材质：
         ```bash
         # 测试磨砂玻璃
         blender --background --python kiro_core.py -- \
           --input test_sphere.obj \
           --output output/sphere_frosted.ies \
           --material frosted_glass \
           --mode preview
         
         # 测试乳白亚克力
         blender --background --python kiro_core.py -- \
           --input test_sphere.obj \
           --output output/sphere_opal.ies \
           --material opal_acrylic \
           --mode preview
         
         # 测试透明玻璃
         blender --background --python kiro_core.py -- \
           --input test_sphere.obj \
           --output output/sphere_clear.ies \
           --material clear_glass \
           --mode preview
         ```
      2. 对比三个 IES 文件的光分布
      3. 使用 IES 查看器可视化对比
    - **预期结果**：
      - 三个材质都成功生成 IES 文件
      - 光分布有明显差异：
        - frosted_glass：较强的散射，光分布较均匀
        - opal_acrylic：强散射，光分布非常均匀
        - clear_glass：弱散射，光分布更集中
      - 总光通量相近（能量守恒）
    - **验证要点**：
      - 不同材质是否产生不同的光分布
      - 材质的物理特性是否正确反映在 IES 数据中
      - 能量守恒是否满足
  
  - [ ] 12.5.5 测试用例 5：生产模式高质量输出测试
    - **测试步骤**：
      1. 使用生产模式生成高质量 IES 文件：
         ```bash
         blender --background --python kiro_core.py -- \
           --input final_fixture.obj \
           --output output/final_production.ies \
           --lumens 1200 \
           --material frosted_glass \
           --mode production
         ```
      2. 等待完成（生产模式约 20-60 分钟）
      3. 对比预览模式和生产模式的输出
    - **预期结果**：
      - 生产模式执行时间明显更长
      - 生成的 IES 文件数据点更多（5° 间隔 vs 10° 间隔）
      - 光分布曲线更平滑
      - 噪点更少（更高采样率和去噪）
    - **验证要点**：
      - 生产模式是否使用更高的采样率和更小的角度间隔
      - 输出质量是否明显优于预览模式
      - 是否适合用于最终产品交付
  
  - **测试数据**：
    - 测试模型：
      - `test_sphere.obj`：简单球体（半径 50mm）
      - `chandelier.obj`：多光源吊灯模型
      - `final_fixture.obj`：实际灯具模型
    - 材质预设：frosted_glass, opal_acrylic, clear_glass
    - 光源参数：800-1200 流明
    - 模式：preview（10° 间隔，64 采样）和 production（5° 间隔，256 采样）
  
  - **IES 文件验证工具推荐**：
    - 在线工具：
      - Photometric Viewer: https://www.photometricviewer.com/
      - IES Viewer: https://www.iesviewer.com/
    - 桌面软件：
      - Dialux（免费照明设计软件）
      - AGi32（专业照明设计软件）
      - Blender 本身（可导入 IES 文件作为灯光）

- [ ] 13. 实现基准测试
  - [ ] 13.1 创建球体基准测试（test_sphere.py）
    - 创建程序化球体网格
    - 应用各向同性材质
    - 验证所有方向光强度相等（容差范围内）
    - 用于校准基线
  
  - [ ] 13.2 创建遮挡基准测试（test_occlusion.py）
    - 创建半球遮罩模型
    - 验证一半球面光强为零
    - 验证另一半球面光强均匀
    - 验证几何遮挡正确性
  
  - [ ] 13.3 创建校准基准测试（test_calibration.py）
    - 使用已知流明值的光源
    - 验证总坎德拉值与流明值的关系
    - 验证单位转换准确性

- [ ] 14. 文档和使用示例
  - [ ] 14.1 创建 README.md
    - 项目概述和功能
    - 安装说明（Blender 版本要求）
    - 使用示例（命令行）
    - 材质预设说明
  
  - [ ] 14.2 创建示例脚本
    - 创建简单灯具示例
    - 创建多光源灯具示例
    - 创建自定义材质示例

- [ ] 15. 最终验证和优化
  - [ ] 15.1 运行完整测试套件
    - 运行所有单元测试
    - 运行所有属性测试（每个 100+ 次迭代）
    - 运行所有基准测试
    - 验证测试覆盖率 > 80%
  
  - [ ] 15.2 性能优化
    - 分析渲染性能
    - 优化 NumPy 数组操作
    - 验证预览模式时间（5-10 分钟）
    - 验证生产模式时间（20-60 分钟）
  
  - [ ] 15.3 最终代码审查
    - 检查所有函数都有中文 docstring
    - 检查命名约定一致性
    - 检查错误处理完整性
    - 验证所有需求都已实现
  
  - [ ] 15.4 人工测试 - 最终验证和真实场景测试
    - **测试时机**：完成所有开发和自动化测试后，准备交付前
    - **测试目标**：在真实使用场景中验证系统的完整性、稳定性和实用性
    - **需要 Blender**：是，需要在实际工作环境中测试
    
    - [ ] 15.4.1 测试用例 1：真实灯具模型端到端测试
      - **测试步骤**：
        1. 获取一个真实的灯具 3D 模型（从设计师或模型库）
        2. 检查模型质量（网格完整性、尺寸单位）
        3. 运行完整流程：
           ```bash
           blender --background --python kiro_core.py -- \
             --input real_fixture.obj \
             --output output/real_fixture.ies \
             --lumens 1500 \
             --material frosted_glass \
             --mode production
           ```
        4. 将生成的 IES 文件导入到渲染引擎（V-Ray、Unreal Engine 或 Blender）
        5. 在渲染场景中使用该 IES 文件作为光源
        6. 渲染一个测试场景并检查光照效果
      - **预期结果**：
        - 模型成功导入，网格验证通过或仅有合理警告
        - IES 文件成功生成
        - IES 文件可被渲染引擎正确识别和导入
        - 渲染场景中的光照效果真实且符合预期
        - 光分布与灯具的物理形状和材质相符
      - **验证要点**：
        - 系统是否能处理真实的、可能不完美的模型
        - 生成的 IES 文件是否与主流渲染引擎兼容
        - 光照效果是否真实可信
        - 是否满足实际工作流程需求
    
    - [ ] 15.4.2 测试用例 2：批量处理测试
      - **测试步骤**：
        1. 准备 5-10 个不同的灯具模型
        2. 创建批处理脚本：
           ```bash
           # batch_process.sh (Windows: batch_process.bat)
           for model in models/*.obj; do
             basename=$(basename "$model" .obj)
             blender --background --python kiro_core.py -- \
               --input "$model" \
               --output "output/${basename}.ies" \
               --lumens 1000 \
               --material frosted_glass \
               --mode preview
           done
           ```
        3. 运行批处理脚本
        4. 监控执行过程和资源使用
        5. 检查所有输出文件
      - **预期结果**：
        - 所有模型都成功处理
        - 没有内存泄漏或资源耗尽
        - 每个模型的处理时间稳定
        - 所有 IES 文件都有效
      - **验证要点**：
        - 系统稳定性（长时间运行）
        - 资源管理（内存、CPU）
        - 错误恢复能力
        - 批量处理的实用性
    
    - [ ] 15.4.3 测试用例 3：极端情况和边界测试
      - **测试步骤**：
        1. 测试非常小的模型（< 10mm）
        2. 测试非常大的模型（> 1000mm）
        3. 测试高多边形模型（> 100k 面）
        4. 测试低多边形模型（< 100 面）
        5. 测试开放式灯具（非封闭网格）
        6. 测试复杂几何（多个独立部件）
        7. 测试极端材质参数（高透射、高散射）
      - **预期结果**：
        - 小模型：正确处理，可能需要调整光源半径
        - 大模型：正确处理，渲染时间可能更长
        - 高多边形：成功处理，但渲染较慢
        - 低多边形：成功处理，可能有警告
        - 开放式灯具：成功处理，有警告但不报错
        - 复杂几何：正确处理所有部件
        - 极端材质：生成有效的 IES，光分布可能极端但合理
      - **验证要点**：
        - 系统的鲁棒性
        - 边界情况处理
        - 错误信息的清晰度
        - 是否提供有用的警告和建议
    
    - [ ] 15.4.4 测试用例 4：性能基准测试
      - **测试步骤**：
        1. 使用标准测试模型（中等复杂度）
        2. 记录预览模式执行时间：
           ```bash
           time blender --background --python kiro_core.py -- \
             --input standard_fixture.obj \
             --output output/perf_preview.ies \
             --mode preview
           ```
        3. 记录生产模式执行时间：
           ```bash
           time blender --background --python kiro_core.py -- \
             --input standard_fixture.obj \
             --output output/perf_production.ies \
             --mode production
           ```
        4. 分析各阶段耗时（可在代码中添加计时）
        5. 对比不同硬件配置的性能
      - **预期结果**：
        - 预览模式：5-10 分钟
        - 生产模式：20-60 分钟
        - 渲染阶段占用大部分时间（> 90%）
        - 其他阶段（导入、格式化）耗时很短（< 1 分钟）
      - **验证要点**：
        - 性能是否符合设计目标
        - 瓶颈在哪里（通常是渲染）
        - 是否有优化空间
        - 不同硬件的性能差异
    
    - [ ] 15.4.5 测试用例 5：用户体验和文档验证
      - **测试步骤**：
        1. 邀请一位新用户（未参与开发）
        2. 仅提供 README.md 文档
        3. 让用户尝试：
           - 安装和配置环境
           - 运行第一个示例
           - 处理自己的模型
           - 解决遇到的问题
        4. 记录用户遇到的困难和疑问
        5. 收集用户反馈
      - **预期结果**：
        - 用户能够根据文档成功安装
        - 用户能够运行基本示例
        - 用户能够理解参数含义
        - 用户能够根据错误信息解决问题
        - 用户对工具的整体满意度高
      - **验证要点**：
        - 文档的完整性和清晰度
        - 工具的易用性
        - 错误信息的可理解性
        - 学习曲线是否合理
    
    - [ ] 15.4.6 测试用例 6：IES 文件在不同软件中的兼容性测试
      - **测试步骤**：i
        1. 生成一个标准的 IES 文件
        2. 在以下软件中导入和测试：
           - **Blender**：作为 IES 纹理导入到灯光
           - **V-Ray**（如果可用）：作为 IES 光源
           - **Unreal Engine**（如果可用）：作为 IES 光源配置文件
           - **Dialux**：照明设计和验证
           - **在线 IES 查看器**：快速验证
        3. 在每个软件中检查：
           - 文件是否能正确导入
           - 光分布是否正确显示
           - 是否有警告或错误
           - 渲染效果是否符合预期
      - **预期结果**：
        - 所有软件都能成功导入 IES 文件
        - 光分布在不同软件中一致
        - 没有格式兼容性问题
        - 渲染效果真实可信
      - **验证要点**：
        - IES 文件的标准兼容性
        - 跨平台可用性
        - 实际应用场景的适用性
    
    - **测试数据**：
      - 真实灯具模型（从设计师或模型库获取）
      - 标准测试模型（用于性能基准）
      - 极端情况模型（边界测试）
    
    - **测试环境**：
      - 主要测试环境：Blender 3.6+ 或 4.x，Windows/Linux/macOS
      - 渲染引擎：Blender Cycles, V-Ray, Unreal Engine
      - 验证工具：Dialux, 在线 IES 查看器
    
    - **成功标准**：
      - 所有真实场景测试通过
      - 批量处理稳定可靠
      - 极端情况有合理的处理和提示
      - 性能符合预期目标
      - 用户能够独立使用工具
      - IES 文件在主流软件中兼容

## 注意事项

- 标记为 `*` 的任务是可选的测试任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求编号以确保可追溯性
- 检查点任务确保增量验证和用户反馈
- 属性测试使用 Python 的 `hypothesis` 库，每个测试至少 100 次迭代
- 所有代码必须包含中文注释和 docstring
- 核心脚本（kiro_core.py）是 Phase 1 的交付物，插件（kiro_addon.py）留待 Phase 2
