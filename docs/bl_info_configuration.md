# Blender 插件元数据配置 (bl_info)

## 配置概述

`bl_info` 是 Blender 插件的元数据字典，包含插件的基本信息。这些信息会显示在 Blender 的插件管理界面中。

## 当前配置

```python
bl_info = {
    "name": "Kiro IES Generator",
    "author": "Kiro Team",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > IES Generator",
    "description": "从 Blender 场景生成 IESNA LM-63 标准的 IES 光度学文件，使用 Cycles 物理渲染进行球面采样",
    "warning": "需要 Cycles 渲染引擎，建议使用 GPU 加速",
    "doc_url": "https://github.com/kiro-team/kiro-ies-generator",
    "support": "COMMUNITY",
    "category": "Lighting",
}
```

## 字段说明

### 必需字段

| 字段 | 类型 | 值 | 说明 |
|------|------|-----|------|
| `name` | str | "Kiro IES Generator" | 插件名称，显示在插件列表中 |
| `author` | str | "Kiro Team" | 插件作者 |
| `version` | tuple | (1, 0, 0) | 插件版本号 (major, minor, patch) |
| `blender` | tuple | (3, 6, 0) | 最低支持的 Blender 版本 |
| `location` | str | "View3D > Sidebar > IES Generator" | 插件在 Blender UI 中的位置 |
| `description` | str | "从 Blender 场景生成..." | 插件功能描述 |
| `category` | str | "Lighting" | 插件分类 |

### 可选字段

| 字段 | 类型 | 值 | 说明 |
|------|------|-----|------|
| `warning` | str | "需要 Cycles 渲染引擎..." | 警告信息，提示用户注意事项 |
| `doc_url` | str | "https://github.com/..." | 文档链接 |
| `support` | str | "COMMUNITY" | 支持级别 (OFFICIAL, COMMUNITY, TESTING) |

## 版本号说明

版本号使用语义化版本控制 (Semantic Versioning)：

- **Major (1)**: 主版本号，重大更新或不兼容的 API 变更
- **Minor (0)**: 次版本号，向后兼容的功能新增
- **Patch (0)**: 修订号，向后兼容的问题修正

当前版本：**1.0.0** (首次发布版本)

## Blender 版本兼容性

- **最低版本**: Blender 3.6.0
- **测试版本**: Blender 3.6.x, 4.x
- **原因**: 需要 Python 3.10+ 和现代 Cycles 渲染引擎特性

## 分类说明

插件分类为 **"Lighting"**，因为：
- 主要功能是生成光度学文件
- 与照明设计和渲染相关
- 在 Blender 插件管理器中归类到照明类别

## 警告信息

插件包含警告信息：**"需要 Cycles 渲染引擎，建议使用 GPU 加速"**

这提醒用户：
1. 必须使用 Cycles 渲染引擎（不支持 Eevee）
2. 建议启用 GPU 加速以提高性能（5-20 倍速度提升）

## 支持级别

支持级别设置为 **"COMMUNITY"**，表示：
- 这是社区开发的插件
- 不是 Blender 官方插件
- 由社区提供支持和维护

## 验证清单

- [x] 所有必需字段已配置
- [x] 版本号格式正确 (三元组)
- [x] Blender 版本要求正确 (3.6.0+)
- [x] 分类有效 ("Lighting")
- [x] 描述清晰准确
- [x] 包含警告信息
- [x] 包含文档链接
- [x] 支持级别已设置

## 在 Blender 中的显示

当用户在 Blender 中打开插件管理器时，会看到：

```
插件名称: Kiro IES Generator
作者: Kiro Team
版本: 1.0.0
分类: Lighting
位置: View3D > Sidebar > IES Generator

描述:
从 Blender 场景生成 IESNA LM-63 标准的 IES 光度学文件，
使用 Cycles 物理渲染进行球面采样

警告:
需要 Cycles 渲染引擎，建议使用 GPU 加速

文档: https://github.com/kiro-team/kiro-ies-generator
支持: COMMUNITY
```

## 更新历史

### 版本 1.0.0 (当前)
- 初始配置
- 设置基本元数据
- 添加警告信息和文档链接
- 设置支持级别为 COMMUNITY

## 未来版本规划

### 版本 1.1.0 (计划)
- 添加新功能（待定）
- 性能优化

### 版本 2.0.0 (计划)
- 重大功能更新
- 可能的 API 变更

## 参考资料

- [Blender Add-on Tutorial](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
- [Blender Python API](https://docs.blender.org/api/current/index.html)
- [Semantic Versioning](https://semver.org/)
