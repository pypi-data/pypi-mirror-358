"""
命令行接口
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core import VersionManager
from .git_utils import GitManager


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        参数解析器
    """
    parser = argparse.ArgumentParser(
        description="Bump Version - 一个简单易用的版本管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
版本类型说明:
  patch      - 补丁版本 (1.0.0 -> 1.0.1)
  minor      - 次要版本 (1.0.0 -> 1.1.0)
  major      - 主要版本 (1.0.0 -> 2.0.0)
  prepatch   - 预发布补丁版本 (1.0.0 -> 1.0.1-0)
  preminor   - 预发布次要版本 (1.0.0 -> 1.1.0-0)
  premajor   - 预发布主要版本 (1.0.0 -> 2.0.0-0)
  prerelease - 预发布版本 (1.0.0 -> 1.0.1-0, 1.0.1-0 -> 1.0.1-1)

使用示例:
  bump patch                    # 增加补丁版本
  bump minor --push             # 增加次要版本并推送
  bump prerelease --file custom_version.py  # 使用自定义版本文件
        """
    )
    
    parser.add_argument(
        'version_type',
        choices=['patch', 'minor', 'major', 'prepatch', 'preminor', 'premajor', 'prerelease'],
        help='版本类型'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='版本文件路径 (默认自动查找)'
    )
    
    parser.add_argument(
        '--push', '-p',
        action='store_true',
        help='自动推送到远程仓库'
    )
    
    parser.add_argument(
        '--message', '-m',
        help='自定义提交信息'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅显示将要执行的操作，不实际执行'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细信息'
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """
    命令行主函数
    
    Args:
        args: 命令行参数，如果为 None 则从 sys.argv 读取
        
    Returns:
        退出码
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    try:
        # 初始化版本管理器
        vm = VersionManager(parsed_args.file)
        
        # 显示当前版本
        current_version = vm.read()
        print(f"当前版本: {current_version}")
        
        if parsed_args.dry_run:
            # 仅显示将要执行的操作
            new_version = vm.bump(parsed_args.version_type)
            print(f"将要更新版本: {current_version} -> {new_version}")
            
            if parsed_args.push:
                print("将要推送到远程仓库")
            
            return 0
        
        # 更新版本
        new_version = vm.bump(parsed_args.version_type)
        print(f"✅ 版本已更新: {current_version} -> {new_version}")
        
        # Git 操作
        git_manager = GitManager()
        
        if git_manager.is_git_repo():
            if parsed_args.verbose:
                print(f"Git 仓库: {git_manager.get_remote_url() or '本地仓库'}")
                print(f"当前分支: {git_manager.get_current_branch()}")
            
            # 提交和标签
            git_manager.commit_and_tag(
                version=new_version,
                message=parsed_args.message,
                auto_push=parsed_args.push
            )
        else:
            print("⚠️  当前目录不是 Git 仓库，跳过 Git 操作")
        
        return 0
        
    except ValueError as e:
        print(f"❌ 错误: {e}")
        return 1
    except RuntimeError as e:
        print(f"❌ 运行时错误: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        if parsed_args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def show_info() -> None:
    """
    显示版本信息
    """
    from . import __version__
    print(f"Python Version Manager v{__version__}")


if __name__ == "__main__":
    sys.exit(main()) 