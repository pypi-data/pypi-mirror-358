"""
版本文件操作工具
"""

import re
from pathlib import Path
from typing import Optional


class VersionFileManager:
    """版本文件管理器"""
    
    def __init__(self, version_file: Optional[str] = None):
        """
        初始化版本文件管理器
        
        Args:
            version_file: 版本文件路径，如果为 None 则自动查找
        """
        self.version_file = Path(version_file) if version_file else self._find_version_file()
    
    def _find_version_file(self) -> Path:
        """
        自动查找版本文件
        
        Returns:
            版本文件路径
            
        Raises:
            FileNotFoundError: 找不到版本文件
        """
        # 按优先级查找版本文件
        candidates = [
            "__init__.py",
            "version.py",
            "setup.py",
            "pyproject.toml"
        ]
        
        for candidate in candidates:
            if Path(candidate).exists():
                return Path(candidate)
        
        # 如果都找不到，创建 __init__.py
        init_file = Path("__init__.py")
        if not init_file.exists():
            init_file.write_text('__version__ = "0.0.0"\n')
        
        return init_file
    
    def read_version(self) -> str:
        """
        从文件中读取版本号
        
        Returns:
            版本号字符串
            
        Raises:
            ValueError: 无法解析版本号
        """
        if not self.version_file.exists():
            return "0.0.0"
        
        content = self.version_file.read_text(encoding='utf-8')
        
        # 根据文件类型使用不同的解析策略
        if self.version_file.name == "pyproject.toml":
            return self._parse_pyproject_toml(content)
        else:
            return self._parse_python_file(content)
    
    def write_version(self, version: str) -> None:
        """
        将版本号写入文件
        
        Args:
            version: 要写入的版本号
        """
        if not self.version_file.exists():
            # 创建新文件
            if self.version_file.name == "pyproject.toml":
                content = f'[tool.version-manager]\nversion = "{version}"\n'
            else:
                content = f'__version__ = "{version}"\n'
            
            self.version_file.write_text(content, encoding='utf-8')
            return
        
        content = self.version_file.read_text(encoding='utf-8')
        
        # 根据文件类型使用不同的写入策略
        if self.version_file.name == "pyproject.toml":
            new_content = self._update_pyproject_toml(content, version)
        else:
            new_content = self._update_python_file(content, version)
        
        self.version_file.write_text(new_content, encoding='utf-8')
    
    def _parse_python_file(self, content: str) -> str:
        """
        解析 Python 文件中的版本号
        
        Args:
            content: 文件内容
            
        Returns:
            版本号字符串
        """
        # 匹配 __version__ = "1.0.0" 或 __version__ = '1.0.0'
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        
        # 匹配 version = "1.0.0" 或 version = '1.0.0'
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        
        return "0.0.0"
    
    def _parse_pyproject_toml(self, content: str) -> str:
        """
        解析 pyproject.toml 文件中的版本号
        
        Args:
            content: 文件内容
            
        Returns:
            版本号字符串
        """
        # 匹配 [tool.version-manager] 下的 version
        match = re.search(r'\[tool\.version-manager\].*?version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        if match:
            return match.group(1)
        
        # 匹配 [project] 下的 version
        match = re.search(r'\[project\].*?version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        if match:
            return match.group(1)
        
        return "0.0.0"
    
    def _update_python_file(self, content: str, version: str) -> str:
        """
        更新 Python 文件中的版本号，保留原有引号风格，支持单引号和双引号
        """
        # 替换 __version__ = "xxx" 或 __version__ = 'xxx'
        def repl_version(m):
            quote = m.group(1)
            return f'__version__ = {quote}{version}{quote}'
        content = re.sub(
            r'__version__\s*=\s*([\'\"])\S+\1',
            repl_version,
            content
        )
        # 替换 version = "xxx" 或 version = 'xxx'
        def repl_version2(m):
            quote = m.group(1)
            return f'version = {quote}{version}{quote}'
        content = re.sub(
            r'version\s*=\s*([\'\"])\S+\1',
            repl_version2,
            content
        )
        return content
    
    def _update_pyproject_toml(self, content: str, version: str) -> str:
        """
        更新 pyproject.toml 文件中的版本号，修复 group 超过9时报错
        """
        # 替换 [tool.version-manager] 下的 version
        content = re.sub(
            r'(\[tool\.version-manager\].*?version\s*=\s*["\"][^"\']+["\"])(.*)',
            lambda m: re.sub(r'(version\s*=\s*["\"])\d+\.\d+\.\d+(-[\w\.]+)?(["\"])',
                             rf'\g<1>{version}\g<3>', m.group(0)),
            content,
            flags=re.DOTALL
        )
        # 替换 [project] 下的 version
        content = re.sub(
            r'(\[project\].*?version\s*=\s*["\"][^"\']+["\"])(.*)',
            lambda m: re.sub(r'(version\s*=\s*["\"])\d+\.\d+\.\d+(-[\w\.]+)?(["\"])',
                             rf'\g<1>{version}\g<3>', m.group(0)),
            content,
            flags=re.DOTALL
        )
        return content
    
    def get_file_type(self) -> str:
        """
        获取版本文件类型
        
        Returns:
            文件类型描述
        """
        if self.version_file.name == "pyproject.toml":
            return "pyproject.toml"
        elif self.version_file.name == "setup.py":
            return "setup.py"
        elif self.version_file.name == "__init__.py":
            return "Python package"
        else:
            return "Python file" 