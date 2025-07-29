import base64
import json
import logging
import os
import time
import uuid
import grpc
from typing import Optional, Union, Iterable, Iterator
from contextvars import ContextVar

from openai import NOT_GIVEN
from pydantic import BaseModel

from .auth import JWTAuthHandler
from .enums import ProviderType, InvokeType
from .exceptions import ConnectionError
from .generated import model_service_pb2, model_service_pb2_grpc
from .schemas import BatchModelResponse, ModelResponse
from .schemas.inputs import GoogleGenAiInput, GoogleVertexAIImagesInput, OpenAIResponsesInput, \
    OpenAIChatCompletionsInput, OpenAIImagesInput, OpenAIImagesEditInput, BatchModelRequest, ModelRequest
from .json_formatter import JSONFormatter

logger = logging.getLogger(__name__)

_request_id: ContextVar[str] = ContextVar('request_id', default='-')


class RequestIdFilter(logging.Filter):
    """自定义日志过滤器，向日志中添加 request_id"""

    def filter(self, record):
        # 从 ContextVar 中获取当前的 request_id
        record.request_id = _request_id.get()
        return True


if not logger.hasHandlers():
    # 创建日志处理器，输出到控制台
    console_handler = logging.StreamHandler()

    # 使用 JSON 格式化器
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)

    # 为当前记录器添加处理器
    logger.addHandler(console_handler)

    # 设置日志级别
    logger.setLevel(logging.INFO)

    # 将自定义的 RequestIdFilter 添加到 logger 中
    logger.addFilter(RequestIdFilter())

MAX_MESSAGE_LENGTH = 2 ** 31 - 1  # 对于32位系统


def is_effective_value(value) -> bool:
    """
    递归判断value是否是有意义的有效值
    """
    if value is None or value is NOT_GIVEN:
        return False

    if isinstance(value, str):
        return value.strip() != ""

    if isinstance(value, bytes):
        return len(value) > 0

    if isinstance(value, dict):
        for v in value.values():
            if is_effective_value(v):
                return True
        return False

    if isinstance(value, list):
        for item in value:
            if is_effective_value(item):
                return True
        return False

    return True  # 其他类型（int/float/bool）只要不是None就算有效


def serialize_value(value):
    """递归处理单个值，处理BaseModel, dict, list, bytes"""
    if not is_effective_value(value):
        return None
    if isinstance(value, BaseModel):
        return serialize_value(value.model_dump())
    if hasattr(value, "dict") and callable(value.dict):
        return serialize_value(value.dict())
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, list) or (isinstance(value, Iterable) and not isinstance(value, (str, bytes))):
        return [serialize_value(v) for v in value]
    if isinstance(value, bytes):
        return f"bytes:{base64.b64encode(value).decode('utf-8')}"
    return value


from typing import Any


def remove_none_from_dict(data: Any) -> Any:
    """
    遍历 dict/list，递归删除 value 为 None 的字段
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if value is None:
                continue
            cleaned_value = remove_none_from_dict(value)
            new_dict[key] = cleaned_value
        return new_dict
    elif isinstance(data, list):
        return [remove_none_from_dict(item) for item in data]
    else:
        return data


def generate_request_id():
    """生成一个唯一的request_id"""
    return str(uuid.uuid4())


def set_request_id(request_id: str):
    """设置当前请求的 request_id"""
    _request_id.set(request_id)


class TamarModelClient:
    def __init__(
            self,
            server_address: Optional[str] = None,
            jwt_secret_key: Optional[str] = None,
            jwt_token: Optional[str] = None,
            default_payload: Optional[dict] = None,
            token_expires_in: int = 3600,
            max_retries: Optional[int] = None,  # 最大重试次数
            retry_delay: Optional[float] = None,  # 初始重试延迟（秒）
    ):
        self.server_address = server_address or os.getenv("MODEL_MANAGER_SERVER_ADDRESS")
        if not self.server_address:
            raise ValueError("Server address must be provided via argument or environment variable.")
        self.default_invoke_timeout = float(os.getenv("MODEL_MANAGER_SERVER_INVOKE_TIMEOUT", 30.0))

        # JWT 配置
        self.jwt_secret_key = jwt_secret_key or os.getenv("MODEL_MANAGER_SERVER_JWT_SECRET_KEY")
        self.jwt_handler = JWTAuthHandler(self.jwt_secret_key)
        self.jwt_token = jwt_token  # 用户传入的 Token（可选）
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

        # === gRPC 通道相关 ===
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[model_service_pb2_grpc.ModelServiceStub] = None
        self._closed = False

    def _retry_request(self, func, *args, **kwargs):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                return func(*args, **kwargs)
            except (grpc.RpcError) as e:
                if e.code() in {grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED}:
                    retry_count += 1
                    logger.warning(f"⚠️ gRPC error {e.code()}, retrying {retry_count}/{self.max_retries}...",
                                 extra={"log_type": "info", "data": {"retry_count": retry_count, "max_retries": self.max_retries, "error_code": str(e.code())}})
                    if retry_count < self.max_retries:
                        delay = self.retry_delay * (2 ** (retry_count - 1))
                        time.sleep(delay)
                    else:
                        logger.error(f"❌ Max retry reached for {e.code()}",
                                   extra={"log_type": "info", "data": {"error_code": str(e.code()), "max_retries_reached": True}})
                        raise
                else:
                    logger.error(f"❌ Non-retryable gRPC error: {e}", exc_info=True,
                               extra={"log_type": "info", "data": {"error_code": str(e.code()) if hasattr(e, 'code') else None, "retryable": False}})
                    raise

    def _build_auth_metadata(self, request_id: str) -> list:
        metadata = [("x-request-id", request_id)]  # 将 request_id 添加到 headers
        if self.jwt_handler:
            self.jwt_token = self.jwt_handler.encode_token(self.default_payload, expires_in=self.token_expires_in)
            metadata.append(("authorization", f"Bearer {self.jwt_token}"))
        return metadata

    def _ensure_initialized(self):
        """初始化 gRPC 通道，支持 TLS 与重试机制"""
        if self.channel and self.stub:
            return

        retry_count = 0
        options = [
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.keepalive_permit_without_calls', True)  # 即使没有活跃请求也保持连接
        ]
        if self.default_authority:
            options.append(("grpc.default_authority", self.default_authority))

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
                              extra={"log_type": "info", "data": {"tls_enabled": True, "server_address": self.server_address}})
                else:
                    self.channel = grpc.insecure_channel(
                        self.server_address,
                        options=options
                    )
                    logger.info("🔓 Using insecure gRPC channel (TLS disabled)",
                              extra={"log_type": "info", "data": {"tls_enabled": False, "server_address": self.server_address}})

                # Wait for the channel to be ready (synchronously)
                grpc.channel_ready_future(self.channel).result()  # This is blocking in sync mode

                self.stub = model_service_pb2_grpc.ModelServiceStub(self.channel)
                logger.info(f"✅ gRPC channel initialized to {self.server_address}",
                          extra={"log_type": "info", "data": {"status": "success", "server_address": self.server_address}})
                return
            except grpc.FutureTimeoutError as e:
                logger.error(f"❌ gRPC channel initialization timed out: {str(e)}", exc_info=True,
                           extra={"log_type": "info", "data": {"error_type": "timeout", "server_address": self.server_address}})
            except grpc.RpcError as e:
                logger.error(f"❌ gRPC channel initialization failed: {str(e)}", exc_info=True,
                           extra={"log_type": "info", "data": {"error_type": "rpc_error", "server_address": self.server_address}})
            except Exception as e:
                logger.error(f"❌ Unexpected error during channel initialization: {str(e)}", exc_info=True,
                           extra={"log_type": "info", "data": {"error_type": "unexpected", "server_address": self.server_address}})

            retry_count += 1
            if retry_count > self.max_retries:
                logger.error(f"❌ Failed to initialize gRPC channel after {self.max_retries} retries.", exc_info=True,
                           extra={"log_type": "info", "data": {"max_retries_reached": True, "server_address": self.server_address}})
                raise ConnectionError(f"❌ Failed to initialize gRPC channel after {self.max_retries} retries.")

            # 指数退避：延迟时间 = retry_delay * (2 ^ (retry_count - 1))
            delay = self.retry_delay * (2 ** (retry_count - 1))
            logger.warning(f"🔄 Retrying connection (attempt {retry_count}/{self.max_retries}) after {delay:.2f}s delay...",
                      extra={"log_type": "info", "data": {"retry_count": retry_count, "max_retries": self.max_retries, "delay": delay}})
            time.sleep(delay)  # Blocking sleep in sync version

    def _stream(self, request, metadata, invoke_timeout) -> Iterator[ModelResponse]:
        for response in self.stub.Invoke(request, metadata=metadata, timeout=invoke_timeout):
            yield ModelResponse(
                content=response.content,
                usage=json.loads(response.usage) if response.usage else None,
                error=response.error or None,
                raw_response=json.loads(response.raw_response) if response.raw_response else None,
                request_id=response.request_id if response.request_id else None,
            )
    
    def _stream_with_logging(self, request, metadata, invoke_timeout, start_time, model_request) -> Iterator[ModelResponse]:
        """流式响应的包装器，用于记录完整的响应日志"""
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
            
            # 流式响应完成，记录成功日志
            duration = time.time() - start_time
            logger.info(
                f"✅ Stream completed successfully | chunks: {chunk_count}",
                extra={
                    "log_type": "response",
                    "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                    "duration": duration,
                    "data": {
                        "provider": model_request.provider.value,
                        "invoke_type": model_request.invoke_type.value,
                        "model": model_request.model,
                        "stream": True,
                        "chunks_count": chunk_count,
                        "total_length": len(total_content),
                        "usage": final_usage
                    }
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
                    "data": {
                        "provider": model_request.provider.value,
                        "invoke_type": model_request.invoke_type.value,
                        "model": model_request.model,
                        "stream": True,
                        "chunks_count": chunk_count,
                        "error_type": type(e).__name__,
                        "partial_content_length": len(total_content)
                    }
                }
            )
            raise

    def _invoke_request(self, request, metadata, invoke_timeout):
        response = self.stub.Invoke(request, metadata=metadata, timeout=invoke_timeout)
        for response in response:
            return ModelResponse(
                content=response.content,
                usage=json.loads(response.usage) if response.usage else None,
                error=response.error or None,
                raw_response=json.loads(response.raw_response) if response.raw_response else None,
                request_id=response.request_id if response.request_id else None,
            )

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
            request_id = generate_request_id()  # 生成一个新的 request_id
        set_request_id(request_id)  # 设置当前请求的 request_id
        metadata = self._build_auth_metadata(request_id)  # 将 request_id 加入到请求头

        # 记录开始日志
        start_time = time.time()
        logger.info(
            f"🔵 Request Start | request_id: {request_id} | provider: {model_request.provider} | invoke_type: {model_request.invoke_type}",
            extra={
                "log_type": "request",
                "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                "data": {
                    "provider": model_request.provider.value,
                    "invoke_type": model_request.invoke_type.value,
                    "model": model_request.model,
                    "stream": model_request.stream,
                    "org_id": model_request.user_context.org_id,
                    "user_id": model_request.user_context.user_id,
                    "client_type": model_request.user_context.client_type
                }
            })

        # 动态根据 provider/invoke_type 决定使用哪个 input 字段
        try:
            # 选择需要校验的字段集合
            # 动态分支逻辑
            match (model_request.provider, model_request.invoke_type):
                case (ProviderType.GOOGLE, InvokeType.GENERATION):
                    allowed_fields = GoogleGenAiInput.model_fields.keys()
                case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
                    allowed_fields = GoogleVertexAIImagesInput.model_fields.keys()
                case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
                    allowed_fields = OpenAIResponsesInput.model_fields.keys()
                case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
                    allowed_fields = OpenAIChatCompletionsInput.model_fields.keys()
                case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
                    allowed_fields = OpenAIImagesInput.model_fields.keys()
                case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_EDIT_GENERATION):
                    allowed_fields = OpenAIImagesEditInput.model_fields.keys()
                case _:
                    raise ValueError(
                        f"Unsupported provider/invoke_type combination: {model_request.provider} + {model_request.invoke_type}")

            # 将 ModelRequest 转 dict，过滤只保留 base + allowed 的字段
            model_request_dict = model_request.model_dump(exclude_unset=True)

            grpc_request_kwargs = {}
            for field in allowed_fields:
                if field in model_request_dict:
                    value = model_request_dict[field]

                    # 跳过无效的值
                    if not is_effective_value(value):
                        continue

                    # 序列化grpc不支持的类型
                    grpc_request_kwargs[field] = serialize_value(value)

                    # 清理 serialize后的 grpc_request_kwargs
                    grpc_request_kwargs = remove_none_from_dict(grpc_request_kwargs)

            request = model_service_pb2.ModelRequestItem(
                provider=model_request.provider.value,
                channel=model_request.channel.value,
                invoke_type=model_request.invoke_type.value,
                stream=model_request.stream or False,
                org_id=model_request.user_context.org_id or "",
                user_id=model_request.user_context.user_id or "",
                client_type=model_request.user_context.client_type or "",
                extra=grpc_request_kwargs
            )

        except Exception as e:
            raise ValueError(f"构建请求失败: {str(e)}") from e

        try:
            invoke_timeout = timeout or self.default_invoke_timeout
            if model_request.stream:
                # 对于流式响应，使用带日志记录的包装器
                return self._stream_with_logging(request, metadata, invoke_timeout, start_time, model_request)
            else:
                result = self._retry_request(self._invoke_request, request, metadata, invoke_timeout)
                
                # 记录非流式响应的成功日志
                duration = time.time() - start_time
                logger.info(
                    f"✅ Request completed successfully",
                    extra={
                        "log_type": "response",
                        "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                        "duration": duration,
                        "data": {
                            "provider": model_request.provider.value,
                            "invoke_type": model_request.invoke_type.value,
                            "model": model_request.model,
                            "stream": False,
                            "content_length": len(result.content) if result.content else 0,
                            "usage": result.usage
                        }
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
                           "data": {
                               "error_type": "grpc_error",
                               "error_code": str(e.code()) if hasattr(e, 'code') else None,
                               "provider": model_request.provider.value,
                               "invoke_type": model_request.invoke_type.value,
                               "model": model_request.model
                           }
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
                           "data": {
                               "error_type": "other_error",
                               "provider": model_request.provider.value,
                               "invoke_type": model_request.invoke_type.value,
                               "model": model_request.model
                           }
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
            request_id = generate_request_id()  # 生成一个新的 request_id
        set_request_id(request_id)  # 设置当前请求的 request_id
        metadata = self._build_auth_metadata(request_id)  # 将 request_id 加入到请求头

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

        # 构造批量请求
        items = []
        for model_request_item in batch_request_model.items:
            # 动态根据 provider/invoke_type 决定使用哪个 input 字段
            try:
                match (model_request_item.provider, model_request_item.invoke_type):
                    case (ProviderType.GOOGLE, InvokeType.GENERATION):
                        allowed_fields = GoogleGenAiInput.model_fields.keys()
                    case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
                        allowed_fields = GoogleVertexAIImagesInput.model_fields.keys()
                    case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
                        allowed_fields = OpenAIResponsesInput.model_fields.keys()
                    case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
                        allowed_fields = OpenAIChatCompletionsInput.model_fields.keys()
                    case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
                        allowed_fields = OpenAIImagesInput.model_fields.keys()
                    case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_EDIT_GENERATION):
                        allowed_fields = OpenAIImagesEditInput.model_fields.keys()
                    case _:
                        raise ValueError(
                            f"Unsupported provider/invoke_type combination: {model_request_item.provider} + {model_request_item.invoke_type}")

                # 将 ModelRequest 转 dict，过滤只保留 base + allowed 的字段
                model_request_dict = model_request_item.model_dump(exclude_unset=True)

                grpc_request_kwargs = {}
                for field in allowed_fields:
                    if field in model_request_dict:
                        value = model_request_dict[field]

                        # 跳过无效的值
                        if not is_effective_value(value):
                            continue

                        # 序列化grpc不支持的类型
                        grpc_request_kwargs[field] = serialize_value(value)

                        # 清理 serialize后的 grpc_request_kwargs
                        grpc_request_kwargs = remove_none_from_dict(grpc_request_kwargs)

                items.append(model_service_pb2.ModelRequestItem(
                    provider=model_request_item.provider.value,
                    channel=model_request_item.channel.value,
                    invoke_type=model_request_item.invoke_type.value,
                    stream=model_request_item.stream or False,
                    custom_id=model_request_item.custom_id or "",
                    priority=model_request_item.priority or 1,
                    org_id=batch_request_model.user_context.org_id or "",
                    user_id=batch_request_model.user_context.user_id or "",
                    client_type=batch_request_model.user_context.client_type or "",
                    extra=grpc_request_kwargs,
                ))

            except Exception as e:
                raise ValueError(f"构建请求失败: {str(e)}，item={model_request_item.custom_id}") from e

        try:
            # 超时处理逻辑
            invoke_timeout = timeout or self.default_invoke_timeout

            # 调用 gRPC 接口
            response = self._retry_request(self.stub.BatchInvoke, model_service_pb2.ModelRequest(items=items),
                                           timeout=invoke_timeout, metadata=metadata)

            result = []
            for res_item in response.items:
                result.append(ModelResponse(
                    content=res_item.content,
                    usage=json.loads(res_item.usage) if res_item.usage else None,
                    raw_response=json.loads(res_item.raw_response) if res_item.raw_response else None,
                    error=res_item.error or None,
                    custom_id=res_item.custom_id if res_item.custom_id else None
                ))
            batch_response = BatchModelResponse(
                request_id=response.request_id if response.request_id else None,
                responses=result
            )
            
            # 记录成功日志
            duration = time.time() - start_time
            logger.info(
                f"✅ Batch request completed successfully",
                extra={
                    "log_type": "response",
                    "uri": "/batch_invoke",
                    "duration": duration,
                    "data": {
                        "batch_size": len(batch_request_model.items),
                        "responses_count": len(result)
                    }
                }
            )
            return batch_response
        except grpc.RpcError as e:
            duration = time.time() - start_time
            error_message = f"❌ BatchInvoke gRPC failed: {str(e)}"
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
            error_message = f"❌ BatchInvoke other error: {str(e)}"
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

    def close(self):
        """关闭 gRPC 通道"""
        if self.channel and not self._closed:
            self.channel.close()
            self._closed = True
            logger.info("✅ gRPC channel closed",
                      extra={"log_type": "info", "data": {"status": "success"}})

    def _safe_sync_close(self):
        """进程退出时自动关闭 channel（事件循环处理兼容）"""
        if self.channel and not self._closed:
            try:
                self.close()  # 直接调用关闭方法
            except Exception as e:
                logger.warning(f"⚠️ gRPC channel close failed at exit: {e}",
                           extra={"log_type": "info", "data": {"status": "failed", "error": str(e)}})

    def __enter__(self):
        """同步初始化连接"""
        self._ensure_initialized()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """同步关闭连接"""
        self.close()
