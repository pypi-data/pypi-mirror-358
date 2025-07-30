"""
Tamar Model Client 同步客户端实现

本模块实现了同步的 gRPC 客户端，用于与 Model Manager Server 进行通信。
提供了与异步客户端相同的功能，但使用同步 API，适合在同步环境中使用。

主要功能：
- 同步 gRPC 通信
- JWT 认证
- 自动重试和错误处理
- 连接池管理
- 详细的日志记录

使用示例：
    with TamarModelClient() as client:
        request = ModelRequest(...)
        response = client.invoke(request)
        
注意：对于需要高并发的场景，建议使用 AsyncTamarModelClient
"""

import json
import logging
import random
import time
from typing import Optional, Union, Iterator

import grpc

from .core import (
    generate_request_id,
    set_request_id,
    setup_logger,
    MAX_MESSAGE_LENGTH
)
from .core.base_client import BaseClient
from .core.request_builder import RequestBuilder
from .core.response_handler import ResponseHandler
from .exceptions import ConnectionError, TamarModelException, is_retryable_error
from .generated import model_service_pb2, model_service_pb2_grpc
from .schemas import BatchModelResponse, ModelResponse
from .schemas.inputs import BatchModelRequest, ModelRequest

# 配置日志记录器
logger = setup_logger(__name__)


class TamarModelClient(BaseClient):
    """
    Tamar Model Client 同步客户端
    
    提供与 Model Manager Server 的同步通信能力，支持：
    - 单个和批量模型调用
    - 流式和非流式响应  
    - 自动重试和错误恢复
    - JWT 认证
    - 连接池管理
    
    使用示例：
        # 基本用法
        client = TamarModelClient()
        client.connect()
        
        request = ModelRequest(...)
        response = client.invoke(request)
        
        # 上下文管理器用法（推荐）
        with TamarModelClient() as client:
            response = client.invoke(request)
    
    环境变量配置：
        MODEL_MANAGER_SERVER_ADDRESS: gRPC 服务器地址
        MODEL_MANAGER_SERVER_JWT_SECRET_KEY: JWT 密钥
        MODEL_MANAGER_SERVER_GRPC_USE_TLS: 是否使用 TLS
        MODEL_MANAGER_SERVER_GRPC_MAX_RETRIES: 最大重试次数
        MODEL_MANAGER_SERVER_GRPC_RETRY_DELAY: 重试延迟
    """
    
    def __init__(self, **kwargs):
        """
        初始化同步客户端
        
        参数继承自 BaseClient，包括：
        - server_address: gRPC 服务器地址
        - jwt_secret_key: JWT 签名密钥
        - jwt_token: 预生成的 JWT 令牌
        - default_payload: JWT 令牌的默认载荷
        - token_expires_in: JWT 令牌过期时间
        - max_retries: 最大重试次数
        - retry_delay: 初始重试延迟
        """
        super().__init__(logger_name=__name__, **kwargs)
        
        # === gRPC 通道和连接管理 ===
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[model_service_pb2_grpc.ModelServiceStub] = None

    def close(self):
        """
        关闭客户端连接
        
        优雅地关闭 gRPC 通道并清理资源。
        建议在程序结束前调用此方法，或使用上下文管理器自动管理。
        """
        if self.channel and not self._closed:
            self.channel.close()
            self._closed = True
            logger.info("🔒 gRPC channel closed",
                        extra={"log_type": "info", "data": {"status": "closed"}})

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def connect(self):
        """
        显式连接到服务器
        
        建立与 gRPC 服务器的连接。通常不需要手动调用，
        因为 invoke 方法会自动确保连接已建立。
        """
        self._ensure_initialized()

    def _ensure_initialized(self):
        """
        初始化gRPC通道
        
        确保gRPC通道和存根已正确初始化。如果初始化失败，
        会进行重试，支持TLS配置和完整的keepalive选项。
        
        连接配置包括：
        - 消息大小限制
        - Keepalive设置（30秒ping间隔，10秒超时）
        - 连接生命周期管理（1小时最大连接时间）
        - 性能优化选项（带宽探测、内置重试）
        
        Raises:
            ConnectionError: 当达到最大重试次数仍无法连接时
        """
        if self.channel and self.stub:
            return

        retry_count = 0
        options = self.build_channel_options()

        while retry_count <= self.max_retries:
            try:
                if self.use_tls:
                    credentials = grpc.ssl_channel_credentials()
                    self.channel = grpc.secure_channel(
                        self.server_address,
                        credentials,
                        options=options
                    )
                    logger.info("🔐 Using secure gRPC channel (TLS enabled)",
                                extra={"log_type": "info",
                                       "data": {"tls_enabled": True, "server_address": self.server_address}})
                else:
                    self.channel = grpc.insecure_channel(
                        self.server_address,
                        options=options
                    )
                    logger.info("🔓 Using insecure gRPC channel (TLS disabled)",
                                extra={"log_type": "info",
                                       "data": {"tls_enabled": False, "server_address": self.server_address}})
                
                # 等待通道就绪
                grpc.channel_ready_future(self.channel).result(timeout=10)
                self.stub = model_service_pb2_grpc.ModelServiceStub(self.channel)
                logger.info(f"✅ gRPC channel initialized to {self.server_address}",
                            extra={"log_type": "info",
                                   "data": {"status": "success", "server_address": self.server_address}})
                return
                
            except grpc.FutureTimeoutError as e:
                logger.error(f"❌ gRPC channel initialization timed out: {str(e)}", exc_info=True,
                             extra={"log_type": "info",
                                    "data": {"error_type": "timeout", "server_address": self.server_address}})
            except grpc.RpcError as e:
                logger.error(f"❌ gRPC channel initialization failed: {str(e)}", exc_info=True,
                             extra={"log_type": "info",
                                    "data": {"error_type": "grpc_error", "server_address": self.server_address}})
            except Exception as e:
                logger.error(f"❌ Unexpected error during gRPC channel initialization: {str(e)}", exc_info=True,
                             extra={"log_type": "info",
                                    "data": {"error_type": "unknown", "server_address": self.server_address}})
            
            retry_count += 1
            if retry_count <= self.max_retries:
                time.sleep(self.retry_delay * retry_count)

        raise ConnectionError(f"Failed to connect to {self.server_address} after {self.max_retries} retries")

    def _retry_request(self, func, *args, **kwargs):
        """
        使用增强的错误处理器进行重试（同步版本）
        """
        # 构建请求上下文
        context = {
            'method': func.__name__ if hasattr(func, '__name__') else 'unknown',
            'client_version': 'sync',
        }

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                context['retry_count'] = attempt
                return func(*args, **kwargs)

            except grpc.RpcError as e:
                # 使用新的错误处理逻辑
                context['retry_count'] = attempt

                # 判断是否可以重试
                if not is_retryable_error(e.code()) or attempt >= self.max_retries:
                    # 不可重试或已达到最大重试次数
                    last_exception = self.error_handler.handle_error(e, context)
                    break

                # 记录重试日志
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {e.code()}",
                    extra=context
                )

                # 执行退避等待
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    time.sleep(delay)

                last_exception = self.error_handler.handle_error(e, context)

            except Exception as e:
                # 非 gRPC 错误，直接包装抛出
                context['retry_count'] = attempt
                last_exception = TamarModelException(str(e))
                break

        # 抛出最后的异常
        if last_exception:
            raise last_exception
        else:
            raise TamarModelException("Unknown error occurred")

    def _calculate_backoff(self, attempt: int) -> float:
        """计算退避时间"""
        max_delay = 60.0
        jitter_factor = 0.1

        delay = min(self.retry_delay * (2 ** attempt), max_delay)
        jitter = random.uniform(0, delay * jitter_factor)
        return delay + jitter

    def _retry_request_stream(self, func, *args, **kwargs):
        """
        流式请求的重试逻辑（同步版本）
        
        对于流式响应，需要特殊的重试处理，因为流不能简单地重新执行。
        
        Args:
            func: 生成流的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Yields:
            流式响应的每个元素
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # 尝试创建流
                for item in func(*args, **kwargs):
                    yield item
                return
                
            except grpc.RpcError as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Stream attempt {attempt + 1}/{self.max_retries + 1} failed: {e.code()}",
                        extra={"retry_count": attempt, "error_code": str(e.code())}
                    )
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    break
            except Exception as e:
                raise TamarModelException(str(e)) from e
        
        if last_exception:
            raise self.error_handler.handle_error(last_exception, {"retry_count": self.max_retries})
        else:
            raise TamarModelException("Unknown streaming error occurred")

    def _stream(self, request, metadata, invoke_timeout) -> Iterator[ModelResponse]:
        """
        处理流式响应
        
        Args:
            request: gRPC 请求对象
            metadata: 请求元数据
            invoke_timeout: 总体超时时间
            
        Yields:
            ModelResponse: 流式响应的每个数据块
            
        Raises:
            TimeoutError: 当等待下一个数据块超时时
        """
        import threading
        import queue
        
        # 创建队列用于线程间通信
        response_queue = queue.Queue()
        exception_queue = queue.Queue()
        
        def fetch_responses():
            """在单独线程中获取流式响应"""
            try:
                for response in self.stub.Invoke(request, metadata=metadata, timeout=invoke_timeout):
                    response_queue.put(response)
                response_queue.put(None)  # 标记流结束
            except Exception as e:
                exception_queue.put(e)
                response_queue.put(None)
        
        # 启动响应获取线程
        fetch_thread = threading.Thread(target=fetch_responses)
        fetch_thread.daemon = True
        fetch_thread.start()
        
        chunk_timeout = 30.0  # 单个数据块的超时时间
        
        while True:
            # 检查是否有异常
            if not exception_queue.empty():
                raise exception_queue.get()
            
            try:
                # 等待下一个响应，带超时
                response = response_queue.get(timeout=chunk_timeout)
                
                if response is None:
                    # 流结束
                    break
                    
                yield ResponseHandler.build_model_response(response)
                
            except queue.Empty:
                raise TimeoutError(f"流式响应在等待下一个数据块时超时 ({chunk_timeout}s)")

    def _stream_with_logging(self, request, metadata, invoke_timeout, start_time, model_request) -> Iterator[
        ModelResponse]:
        """流式响应的包装器，用于记录完整的响应日志并处理重试"""
        total_content = ""
        final_usage = None
        error_occurred = None
        chunk_count = 0

        try:
            for response in self._stream(request, metadata, invoke_timeout):
                chunk_count += 1
                if response.content:
                    total_content += response.content
                if response.usage:
                    final_usage = response.usage
                if response.error:
                    error_occurred = response.error
                yield response

            # 流式响应完成，记录日志
            duration = time.time() - start_time
            if error_occurred:
                # 流式响应中包含错误
                logger.warning(
                    f"⚠️ Stream completed with errors | chunks: {chunk_count}",
                    extra={
                        "log_type": "response",
                        "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                        "duration": duration,
                        "data": ResponseHandler.build_log_data(
                            model_request,
                            stream_stats={
                                "chunks_count": chunk_count,
                                "total_length": len(total_content),
                                "usage": final_usage,
                                "error": error_occurred
                            }
                        )
                    }
                )
            else:
                # 流式响应成功完成
                logger.info(
                    f"✅ Stream completed successfully | chunks: {chunk_count}",
                    extra={
                        "log_type": "response",
                        "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                        "duration": duration,
                        "data": ResponseHandler.build_log_data(
                            model_request,
                            stream_stats={
                                "chunks_count": chunk_count,
                                "total_length": len(total_content),
                                "usage": final_usage
                            }
                        )
                    }
                )
        except Exception as e:
            # 流式响应出错，记录错误日志
            duration = time.time() - start_time
            logger.error(
                f"❌ Stream failed after {chunk_count} chunks: {str(e)}",
                exc_info=True,
                extra={
                    "log_type": "response",
                    "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                    "duration": duration,
                    "data": ResponseHandler.build_log_data(
                        model_request,
                        error=e,
                        stream_stats={
                            "chunks_count": chunk_count,
                            "partial_content_length": len(total_content)
                        }
                    )
                }
            )
            raise

    def _invoke_request(self, request, metadata, invoke_timeout):
        """执行单个非流式请求"""
        response = self.stub.Invoke(request, metadata=metadata, timeout=invoke_timeout)
        for response in response:
            return ResponseHandler.build_model_response(response)

    def invoke(self, model_request: ModelRequest, timeout: Optional[float] = None, request_id: Optional[str] = None) -> \
            Union[ModelResponse, Iterator[ModelResponse]]:
        """
       通用调用模型方法。

        Args:
            model_request: ModelRequest 对象，包含请求参数。
            timeout: Optional[float]
            request_id: Optional[str]
        Yields:
            ModelResponse: 支持流式或非流式的模型响应

        Raises:
            ValidationError: 输入验证失败。
            ConnectionError: 连接服务端失败。
        """
        self._ensure_initialized()

        if not self.default_payload:
            self.default_payload = {
                "org_id": model_request.user_context.org_id or "",
                "user_id": model_request.user_context.user_id or ""
            }

        if not request_id:
            request_id = generate_request_id()
        set_request_id(request_id)
        metadata = self._build_auth_metadata(request_id)

        # 记录开始日志
        start_time = time.time()
        logger.info(
            f"🔵 Request Start | request_id: {request_id} | provider: {model_request.provider} | invoke_type: {model_request.invoke_type}",
            extra={
                "log_type": "request",
                "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                "data": ResponseHandler.build_log_data(model_request)
            })

        try:
            # 构建 gRPC 请求
            request = RequestBuilder.build_single_request(model_request)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"❌ Request build failed: {str(e)}",
                exc_info=True,
                extra={
                    "log_type": "response",
                    "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                    "duration": duration,
                    "data": {
                        "provider": model_request.provider.value,
                        "invoke_type": model_request.invoke_type.value,
                        "model": getattr(model_request, 'model', None),
                        "error_type": "build_error",
                        "error_message": str(e)
                    }
                }
            )
            raise ValueError(f"构建请求失败: {str(e)}") from e

        try:
            invoke_timeout = timeout or self.default_invoke_timeout
            if model_request.stream:
                # 对于流式响应，使用重试包装器
                return self._retry_request_stream(
                    self._stream_with_logging,
                    request, metadata, invoke_timeout, start_time, model_request
                )
            else:
                result = self._retry_request(self._invoke_request, request, metadata, invoke_timeout)

                # 记录非流式响应的成功日志
                duration = time.time() - start_time
                content_length = len(result.content) if result.content else 0
                logger.info(
                    f"✅ Request completed | content_length: {content_length}",
                    extra={
                        "log_type": "response",
                        "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                        "duration": duration,
                        "data": ResponseHandler.build_log_data(model_request, result)
                    }
                )
                return result
                
        except grpc.RpcError as e:
            duration = time.time() - start_time
            error_message = f"❌ Invoke gRPC failed: {str(e)}"
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                             "duration": duration,
                             "data": ResponseHandler.build_log_data(
                                 model_request,
                                 error=e
                             )
                         })
            raise e
        except Exception as e:
            duration = time.time() - start_time
            error_message = f"❌ Invoke other error: {str(e)}"
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                             "duration": duration,
                             "data": ResponseHandler.build_log_data(
                                 model_request,
                                 error=e
                             )
                         })
            raise e

    def invoke_batch(self, batch_request_model: BatchModelRequest, timeout: Optional[float] = None,
                     request_id: Optional[str] = None) -> BatchModelResponse:
        """
        批量模型调用接口

        Args:
            batch_request_model: 多条 BatchModelRequest 输入
            timeout: 调用超时，单位秒
            request_id: 请求id
        Returns:
            BatchModelResponse: 批量请求的结果
        """
        self._ensure_initialized()

        if not self.default_payload:
            self.default_payload = {
                "org_id": batch_request_model.user_context.org_id or "",
                "user_id": batch_request_model.user_context.user_id or ""
            }

        if not request_id:
            request_id = generate_request_id()
        set_request_id(request_id)
        metadata = self._build_auth_metadata(request_id)

        # 记录开始日志
        start_time = time.time()
        logger.info(
            f"🔵 Batch Request Start | request_id: {request_id} | batch_size: {len(batch_request_model.items)}",
            extra={
                "log_type": "request",
                "uri": "/batch_invoke",
                "data": {
                    "batch_size": len(batch_request_model.items),
                    "org_id": batch_request_model.user_context.org_id,
                    "user_id": batch_request_model.user_context.user_id,
                    "client_type": batch_request_model.user_context.client_type
                }
            })

        try:
            # 构建批量请求
            batch_request = RequestBuilder.build_batch_request(batch_request_model)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"❌ Batch request build failed: {str(e)}",
                exc_info=True,
                extra={
                    "log_type": "response",
                    "uri": "/batch_invoke",
                    "duration": duration,
                    "data": {
                        "batch_size": len(batch_request_model.items),
                        "error_type": "build_error",
                        "error_message": str(e)
                    }
                }
            )
            raise ValueError(f"构建批量请求失败: {str(e)}") from e

        try:
            invoke_timeout = timeout or self.default_invoke_timeout
            batch_response = self._retry_request(
                self.stub.BatchInvoke,
                batch_request,
                metadata=metadata,
                timeout=invoke_timeout
            )

            # 构建响应对象
            result = ResponseHandler.build_batch_response(batch_response)

            # 记录成功日志
            duration = time.time() - start_time
            logger.info(
                f"✅ Batch Request completed | batch_size: {len(result.responses)}",
                extra={
                    "log_type": "response",
                    "uri": "/batch_invoke",
                    "duration": duration,
                    "data": {
                        "batch_size": len(result.responses),
                        "success_count": sum(1 for item in result.responses if not item.error),
                        "error_count": sum(1 for item in result.responses if item.error)
                    }
                })

            return result

        except grpc.RpcError as e:
            duration = time.time() - start_time
            error_message = f"❌ Batch invoke gRPC failed: {str(e)}"
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": "/batch_invoke",
                             "duration": duration,
                             "data": {
                                 "error_type": "grpc_error",
                                 "error_code": str(e.code()) if hasattr(e, 'code') else None,
                                 "batch_size": len(batch_request_model.items)
                             }
                         })
            raise e
        except Exception as e:
            duration = time.time() - start_time
            error_message = f"❌ Batch invoke other error: {str(e)}"
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": "/batch_invoke",
                             "duration": duration,
                             "data": {
                                 "error_type": "other_error",
                                 "batch_size": len(batch_request_model.items)
                             }
                         })
            raise e