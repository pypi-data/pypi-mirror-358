"""
Git 操作工具
"""

import subprocess
from typing import Optional, List


class GitManager:
    """Git 管理器"""
    
    def __init__(self, cwd: Optional[str] = None):
        """
        初始化 Git 管理器
        
        Args:
            cwd: 工作目录，默认为当前目录
        """
        self.cwd = cwd
    
    def is_git_repo(self) -> bool:
        """
        检查当前目录是否为 Git 仓库
        
        Returns:
            是否为 Git 仓库
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def get_status(self) -> str:
        """
        获取 Git 状态
        
        Returns:
            Git 状态信息
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取 Git 状态失败: {e}")
    
    def has_uncommitted_changes(self) -> bool:
        """
        检查是否有未提交的更改
        
        Returns:
            是否有未提交的更改
        """
        return bool(self.get_status())
    
    def add_files(self, files: Optional[List[str]] = None) -> None:
        """
        添加文件到暂存区
        
        Args:
            files: 要添加的文件列表，如果为 None 则添加所有文件
        """
        try:
            if files:
                subprocess.run(['git', 'add'] + files, cwd=self.cwd, check=True)
            else:
                subprocess.run(['git', 'add', '.'], cwd=self.cwd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"添加文件失败: {e}")
    
    def commit(self, message: str) -> None:
        """
        提交更改
        
        Args:
            message: 提交信息
        """
        try:
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.cwd,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"提交失败: {e}")
    
    def create_tag(self, tag_name: str, message: Optional[str] = None) -> None:
        """
        创建标签
        
        Args:
            tag_name: 标签名
            message: 标签信息，可选
        """
        try:
            if message:
                subprocess.run(
                    ['git', 'tag', '-a', tag_name, '-m', message],
                    cwd=self.cwd,
                    check=True
                )
            else:
                subprocess.run(
                    ['git', 'tag', tag_name],
                    cwd=self.cwd,
                    check=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"创建标签失败: {e}")
    
    def push(self, ref: Optional[str] = None) -> None:
        """
        推送到远程仓库
        
        Args:
            ref: 要推送的引用，如果为 None 则推送当前分支
        """
        try:
            if ref:
                subprocess.run(['git', 'push', 'origin', ref], cwd=self.cwd, check=True)
            else:
                subprocess.run(['git', 'push'], cwd=self.cwd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"推送失败: {e}")
    
    def push_tags(self) -> None:
        """
        推送所有标签
        """
        try:
            subprocess.run(['git', 'push', '--tags'], cwd=self.cwd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"推送标签失败: {e}")
    
    def get_latest_tag(self) -> Optional[str]:
        """
        获取最新标签
        
        Returns:
            最新标签名，如果没有标签则返回 None
        """
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except FileNotFoundError:
            return None
    
    def get_current_branch(self) -> str:
        """
        获取当前分支名
        
        Returns:
            当前分支名
        """
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取当前分支失败: {e}")
    
    def commit_and_tag(self, version: str, message: Optional[str] = None, auto_push: bool = False) -> None:
        """
        提交更改并创建标签
        
        Args:
            version: 版本号
            message: 提交信息，如果为 None 则使用默认信息
            auto_push: 是否自动推送
        """
        if not self.is_git_repo():
            raise RuntimeError("当前目录不是 Git 仓库")
        
        # 检查是否有未提交的更改
        if not self.has_uncommitted_changes():
            print("没有需要提交的更改")
            return
        
        # 添加文件
        self.add_files()
        
        # 提交
        commit_message = message or f"chore: bump version to {version}"
        self.commit(commit_message)
        
        # 创建标签
        tag_name = f"v{version}"
        self.create_tag(tag_name, f"Release {version}")
        
        print(f"✅ 版本已更新到 {version}")
        print(f"✅ Git 提交和标签已创建")
        
        if auto_push:
            # 推送提交
            self.push()
            
            # 推送标签
            self.push_tags()
            
            print(f"✅ 代码和标签已推送到远端")
        else:
            print(f"📦 请手动推送: git push && git push --tags")
    
    def get_remote_url(self) -> Optional[str]:
        """
        获取远程仓库 URL
        
        Returns:
            远程仓库 URL，如果没有则返回 None
        """
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except FileNotFoundError:
            return None 