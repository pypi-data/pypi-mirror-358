"""
Logging configuration for Tamar Model Client

This module provides centralized logging setup for both sync and async clients.
It includes request ID tracking, JSON formatting, and consistent log configuration.
"""

import logging
from typing import Optional

from ..json_formatter import JSONFormatter
from .utils import get_request_id

# gRPC 消息长度限制（32位系统兼容）
MAX_MESSAGE_LENGTH = 2 ** 31 - 1


class RequestIdFilter(logging.Filter):
    """
    自定义日志过滤器，向日志记录中添加 request_id
    
    这个过滤器从 ContextVar 中获取当前请求的 ID，
    并将其添加到日志记录中，便于追踪和调试。
    """

    def filter(self, record):
        """
        过滤日志记录，添加 request_id 字段
        
        Args:
            record: 日志记录对象
            
        Returns:
            bool: 总是返回 True，表示记录应被处理
        """
        # 从 ContextVar 中获取当前的 request_id
        record.request_id = get_request_id()
        return True


def setup_logger(logger_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    设置并配置logger
    
    为指定的logger配置处理器、格式化器和过滤器。
    如果logger已经有处理器，则不会重复配置。
    
    Args:
        logger_name: logger的名称
        level: 日志级别，默认为 INFO
        
    Returns:
        logging.Logger: 配置好的logger实例
        
    特性：
    - 使用 JSON 格式化器提供结构化日志输出
    - 添加请求ID过滤器用于请求追踪
    - 避免重复配置
    """
    logger = logging.getLogger(logger_name)
    
    # 仅在没有处理器时配置，避免重复配置
    if not logger.hasHandlers():
        # 创建控制台日志处理器
        console_handler = logging.StreamHandler()
        
        # 使用自定义的 JSON 格式化器，提供结构化日志输出
        formatter = JSONFormatter()
        console_handler.setFormatter(formatter)
        
        # 为logger添加处理器
        logger.addHandler(console_handler)
        
        # 设置日志级别
        logger.setLevel(level)
        
        # 添加自定义的请求ID过滤器，用于请求追踪
        logger.addFilter(RequestIdFilter())
        
        # 关键：设置 propagate = False，防止日志传播到父logger
        # 这样可以避免测试脚本的日志格式影响客户端日志
        logger.propagate = False
    
    return logger