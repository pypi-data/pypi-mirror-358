from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os


class BaseSetup(ABC):
    """测试前置任务的基类，允许用户以插件形式自定义"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化Setup
        
        Args:
            config: 配置参数字典
        """
        self.config = config or {}
    
    @abstractmethod
    def setup(self) -> None:
        """
        执行前置任务设置
        子类必须实现此方法
        """
        pass
    
    @abstractmethod
    def teardown(self) -> None:
        """
        执行后置清理任务
        子类必须实现此方法
        """
        pass
    
    def get_name(self) -> str:
        """返回Setup的名称"""
        return self.__class__.__name__


class EnvironmentSetup(BaseSetup):
    """内置的环境变量设置插件"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._original_env = {}  # 存储原始环境变量值
        self._added_env = set()  # 存储新添加的环境变量
    
    def setup(self) -> None:
        """设置环境变量"""
        env_vars = self.config.get('environment_variables', {})
        
        if not env_vars:
            return
            
        print(f"Setting up environment variables...")
        
        for key, value in env_vars.items():
            # 保存原始值
            if key in os.environ:
                self._original_env[key] = os.environ[key]
            else:
                self._added_env.add(key)
            
            # 设置新值
            os.environ[key] = str(value)
            print(f"  {key} = {value}")
    
    def teardown(self) -> None:
        """恢复环境变量"""
        if not self._original_env and not self._added_env:
            return
            
        print(f"Restoring environment variables...")
        
        # 恢复原始值
        for key, value in self._original_env.items():
            os.environ[key] = value
            print(f"  Restored {key}")
        
        # 删除新添加的环境变量
        for key in self._added_env:
            if key in os.environ:
                del os.environ[key]
                print(f"  Removed {key}")
        
        # 清空记录
        self._original_env.clear()
        self._added_env.clear()


class SetupManager:
    """Setup管理器，负责管理多个Setup插件"""
    
    def __init__(self):
        self.setups = []
    
    def add_setup(self, setup: BaseSetup) -> None:
        """添加Setup插件"""
        self.setups.append(setup)
    
    def setup_all(self) -> None:
        """执行所有Setup的前置任务"""
        if not self.setups:
            return
            
        print("\n" + "=" * 50)
        print("Executing setup tasks...")
        print("=" * 50)
        
        for setup in self.setups:
            try:
                print(f"\nRunning setup: {setup.get_name()}")
                setup.setup()
            except Exception as e:
                print(f"Error in setup {setup.get_name()}: {str(e)}")
                raise
    
    def teardown_all(self) -> None:
        """执行所有Setup的后置清理任务（逆序执行）"""
        if not self.setups:
            return
            
        print("\n" + "=" * 50)
        print("Executing teardown tasks...")
        print("=" * 50)
        
        # 逆序执行teardown
        for setup in reversed(self.setups):
            try:
                print(f"\nRunning teardown: {setup.get_name()}")
                setup.teardown()
            except Exception as e:
                print(f"Error in teardown {setup.get_name()}: {str(e)}")
                # teardown错误不应该阻止其他teardown的执行
                continue 