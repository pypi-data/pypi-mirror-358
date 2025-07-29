"""
测试文件操作功能
"""

import pytest
from pathlib import Path
from version_manager.file_utils import VersionFileManager


class TestVersionFileManager:
    """测试版本文件管理器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = Path("temp_test")
        self.temp_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_find_version_file_init_py(self):
        """测试查找 __init__.py 文件"""
        init_file = self.temp_dir / "__init__.py"
        init_file.write_text('__version__ = "1.0.0"\n')
        
        vm = VersionFileManager()
        vm.version_file = self.temp_dir / "__init__.py"
        
        assert vm.get_file_type() == "Python package"
    
    def test_find_version_file_version_py(self):
        """测试查找 version.py 文件"""
        version_file = self.temp_dir / "version.py"
        version_file.write_text('__version__ = "1.0.0"\n')
        
        vm = VersionFileManager(str(version_file))
        
        assert vm.get_file_type() == "Python file"
    
    def test_find_version_file_setup_py(self):
        """测试查找 setup.py 文件"""
        setup_file = self.temp_dir / "setup.py"
        setup_file.write_text('version = "1.0.0"\n')
        
        vm = VersionFileManager(str(setup_file))
        
        assert vm.get_file_type() == "setup.py"
    
    def test_find_version_file_pyproject_toml(self):
        """测试查找 pyproject.toml 文件"""
        pyproject_file = self.temp_dir / "pyproject.toml"
        pyproject_file.write_text('[project]\nversion = "1.0.0"\n')
        
        vm = VersionFileManager(str(pyproject_file))
        
        assert vm.get_file_type() == "pyproject.toml"
    
    def test_parse_python_file_version(self):
        """测试解析 Python 文件中的版本号"""
        # 测试 __version__ 格式
        content = '__version__ = "1.0.0"\n'
        vm = VersionFileManager()
        result = vm._parse_python_file(content)
        assert result == "1.0.0"
        
        # 测试 version 格式
        content = 'version = "2.0.0"\n'
        result = vm._parse_python_file(content)
        assert result == "2.0.0"
        
        # 测试单引号
        content = "__version__ = '3.0.0'\n"
        result = vm._parse_python_file(content)
        assert result == "3.0.0"
        
        # 测试没有版本号
        content = "print('Hello World')\n"
        result = vm._parse_python_file(content)
        assert result == "0.0.0"
    
    def test_parse_pyproject_toml_version(self):
        """测试解析 pyproject.toml 文件中的版本号"""
        # 测试 [project] 格式
        content = '[project]\nversion = "1.0.0"\n'
        vm = VersionFileManager()
        result = vm._parse_pyproject_toml(content)
        assert result == "1.0.0"
        
        # 测试 [tool.version-manager] 格式
        content = '[tool.version-manager]\nversion = "2.0.0"\n'
        result = vm._parse_pyproject_toml(content)
        assert result == "2.0.0"
        
        # 测试没有版本号
        content = '[project]\nname = "test"\n'
        result = vm._parse_pyproject_toml(content)
        assert result == "0.0.0"
    
    def test_update_python_file_version(self):
        """测试更新 Python 文件中的版本号"""
        # 测试更新 __version__
        content = '__version__ = "1.0.0"\nprint("Hello")\n'
        vm = VersionFileManager()
        new_content = vm._update_python_file(content, "2.0.0")
        assert '__version__ = "2.0.0"' in new_content
        assert 'print("Hello")' in new_content
        
        # 测试更新 version
        content = 'version = "1.0.0"\nprint("Hello")\n'
        new_content = vm._update_python_file(content, "3.0.0")
        assert 'version = "3.0.0"' in new_content
        
        # 测试单引号
        content = "__version__ = '1.0.0'\n"
        new_content = vm._update_python_file(content, "4.0.0")
        assert "__version__ = '4.0.0'" in new_content
    
    def test_update_pyproject_toml_version(self):
        """测试更新 pyproject.toml 文件中的版本号"""
        # 测试更新 [project] 格式
        content = '[project]\nversion = "1.0.0"\nname = "test"\n'
        vm = VersionFileManager()
        new_content = vm._update_pyproject_toml(content, "2.0.0")
        assert 'version = "2.0.0"' in new_content
        assert 'name = "test"' in new_content
        
        # 测试更新 [tool.version-manager] 格式
        content = '[tool.version-manager]\nversion = "1.0.0"\n'
        new_content = vm._update_pyproject_toml(content, "3.0.0")
        assert 'version = "3.0.0"' in new_content
    
    def test_write_version_new_file(self):
        """测试写入版本号到新文件"""
        file_path = self.temp_dir / "new_version.py"
        vm = VersionFileManager(str(file_path))
        
        vm.write_version("1.0.0")
        
        assert file_path.exists()
        content = file_path.read_text()
        assert '__version__ = "1.0.0"' in content
    
    def test_write_version_new_pyproject_toml(self):
        """测试写入版本号到新的 pyproject.toml 文件"""
        file_path = self.temp_dir / "pyproject.toml"
        vm = VersionFileManager(str(file_path))
        
        vm.write_version("1.0.0")
        
        assert file_path.exists()
        content = file_path.read_text()
        assert 'version = "1.0.0"' in content
    
    def test_read_write_version_cycle(self):
        """测试版本号读写循环"""
        file_path = self.temp_dir / "test_version.py"
        vm = VersionFileManager(str(file_path))
        
        # 写入版本号
        vm.write_version("1.0.0")
        assert vm.read_version() == "1.0.0"
        
        # 更新版本号
        vm.write_version("2.0.0")
        assert vm.read_version() == "2.0.0"
        
        # 再次更新
        vm.write_version("2.1.0")
        assert vm.read_version() == "2.1.0" 