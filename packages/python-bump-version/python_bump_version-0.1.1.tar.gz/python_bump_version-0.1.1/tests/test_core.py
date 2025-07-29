"""
测试版本管理核心功能
"""

import pytest
from pathlib import Path
from version_manager.core import VersionManager


class TestVersionManager:
    """测试版本管理器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_file = Path("temp_version.py")
        self.vm = VersionManager(str(self.temp_file))
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        if self.temp_file.exists():
            self.temp_file.unlink()
    
    def test_parse_version(self):
        """测试版本号解析"""
        # 标准版本
        result = self.vm.parse("1.0.0")
        assert result == {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': None}
        
        # 预发布版本
        result = self.vm.parse("1.0.0-0")
        assert result == {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': '0'}
        
        # 带标签的预发布版本
        result = self.vm.parse("1.0.0-alpha.1")
        assert result == {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': 'alpha.1'}
    
    def test_parse_invalid_version(self):
        """测试无效版本号解析"""
        with pytest.raises(ValueError):
            self.vm.parse("invalid")
        
        with pytest.raises(ValueError):
            self.vm.parse("1.0")
        
        with pytest.raises(ValueError):
            self.vm.parse("1.0.0.0")
    
    def test_format_version(self):
        """测试版本号格式化"""
        # 标准版本
        version_dict = {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': None}
        assert self.vm.format(version_dict) == "1.0.0"
        
        # 预发布版本
        version_dict = {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': '0'}
        assert self.vm.format(version_dict) == "1.0.0-0"
        
        # 带标签的预发布版本
        version_dict = {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': 'alpha.1'}
        assert self.vm.format(version_dict) == "1.0.0-alpha.1"
    
    def test_bump_patch(self):
        """测试补丁版本递增"""
        # 设置初始版本
        self.vm.write("1.0.0")
        
        # 递增补丁版本
        new_version = self.vm.bump('patch')
        assert new_version == "1.0.1"
        assert self.vm.read() == "1.0.1"
    
    def test_bump_minor(self):
        """测试次要版本递增"""
        # 设置初始版本
        self.vm.write("1.0.0")
        
        # 递增次要版本
        new_version = self.vm.bump('minor')
        assert new_version == "1.1.0"
        assert self.vm.read() == "1.1.0"
    
    def test_bump_major(self):
        """测试主要版本递增"""
        # 设置初始版本
        self.vm.write("1.0.0")
        
        # 递增主要版本
        new_version = self.vm.bump('major')
        assert new_version == "2.0.0"
        assert self.vm.read() == "2.0.0"
    
    def test_bump_prepatch(self):
        """测试预发布补丁版本"""
        # 设置初始版本
        self.vm.write("1.0.0")
        
        # 创建预发布补丁版本
        new_version = self.vm.bump('prepatch')
        assert new_version == "1.0.1-0"
        assert self.vm.read() == "1.0.1-0"
    
    def test_bump_preminor(self):
        """测试预发布次要版本"""
        # 设置初始版本
        self.vm.write("1.0.0")
        
        # 创建预发布次要版本
        new_version = self.vm.bump('preminor')
        assert new_version == "1.1.0-0"
        assert self.vm.read() == "1.1.0-0"
    
    def test_bump_premajor(self):
        """测试预发布主要版本"""
        # 设置初始版本
        self.vm.write("1.0.0")
        
        # 创建预发布主要版本
        new_version = self.vm.bump('premajor')
        assert new_version == "2.0.0-0"
        assert self.vm.read() == "2.0.0-0"
    
    def test_bump_prerelease(self):
        """测试预发布版本递增"""
        # 从标准版本开始
        self.vm.write("1.0.0")
        new_version = self.vm.bump('prerelease')
        assert new_version == "1.0.1-0"
        
        # 递增预发布版本
        new_version = self.vm.bump('prerelease')
        assert new_version == "1.0.1-1"
        
        # 再次递增
        new_version = self.vm.bump('prerelease')
        assert new_version == "1.0.1-2"
    
    def test_bump_prerelease_with_label(self):
        """测试带标签的预发布版本递增"""
        # 设置带标签的预发布版本
        self.vm.write("1.0.0-alpha.1")
        
        # 递增预发布版本
        new_version = self.vm.bump('prerelease')
        assert new_version == "1.0.0-alpha.2"
        
        # 再次递增
        new_version = self.vm.bump('prerelease')
        assert new_version == "1.0.0-alpha.3"
    
    def test_bump_invalid_type(self):
        """测试无效的版本类型"""
        self.vm.write("1.0.0")
        
        with pytest.raises(ValueError):
            self.vm.bump('invalid')
    
    def test_validate_version(self):
        """测试版本号验证"""
        # 有效版本号
        assert self.vm.validate("1.0.0") == True
        assert self.vm.validate("1.0.0-0") == True
        assert self.vm.validate("1.0.0-alpha.1") == True
        
        # 无效版本号
        assert self.vm.validate("invalid") == False
        assert self.vm.validate("1.0") == False
        assert self.vm.validate("1.0.0.0") == False
    
    def test_read_write_version(self):
        """测试版本号读写"""
        # 写入版本号
        self.vm.write("1.0.0")
        assert self.vm.read() == "1.0.0"
        
        # 更新版本号
        self.vm.write("2.0.0")
        assert self.vm.read() == "2.0.0" 