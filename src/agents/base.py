"""
Agent 基类定义
所有Agent继承此基类，确保统一接口和可扩展性
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class InvestigationContext:
    """调查上下文，在Agent间传递"""
    investigation_id: str
    user_submission: str  # 用户提交的链接或描述
    submission_type: str  # "url" or "text"
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Agent间共享的发现
    findings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Agent执行结果"""
    agent_name: str
    status: AgentStatus
    data: Dict[str, Any]
    errors: Optional[list] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def is_success(self) -> bool:
        """判断是否执行成功"""
        return self.status == AgentStatus.COMPLETED and not self.errors


class BaseAgent(ABC):
    """
    Agent基类
    所有具体Agent必须继承此类并实现execute方法
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化Agent

        Args:
            name: Agent名称
            config: Agent配置
        """
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

    @abstractmethod
    async def execute(self, context: InvestigationContext) -> AgentResult:
        """
        执行Agent的核心逻辑（子类必须实现）

        Args:
            context: 调查上下文

        Returns:
            AgentResult: Agent执行结果
        """
        raise NotImplementedError(f"{self.name} must implement execute()")

    async def validate_input(self, context: InvestigationContext) -> bool:
        """
        验证输入是否满足Agent执行条件

        Args:
            context: 调查上下文

        Returns:
            bool: 是否验证通过
        """
        # 默认实现：检查基本字段
        return bool(context.investigation_id and context.user_submission)

    async def pre_execute(self, context: InvestigationContext) -> None:
        """执行前的钩子（可选重写）"""
        pass

    async def post_execute(self, result: AgentResult) -> None:
        """执行后的钩子（可选重写）"""
        pass

    async def run(self, context: InvestigationContext) -> AgentResult:
        """
        Agent执行的完整流程（包含验证、前后钩子）

        Args:
            context: 调查上下文

        Returns:
            AgentResult: 执行结果
        """
        import time

        # 检查是否启用
        if not self.enabled:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={"skipped": True, "reason": "Agent disabled"}
            )

        # 验证输入
        if not await self.validate_input(context):
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                errors=["Input validation failed"]
            )

        try:
            # 前置钩子
            await self.pre_execute(context)

            # 执行核心逻辑
            start_time = time.time()
            result = await self.execute(context)
            result.execution_time = time.time() - start_time

            # 后置钩子
            await self.post_execute(result)

            return result

        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                errors=[f"Execution error: {str(e)}"],
                execution_time=time.time() - start_time if 'start_time' in locals() else 0
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})>"
