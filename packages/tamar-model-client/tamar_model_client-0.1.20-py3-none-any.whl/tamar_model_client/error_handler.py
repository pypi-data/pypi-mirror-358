"""
gRPC 错误处理器

提供统一的错误处理、恢复策略和重试逻辑。
"""

import asyncio
import random
import grpc
import logging
from typing import Optional, Dict, Any, Callable, Union
from collections import defaultdict

from .exceptions import (
    ErrorContext, TamarModelException,
    NetworkException, ConnectionException, TimeoutException,
    AuthenticationException, TokenExpiredException, PermissionDeniedException,
    ValidationException, InvalidParameterException,
    RateLimitException, ProviderException,
    ERROR_CATEGORIES, RETRY_POLICY, ErrorStats
)


logger = logging.getLogger(__name__)


class GrpcErrorHandler:
    """统一的 gRPC 错误处理器"""
    
    def __init__(self, client_logger: Optional[logging.Logger] = None):
        self.logger = client_logger or logger
        self.error_stats = ErrorStats()
        
    def handle_error(self, error: Union[grpc.RpcError, Exception], context: dict) -> TamarModelException:
        """
        统一错误处理流程：
        1. 创建错误上下文
        2. 记录错误日志
        3. 更新错误统计
        4. 决定错误类型
        5. 返回相应异常
        """
        error_context = ErrorContext(error, context)
        
        # 记录详细错误日志
        self.logger.error(
            f"gRPC Error occurred: {error_context.error_code}",
            extra=error_context.to_dict()
        )
        
        # 更新错误统计
        if error_context.error_code:
            self.error_stats.record_error(error_context.error_code)
        
        # 根据错误类型返回相应异常
        return self._create_exception(error_context)
    
    def _create_exception(self, error_context: ErrorContext) -> TamarModelException:
        """根据错误上下文创建相应的异常"""
        error_code = error_context.error_code
        
        if not error_code:
            return TamarModelException(error_context)
        
        # 认证相关错误
        if error_code in ERROR_CATEGORIES['AUTH']:
            if error_code == grpc.StatusCode.UNAUTHENTICATED:
                return TokenExpiredException(error_context)
            else:
                return PermissionDeniedException(error_context)
        
        # 网络相关错误
        elif error_code in ERROR_CATEGORIES['NETWORK']:
            if error_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                return TimeoutException(error_context)
            else:
                return ConnectionException(error_context)
        
        # 验证相关错误
        elif error_code in ERROR_CATEGORIES['VALIDATION']:
            return InvalidParameterException(error_context)
        
        # 资源相关错误
        elif error_code == grpc.StatusCode.RESOURCE_EXHAUSTED:
            return RateLimitException(error_context)
        
        # 服务商相关错误
        elif error_code in ERROR_CATEGORIES['PROVIDER']:
            return ProviderException(error_context)
        
        # 默认错误
        else:
            return TamarModelException(error_context)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        return self.error_stats.get_stats()
    
    def reset_stats(self):
        """重置错误统计"""
        self.error_stats.reset()


class ErrorRecoveryStrategy:
    """错误恢复策略"""
    
    RECOVERY_ACTIONS = {
        'refresh_token': 'handle_token_refresh',
        'reconnect': 'handle_reconnect',
        'backoff': 'handle_backoff',
        'circuit_break': 'handle_circuit_break',
    }
    
    def __init__(self, client):
        self.client = client
        
    async def recover_from_error(self, error_context: ErrorContext):
        """根据错误类型执行恢复动作"""
        if not error_context.error_code:
            return
            
        policy = RETRY_POLICY.get(error_context.error_code, {})
        
        if action := policy.get('action'):
            if action in self.RECOVERY_ACTIONS:
                handler = getattr(self, self.RECOVERY_ACTIONS[action])
                await handler(error_context)
    
    async def handle_token_refresh(self, error_context: ErrorContext):
        """处理 Token 刷新"""
        self.client.logger.info("Attempting to refresh JWT token")
        # 这里需要客户端实现 _refresh_jwt_token 方法
        if hasattr(self.client, '_refresh_jwt_token'):
            await self.client._refresh_jwt_token()
    
    async def handle_reconnect(self, error_context: ErrorContext):
        """处理重连"""
        self.client.logger.info("Attempting to reconnect channel")
        # 这里需要客户端实现 _reconnect_channel 方法
        if hasattr(self.client, '_reconnect_channel'):
            await self.client._reconnect_channel()
    
    async def handle_backoff(self, error_context: ErrorContext):
        """处理退避等待"""
        wait_time = self._calculate_backoff(error_context.retry_count)
        await asyncio.sleep(wait_time)
    
    async def handle_circuit_break(self, error_context: ErrorContext):
        """处理熔断"""
        self.client.logger.warning("Circuit breaker activated")
        # 这里可以实现熔断逻辑
        pass
    
    def _calculate_backoff(self, retry_count: int) -> float:
        """计算退避时间"""
        base_delay = 1.0
        max_delay = 60.0
        jitter_factor = 0.1
        
        delay = min(base_delay * (2 ** retry_count), max_delay)
        jitter = random.uniform(0, delay * jitter_factor)
        return delay + jitter


class EnhancedRetryHandler:
    """增强的重试处理器"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.error_handler = GrpcErrorHandler()
        
    async def execute_with_retry(
        self, 
        func: Callable, 
        *args, 
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        执行函数并处理重试
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            context: 请求上下文信息
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            TamarModelException: 包装后的异常
        """
        context = context or {}
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                context['retry_count'] = attempt
                return await func(*args, **kwargs)
                
            except (grpc.RpcError, grpc.aio.AioRpcError) as e:
                # 创建错误上下文
                error_context = ErrorContext(e, context)
                
                # 判断是否可以重试
                if not self._should_retry(e, attempt):
                    # 不可重试或已达到最大重试次数
                    last_exception = self.error_handler.handle_error(e, context)
                    break
                    
                # 记录重试日志
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {e.code()}",
                    extra=error_context.to_dict()
                )
                
                # 执行退避等待
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    await asyncio.sleep(delay)
                
                last_exception = self.error_handler.handle_error(e, context)
            
            except Exception as e:
                # 非 gRPC 错误，直接包装抛出
                context['retry_count'] = attempt
                error_context = ErrorContext(None, context)
                error_context.error_message = str(e)
                last_exception = TamarModelException(error_context)
                break
        
        # 抛出最后的异常
        if last_exception:
            raise last_exception
        else:
            raise TamarModelException("Unknown error occurred")
    
    def _should_retry(self, error: grpc.RpcError, attempt: int) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
            
        error_code = error.code()
        policy = RETRY_POLICY.get(error_code, {})
        
        # 检查基本重试策略
        retryable = policy.get('retryable', False)
        if retryable == False:
            return False
        elif retryable == True:
            return True
        elif retryable == 'conditional':
            # 条件重试，需要检查错误详情
            return self._check_conditional_retry(error)
        
        return False
    
    def _check_conditional_retry(self, error: grpc.RpcError) -> bool:
        """检查条件重试"""
        error_message = error.details().lower() if error.details() else ""
        
        # 一些可重试的内部错误模式
        retryable_patterns = [
            'temporary', 'timeout', 'unavailable', 
            'connection', 'network', 'try again'
        ]
        
        for pattern in retryable_patterns:
            if pattern in error_message:
                return True
                
        return False
    
    def _calculate_backoff(self, attempt: int) -> float:
        """计算退避时间"""
        max_delay = 60.0
        jitter_factor = 0.1
        
        delay = min(self.base_delay * (2 ** attempt), max_delay)
        jitter = random.uniform(0, delay * jitter_factor)
        return delay + jitter