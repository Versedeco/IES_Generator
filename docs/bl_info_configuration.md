# bl_info 配置说明

## 概述

本文档说明 Kiro IES Generator Blender 插件的 `bl_info` 元数据配置。

## bl_info 字典

`bl_info` 是 Blender 插件的元数据字典，包含插件的基本信息。它位于 `kiro_ies_generator/__init__.py` 文件的顶部。

## 配置内容

```python
bl_info = {
    "name": "Kiro IES Generator",
    "author": "Kiro Team",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > IES Generator",
    "description": "从 Blender 场景生成 IESNA LM-63 标准的 IES 光度学文件。支持 Cycles 物理渲染，模拟半透明材质的光学特性",
    "warning": "需要 Cycles 渲染引擎。推荐使用 GPU 渲染以获得最佳性能",
    "doc_url": "https://github.com/kiro-team/kiro-ies-generator",
    "support": "COMMUNITY",
    "category": "Lighting",
}
```

## 字段说明

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | str | 插件名称，显示在 Blender 插件列表中 |
| `author` | str | 插件作者或团队名称 |
| `version` | tuple | 插件版本号 (major, minor, patch) |
| `blender` | tuple | 最低支持的 Blender 版本 (major, minor, patch) |
| `location` | str | 插件在 Blender UI 中的位置 |
| `description` | str | 插件功能描述 |
| `category` | str | 插件分类，用于在插件管理器中分组 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `warning` | str | 警告信息，显示在插件列表中 |
| `doc_url` | str | 文档链接 |
| `support` | str | 支持级别：OFFICIAL、COMMUNITY 或 TESTING |

## 版本信息

- **插件版本**: 1.0.0
  - 主版本号 (major): 1
  - 次版本号 (minor): 0
  - 修订号 (patch): 0

- **Blender 版本要求**: 3.6.0+
  - 支持 Blender 3.6.x
  - 支持 Blender 4.x

## 分类

插件分类为 **Lighting**，表示这是一个照明相关的工具。

在 Blender 插件管理器中，用户可以通过以下路径找到插件：
- Edit > Preferences > Add-ons > Lighting > Kiro IES Generator

## 位置

插件面板位于：
- **3D 视图** (View3D)
- **侧边栏** (Sidebar)
- **IES Generator** 标签页

用户可以通过以下方式访问：
1. 在 3D 视图中按 `N` 键打开侧边栏
2. 点击 "IES Generator" 标签页

## 警告信息

插件显示以下警告信息：
> 需要 Cycles 渲染引擎。推荐使用 GPU 渲染以获得最佳性能

这提醒用户：
- 插件依赖 Cycles 渲染引擎
- 使用 GPU 渲染可以显著提升性能（5-20 倍速度提升）

## 支持级别

插件的支持级别为 **COMMUNITY**，表示：
- 这是一个社区支持的插件
- 不是 Blender 官方插件
- 由社区维护和支持

## 验证

可以使用以下命令验证 bl_info 配置：

```bash
python tests/validate_bl_info.py
```

验证脚本会检查：
- 所有必需字段是否存在
- 字段类型是否正确
- 版本号格式是否正确
- 分类是否有效
- 内容是否符合规范

## 更新历史

### 版本 1.0.0 (当前)
- 初始配置
- 添加完整的描述信息
- 添加警告信息
- 设置支持级别为 COMMUNITY
- 配置文档 URL

## 参考资料

- [Blender Add-on Tutorial](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
- [Blender Python API - bl_info](https://docs.blender.org/api/current/info_overview.html#add-on-metadata)
