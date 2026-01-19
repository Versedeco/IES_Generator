# 设计文档

## 概述

Kiro IES Generator 采用模块化架构，将 3D 灯具模型转换为 IESNA LM-63 标准光度学文件的过程分解为六个独立的模块。系统利用 Blender 的 Cycles 渲染引擎进行物理精确的光传输模拟，通过球面采样测量光分布，并将结果转换为行业标准的 IES 格式。

核心工作流程：
1. 导入并验证 3D 模型几何体
2. 构建包含光源和材质的 Blender 场景
3. 配置 Cycles 渲染引擎参数
4. 在球面上采样并测量光强度
5. 校准单位并格式化为 IES 文件
6. 验证并输出最终文件

系统设计支持两种运行模式：
- **MVP 核心脚本（kiro_core.py）**：命令行工具，无 UI，适用于批处理和自动化
- **Blender 插件（kiro_addon.py）**：带图形界面的完整版本，适用于交互式设计工作流

### 灯具模型类型支持

系统设计考虑了实际商业灯具的多样性：

1. **封闭式灯具**：完全封闭的灯罩（如球形吊灯、筒灯）
   - 网格应该是水密的
   - 光线完全通过半透明材质散射

2. **半封闭式灯具**：带有内部支撑结构的灯具
   - 支撑结构可能部分遮挡光源
   - 系统通过 Cycles 路径追踪自动处理遮挡效果
   - 不需要手动标记遮挡区域

3. **开放式灯具**：无灯罩结构（如树状灯、多灯珠灯具）
   - 网格可能不封闭
   - 多个小灯珠分布在不同位置
   - 支持多光源配置

4. **预定义光源位置**：
   - 灯具模型中光源位置是固定的（商品化设计）
   - 用户只需调整光通量（流明值）
   - 系统支持从模型元数据或配置文件读取光源位置

## 架构

### 模块依赖关系

```
用户输入
    ↓
输入管理器 (input_manager.py)
    ↓
场景构建器 (scene_builder.py)
    ↓
模拟引擎 (simulation_engine.py)
    ↓
数据采集器 (data_collector.py)
    ↓
IES格式化器 (ies_formatter.py)
    ↓
输出管理器 (output_manager.py)
    ↓
IES 文件输出
```

### 模块职责

**输入管理器（Input Manager）**
- 导入 OBJ、FBX、STL 格式的 3D 模型
- 验证网格完整性（封闭性、法线方向、流形性）
- 执行几何预处理和修复

**场景构建器（Scene Builder）**
- 清空并初始化 Blender 场景
- 创建和配置点光源
- 应用材质节点（Principled BSDF）
- 加载和管理材质预设
- 设置场景单位和坐标系

**模拟引擎（Simulation Engine）**
- 配置 Cycles 渲染引擎
- 设置采样率和去噪参数
- 管理预览/生产模式切换
- 优化渲染性能

**数据采集器（Data Collector）**
- 实现球面采样算法（IESNA C-Plane）
- 计算传感器位置（球面坐标转换）
- 执行渲染并提取亮度数据
- 存储测量结果到 NumPy 数组

**IES格式化器（IES Formatter）**
- 执行单位校准（Blender → Candela）
- 生成 LM-63-2002 标准文件头
- 格式化角度和光强数据
- 验证输出合规性

**输出管理器（Output Manager）**
- 处理文件路径和目录创建
- 写入 IES 文件到磁盘
- 验证文件完整性
- 处理覆盖确认

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

### 输入管理器（input_manager.py）

#### 主要函数

```python
def import_model(file_path: str, file_format: str) -> bpy.types.Object:
    """
    导入 3D 模型到 Blender 场景
    
    参数:
        file_path: 模型文件的完整路径
        file_format: 文件格式 ('OBJ', 'FBX', 'STL')
    
    返回:
        导入的 Blender 对象
    
    异常:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的文件格式
        ImportError: 导入失败
    """
    pass

def validate_mesh(mesh_obj: bpy.types.Object) -> dict:
    """
    验证网格几何体的完整性
    
    注意：对于开放式灯具（如树状灯），网格可能不封闭，这是正常的。
    验证会报告状态但不会将其视为错误。
    
    参数:
        mesh_obj: 要验证的 Blender 网格对象
    
    返回:
        验证结果字典:
        {
            'is_valid': bool,           # 是否可用于模拟
            'is_closed': bool,          # 是否封闭（可选）
            'is_manifold': bool,        # 是否流形
            'has_consistent_normals': bool,
            'warnings': List[str],      # 警告信息
            'errors': List[str]         # 错误信息
        }
    """
    pass

def check_mesh_closed(mesh: bpy.types.Mesh) -> bool:
    """检查网格是否封闭（水密）"""
    pass

def check_mesh_manifold(mesh: bpy.types.Mesh) -> Tuple[bool, List[int]]:
    """检查网格是否为流形，返回问题顶点列表"""
    pass

def check_normals_consistent(mesh: bpy.types.Mesh) -> Tuple[bool, List[int]]:
    """检查法线方向是否一致，返回问题面列表"""
    pass
```

#### 接口规范

- **输入**：文件路径字符串，文件格式枚举
- **输出**：Blender 对象引用，验证结果字典
- **错误处理**：抛出特定异常，包含详细错误信息

### 场景构建器（scene_builder.py）

#### 主要函数

```python
def clear_scene():
    """清空 Blender 默认场景中的所有对象"""
    pass

def create_light_source(position: Tuple[float, float, float], 
                       lumens: float, 
                       radius: float = 0.01) -> bpy.types.Object:
    """
    创建点光源
    
    参数:
        position: 光源位置 (x, y, z) 单位：米
        lumens: 光通量，单位：流明
        radius: 光源半径，单位：米（默认 0.01m = 10mm）
    
    返回:
        光源对象
    """
    pass

def create_multiple_light_sources(positions: List[Tuple[float, float, float]], 
                                  lumens_per_source: float) -> List[bpy.types.Object]:
    """
    创建多个点光源（用于多灯珠灯具）
    
    参数:
        positions: 光源位置列表 [(x1, y1, z1), (x2, y2, z2), ...]
        lumens_per_source: 每个光源的光通量
    
    返回:
        光源对象列表
    """
    pass

def load_light_positions_from_model(mesh_obj: bpy.types.Object) -> List[Tuple[float, float, float]]:
    """
    从模型元数据或空对象（Empty）读取预定义的光源位置
    
    灯具模型可以包含命名为 "LightSource" 或 "Bulb" 的空对象来标记光源位置
    
    参数:
        mesh_obj: 灯具模型对象
    
    返回:
        光源位置列表
    """
    pass

def apply_material(mesh_obj: bpy.types.Object, 
                  material_params: dict):
    """
    应用 Principled BSDF 材质
    
    参数:
        mesh_obj: 目标网格对象
        material_params: 材质参数字典
        {
            'transmission': float,      # 透射率 [0, 1]
            'roughness': float,         # 粗糙度 [0, 1]
            'ior': float,              # 折射率 [1.0, 3.0]
            'subsurface_weight': float, # SSS 权重 [0, 1]
            'sss_radius': [float, float, float],  # SSS 半径 RGB
            'sss_method': str          # 'RANDOM_WALK'
        }
    """
    pass

def load_material_presets(config_path: str = 'config/materials.json') -> dict:
    """
    从配置文件加载材质预设
    
    返回:
        材质预设字典 {preset_name: material_params}
    """
    pass

def setup_scene_units():
    """设置场景单位为公制毫米"""
    pass
```

#### 材质预设结构

```json
{
  "frosted_glass": {
    "transmission": 0.85,
    "roughness": 0.4,
    "ior": 1.5,
    "subsurface_weight": 0.3,
    "sss_radius": [5.0, 5.0, 5.0],
    "sss_method": "RANDOM_WALK"
  },
  "opal_acrylic": {
    "transmission": 0.7,
    "roughness": 0.6,
    "ior": 1.49,
    "subsurface_weight": 0.8,
    "sss_radius": [10.0, 10.0, 10.0],
    "sss_method": "RANDOM_WALK"
  },
  "clear_glass": {
    "transmission": 0.95,
    "roughness": 0.0,
    "ior": 1.52,
    "subsurface_weight": 0.0,
    "sss_radius": [0.0, 0.0, 0.0],
    "sss_method": "RANDOM_WALK"
  }
}
```

### 模拟引擎（simulation_engine.py）

#### 主要函数

```python
def configure_cycles(mode: str = 'preview'):
    """
    配置 Cycles 渲染引擎
    
    参数:
        mode: 'preview' 或 'production'
    """
    pass

def set_sampling(samples: int):
    """设置 Cycles 采样数"""
    pass

def enable_denoising(denoiser: str = 'OPENIMAGEDENOISE'):
    """
    启用去噪
    
    参数:
        denoiser: 'OPENIMAGEDENOISE' 或 'OPTIX'
    """
    pass

def get_render_settings(mode: str) -> dict:
    """
    获取渲染设置
    
    返回:
        {
            'samples': int,
            'angular_interval': float,  # 度
            'estimated_time': str
        }
    """
    pass
```

#### 渲染模式配置

| 模式 | 采样数 | 角度间隔 | 估计时间 |
|------|--------|----------|----------|
| 预览 | 64 | 10° | 5-10 分钟 |
| 生产 | 256+ | 5° | 20-60 分钟 |

### 数据采集器（data_collector.py）

#### 主要函数

```python
def calculate_sensor_positions(angular_interval: float, 
                              distance: float) -> np.ndarray:
    """
    计算球面采样点位置
    
    参数:
        angular_interval: 角度间隔（度）
        distance: 传感器距离光源的距离（米）
    
    返回:
        形状为 (N, 3) 的 NumPy 数组，包含传感器位置 (x, y, z)
    """
    pass

def spherical_to_cartesian(theta: float, phi: float, r: float) -> Tuple[float, float, float]:
    """
    球面坐标转笛卡尔坐标（Blender Z-up）
    
    参数:
        theta: 垂直角（0° = 天顶，180° = 天底）
        phi: 水平角（0° = X 轴正方向）
        r: 半径
    
    返回:
        (x, y, z) 笛卡尔坐标
    """
    pass

def render_at_position(position: Tuple[float, float, float]) -> float:
    """
    在指定位置渲染并提取亮度
    
    参数:
        position: 传感器位置 (x, y, z)
    
    返回:
        测量的亮度值（Blender 单位）
    """
    pass

def collect_spherical_data(angular_interval: float, 
                          distance: float = 5.0) -> np.ndarray:
    """
    执行完整的球面采样
    
    参数:
        angular_interval: 角度间隔（度）
        distance: 采样距离（米）
    
    返回:
        形状为 (N_theta, N_phi) 的 NumPy 数组，包含亮度数据
    """
    pass
```

#### 球面采样算法

IESNA LM-63 C-Plane 坐标系定义：
- **垂直角（Theta）**：0° 到 180°，0° 为天顶（正上方），90° 为水平面，180° 为天底
- **水平角（Phi）**：0° 到 360°，0° 为参考方向（通常为 X 轴正方向）

采样点计算：
```
对于每个 theta 从 0° 到 180°（步长 = angular_interval）:
    对于每个 phi 从 0° 到 360°（步长 = angular_interval）:
        x = distance * sin(theta) * cos(phi)
        y = distance * sin(theta) * sin(phi)
        z = distance * cos(theta)
        
        在位置 (x, y, z) 放置相机
        相机朝向光源 (0, 0, 0)
        执行渲染
        提取中心像素亮度值
        存储到数组 [theta_index, phi_index]
```

### IES格式化器（ies_formatter.py）

#### 主要函数

```python
def calibrate_to_candela(luminance_data: np.ndarray, 
                        lumens: float, 
                        distance: float) -> np.ndarray:
    """
    将 Blender 亮度单位校准为坎德拉
    
    参数:
        luminance_data: 原始亮度数据数组
        lumens: 光源总光通量（流明）
        distance: 采样距离（米）
    
    返回:
        校准后的坎德拉值数组
    """
    pass

def generate_ies_header(lumens: float, 
                       fixture_name: str = "Kiro Generated") -> str:
    """
    生成 IESNA LM-63-2002 文件头
    
    返回:
        格式化的文件头字符串
    """
    pass

def format_ies_data(candela_data: np.ndarray, 
                   vertical_angles: np.ndarray, 
                   horizontal_angles: np.ndarray) -> str:
    """
    格式化 IES 数据部分
    
    返回:
        格式化的数据字符串
    """
    pass

def validate_ies_compliance(ies_content: str) -> Tuple[bool, List[str]]:
    """
    验证 IES 文件是否符合 LM-63-2002 标准
    
    返回:
        (is_valid, error_messages)
    """
    pass
```

#### IES 文件格式

```
IESNA:LM-63-2002
[MANUFAC] Kiro IES Generator
[LUMCAT] {fixture_name}
[LUMINAIRE] Generated from 3D model
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
def write_ies_file(ies_content: str, output_path: str, overwrite: bool = False):
    """
    写入 IES 文件到磁盘
    
    参数:
        ies_content: IES 文件内容字符串
        output_path: 输出文件路径
        overwrite: 是否覆盖现有文件
    
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
            'path': str
        }
    """
    pass
```

## 数据模型

### 材质参数

```python
@dataclass
class MaterialParams:
    """材质参数数据类"""
    transmission: float  # 透射率 [0, 1]
    roughness: float     # 粗糙度 [0, 1]
    ior: float          # 折射率 [1.0, 3.0]
    subsurface_weight: float  # SSS 权重 [0, 1]
    sss_radius: Tuple[float, float, float]  # SSS 半径 RGB (mm)
    sss_method: str = 'RANDOM_WALK'  # SSS 方法
    
    def validate(self) -> bool:
        """验证参数范围"""
        return (0 <= self.transmission <= 1 and
                0 <= self.roughness <= 1 and
                1.0 <= self.ior <= 3.0 and
                0 <= self.subsurface_weight <= 1 and
                all(r >= 0 for r in self.sss_radius))
```

### 渲染配置

```python
@dataclass
class RenderConfig:
    """渲染配置数据类"""
    mode: str  # 'preview' 或 'production'
    samples: int  # 采样数
    angular_interval: float  # 角度间隔（度）
    distance: float  # 采样距离（米）
    denoiser: str  # 'OPENIMAGEDENOISE' 或 'OPTIX'
    
    @staticmethod
    def preview() -> 'RenderConfig':
        """预览模式预设"""
        return RenderConfig(
            mode='preview',
            samples=64,
            angular_interval=10.0,
            distance=5.0,
            denoiser='OPENIMAGEDENOISE'
        )
    
    @staticmethod
    def production() -> 'RenderConfig':
        """生产模式预设"""
        return RenderConfig(
            mode='production',
            samples=256,
            angular_interval=5.0,
            distance=5.0,
            denoiser='OPENIMAGEDENOISE'
        )
```

### 验证结果

```python
@dataclass
class ValidationResult:
    """网格验证结果数据类"""
    is_valid: bool              # 是否可用于模拟
    is_closed: bool             # 是否封闭（对开放式灯具可为 False）
    is_manifold: bool           # 是否流形
    has_consistent_normals: bool
    warnings: List[str]         # 警告信息（如：网格不封闭）
    errors: List[str]           # 错误信息（如：非流形几何）
    
    def __str__(self) -> str:
        """格式化验证结果为可读字符串"""
        if self.is_valid:
            result = "✓ 网格验证通过"
            if self.warnings:
                result += "\n警告:\n" + "\n".join(f"  ⚠ {w}" for w in self.warnings)
            return result
        else:
            return f"✗ 网格验证失败:\n" + "\n".join(f"  - {e}" for e in self.errors)
```

### 光源配置

```python
@dataclass
class LightConfig:
    """光源配置数据类"""
    positions: List[Tuple[float, float, float]]  # 光源位置列表
    lumens_per_source: float                     # 每个光源的流明值
    total_lumens: float                          # 总光通量
    radius: float = 0.01                         # 光源半径（米）
    
    @staticmethod
    def single_source(position: Tuple[float, float, float], 
                     lumens: float) -> 'LightConfig':
        """单光源配置"""
        return LightConfig(
            positions=[position],
            lumens_per_source=lumens,
            total_lumens=lumens
        )
    
    @staticmethod
    def multi_source(positions: List[Tuple[float, float, float]], 
                    total_lumens: float) -> 'LightConfig':
        """多光源配置（均分总流明）"""
        lumens_per = total_lumens / len(positions)
        return LightConfig(
            positions=positions,
            lumens_per_source=lumens_per,
            total_lumens=total_lumens
        )
```

### 光度学数据

```python
@dataclass
class PhotometricData:
    """光度学数据数据类"""
    vertical_angles: np.ndarray  # 垂直角度数组（度）
    horizontal_angles: np.ndarray  # 水平角度数组（度）
    candela_values: np.ndarray  # 坎德拉值数组 (N_theta, N_phi)
    lumens: float  # 总光通量（流明）
    distance: float  # 测量距离（米）
    
    def to_ies(self, fixture_name: str = "Kiro Generated") -> str:
        """转换为 IES 文件格式"""
        pass
```


## 正确性属性

属性是关于系统行为的特征或规则，应该在所有有效执行中保持为真。属性是人类可读规范与机器可验证正确性保证之间的桥梁。以下属性将通过基于属性的测试来验证，每个属性将在至少 100 次随机生成的输入上进行测试。

### 属性 1：多格式导入一致性

*对于任何*支持的 3D 文件格式（OBJ、FBX、STL）和有效的文件路径，导入函数应该成功将模型加载到 Blender 场景中，并返回有效的对象引用。

**验证需求：1.1, 1.2, 1.3**

### 属性 2：网格验证完整性

*对于任何*导入的网格对象，验证函数应该检查所有关键几何属性（封闭性、流形性、法线一致性），并在验证结果中报告所有发现的问题，而不是在第一个问题处停止。对于开放式灯具，网格不封闭应该作为警告而非错误报告。

**验证需求：2.1, 2.2, 2.3, 2.4, 11.4**

### 属性 3：无效几何检测

*对于任何*包含几何缺陷的网格（非流形、翻转法线），验证函数应该正确识别问题类型并报告具体的问题元素（顶点、边或面）。注意：非封闭网格不应被视为致命错误。

**验证需求：1.4, 1.5, 2.2, 2.3**

### 属性 3a：多光源配置一致性

*对于任何*光源位置列表和总流明值，创建多光源配置时，所有单个光源的流明值之和应该等于总流明值。

**验证需求：3.2, 3.3**

### 属性 4：光源位置精度

*对于任何*指定的 3D 坐标和流明值，创建的光源对象应该精确位于指定位置，并且光通量应该与指定值匹配。

**验证需求：3.2, 3.3**

### 属性 5：材质参数应用

*对于任何*有效的材质参数集（透射、粗糙度、IOR、SSS），应用材质后，网格对象的 Principled BSDF 节点应该包含所有指定的参数值。

**验证需求：3.5, 4.3**

### 属性 6：材质预设一致性

*对于任何*材质预设名称，应用预设后的材质参数应该与配置文件中该预设的定义完全匹配。

**验证需求：4.1, 4.2, 13.3**

### 属性 7：SSS 方法强制

*对于任何*包含次表面散射的材质配置，应用后的材质节点的 SSS 方法必须设置为 RANDOM_WALK。

**验证需求：4.4**

### 属性 8：材质参数验证

*对于任何*超出有效范围的材质参数（透射 < 0 或 > 1，IOR < 1.0 或 > 3.0 等），系统应该拒绝参数并报告具体的验证错误和可接受的范围。

**验证需求：4.5, 15.5**

### 属性 9：SSS 自动去噪

*对于任何*包含次表面散射材质的场景，模拟引擎应该自动启用去噪功能。

**验证需求：5.5**

### 属性 10：球面坐标计算

*对于任何*角度对（theta, phi）和距离 r，球面到笛卡尔坐标转换应该产生一个点，该点到原点的距离等于 r（在浮点精度范围内）。

**验证需求：6.1, 6.5**

### 属性 11：坐标系转换往返

*对于任何*在 Blender Z-up 坐标系中的 3D 点，转换到 IES Y-up 坐标系然后再转换回来，应该得到原始点（在浮点精度范围内）。

**验证需求：6.2, 14.2**

### 属性 12：坐标系几何不变性

*对于任何*光分布数据集，在 Blender 和 IES 坐标系之间转换时，点之间的相对距离和角度关系应该保持不变。

**验证需求：14.4**

### 属性 13：数据存储格式

*对于任何*采样操作，存储的测量数据应该是 NumPy 数组类型，并且数组维度应该与采样点数量（垂直角度数 × 水平角度数）匹配。

**验证需求：7.3, 7.5**

### 属性 14：渲染错误恢复

*对于任何*包含部分失败渲染的采样序列，数据采集器应该记录错误但继续处理剩余的采样点，最终返回部分完整的数据数组。

**验证需求：7.4**

### 属性 15：单位校准一致性

*对于任何*亮度数据数组和校准参数（流明、距离），校准函数应该对所有数据点应用相同的转换因子，结果数组的形状应该与输入数组相同。

**验证需求：8.1, 8.2, 8.4**

### 属性 16：校准参数验证

*对于任何*无效的校准参数（零或负流明值、零或负距离），校准函数应该抛出异常并提供诊断信息。

**验证需求：8.3**

### 属性 17：IES 文件头合规性

*对于任何*生成的 IES 文件头，它应该包含所有 IESNA LM-63-2002 标准要求的字段（IESNA 标识、制造商、灯具目录等）。

**验证需求：9.1**

### 属性 18：角度数据排序

*对于任何*角度数据集（垂直和水平），格式化后的输出应该以严格升序排列。

**验证需求：9.2, 9.3**

### 属性 19：IES 格式验证往返

*对于任何*生成的 IES 文件内容，通过验证函数检查应该返回合规（无错误），确认输出符合 LM-63-2002 标准。

**验证需求：9.5**

### 属性 20：坎德拉值格式化

*对于任何*坎德拉值数组，格式化输出应该符合 LM-63-2002 规范的数值格式要求（精度、分隔符、换行）。

**验证需求：9.4**

### 属性 21：文件写入验证

*对于任何*有效的输出路径和 IES 内容，写入操作成功后，文件应该存在于指定位置，并且文件内容应该与写入的内容匹配。

**验证需求：10.1, 10.5**

### 属性 22：目录自动创建

*对于任何*不存在的目录路径，输出管理器应该创建所有必要的父目录，使得文件可以成功写入。

**验证需求：10.2**

### 属性 23：文件写入错误处理

*对于任何*导致写入失败的条件（权限不足、磁盘已满等），输出管理器应该捕获异常并报告具体的失败原因。

**验证需求：10.4**

### 属性 24：错误日志完整性

*对于任何*模块中发生的错误，日志条目应该包含时间戳、模块名称和错误描述。

**验证需求：11.1**

### 属性 25：可恢复错误建议

*对于任何*可恢复的错误情况，错误消息应该包含建议的纠正措施或下一步操作。

**验证需求：11.2**

### 属性 26：异常堆栈跟踪

*对于任何*未预期的异常，系统应该记录完整的堆栈跟踪信息以供调试。

**验证需求：11.5**

### 属性 27：进度报告完整性

*对于任何*完成的处理阶段，进度报告应该包含阶段名称和经过的时间。

**验证需求：12.3**

### 属性 28：材质预设加载往返

*对于任何*有效的材质预设配置文件，加载后的预设数据应该与文件中定义的数据结构匹配，并且所有预设都应该可以通过名称访问。

**验证需求：13.1, 13.2**

### 属性 29：预设回退机制

*对于任何*配置文件丢失或无效的情况，系统应该回退到内置默认预设，并且这些默认预设应该是有效的材质参数。

**验证需求：13.4**

### 属性 30：自定义预设验证

*对于任何*自定义材质预设，在应用之前系统应该验证所有参数是否在有效范围内，拒绝无效的预设。

**验证需求：13.5**

### 属性 31：坐标系约定一致性

*对于所有*角度测量和位置计算，系统应该在内部一致地使用 Blender Z-up 坐标系，仅在输出 IES 文件时转换为 Y-up。

**验证需求：14.1, 14.3**

## 错误处理

### 错误分类

系统将错误分为三类：

1. **可恢复错误**：系统可以继续运行
   - 单个采样点渲染失败
   - 部分网格验证警告
   - 材质预设加载失败（回退到默认）

2. **用户错误**：需要用户纠正
   - 无效的文件路径
   - 不支持的文件格式
   - 无效的参数值

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

class ValidationError(KiroError):
    """验证错误"""
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message, "Validation", recoverable=False)
        self.errors = errors

class RenderError(KiroError):
    """渲染错误"""
    def __init__(self, message: str, position: Tuple[float, float, float]):
        super().__init__(message, "Renderer", recoverable=True)
        self.position = position
```

### 错误日志格式

```
[2024-01-15 14:32:45] [ERROR] [input_manager] 网格验证失败
  - 网格不封闭：发现 3 个开放边
  - 非流形几何：顶点 [42, 108, 256]
  建议：使用 Blender 的 "Make Manifold" 工具修复几何体
```

### 资源清理

所有模块应该实现上下文管理器协议，确保资源正确清理：

```python
class SceneBuilder:
    def __enter__(self):
        self.clear_scene()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理临时对象
        # 恢复场景状态
        pass
```

## 测试策略

### 双重测试方法

系统将使用单元测试和基于属性的测试的组合：

**单元测试**：
- 验证特定示例和边缘情况
- 测试错误条件和异常处理
- 验证集成点和模块交互
- 测试具体的材质预设（磨砂玻璃、乳白亚克力）
- 测试具体的渲染模式配置（预览、生产）

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
    属性 10：球面坐标计算
    Feature: kiro-ies-generator, Property 10: 对于任何角度对和距离，
    球面到笛卡尔转换应该产生距原点指定距离的点
    """
    x, y, z = spherical_to_cartesian(theta, phi, distance)
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

### 基准测试

系统包含三个关键基准测试：

1. **球体测试（test_sphere.py）**
   - 验证各向同性光源（裸灯泡）
   - 预期结果：所有方向的光强度相等
   - 用于校准基线

2. **遮挡测试（test_occlusion.py）**
   - 验证半球遮罩的光分布
   - 预期结果：一半球面为零，另一半为均匀分布
   - 验证几何遮挡正确性

3. **校准测试（test_calibration.py）**
   - 验证单位转换准确性
   - 使用已知光通量的光源
   - 验证总坎德拉值与流明值的关系

### 测试覆盖目标

- 单元测试代码覆盖率：> 80%
- 属性测试：所有 31 个属性
- 集成测试：完整的端到端工作流
- 基准测试：所有三个基准场景

### 持续集成

测试应该在以下情况下运行：
- 每次代码提交
- 每次拉取请求
- 每日构建（包括长时间运行的生产模式测试）

CI 环境要求：
- Blender 3.6+ 或 4.x
- Python 3.10+
- hypothesis 库
- numpy 库
