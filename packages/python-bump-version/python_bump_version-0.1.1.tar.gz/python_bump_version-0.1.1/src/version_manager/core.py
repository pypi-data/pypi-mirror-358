"""
版本管理核心逻辑
"""

import re
from typing import Dict, Optional
from .file_utils import VersionFileManager


class VersionManager:
    """版本管理器核心类"""
    
    def __init__(self, version_file: Optional[str] = None):
        """
        初始化版本管理器
        
        Args:
            version_file: 版本文件路径，如果为 None 则自动查找
        """
        self.file_manager = VersionFileManager(version_file)
    
    def read(self) -> str:
        """
        读取当前版本号
        
        Returns:
            当前版本号字符串
        """
        return self.file_manager.read_version()
    
    def write(self, version: str) -> None:
        """
        写入版本号到文件
        
        Args:
            version: 要写入的版本号
        """
        self.file_manager.write_version(version)
    
    def parse(self, version: str) -> Dict[str, any]:
        """
        解析版本号，支持预发布版本
        
        Args:
            version: 版本号字符串
            
        Returns:
            解析后的版本字典
            
        Raises:
            ValueError: 版本号格式无效
        """
        # 匹配格式: 1.0.0 或 1.0.0-0 或 1.0.0-alpha.1，必须结尾
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$', version)
        if not match:
            raise ValueError(f"无效的版本号格式: {version}")
        major, minor, patch, prerelease = match.groups()
        return {
            'major': int(major),
            'minor': int(minor),
            'patch': int(patch),
            'prerelease': prerelease
        }
    
    def format(self, version_dict: Dict[str, any]) -> str:
        """
        格式化版本号
        
        Args:
            version_dict: 版本字典
            
        Returns:
            格式化后的版本号字符串
        """
        version = f"{version_dict['major']}.{version_dict['minor']}.{version_dict['patch']}"
        if version_dict['prerelease']:
            version += f"-{version_dict['prerelease']}"
        return version
    
    def _get_next_prerelease_number(self, version_dict: Dict[str, any]) -> int:
        """
        获取下一个预发布版本号
        
        Args:
            version_dict: 版本字典
            
        Returns:
            下一个预发布版本号
        """
        prerelease = version_dict['prerelease']
        if not prerelease:
            return 0
        
        # 如果预发布版本就是纯数字，直接递增
        if prerelease.isdigit():
            return int(prerelease) + 1
        
        # 匹配预发布版本号，如 alpha.1, beta.2, rc.3
        match = re.match(r'(\w+)\.(\d+)', prerelease)
        if match:
            label, number = match.groups()
            return int(number) + 1
        
        # 如果没有数字，返回 1
        return 1
    
    def bump(self, version_type: str) -> str:
        """
        增加版本号
        
        Args:
            version_type: 版本类型 (patch, minor, major, prepatch, preminor, premajor, prerelease)
            
        Returns:
            新的版本号
            
        Raises:
            ValueError: 无效的版本类型
        """
        current = self.read()
        version_dict = self.parse(current)
        
        if version_type == 'patch':
            version_dict['patch'] += 1
            version_dict['prerelease'] = None
        elif version_type == 'minor':
            version_dict['minor'] += 1
            version_dict['patch'] = 0
            version_dict['prerelease'] = None
        elif version_type == 'major':
            version_dict['major'] += 1
            version_dict['minor'] = 0
            version_dict['patch'] = 0
            version_dict['prerelease'] = None
        elif version_type == 'prepatch':
            version_dict['patch'] += 1
            version_dict['prerelease'] = '0'
        elif version_type == 'preminor':
            version_dict['minor'] += 1
            version_dict['patch'] = 0
            version_dict['prerelease'] = '0'
        elif version_type == 'premajor':
            version_dict['major'] += 1
            version_dict['minor'] = 0
            version_dict['patch'] = 0
            version_dict['prerelease'] = '0'
        elif version_type == 'prerelease':
            # 如果当前已经是预发布版本，增加预发布号
            if version_dict['prerelease']:
                next_number = self._get_next_prerelease_number(version_dict)
                prerelease_label = re.match(r'(\w+)', version_dict['prerelease'])
                if prerelease_label and '.' in version_dict['prerelease']:
                    # 如果是 alpha.1 这种格式，保持标签
                    version_dict['prerelease'] = f"{prerelease_label.group(1)}.{next_number}"
                else:
                    # 如果是纯数字，直接使用数字
                    version_dict['prerelease'] = str(next_number)
            else:
                # 如果当前不是预发布版本，创建补丁预发布版本
                version_dict['patch'] += 1
                version_dict['prerelease'] = '0'
        else:
            raise ValueError(f"未知的版本类型: {version_type}")
        
        new_version = self.format(version_dict)
        self.write(new_version)
        return new_version
    
    def validate(self, version: str) -> bool:
        """
        验证版本号格式
        
        Args:
            version: 要验证的版本号
            
        Returns:
            是否有效
        """
        # 严格匹配结尾
        return bool(re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$', version)) 