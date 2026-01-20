"""
输出管理器模块 (Output Manager)

负责文件写入、元数据生成和文件验证。
"""

from typing import Dict, List, Tuple, Optional
import os
import json
from datetime import datetime


class OutputError(Exception):
    """输出错误"""
    pass


def write_ies_file(ies_content: str, output_path: str, overwrite: bool = False) -> bool:
    """
    写入 IES 文件到磁盘
    
    参数:
        ies_content: IES 文件内容
        output_path: 输出文件路径
        overwrite: 是否覆盖已存在的文件
    
    返回:
        True 如果写入成功
    
    异常:
        OutputError: 文件写入失败
    """
    # 确保目录存在
    ensure_directory_exists(os.path.dirname(output_path))
    
    # 检查文件是否存在
    if os.path.exists(output_path) and not overwrite:
        raise OutputError(f"文件已存在：{output_path}，请确认是否覆盖")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ies_content)
        return True
    except Exception as e:
        raise OutputError(f"写入 IES 文件失败：{str(e)}")


def write_metadata_file(metadata: Dict, output_path: str, overwrite: bool = False) -> bool:
    """
    写入 JSON 元数据文件到磁盘
    
    参数:
        metadata: 元数据字典
        output_path: 输出文件路径
        overwrite: 是否覆盖已存在的文件
    
    返回:
        True 如果写入成功
    
    异常:
        OutputError: 文件写入失败
    """
    # 确保目录存在
    ensure_directory_exists(os.path.dirname(output_path))
    
    # 检查文件是否存在
    if os.path.exists(output_path) and not overwrite:
        raise OutputError(f"文件已存在：{output_path}，请确认是否覆盖")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        raise OutputError(f"写入元数据文件失败：{str(e)}")


def ensure_directory_exists(directory: str):
    """
    创建必要的目录
    
    参数:
        directory: 目录路径
    """
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            raise OutputError(f"创建目录失败：{str(e)}")


def generate_metadata(fixture_name: str,
                     photometric_center_world: Tuple[float, float, float],
                     photometric_center_relative: Tuple[float, float, float],
                     light_sources: List[Dict],
                     total_lumens: float) -> Dict:
    """
    生成完整的元数据字典
    
    参数:
        fixture_name: 灯具名称
        photometric_center_world: 光度中心世界坐标 (x, y, z)
        photometric_center_relative: 光度中心相对坐标 (x, y, z)
        light_sources: 光源信息列表
        total_lumens: 总流明值
    
    返回:
        元数据字典
    """
    metadata = {
        "fixture_name": fixture_name,
        "generated_date": datetime.now().isoformat(),
        "photometric_center": {
            "world_coordinates": {
                "x": photometric_center_world[0],
                "y": photometric_center_world[1],
                "z": photometric_center_world[2],
                "unit": "meters"
            },
            "relative_to_fixture_origin": {
                "x": photometric_center_relative[0],
                "y": photometric_center_relative[1],
                "z": photometric_center_relative[2],
                "unit": "meters",
                "note": "相对于灯具模型的原点（Pivot）"
            }
        },
        "light_sources": light_sources,
        "total_lumens": total_lumens,
        "usage_instructions": {
            "unreal_engine": f"在灯具模型原点偏移 ({photometric_center_relative[0]:.3f}, {photometric_center_relative[1]:.3f}, {photometric_center_relative[2]:.3f}) 处放置 IES 光源",
            "vray": f"使用 VRayIES 光源，位置偏移 ({photometric_center_relative[0]:.3f}, {photometric_center_relative[1]:.3f}, {photometric_center_relative[2]:.3f})",
            "corona": f"使用 CoronaLight，位置偏移 ({photometric_center_relative[0]:.3f}, {photometric_center_relative[1]:.3f}, {photometric_center_relative[2]:.3f})"
        }
    }
    
    return metadata


def verify_file_written(file_path: str) -> bool:
    """
    验证文件成功写入
    
    参数:
        file_path: 文件路径
    
    返回:
        True 如果文件存在且可读
    """
    if not os.path.exists(file_path):
        return False
    
    if not os.path.isfile(file_path):
        return False
    
    # 检查文件大小
    if os.path.getsize(file_path) == 0:
        return False
    
    # 尝试读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1)  # 读取第一个字符
        return True
    except Exception:
        return False


def get_default_output_path(fixture_name: str, output_dir: Optional[str] = None) -> str:
    """
    生成默认输出路径
    
    参数:
        fixture_name: 灯具名称
        output_dir: 输出目录（可选）
    
    返回:
        默认的 IES 文件路径
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    # 清理文件名（移除非法字符）
    safe_name = "".join(c for c in fixture_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    
    if not safe_name:
        safe_name = "fixture"
    
    ies_filename = f"{safe_name}.ies"
    return os.path.join(output_dir, ies_filename)


def get_metadata_path(ies_path: str) -> str:
    """
    根据 IES 文件路径生成元数据文件路径
    
    参数:
        ies_path: IES 文件路径
    
    返回:
        元数据文件路径
    """
    base_path = os.path.splitext(ies_path)[0]
    return f"{base_path}_metadata.json"
