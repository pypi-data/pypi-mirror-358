"""
Base client class for Tamar Model Client

This module provides the base client class with shared initialization logic
and configuration management for both sync and async clients.
"""

import os
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from ..auth import JWTAuthHandler
from ..error_handler import GrpcErrorHandler, ErrorRecoveryStrategy
from .logging_setup import MAX_MESSAGE_LENGTH, setup_logger


class BaseClient(ABC):
    """
    基础客户端抽象类
    
    提供同步和异步客户端的共享功能：
    - 配置管理
    - 认证设置
    - 连接选项构建
    - 错误处理器初始化
    """
    
    def __init__(
            self,
            server_address: Optional[str] = None,
            jwt_secret_key: Optional[str] = None,
            jwt_token: Optional[str] = None,
            default_payload: Optional[dict] = None,
            token_expires_in: int = 3600,
            max_retries: Optional[int] = None,
            retry_delay: Optional[float] = None,
            logger_name: str = None,
    ):
        """
        初始化基础客户端
        
        Args:
            server_address: gRPC 服务器地址，格式为 "host:port"
            jwt_secret_key: JWT 签名密钥，用于生成认证令牌
            jwt_token: 预生成的 JWT 令牌（可选）
            default_payload: JWT 令牌的默认载荷
            token_expires_in: JWT 令牌过期时间（秒）
            max_retries: 最大重试次数（默认从环境变量读取）
            retry_delay: 初始重试延迟（秒，默认从环境变量读取）
            logger_name: 日志记录器名称
            
        Raises:
            ValueError: 当服务器地址未提供时
        """
        # === 服务端地址配置 ===
        self.server_address = server_address or os.getenv("MODEL_MANAGER_SERVER_ADDRESS")
        if not self.server_address:
            raise ValueError("Server address must be provided via argument or environment variable.")
        
        # 默认调用超时时间
        self.default_invoke_timeout = float(os.getenv("MODEL_MANAGER_SERVER_INVOKE_TIMEOUT", 30.0))
        
        # === JWT 认证配置 ===
        self.jwt_secret_key = jwt_secret_key or os.getenv("MODEL_MANAGER_SERVER_JWT_SECRET_KEY")
        self.jwt_handler = JWTAuthHandler(self.jwt_secret_key) if self.jwt_secret_key else None
        self.jwt_token = jwt_token  # 用户传入的预生成 Token（可选）
        self.default_payload = default_payload
        self.token_expires_in = token_expires_in
        
        # === TLS/Authority 配置 ===
        self.use_tls = os.getenv("MODEL_MANAGER_SERVER_GRPC_USE_TLS", "true").lower() == "true"
        self.default_authority = os.getenv("MODEL_MANAGER_SERVER_GRPC_DEFAULT_AUTHORITY")
        
        # === 重试配置 ===
        self.max_retries = max_retries if max_retries is not None else int(
            os.getenv("MODEL_MANAGER_SERVER_GRPC_MAX_RETRIES", 3))
        self.retry_delay = retry_delay if retry_delay is not None else float(
            os.getenv("MODEL_MANAGER_SERVER_GRPC_RETRY_DELAY", 1.0))
        
        # === 日志配置 ===
        self.logger = setup_logger(logger_name or __name__)
        
        # === 错误处理器 ===
        self.error_handler = GrpcErrorHandler(self.logger)
        self.recovery_strategy = ErrorRecoveryStrategy(self)
        
        # === 连接状态 ===
        self._closed = False
    
    def build_channel_options(self) -> list:
        """
        构建 gRPC 通道选项
        
        Returns:
            list: gRPC 通道配置选项列表
            
        包含的配置：
        - 消息大小限制
        - Keepalive 设置（30秒ping间隔，10秒超时）
        - 连接生命周期管理（1小时最大连接时间）
        - 性能优化选项（带宽探测、内置重试）
        """
        options = [
            # 消息大小限制
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            
            # Keepalive 核心配置
            ('grpc.keepalive_time_ms', 30000),  # 30秒发送一次 keepalive ping
            ('grpc.keepalive_timeout_ms', 10000),  # ping 响应超时时间 10秒
            ('grpc.keepalive_permit_without_calls', True),  # 空闲时也发送 keepalive
            ('grpc.http2.max_pings_without_data', 2),  # 无数据时最大 ping 次数
            
            # 连接管理增强配置
            ('grpc.http2.min_time_between_pings_ms', 10000),  # ping 最小间隔 10秒
            ('grpc.http2.max_connection_idle_ms', 300000),  # 最大空闲时间 5分钟
            ('grpc.http2.max_connection_age_ms', 3600000),  # 连接最大生存时间 1小时
            ('grpc.http2.max_connection_age_grace_ms', 5000),  # 优雅关闭时间 5秒
            
            # 性能相关配置
            ('grpc.http2.bdp_probe', 1),  # 启用带宽延迟探测
            ('grpc.enable_retries', 1),  # 启用内置重试
        ]
        
        if self.default_authority:
            options.append(("grpc.default_authority", self.default_authority))
            
        return options
    
    def _build_auth_metadata(self, request_id: str) -> list:
        """
        构建认证元数据
        
        为每个请求构建包含认证信息和请求ID的gRPC元数据。
        JWT令牌会在每次请求时重新生成以确保有效性。
        
        Args:
            request_id: 当前请求的唯一标识符
            
        Returns:
            list: gRPC元数据列表，包含请求ID和认证令牌
        """
        metadata = [("x-request-id", request_id)]  # 将 request_id 添加到 headers
        
        if self.jwt_handler:
            self.jwt_token = self.jwt_handler.encode_token(
                self.default_payload, 
                expires_in=self.token_expires_in
            )
            metadata.append(("authorization", f"Bearer {self.jwt_token}"))
            
        return metadata
    
    @abstractmethod
    def close(self):
        """关闭客户端连接（由子类实现）"""
        pass
    
    @abstractmethod
    def __enter__(self):
        """进入上下文管理器（由子类实现）"""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器（由子类实现）"""
        pass