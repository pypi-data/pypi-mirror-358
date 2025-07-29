# Tamar Model Client

**Tamar Model Client** 是一款高性能的 Python SDK，用于连接 Model Manager gRPC 服务，统一调用多家第三方 AI
模型服务商（如OpenAI、Google、Azure OpenAI）。

## ✨ 特性亮点

- 🧩 支持 **同步** / **异步**调用，**流式** / **非流式** 响应
- ⚡ 统一封装 **OpenAI** / **Google** / **Azure OpenAI**，并兼容 **官方SDK** 调用标准
- 🔗 **gRPC** 高效通信，内置 **JWT** 认证、重试机制
- 🛡️ **类型安全校验**（基于 Pydantic v2）
- 📚 **完整异常处理**，API 简单直观，支持批量调用

## 📋 安装

```bash
pip install tamar-model-client
```

支持环境：

- Python ≥ 3.8
- Windows / Linux / macOS

## 🏗️ 项目结构概览

```
tamar_model_client/
├── generated/                      # gRPC 生成的代码
│   ├── model_service.proto         # 协议定义文件
│   ├── model_service_pb2.py        # 生成的 protobuf 代码
│   └── model_service_pb2_grpc.py   # 生成的 gRPC 代码
├── schemas/                  # 数据模型定义
│   ├── inputs.py             # 输入模型定义
│   └── outputs.py            # 输出模型定义
├── enums/                    # 枚举类型定义
│   ├── providers.py          # 模型提供商枚举
│   ├── invoke.py             # 调用类型枚举
│   └── channel.py            # 渠道类型枚举
├── async_client.py           # 异步客户端实现
├── sync_client.py            # 同步客户端实现
├── exceptions.py             # 自定义异常
├── auth.py                   # JWT认证处理器
└── __init__.py               # 包初始化
```

## 🚀 快速开始

### 客户端初始化

```python
from tamar_model_client import TamarModelClient, AsyncTamarModelClient

# 同步客户端
client = TamarModelClient(
    server_address="localhost:50051",
    jwt_token="your-jwt-token"
)

# 异步客户端
async_client = AsyncTamarModelClient(
    server_address="localhost:50051",
    jwt_secret_key="your-jwt-secret-key"  # 使用固定密钥自动生成 JWT
)
```

> 💡 建议通过环境变量配置连接信息，减少硬编码风险（见下文）。


## 🎯 使用示例

#### OpenAI 调用示例

```python
from tamar_model_client import TamarModelClient
from tamar_model_client.schemas import ModelRequest, UserContext
from tamar_model_client.enums import ProviderType, InvokeType, Channel

# 创建同步客户端
client = TamarModelClient()

# OpenAI 调用示例
request_data = ModelRequest(
    provider=ProviderType.OPENAI,  # 选择 OpenAI 作为提供商
    channel=Channel.OPENAI,  # 使用 OpenAI 渠道
    invoke_type=InvokeType.CHAT_COMPLETIONS,  # 使用 chat completions 调用类型
    model="gpt-4",  # 指定具体模型
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ],
    user_context=UserContext(
        user_id="test_user",
        org_id="test_org",
        client_type="python-sdk"
    ),
    stream=False,  # 非流式调用
    temperature=0.7,  # 可选参数
    max_tokens=1000,  # 可选参数
)

# 发送请求并获取响应
response = client.invoke(request_data)
if response.error:
    print(f"错误: {response.error}")
else:
    print(f"响应: {response.content}")
    if response.usage:
        print(f"Token 使用情况: {response.usage}")
```

#### Google 调用示例 （AI Studio / Vertex AI）

```python
from tamar_model_client import TamarModelClient
from tamar_model_client.schemas import ModelRequest, UserContext
from tamar_model_client.enums import ProviderType, InvokeType, Channel

# 创建同步客户端
client = TamarModelClient()

# Google AI Studio 调用示例
request_data = ModelRequest(
    provider=ProviderType.GOOGLE,  # 选择 Google 作为提供商
    channel=Channel.AI_STUDIO,  # 使用 AI Studio 渠道
    invoke_type=InvokeType.GENERATION,  # 使用生成调用类型
    model="gemini-pro",  # 指定具体模型
    contents=[
        {"role": "user", "parts": [{"text": "你好，请介绍一下你自己。"}]}
    ],
    user_context=UserContext(
        user_id="test_user",
        org_id="test_org",
        client_type="python-sdk"
    ),
    temperature=0.7,  # 可选参数
)

# 发送请求并获取响应
response = client.invoke(request_data)
if response.error:
    print(f"错误: {response.error}")
else:
    print(f"响应: {response.content}")
    if response.usage:
        print(f"Token 使用情况: {response.usage}")

# Google Vertex AI 调用示例
vertex_request = ModelRequest(
    provider=ProviderType.GOOGLE,  # 选择 Google 作为提供商
    channel=Channel.VERTEXAI,  # 使用 Vertex AI 渠道
    invoke_type=InvokeType.GENERATION,  # 使用生成调用类型
    model="gemini-pro",  # 指定具体模型
    contents=[
        {"role": "user", "parts": [{"text": "你好，请介绍一下你自己。"}]}
    ],
    user_context=UserContext(
        user_id="test_user",
        org_id="test_org",
        client_type="python-sdk"
    ),
    temperature=0.7,  # 可选参数
)

# 发送请求并获取响应
vertex_response = client.invoke(vertex_request)
if vertex_response.error:
    print(f"错误: {vertex_response.error}")
else:
    print(f"响应: {vertex_response.content}")
    if vertex_response.usage:
        print(f"Token 使用情况: {vertex_response.usage}")
```

#### Azure OpenAI 调用示例

```python
from tamar_model_client import TamarModelClient
from tamar_model_client.schemas import ModelRequest, UserContext
from tamar_model_client.enums import ProviderType, InvokeType, Channel

# 创建同步客户端
client = TamarModelClient()

# Azure OpenAI 调用示例
request_data = ModelRequest(
    provider=ProviderType.AZURE,  # 选择 Azure 作为提供商
    channel=Channel.OPENAI,  # 使用 OpenAI 渠道
    invoke_type=InvokeType.CHAT_COMPLETIONS,  # 使用 chat completions 调用类型
    model="gpt-4o-mini",  # 指定具体模型
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ],
    user_context=UserContext(
        user_id="test_user",
        org_id="test_org",
        client_type="python-sdk"
    ),
    stream=False,  # 非流式调用
    temperature=0.7,  # 可选参数
    max_tokens=1000,  # 可选参数
)

# 发送请求并获取响应
response = client.invoke(request_data)
if response.error:
    print(f"错误: {response.error}")
else:
    print(f"响应: {response.content}")
    if response.usage:
        print(f"Token 使用情况: {response.usage}")
```

### 异步调用示例

```python
import asyncio
from tamar_model_client import AsyncTamarModelClient
from tamar_model_client.schemas import ModelRequest, UserContext
from tamar_model_client.enums import ProviderType, InvokeType, Channel


async def main():
    # 创建异步客户端
    client = AsyncTamarModelClient()

    # 组装请求参数
    request_data = ModelRequest(
        provider=ProviderType.OPENAI,
        channel=Channel.OPENAI,
        invoke_type=InvokeType.CHAT_COMPLETIONS,
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "你好，请介绍一下你自己。"}
        ],
        user_context=UserContext(
            user_id="test_user",
            org_id="test_org",
            client_type="python-sdk"
        ),
        stream=False,
        temperature=0.7,
        max_tokens=1000,
    )

    # 发送请求并获取响应
    async for r in await client.invoke(model_request):
        if r.error:
            print(f"错误: {r.error}")
        else:
            print(f"响应: {r.content}")
            if r.usage:
                print(f"Token 使用情况: {r.usage}")


# 运行异步示例
asyncio.run(main())
```

### 流式调用示例

```python
import asyncio
from tamar_model_client import AsyncTamarModelClient
from tamar_model_client.schemas import ModelRequest, UserContext
from tamar_model_client.enums import ProviderType, InvokeType, Channel


async def stream_example():
    # 创建异步客户端
    client = AsyncTamarModelClient()

    # 组装请求参数
    request_data = ModelRequest(
        provider=ProviderType.OPENAI,
        channel=Channel.OPENAI,
        invoke_type=InvokeType.CHAT_COMPLETIONS,
        model="gpt-4",
        messages=[
            {"role": "user", "content": "你好，请介绍一下你自己。"}
        ],
        user_context=UserContext(
            user_id="test_user",
            org_id="test_org",
            client_type="python-sdk"
        ),
        stream=True,  # 启用流式输出
        temperature=0.7,
    )

    # 发送请求并获取流式响应
    async for response in client.invoke(request_data):
        if response.error:
            print(f"错误: {response.error}")
        else:
            print(f"响应片段: {response.content}", end="", flush=True)
            if response.usage:
                print(f"\nToken 使用情况: {response.usage}")


# 运行流式示例
asyncio.run(stream_example())
```

### 批量调用示例

支持批量处理多个模型请求：

```python
import asyncio
from tamar_model_client import AsyncTamarModelClient
from tamar_model_client.schemas import (
    BatchModelRequest, BatchModelRequestItem,
    UserContext
)
from tamar_model_client.enums import ProviderType, InvokeType, Channel


async def batch_example():
    # 创建异步客户端
    client = AsyncTamarModelClient()

    # 组装批量请求参数
    batch_request = BatchModelRequest(
        user_context=UserContext(
            user_id="test_user",
            org_id="test_org",
            client_type="python-sdk"
        ),
        items=[
            BatchModelRequestItem(
                provider=ProviderType.OPENAI,
                channel=Channel.OPENAI,
                invoke_type=InvokeType.CHAT_COMPLETIONS,
                model="gpt-4",
                messages=[
                    {"role": "user", "content": "第一个问题：什么是人工智能？"}
                ],
                priority=1,
                custom_id="q1"
            ),
            BatchModelRequestItem(
                provider=ProviderType.GOOGLE,
                channel=Channel.AI_STUDIO,
                invoke_type=InvokeType.GENERATION,
                model="gemini-pro",
                contents=[
                    {"role": "user", "parts": [{"text": "第二个问题：什么是机器学习？"}]}
                ],
                priority=2,
                custom_id="q2"
            )
        ]
    )

    # 发送批量请求并获取响应
    response = await client.invoke_batch(batch_request)
    if response.responses:
        for resp in response.responses:
            print(f"\n问题 {resp.custom_id} 的响应:")
            if resp.error:
                print(f"错误: {resp.error}")
            else:
                print(f"内容: {resp.content}")
                if resp.usage:
                    print(f"Token 使用情况: {resp.usage}")


# 运行批量调用示例
asyncio.run(batch_example())
```

### 文件输入示例

支持处理图像等文件输入（需使用支持多模态的模型，如 gemini-2.0-flash）：

```python
from tamar_model_client import TamarModelClient
from tamar_model_client.schemas import ModelRequest, UserContext
from tamar_model_client.enums import ProviderType
from google.genai.types import Part
model_request = ModelRequest(
    provider=ProviderType.GOOGLE,  # 选择 Google作为提供商
    model="gemini-2.0-flash",
    contents=[
        "What is shown in this image?",
        Part.from_uri( # 这个是Google那边的参数支持
            file_uri="https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg",
            mime_type="image/jpeg",
        ),
    ],
    user_context=UserContext(
        org_id="testllm",
        user_id="testllm",
        client_type="conversation-service"
    ),
)
client = TamarModelClient("localhost:50051")
response = client.invoke(
    model_request=model_request
)
```

### ⚠️ 注意事项

以下是使用 Tamar Model Client 时的重要提示：

- **参数处理**
  - 公共参数包括：**服务商 (provider)**、**渠道 (channel)** 、 **调用方法 (invoke_type)** 以及 **用户信息（user_context）**
  - 其中 **channel** 和 **invoke_type** 为可选参数，**建议默认使用系统自动推断**，除非有特殊需求再显式指定
  - 是否流式输出由公共参数 **stream** 控制，其他参数遵循对应服务商官方 SDK 的标准定义
- **客户端连接管理**
  - gRPC 使用 HTTP/2 长连接，**建议将客户端实例作为单例使用**
  - 若需创建多个实例，**请务必调用** `client.close()` **方法手动关闭连接**，以防止连接堆积或资源泄露
- **异常处理**：
  - 所有接口均提供详细的**错误信息** 以及 **请求ID（request_id）**，业务调用时建议纳入对应日志便于后期排错

## ⚙️ 环境变量配置（推荐）

可以通过 .env 文件或系统环境变量，自动配置连接信息

```bash
export MODEL_MANAGER_SERVER_ADDRESS="localhost:50051"
export MODEL_MANAGER_SERVER_JWT_TOKEN="your-jwt-secret"
export MODEL_MANAGER_SERVER_GRPC_USE_TLS="false"
export MODEL_MANAGER_SERVER_GRPC_DEFAULT_AUTHORITY="localhost"
export MODEL_MANAGER_SERVER_GRPC_MAX_RETRIES="5"
export MODEL_MANAGER_SERVER_GRPC_RETRY_DELAY="1.5"
```

或者本地 `.env` 文件

```
# ========================
# 🔌 gRPC 通信配置
# ========================

# gRPC 服务端地址（必填）
MODEL_MANAGER_SERVER_ADDRESS=localhost:50051

# 是否启用 TLS 加密通道（true/false，默认 true）
MODEL_MANAGER_SERVER_GRPC_USE_TLS=true

# 当使用 TLS 时指定 authority（域名必须和证书匹配才需要）
MODEL_MANAGER_SERVER_GRPC_DEFAULT_AUTHORITY=localhost


# ========================
# 🔐 鉴权配置（JWT）
# ========================

# JWT 签名密钥（用于生成 Token）
MODEL_MANAGER_SERVER_JWT_SECRET_KEY=your_jwt_secret_key


# ========================
# 🔁 重试配置（可选）
# ========================

# 最大重试次数（默认 3）
MODEL_MANAGER_SERVER_GRPC_MAX_RETRIES=3

# 初始重试延迟（秒，默认 1.0），指数退避
MODEL_MANAGER_SERVER_GRPC_RETRY_DELAY=1.0
```

加载后，初始化时无需传参：

```python
from tamar_model_client import TamarModelClient

client = TamarModelClient()  # 将使用环境变量中的配置
```

## 开发

### 环境设置

1. 创建虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

2. 安装开发依赖：

```bash
pip install -e .
```

### 生成 gRPC 代码

运行以下命令生成 gRPC 相关代码：

```bash
python make_grpc.py
```

### 部署到 pip
```bash
python setup.py sdist bdist_wheel
twine upload dist/*

```

## 许可证

MIT License

## 作者

- Oscar Ou (oscar.ou@tamaredge.ai)

## 贡献

欢迎提交 Issue 和 Pull Request！ 