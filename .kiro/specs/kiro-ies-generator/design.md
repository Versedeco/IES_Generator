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
